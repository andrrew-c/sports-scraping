 # %% All the stuff needed to start 

######################
## System modules
######################

#import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
import json

import imp

import os, sys


## Change path
#os.chdir(os.path.dirname(sys.argv[0]))

import pickle
## Debugging
#import pdb
#pdb.set_trace()


##########################################
## Import selenium
##########################################

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

#############################
## Import own modules
#############################

## Import functions
print("Imported own modules")

## Import class defintions
import classes_whill_sel            ## mc = my classes
import functions_whill_sel as mf

#############################
## Set up global parameters
#############################

## William Hill URL
url_main = "http://sports.williamhill.com/bet/en-gb"
url_main = "http://sports.williamhill.com/bet/en-gb/betlive/9"

## Added this one on 2019-04-02
url_main = "https://sports.williamhill.com/betting/en-gb/in-play/football"

## William hill changed their website around 2019-03-20
## The URL above takes you to the one here - this is only used as a check if the first one changes:
url_new = "https://sports.williamhill.com/betting/en-gb/in-play/all"

## HTML text file
out_html = 'whill.txt'

## Initialise empty list to hold dictionaries for events
games = []

## Change path
#mainpath = os.path.abspath(os.path.dirname(__file__))
mainpath = os.path.abspath(os.path.dirname(sys.argv[0]))
os.chdir(mainpath)
print("Working directory changed to '{}'".format(mainpath))

## Path of shelve object
whdbpath = os.path.join('..', '..', 'whill', 'whilldb')

# %% Initialise browser 

###########################
## Initialise browser
###########################

## Get browser to webpage
browser = mf.initbrowser(url_main, hidebrowser=False)

## Check that browser has not went to another URL (because no games are loaded)
url_loaded = browser.current_url
if url_loaded not in [url_main, url_new]:
    pdb.set_trace()
    print("*"*30, "\nWARNING: Browser is no longer on the intended URL (", url_main, ").\nThis will need checked.... Program terminated")
    print("URL being sent to is: {}".format(url_loaded))
    
    ## Stop program
    sys.exit()
## Event exclusions
event_exclusions_list = {'MultiMatchMarkets':18351}


# %% Update source
ps = browser.page_source


def reload_modules():
    print(imp.reload(mf))
    print(imp.reload(classes_whill_sel))
    


##lists = []
#for i in range(3):
    #soup = bs(browser.page_source, 'html.parser')
    #lists.append(mf.get_live_info(soup))
#    pdb.set_trace()

##soup = bs(browser.page_source, 'html.parser')
##tns = soup.find_all('div', {'class':'markets-group-container'})
##games = {i:tns[i].find_all('div', {'class':'event'}) for i in range(len(tns))}
##numgames = [len(games[i]) for i in games.keys()]


#pdb.set_trace()

## Main run of browser
game_list = mf.GamesEngine(browser, whdbpath)


iEngineRuns = 0
def RunEngine(iRunNum):

    """
        This function is attempting to run the engine repeatedly if an error occurs.
    """
    try:
        iRunNum = iRunNum+ 1
        mf.GamesEngine(browser)
    except:
        print("Error on run number {}:\n{}".format(iRunNum, e))
        print("Will continue processing")
        iRunNum = iRunNum+ 1
        RunEngine(iRunNum = iRunNum+ 1)

    
def CheckAttributeExists(obj, attr):
    """ Returns True if attribute exists"""
    pass



      



# %%  SOME CODE GOES HERE

g1 = soup.find_all('div', {'class':'btmarket__selection'})


## Get all events (hopefully)
g2 = soup.find_all('div', {'class':'event'})



eventID = g2[0]['data-entityid']
startTime = g2[0]['data-startdatetime']
currentTime = g2[0].find('label', {'class':'wh-label btmarket__live go area-livescore event__status'}).text

## Get the games
games = g2[0].find_all('div', {'class':"btmarket__selection"})
with open('blah2.txt', 'wt') as f: f.write(str(games[0]))


"""
# %% Get Scores
scores = g2[0].find_all('label', {'class':'wh-label btmarket__livescore'})[0].find_all('span')

scoresA = scores[0].text
scoresB = scores[1].text



# %% With a game -get score odds etc.


g1 = games[0].find_next()

## Team name
g1_teamname = g1['data-name']

## Team ID
g1_id = g1['data-entityid']

## Odds
g1_num = g1['data-num']
g1_den = g1['data-denom']

# %%

""" 

"""
## From each game
## 
s = "wh-label btmarket__live go area-livescore event__status"
#g2_0 = {'data-entityid':g2[0]['data-entityid'], 'starttime':}
#g2 = soup.find_all('div', {'class':"btmarket__boundary"})
#g3 =soup.find_all('div', {'class':"btmarket"})
#g3a = g3[1]

#g4 = soup.find_all('a', {'class':"btmarket__name btmarket__name--featured"})
#g5 = soup.find_all('div', {'class':"btmarket__content__icons-side"}) 
                         
#g3 = soup.find_all('div', {'class':"btmarket__content-margins"})
"""

"""

<ul class="btmarket__content-margins"><li><a title="Parma vs Atalanta" class="btmarket__name btmarket__name--featured" href="/betting/en-gb/football/OB_EV14252645/parma-vs-atalanta"><div class="btmarket__link-name btmarket__link-name--2-rows"><span>Parma</span> <span>Atalanta</span></div><div class="btmarket__link-name btmarket__link-name--ellipsis show-for-desktop-medium">Parma v Atalanta</div></a></li></ul>

<div class="btmarket__link-name btmarket__link-name--ellipsis show-for-desktop-medium">Parma v Atalanta</div>
"""

# %% Load in whill db

import shelve 

## Path for the shelve object
whdbpath = os.path.join('..', '..', 'whill', 'whilldb')


## Open shelve
#whdb = open(whdbpath)
whilldb = shelve.open(whdbpath)

## Get keys
ks = [i for i in whilldb.keys()]


# %% Get a game to look at
g1 = whilldb[ks[1001]]
for k in dir(g1):
    print(k)
""" """

# %% Main original loop

def ALL():

    myloads = []
    iters = 10000

                
    #with open('html_info.txt', 'wb') as f: f.write(browser.page_source.encode('utf-8'))

    print("Game registry has length '{}'".format(len(Game._registry)))

    ## Init
    starttime = datetime.utcnow()

    try:
        for i in range(iters):

            ##
            starttime = datetime.utcnow()

            ## Output some information to user
            print("\n{0}\nIter: {1} of {2} ({3:.2%})\n{0}".format("*"*40, i, iters, i/iters))

            ## Refresh browser every n iterations
            if i > 0 and i%iRefreshIters == 0:
                print("\nRefreshing browser! :-)\n\n")
                browser.refresh()
                print("Updating DB with {} games".format(len(Game._registry)))
                mf.updatedb(Game._registry, 'whilldb')
            
            ## Make some soup from browser HTML
            soup = bs(browser.page_source, 'html.parser')

            ## Write out soup to pickle, if wanted
            #with open('soup.s','wb') as f: pickle.dump(soup, f)
            
            ################################
            ## Load up static information
            ################################
            
            ## Load up information on events from web source (static)
            static_info = mf.get_static_events(browser = browser, soup = None \
                                , event_exclusions_list = event_exclusions_list
                                , write_html = False, suffix='_iter_'+str(i) )
            if static_info == -9:
                print("Error with data - please check log.")

            ## Else, no problems, continue processing
            else:
               
                ################################################################
                ## Load up dynamic information - loaded live from browser
                ################################################################
                    
                ## Get soup from browser
                print("Getting live information from:", browser.current_url)
                live_info = mf.get_live_info(soup)
                print("Number of live events to load up - ", len(live_info))
                print("Live information loaded, took {} seconds.".format(datetime.utcnow()-starttime))

                ## For each live event in browser soup
                for game in live_info:

                    ## If game not in registry - add game
                    if game not in Game._registry:

                        ## Tell user new game to be added
                        print("Game not in regitry.  Need to check blacklist")

                        ## Check game ID is not in black list                    
                        if game not in Game._blacklist:
                            print("Game not in blacklist either - will add game, with ID:", game)
                            ## Then, if i > 0 (i.e. don't refresh on first run for each
                            if i > 0:
                                browser.refresh()
                                print("Refresh browser first....")

                        ## Check again, in case of error
                        if game in static_info:
                            ## Exclude any multi markets
                            if static_info[game]['markets'][0]['blurb'] == '':
                                Game( static_info[game], live_info[game] )
                            else:
                                print("Game with event id '{}' has a blurb. Worth checking".format(game))
                            
                    ## Else, live information key is already in registry in memory - update that game
                    else:
                        #print("Game IN registry - to be updated", game)
                        Game._registry[game].update_teams(live_info[game])


                if iters > 1:
                    print("Sleeping....")
                    #endtime = datetime.utcnow()
                    time.sleep(3)
        check = input("Do you want to save the DB?\nY/N... ")
        if check.casefold() == 'y':
            mf.updatedb(Game._registry, 'whilldb')
        else:
            pass
    except KeyboardInterrupt as e:
        check = input("Do you want to save the DB?\nY/N... ")
        if check.casefold() == 'y':
            mf.updatedb(Game._registry, 'whilldb')
        else:
            pass
