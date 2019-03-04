#
sports-scraping
In game betting and scraping related to sports

## Author: Andrew Craik

# Purpose

This project started in 2017.  I started this originally because I was interested in the live, in game, betting provided by online sites, such as William Hill.  I tried to find a way to download the data (badly) using Excel and VBA and got nowhere.  Later on, with some more experian with Python I have been able to get the project to run, using football data only

It collects live data, during play on various tournaments. Teams are recorded and scores and changing odds are scraped.  The code uses an instance of a chrome browser, using Selenium to drive Chrome.  I run this on a headless Unix box.

# What do I need to do?
## whill-stream-windows.py
This is the master program running in python.  The process will only iterate for n times (specified in the code).  This could be updated to run as a daemon.

# classes_whill_sel.py

This program holds the class objects used to run the scraper.

## Game
A game object takes in static_event_info and live_event_info scraped from the browser. The code is currently set up to run for football only at the moment.

### Game properties
#### \_registry
The registry is a dictionary holding all of the event IDs.  This is shared across all instances of of the class object.  
The registry is updated when the new instance is created.
#### \_blacklist
A list of blacklisted IDs.  Common all instances of class.
#### startdate
String holding date in ?? format
#### sport_name
String holding sport name - currently only developed a football version of the code
#### event
Numeric ID of the event (or game).  These might be recycled by the website so I'm currently using start date and event to uniquely identify games.
#### tournament_id
#### tournament
#### start_time
#### secs_to_start
#### selections
#### teams
#### 
## static_event_info
Some information for each game is static and doesn't change unless the browser is refreshed

### Game methods
#### initteams
#### checkexists
#### update_teams
#### update_game
#### hasstarted

### static_event_info
### live_event_info


## Team
#### parent    - game the team belongs to
#### name      - name of the team
#### home      - 'A' for away team, 'H' for home team and 'D' for draw (third team)
#### scoretype - text description of the team's score (home away, etc.)
#### market_id - ID used to identify the team's 'market' ID - used for betting
#### odds      - dictionary holding all recorded odds with time in seconds
#### score     - dictionary holding all recorded scores (time in seconds)

## Required modules

selenium driver
beautiful soup


