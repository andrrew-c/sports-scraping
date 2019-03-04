######################
## System modules
######################

#import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
import json
import time
import os, sys


import pickle
## Debugging
#import pdb
#pdb.set_trace()

##################################
## Some settings
##################################

iRefreshIters = 15

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
from classes_whill_sel import *        ## mc = my classes
import functions_whill_sel as mf

#############################
## Set up global parameters
#############################

## William Hill URL
url_main = "http://sports.williamhill.com/bet/en-gb"
url_main = "http://sports.williamhill.com/bet/en-gb/betlive/9"

## HTML text file
out_html = 'whill.txt'

## Initialise empty list to hold dictionaries for events
games = []

## Change path
mainpath = os.path.abspath(os.path.dirname(__file__))
os.chdir(mainpath)
print("Working directory changed to '{}'".format(mainpath))

###########################
## Initialise browser
###########################

## Get browser to webpage
browser = mf.initbrowser(url_main, False)

## Check that browser has not went to another URL (because no games are loaded)
url_loaded = browser.current_url
if url_main != url_loaded:
    print("*"*30, "\nWARNING: Browser is no longer on the intended URL (", url_main, ").\nThis will need checked.... Program terminated")
    
    ## Stop program
    sys.exit()
## Event exclusions
event_exclusions_list = {'MultiMatchMarkets':18351}

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
