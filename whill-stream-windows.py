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

########################
## Path of shelve object
########################

## This will now handle running in two different base folders (2019-05-15)

## If two folders up is "GitHub" then path should have two folders up;
if os.path.basename(os.path.abspath(os.path.join('..',os.curdir))) == "GitHub":
    whdbpath = os.path.join('..', '..', 'whill', 'whilldb')
    
## Else, is the current folder 'whill'
elif os.path.basename(os.path.abspath(os.curdir)) == 'whill':
    whdbpath = os.path.abspath(os.path.join('.', 'whilldb'))

else:
    print("Error: Current path is '{}'\nNot recognised by program.  Please check")
    input("Press enter to exit...")
    exit()


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
    
