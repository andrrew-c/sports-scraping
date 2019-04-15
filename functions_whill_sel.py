import pdb
from datetime import datetime

import time     ## Time delays



##################################
## Some settings
##################################

## How many iterations until DB saved?
iRefreshIters = 15


## Length of sleep if no games
lenSleep = 15

#refreshCurrentCount, refreshAllowCount, refreshLastTime, refreshAllowance):


def initbrowser(url, hidebrowser=False):

    """
        Initialises browser to scrape web data
        returns object browser (driver) - selenium object.

        Only needs to be run once per session.#

        url: url to load up
        hidebrowser: Minimise browser if True

        Dependencies: Will require selenium to control a browser.
            This has been developed bsaed on Chrome.  Not sure if other browsers will work (they should!)

        Suggested improvements:
            - Ability for python to pick up an existing session 
    """

    ## Import os, system
    import os
    import sys

     
    #############################################
    ## Import selenium
    #############################################import time
    
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys

    ###############################################
    ## Linux 
    ###############################################
    
    ## If running on linux open up pyvirtualdisplay to open browser
    if sys.platform == 'linux':

        from pyvirtualdisplay import Display

        driver_path = r'/home/public/python/chrome/chromedriver'
        print("NOTE: Driver path for chrome set as '{}'\nThis is hard-coded in '{}'".format(driver_path, os.path.abspath(__file__)))
    
        
        
        disp_size = (1024, 768)
        display = Display(visible=0, size=disp_size)
        display.start()
        
        browser = webdriver.Chrome(driver_path)
    
    ## Else, on windows - specify path
    else:
        #browser_path = "C:\\Program Files\\Python36\\selenium\\webdriver\\chrome\\chromedriver.exe"
        browser_path = os.environ['CHROME_DRIVER']
        sys.path.append(os.environ['CHROME_DRIVER'])
        print("Opening browser with URL", url)
        browser = webdriver.Chrome(os.environ['CHROME_DRIVER'])
        
    


    ##  hide browser
    if hidebrowser: 
        print("Hiding browser - current position (before moving)\n", browser.get_window_position())
        browser.set_window_position(0,10000)
    
    ## Get browser to webpage
    browser.get(url)
    return browser


def GamesEngine(browser, dbname, iters=None):

    """

        Purpose:  This is the real engine of the scraper.
            
        Inputs:    browser - is an instance of a selenium browser.
                    iters - Integer, determines how many times to loop over
                    
    """

    ## Import datetime
    from datetime import datetime
    from bs4 import BeautifulSoup as bs

    ## Class definition - game object
    from classes_whill_sel import Game        ## mc = my classes

    ## How many times can browser be updated between allowed time
    refreshAllowCount = 3

    ## How many seconds between refreshed where multiple refreshed are allowed?
    refreshAllowance  = 180     ## 3 minutes

    ## Initialise the counter for the number of refreshes..
    iBrowsRefreshCount = 0

    ## Initialise browser refresh as 'now'
    refreshLastTime = datetime.now()

    
    """ Added: 2019-04-04 """

    ## If user has not specified a number, set to a relatively large number
    if iters == None:
        iters = 1000000

    ## Error handling, try
    try:

        #pdb.set_trace()

        ## Looping over iterations
        for i in range(iters):

            ## Print the iteration number
            print("Iter {:,}".format(i))

            ## Make a note of how long it takes, it starts here
            starttime = datetime.utcnow()

            ## Output some information to user
            print("\n{0}\nIter: {1:,} of {2:,} ({3:.2%})\n{0}\n".format("*"*40, i, iters, i/iters))

            ## Refresh browser every n iterations
            if i > 0 and i%iRefreshIters == 0:
                print("\nRefreshing browser! :-)\n\n")
                canRefresh, refreshLastTime, iBrowsRefreshCount = browserRefreshCheck(iBrowsRefreshCount, refreshAllowCount, refreshLastTime, refreshAllowance)
                
                if canRefresh:
                    browser.refresh()
                    time.sleep(1)
                    
                
                print("Updating DB with {} games".format(len(Game._registry)))
                updatedb(Game._registry, dbname)
            
            ## Make some soup from browser HTML
            soup = bs(browser.page_source, 'html.parser')
     
            ################################################################
            ## Load up dynamic information - loaded live from browser
            ################################################################
                
            ## Get soup from browser
            print("Getting live information from:", browser.current_url)
            live_info = get_live_info(browser, soup)
            print("Number of live events to load up - {}".format(len(live_info)))
            print("Live information loaded, took {} seconds.".format(datetime.utcnow()-starttime))

            ## Init refresh browser to false - sometimes we need to force it            
            refreshBrowser = False

            ## Only need to proceed if there is some live information to loop through
            if len(live_info) > 0:
                
                ## For each live event in browser soup
                for game in live_info:

                    ## if game not ready to load up
                    if live_info[game]['currentTime'] == 'Live':
                        print("Skipping game with ID {} due to live.....".format(game))
                        break

                    ## If game not in registry - add game
                    if game not in Game._registry:

                        ## Tell user new game to be added
                        print("Game not in registry.  Need to check blacklist")

                        ## Check game ID is not in black list                    
                        if game not in Game._blacklist:
                            #print("Game not in blacklist either - will add game, with ID:", game)
                            ## Then, if i > 0 (i.e. don't refresh on first run for each
                            if i > 0:
                                refreshBrowser = True
                                
                            ## Game new to registry and not in blacklist - add it
                            Game(game, live_info[game], i)
                

                    ## Update teams for game
                    Game._registry[game].update_teams(live_info[game], i)

                    ## Remove any games from registry if not been updated in, say 3 minutes
                    

                print("Processed {} games".format(len(live_info)))
                #pdb.set_trace

                ## If something has happened above to force browser refresh, refresh it
                ## Things that will cause it are:
                ## Game found not in registry or blacklist - likely to be others we want to find
                if refreshBrowser:
                    canRefresh, refreshLastTime, iBrowsRefreshCount = browserRefreshCheck(iBrowsRefreshCount, refreshAllowCount, refreshLastTime, refreshAllowance)
                    if canRefresh:
                        print("Forcing browser refresh")
                        browser.refresh()
                        time.sleep(1)
                    
                if iters > 1:
                    print("Sleeping....")
                    #endtime = datetime.utcnow()
                    time.sleep(3)
        ## 
#        checkAndSaveDB(Game, dbname)
            ## Else, there are no games
            else:
                print("No  games, sleep {}".format(lenSleep))
                time.sleep(lenSleep)

        ##### FIND A WAY TO PURGE GAMES WHICH HAVE COMPLETED AND REMOVE THEM FROM THE REGISTRY
            
    except KeyboardInterrupt as e:

        debugStop()
        checkAndSaveDB(Game._registry, dbname)
        return Game._registry
        
    
def checkAndSaveDB(Games, dbname):
    """ Added: 2019-04-11 """
    check = input("Do you want to save the DB?\nY/N... ")
    if check.casefold() == 'y':

        updatedb(Games, dbname)

    else:
        pass

def debugStop():
    check = input("Do you want to debug? Y/N: ")
    if check.casefold() == 'y':
        pdb.set_trace()
        

def get_live_info(browser, soup):

    """
    This module takes soup (from BeautifulSoup (bs4)) and returns a dictionary with information on the game, team and odds.
    The dictionary is in format:
        {game_id:
            {'tournament_id', 'tournament', 'score_home', 'score_away', 'time'
            , team_id_X:
            {'num', 'den'}
    """

    #print("Need to update this to get the tournament ID for each game")
    #print("Need to update this to get the tournament ID for each game")
    

    ## Import any modules required
    import re                       ## Regular expressions
    import dict_recur as dr         ## this module is on python path

    #######################################
    ## Initialise some lists/dicts
    #######################################
    
    ## Missing score strings (goal - when goal happens)
    miss_score_list = ['goal!', 'update', '']

    ## keys to keep
    keysToKeep = ['id', 'data-name', 'data-odds', 'data-num', 'data-denom']

    ## Home-flag re-mapping
    ## The integer is based on the order of the data on the web page
    homeFlagMap = {1:'H', 2:'D', 3:'A'}
        
    ## Key for attribute holding date of game
    sDateKey = 'data-startdatetime'

    ## Check that the home team is always first in the list
    homes = []
    
    ## Init dictionary to hold all games
    gamedict = {}

    ## For counting tournaments and events
    tCounter, eCounter = 0, 0
        
    ## Keep a count of games that didn't have a start date
    iNumMissingDate, iNumMissingCurrentTime = 0, 0
        
    #######################
    ## Tournaments
    #######################

    ## Initialise dictionary holding all tournaments on page
    tournamentEvents = {}

    ## Get all 'tournaments' in the page
    start = datetime.now()
    tournaments = soup.find_all('div', {'class':'markets-group-container'})
    end = datetime.now()
    #print("Processed {} tournaments took {}".format(len(tournaments), end-start))
    
    ## If tournaments empty - return nothing
    if len(tournaments) == 0:
        print("Tournaments object has nothing in it - probably zero events live.".format())
        return {}

 
    ## Loop through each tournament
    for tournament in tournaments: #tournamentsEvents.keys():

        ## Keep note of tournaments being processed
        tCounter = tCounter + 1

        ## Get tournament ID
        tournamentID = tournament.next_element['data-entityid']

        ## Get tournament names
        tName = tournament.find('h2').text
        

        start = datetime.now()
        ## Get all games for each tournament
        events = tournament.find_all('div', {'class':'event'})
        events2 = tournament.find_all('div', {'class':'event disabled-event'})
        #pdb.set_trace()
        
        end = datetime.now()
        #print("Identified {} games for tournament {} with name {}".format(len(events), tCounter, tName))
        

        #print("Getting information for games within tournament {}".format(tName))
        
        ## For each event in each tournament
        for event in events: #tournamentEvents[tournament]['games']:

            ## Boolean - should browser be refreshed?
            refreshBrowser = False

            #pdb.set_trace()
            ## Iterate counter
            eCounter = eCounter + 1

            ## Event ID
            eventID = event['id'] 
            
            ## Start date/time for event
            if event.has_attr(sDateKey):
                startTime = event['data-startdatetime']
                #pdb.set_trace()
            else:
                
                #print("No startdate iteration {}, ID = {}".format(eCounter, eventID))
                #pdb.set_trace()
                
                ## Keep a count of games that didn't have a start date
                iNumMissingDate = iNumMissingDate + 1
                refreshBrowser = True
                #print("Event ID {} has no date '{}'".format(eventID, sDateKey))
                break
                #startTime = None
                
            
            ## Current time
            timeTag = event.find('div', {'class':'btmarket__boundary'})

            ## If there's no time in the 'tag'
            if timeTag != None:
                
                currentTime = timeTag.text
            else:

                ## Can try and find time text using 'label'
                timeTag = event.find('label')

                ## If 
                if timeTag != None:
                    currentTime = timeTag.text

                if timeTag == None:

                    #pdb.set_trace()
                    
                    print("Iteration {:,} of {:,}, no time".format(eCounter, len(events)))
                    iNumMissingCurrentTime = iNumMissingCurrentTime +1
                    refreshBrowser = True
                    #pdb.set_trace()
                    #print("Event with ID {} has no time tag".format())
                    break
                    #currentTime = -9

            
            ## Update game dictionary with this game
            dr.update(gamedict, {eventID:{'startTime':startTime, 'currentTime':currentTime}})

            ##########################
            ## Scores
            ##########################

            ## BS tag for scores
            scoresTagAll = event.find_all('label', {'class':'btmarket__livescore'})

            ## Get the actual tag
            if len(scoresTagAll) > 0:
                scoresTag = scoresTagAll[0]
            else:
                # Score information missing - ignore this team (on this loo
                print("Scores missing - event ID {}".format(eventID))
                break

            ## Scores not missing continue
            scoresDict = {}
  
            ## Score - home
            scoresDict.update({'H':scoresTag.find_next().text})

            ## Score - away
            scoresDict.update({'A':scoresTag.find_next().find_next().text})

            ##############################
            ## Teams
            ##############################
            
            ## For each event, get information on teams

            teamInfo = {}
            ## Get the teams
            teams = event.find_all('div', {'class':"btmarket__selection"})
            teams = [t.next_element for t in teams]
##            if eventID == 'OB_EV14434648':
##                pdb.set_trace()
            teamCounter = 0 
            for team in teams:
                teamCounter = teamCounter + 1

                ## Team information as dictionary
                tDict1 = dict(team.attrs)


                ## String holding A or H
                homeFlag = homeFlagMap[teamCounter]
                
                ## Only keep keys I want
                tDict = {key: tDict1[key] for key in keysToKeep}

                ## Add on score for 'home' or 'away'             
                if homeFlag != 'D':
                    tDict.update({'score':scoresDict[homeFlag]})

                dr.update(gamedict, {eventID:{'tournamentID':tournamentID, 'tournament':tName, homeFlag:tDict}})
##                if eventID == 'OB_EV14441119':
##                    pdb.set_trace()

            
    ## Do we need to fresh the browser?
    if refreshBrowser:
        print("\nThere were {} with no start date and {} with no current time (out of {})".format(iNumMissingDate, iNumMissingCurrentTime, eCounter))
        print("Refreshing browser as a result")
        
        # REMVOED 2019-04-11  browser.refresh()
        time.sleep(1)
    print("End of looping over {} tournaments".format(len(tournaments)))
    
    #pdb.set_trace()
    return gamedict





def gettags(browser, tag, myclass, myclassstring):
    
    """
        Returns list matching tag, myclass, myclasstring

        Suggested Improvements (2019-04-09):
            - make 'find_all' and 'find' options
            - work out whether we need to import bs
            - find out make 'soup' an object we can pass to the function
            - myclassstring can be a dictionary
        
    """
    
    from bs4 import BeautifulSoup as bs
    #import re
    
    ## make soup from items
    soup = bs(browser.page_source, 'html.parser')
    
    if myclass != None:
        return soup.find_all(tag, {myclass:myclassstring})
        print("Returning some soup")
    else:
        return soup.find_all(tag)
    
        

    


###########################################################
###########################################################
###########################################################



def updatedb(games, dbout):

    """
        Purpose:     
        Date:        2019-04-04
        Author:      Andrew Craik
        Inputs:    
           
            games - current registry
            dbout - string contraining name of db to update

     
    
    """
    
    
    import shelve
    from datetime import date
    
    db = shelve.open(dbout, writeback=True)

    testID = '' #'OB_EV14441124'
    
    #pdb.set_trace()
    ## Print message to user
    print("{0} Updating DB {0}".format('*'*40))
    
    ## For each game in memory
    for game in games:

        if game == testID:
            pdb.set_trace()
    
        ## If game ID is already in DB
        if game in db: 
        
            if games_have_same_start_date(db[game], games[game]):
                #print("Game matches start date - can be updated")
                db[game].update_game(games[game])
                #db[game] = tempgame
                #db[game].update_game(games[game])
            else:
                new_id = games[game].event + games[game].startdate.strftime('%Y_%m_%d')
                #print("Games have same ID but different start date - new game will be given new ID: ", new_id)
                db[new_id] = games[game]
                
        ## Else, game can be saved as is...   
        else:
            db[str(game)] = games[game]
        
    db.close()
    
def updatedbforce():

    updatedb(Game._registry, dbname)


def browserRefreshCheck(refreshCurrentCount, refreshAllowCount, refreshLastTime, refreshAllowance):

    """
        Returns a boolean saying whether we can update browsr
                - time since last refreshand the refresh counter

        refreshCurrentCount      = Integer - holding last count of the number of times the browser has been refreshed
        refreshAllowCount
        refreshLastTime       = datetime.time - when was the browser last refreshed?
        refreshAllowance  = Integer, how many seconds between refreshes are allowed for multiple
    """

    #pdb.set_trace()

    secsSince = (datetime.now()-refreshLastTime).seconds 
    ## If browser has been refreshed more than the allowance 
    if refreshCurrentCount > refreshAllowCount:

        ## Check whether it has been long enough since last update
    
        ## If the number of secon
        if secsSince < refreshAllowance:
            print("Browser refresh: There have been {} refreshes within refresh allowance of {} seconds.  Will wait.".format(refreshCurrentCount, refreshAllowance))
            return False, refreshLastTime, refreshCurrentCount + 1
        
        ## It has now been long enough
        else:
            ## Browser can be refreshed, reset counter
            print("Browser refresh: Refresh counter = {} and there have been {} seconds since last refresh".format(refreshCurrentCount, secsSince))
            return True, datetime.now(), 0
        
    ## Else, browser has not been refreshed more than the allowance
        ## Go ahead :-)
    else:
        print("Browser refresh: Not exceeded limit of {} with {}.".format(refreshAllowCount, refreshCurrentCount))
        return True, refreshLastTime, refreshCurrentCount + 1
        
def get_browser(browser):
    browser.set_window_position(0,0)
    
def pickle_livestatic(live, static):
    import pickle
    
    datetime = input("Enter date/time in format you requrie")
    
        
    pickle.dump(staic_info, open(datetime + "static_error.txt") )
    pickle.dump(live_info, open(datetime + "live_error.txt") )
    print("Pickled erro date")
    
    
def games_have_same_start_date(dbgame, newgame):
    """
        Return true if games match start date
    """
    if not hasattr(dbgame, 'startdate') or not hasattr(newgame, 'startdate'):
        pdb.set_trace()
    return dbgame.startdate == newgame.startdate
