import pdb
from datetime import datetime

import time     ## Time delays



##################################
## Some settings
##################################

iRefreshIters = 15

def initbrowser(url, hidebrowser=False):

    """
        Initialises browser to scrape web data
        returns object browser (driver) - selenium object.

        Only needs to be run once per session.#

        url: url to load up
        hidebrowser: Minimise browser if True
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


def GamesEngine(browser, iters=None):

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
    
    """ Added: 2019-04-04 """

    ## If user has not specified a number, set to a relatively large number
    if iters == None:
        iters = 1000000


    ## Error handling, try
    try:

        ## Looping over iterations
        for i in range(iters):

            ## Print the iteration number
            print("Iter {:,}".format(i))

            ## Make a note of how long it takes, it starts here
            starttime = datetime.utcnow()

            ## Output some information to user
            print("\n{0}\nIter: {1:,} of {2:,} ({3:.2%})\n{0}".format("*"*40, i, iters, i/iters))

            ## Refresh browser every n iterations
            if i > 0 and i%iRefreshIters == 0:
                print("\nRefreshing browser! :-)\n\n")
                browser.refresh()
                print("Updating DB with {} games".format(len(Game._registry)))
                updatedb(Game._registry, 'whilldb')
            
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

            ## For each live event in browser soup
            for game in live_info:

                ## if game not ready to load up
                if live_info[game]['currentTime'] == 'Live':
                    print("Skipping due to live.....")
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
                            #print("Refresh browser first....")

                        ## Game new to registry and not in blacklist - add it
                        Game(game, live_info[game])
            
                ## Update teams for game
                
                Game._registry[game].update_teams(live_info[game]) 

            print("Processed {} games".format(len(live_info)))
            #pdb.set_trace

            ## If something has happened above to force browser refresh, refresh it
            ## Things that will cause it are:
            ## Game found not in registry or blacklist - likely to be others we want to find
            if refreshBrowser:
                print("Forcing browser refresh")
                browser.refresh()
                
            

            if iters > 1:
                print("Sleeping....")
                #endtime = datetime.utcnow()
                time.sleep(3)
        check = input("Do you want to save the DB?\nY/N... ")
        if check.casefold() == 'y':
            updatedb(Game._registry, 'whilldb')
        else:
            pass
    except KeyboardInterrupt as e:
        check = input("Do you want to save the DB?\nY/N... ")
        if check.casefold() == 'y':
            updatedb(Game._registry, 'whilldb')
        else:
            pass



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
    
    ## Missing score strings (goal - when goal happens)
    miss_score_list = ['goal!', 'update', '']

    ## keys to keep
    keysToKeep = ['id', 'data-name', 'data-odds', 'data-num', 'data-denom']

    ## Home-flag re-mapping
    ## The integer is based on the order of the data on the web page
    homeFlagMap = {1:'H', 2:'D', 3:'A'}
    

    ## Initialise dictionary holding all tournaments on page
    tournamentEvents = {}

    start = datetime.now()
    ## Get all 'tournaments' in the page
    tournaments = soup.find_all('div', {'class':'markets-group-container'})
    end = datetime.now()
    #print("Processed {} tournaments took {}".format(len(tournaments), end-start))

    
    ## Key for attribute holding date of game
    sDateKey = 'data-startdatetime'

    ## Check that the home team is always first in the list
    homes = []
    
    ## Init dictionary to hold all games
    gamedict = {}

    tCounter = 0

          
    ## For each tournament, keep a note of the number of events
    eCounter = 0

    ## Keep a count of games that didn't have a start date
    iNumMissingDate, iNumMissingCurrentTime = 0, 0
            
    #pdb.set_trace()
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
            else:
                print("No startdate iteration {}, ID = {}".format(eCounter, eventID))
                #pdb.set_trace()
                #browserRefresh = True
                #pdb.set_trace()
                
                ## Keep a count of games that didn't have a start date
                iNumMissingDate = iNumMissingDate + 1
                refreshBrowser = True
                break
                #startTime = None
                
            
            ## Current time
            #pdb.set_trace()
            timeTag = event.find('div', {'class':'btmarket__boundary'})
            #tt2 = event.find('div', {'class':'btmarket__content'}).find('time')
            if timeTag != None:
                
                currentTime = timeTag.text
            else:

                timeTag = event.find('label')
                if timeTag != None:
                    currentTime = timeTag.text

                if timeTag == None:

                    #pdb.set_trace()
                    
                    print("Iteration {:,} of {:,}, no time".format(eCounter, len(events)))
                    iNumMissingCurrentTime = iNumMissingCurrentTime +1
                    refreshBrowser = True
                    #pdb.set_trace()
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

                #pdb.set_trace()
                ## Update (recursively) the event dictionary
                #pdb.set_trace()
                dr.update(gamedict, {eventID:{'tournamentID':tournamentID, 'tournament':tName, homeFlag:tDict}})
            #pdb.set_trace()

            
            #pdb.set_trace()
    ## Do we need to fresh the browser?
    if refreshBrowser:
        print("\nThere were {} with no start date and {} with no current time (out of {})".format(iNumMissingDate, iNumMissingCurrentTime, eCounter))
        print("Refreshing browser as a result")
        
        browser.refresh()
    print("End of looping over {} tournaments".format(len(tournaments)))
    
    #pdb.set_trace()
    return gamedict




def getgameslist_sel(browser
                     , event_exclusions_list
                     , write_html = False
                     , write_scripts = False
                     , suffix=None):

    """

        Run through browser page, and return dictionary with information
        
    """
    

    from bs4 import BeautifulSoup as bs
    import sys
    import json
    
    ## Script string - used to get the script we're interested in
    script_string = "document.aip_list.create_prebuilt_event("      ## used to identify scripts of interest
    script_string_end = ")\n"

    ################################
    ## Get page source
    ################################
    
    ps = browser.page_source

    ## Making soup
    print("Making soup.....")
    soup = bs(ps, 'html.parser')

    ################################################
    ## Entire HTML - If user wants to write out html
    ################################################
    
    if write_html:
        #out_html = input("Type name of file to write HTML out to.\nwhill.txt is standard")
        out_html = 'html_out' + str(suffix) + '.txt'
        ## Write out text file of HTML
        file = open(out_html, 'wb')
        file.write(ps.encode('utf-8'))
        file.close()
        print("HTML data written to file: ", out_html)

    ################################################
    ## Create function which returns list of games for tournament in script tag
    ################################################
        
    #### Find all script objects in response - where script_string is in script
    # scripts = [s for s in soup.find_all('script', {'type':'text/javascript', 'language':'Javascript'}) if script_string in s.text]
    scripts = [s.text[s.text.find(script_string)+len(script_string):s.text.find(script_string_end)] for s in soup.find_all('script', {'type':'text/javascript', 'language':'Javascript'}) if script_string in s.text]

    return [json.loads(script) for script in scripts]





def gettags(browser, tag, myclass, myclassstring):
    """
        Returns list matching tag, myclass, myclasstring
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
    
    db = shelve.open(dbout)
    
    #pdb.set_trace()
    ## Print message to user
    print("*"*40, "\nUpdating DB", "*"*40)
    
    ## For each game in memory
    for game in games:
    
        ## If game ID is already in DB
        if game in db.keys():
        
            if games_have_same_start_date(db[game], games[game]):
                #print("Game matches start date - can be updated")
                db[game].update_game(games[game])
            else:
                new_id = games[game].event + games[game].startdate.strftime('%Y_%m_%d')
                #print("Games have same ID but different start date - new game will be given new ID: ", new_id)
                db[new_id] = games[game]
                
        ## Else, game can be saved as is...   
        else:
            db[str(game)] = games[game]
        
    db.close()
    
def updatedbforce():
    updatedb(Game._registry, 'whilldb')
    
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
    return dbgame.startdate == newgame.startdate
