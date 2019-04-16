"""

    Purpose:  This module contains all archived code from the William Hill Python scraping program.
    Author:   Andrew Craik
    Date:     2019-04-06


"""




def get_live_info_20190402(soup):
    
    ## THIS IS INTENDED TO BE THE NEW ONE (2019-04)

    ####################################################################################
    #######  UPDATE 2018-04-26 - COULDN'T GET THIS WORKING!!! RRRRGGH
    ####################################################################################

    """
    This module takes soup (from BeautifulSoup (bs4)) and returns a dictionary with information on the game, team and odds.
    The dictionary is in format:
        {game_id:
            {'score_home', 'score_away', 'time'
            , team_id_X:
            {'num', 'den'}
    """

    ## Import any modules required
    import re                       ## Regular expressions
    import dict_recur as dr         ## this module is on python path
    
    ## Missing score strings (goal - when goal happens)
    miss_score_list = ['goal!', 'update', '']
    
    
    
    ## Key for attribute holding date of game
    sDateKey = 'data-startdatetime'
    
    
    ## Get all events
    
    ## Get all events (hopefully)
    events = soup.find_all('div', {'class':'event'})
    
    ## Check that the home team is always first in the list
    homes = []
    ## Init dictionary to hold all games
    gamedict = {}

    i = 0 
    ## For each event in event list
    for e in events:

        i = i + 1 
        
        try:
                
            ## Init event dictionary ({teamid:{num:-, den:-}})
            
            #########################################################
            ## Some basic checks of event (is this really a game?)
            #########################################################
            
            ## Get basic event information
            
            ## Event ID
            eventID = e['data-entityid']
            
            
            
            ## Start time
            if e.has_attr(sDateKey):
                startTime = e['data-startdatetime']
            else:
                print("Do not have start time key '{}' for event ID {}".format(sDateKey, eventID))
                startTime= ''
            
            ## Current time
            #pdb.set_trace()
            timeTag = e.find('label', {'class':'wh-label btmarket__live go area-livescore event__status'})
            if timeTag != None:
                currentTime = timeTag.text
            else:
                print("Iteration {} of {}, no time".format(i, len(events)))
                currentTime = None
                
            
            
            ## Get the teams
            teams = e.find_all('div', {'class':"btmarket__selection"})
            teams = [t.next_element for t in teams]
                    
            ## Get team ID, name and odds
            iHomeCheck = 0 

            tidx = 0
            for t in teams:
                tidx = tidx + 1
                iHomeCheck = iHomeCheck + 1
                
                #pdb.set_trace()   
                if t.has_attr('id'):
                    teamID = t['id']
                else:
                    print("Iteration team '{}' for game {} has no 'id'".format(tidx, i))

                if t.has_attr('data-name'):
                    teamName = t['data-name']
                else:
                    print("Iteration team '{}' for game {} has no 'data-name'".format(tidx, i))

                ## If first of teams, make note of team name (to check if all first are home)
                if iHomeCheck == 1:
                    homes.append(teamName)
                
                teamNum = t['data-num']
                teamDen = t['data-denom']
                teamOdds = t['data-odds']
                
            
                ## Update game dictionary
                dr.update(gamedict, {eventID:{teamID:{'name':teamName, 'num':teamNum, 'den':teamDen, 'odds':teamOdds}}})
        except AttributeError as ae:
            print("Error on event {}, teams = {}".format(i, teams))
            pdb.set_trace()
            raise(ae)
    print(len(homes))
    pdb.set_trace()   
         
        #with open('blah2.txt', 'wt') as f: f.write(str(games[0]))
        
""" %% Get Scores
#        scores = e.find_all('label', {'class':'wh-label btmarket__livescore'})[0].find_all('span')
#        scoresA = scores[0].text
#        scoresB = scores[1].text
#    
#        t1 = teams[0].next_element['data-name']
#        t2 = teams[1].next_element['data-name']
#        t3 = teams[2].next_element['data-name']
        pdb.set_trace()

"""

def _old():
    
    #print("Some teams are being missed out from live information - so some keys are missing")
    #print("***************************\nCheck get_live_info")
    ###########################################################################
    ## Create a list of all 'live events' in the web page using the soup
    ## Each event has two or more teams
    ## Each team has a score and an odds of winning
    ###########################################################################

    
    ##############################################################################
    ## Get odds information from soup
    ## (each team, including 'draw' should have odds
    ##############################################################################
    
    ## Get odds informcation for each event
    odds_info = soup.find_all('div', {'class':'eventprice'})

    
    ################################################
    ## Team information and odds
    ## From the odds information we isolate team IDs
    ## There will be a 1-1 relationship
    ################################################


    ## Each individual team (within an event) has an ID
    ## Get the team IDs from the odds information
    team_ids = [ re.sub(r'\D', '', team['id']) for team in odds_info]

                
    ##############################
    ## Odds ##
    ##############################
        
    ## Odds of winning - get each teams' odds of winning from the event level information
    odds_string = [ t.contents[0].strip() for t in odds_info ]
    
    odds_num, odds_den = [], []
    ## If odds are evens - set to 1/1
    for string in odds_string:
        if string.casefold() == 'evs':
            odds_num.append(1)
            odds_den.append(1)
            
        ## Else, get numerator and denominator
        else:
            odds_num.append( string[:string.find('/')] )
            odds_den.append( string[string.find('/')+1:] )

    ## Init dictionary
    team_dict = {}
    ## Then loop through each teams with numerator/denominator
    for i in range(len(team_ids)):
        ## Update dictionary 
        team_dict.update({team_ids[i]:{'num':odds_num[i], 'den':odds_den[i]}})
    
    ###################################################
    ## Game information
    ###################################################

    #############################################################
    ## Each of the team will belong to a game M-1 relationship
    ## Each game will have a time (1-1) and a score (1-1)
    #############################################################

    ## tgidt = Team, game ID, time
    tgidt = {}
    
    ## Initialise time and score for this 'game'
    game_dict = {}
    
    odds_num, odds_den = [], []
    
    ## Odds of winning - get each teams' odds of winning from the event level information
    odds_string = [ t.text.strip() for t in odds_info ]

    ## Init o, in case the loop doesn't go anywhere....
    o = 0
    
    ## Loop over each set of odds information
    for o in range(len(odds_info)):

        ## Init variables
        time, secs, mins = -9, -9, -9
            
        #################################################
        ## Time
        ## Time information is needed for next parts
        #################################################
                
        ## Init gameid
        gameid = None
        
        ## For each parent tag in for 'odds_information'
        for game_info in odds_info[o].findAllPrevious('a', {'class':'Score'}):

            ## Get game ID
            gameid = re.sub(r'\D', '', game_info['id'])

            ## If no gameid found, break out
            if gameid in [None, '']:
                break
            dr.update(game_dict, {gameid:{team_ids[o]:team_dict[team_ids[o]]}})
            #pdb.set_trace()
            
            if 'start' in game_info['id']:
                
                time = game_info.text.strip()
                    
                if time.casefold() == 'live':
                    time = -9
                else:
                    mins = time[:time.find(':')]
                    secs = time[time.find(':')+1:]
            
                ## Time in seconds
                try:              
                    time2 = ( int(mins) * 60 + int(secs) )
                except:
                    print("Issue with time.... mins='{}' and secs='{}'".format(mins, secs))
                    next
            
                break

        ## If there's no gameid, stop this loop
        if gameid in [None, '']:
            print("gameid = '{}'.  Loop will be broken.".format(gameid))
            break
        
        ## Update dictionary
        dr.update(game_dict, {gameid:{'time':time2}})
        
        
        ######################################################################
        ## Score
        ## Score information comes in a string like '1-2'
        ## The first score is the home team and the second away
        ## If time is missing (-9) then the scores should also be missing
        ######################################################################

        scorehome, scoreaway = -9, -9
        
        ## For each parent tag in for 'odds_information'
        for game_info in odds_info[o].findAllPrevious('a', {'class':'Score'}):

            ## If tag has score information
            if 'score' in game_info['id']:

                ## Isolate the string
                score = game_info.text.strip()
                
                ## If time refers to a 'live' event and not a game, set to -9
                if game_dict[gameid]['time'] == -9:
                    scorehome, scoreaway = -9, -9
                    break
                
                ## Else, if scores are in the string (i.e. not 'live' or 'update')
                elif score.casefold() not in miss_score_list:
                    #print("game scores string = ", game_scores)
                    scorehome = int(score[:score.find('-')]) 
                    scoreaway = int(score[score.find('-')+1:])
                    break
                
                ## Else, set to missing
                else:
                    #print("*************************** Module: get live info.\nCheck this module for the 'else' case for scores....")
                    scorehome, scoreaway = -9, -9
                    break

        dr.update(game_dict, {gameid:{'score_home':scorehome, 'score_away':scoreaway}})
                
            
    print("Processed {} 'odds information' tags.".format(o+1))   
        
    #pdb.set_trace()        
    return game_dict
    

def get_live_info_20190331(soup):

    ####################################################################################
    ## This was archived on 2019-03-31
    ####################################################################################
    
    
    ####################################################################################
    #######  UPDATE 2018-04-26 - COULDN'T GET THIS WORKING!!! RRRRGGH
    ####################################################################################

    """
    This module takes soup (from BeautifulSoup (bs4)) and returns a dictionary with information on the game, team and odds.
    The dictionary is in format:
        {game_id:
            {'score_home', 'score_away', 'time'
            , team_id_X:
            {'num', 'den'}
    """

    ## Import any modules required
    import re                       ## Regular expressions
    import dict_recur as dr         ## this module is on python path
    
    ## Missing score strings (goal - when goal happens)
    miss_score_list = ['goal!', 'update', '']
    
    #print("Some teams are being missed out from live information - so some keys are missing")
    #print("***************************\nCheck get_live_info")
    ###########################################################################
    ## Create a list of all 'live events' in the web page using the soup
    ## Each event has two or more teams
    ## Each team has a score and an odds of winning
    ###########################################################################

    
    ##############################################################################
    ## Get odds information from soup
    ## (each team, including 'draw' should have odds
    ##############################################################################
    
    ## Get odds informcation for each event
    odds_info = soup.find_all('div', {'class':'eventprice'})

    
    ################################################
    ## Team information and odds
    ## From the odds information we isolate team IDs
    ## There will be a 1-1 relationship
    ################################################


    ## Each individual team (within an event) has an ID
    ## Get the team IDs from the odds information
    team_ids = [ re.sub(r'\D', '', team['id']) for team in odds_info]

                
    ##############################
    ## Odds ##
    ##############################
        
    ## Odds of winning - get each teams' odds of winning from the event level information
    odds_string = [ t.contents[0].strip() for t in odds_info ]
    
    odds_num, odds_den = [], []
    ## If odds are evens - set to 1/1
    for string in odds_string:
        if string.casefold() == 'evs':
            odds_num.append(1)
            odds_den.append(1)
            
        ## Else, get numerator and denominator
        else:
            odds_num.append( string[:string.find('/')] )
            odds_den.append( string[string.find('/')+1:] )

    ## Init dictionary
    team_dict = {}
    ## Then loop through each teams with numerator/denominator
    for i in range(len(team_ids)):
        ## Update dictionary 
        team_dict.update({team_ids[i]:{'num':odds_num[i], 'den':odds_den[i]}})
    
    ###################################################
    ## Game information
    ###################################################

    #############################################################
    ## Each of the team will belong to a game M-1 relationship
    ## Each game will have a time (1-1) and a score (1-1)
    #############################################################

    ## tgidt = Team, game ID, time
    tgidt = {}
    
    ## Initialise time and score for this 'game'
    game_dict = {}
    
    odds_num, odds_den = [], []
    
    ## Odds of winning - get each teams' odds of winning from the event level information
    odds_string = [ t.text.strip() for t in odds_info ]

    ## Init o, in case the loop doesn't go anywhere....
    o = 0
    
    ## Loop over each set of odds information
    for o in range(len(odds_info)):

        ## Init variables
        time, secs, mins = -9, -9, -9
            
        #################################################
        ## Time
        ## Time information is needed for next parts
        #################################################
                
        ## Init gameid
        gameid = None
        
        ## For each parent tag in for 'odds_information'
        for game_info in odds_info[o].findAllPrevious('a', {'class':'Score'}):

            ## Get game ID
            gameid = re.sub(r'\D', '', game_info['id'])

            ## If no gameid found, break out
            if gameid in [None, '']:
                break
            dr.update(game_dict, {gameid:{team_ids[o]:team_dict[team_ids[o]]}})
            #pdb.set_trace()
            
            if 'start' in game_info['id']:
                
                time = game_info.text.strip()
                    
                if time.casefold() == 'live':
                    time = -9
                else:
                    mins = time[:time.find(':')]
                    secs = time[time.find(':')+1:]
            
                ## Time in seconds
                try:              
                    time2 = ( int(mins) * 60 + int(secs) )
                except:
                    print("Issue with time.... mins='{}' and secs='{}'".format(mins, secs))
                    next
            
                break

        ## If there's no gameid, stop this loop
        if gameid in [None, '']:
            print("gameid = '{}'.  Loop will be broken.".format(gameid))
            break
        
        ## Update dictionary
        dr.update(game_dict, {gameid:{'time':time2}})
        
        
        ######################################################################
        ## Score
        ## Score information comes in a string like '1-2'
        ## The first score is the home team and the second away
        ## If time is missing (-9) then the scores should also be missing
        ######################################################################

        scorehome, scoreaway = -9, -9
        
        ## For each parent tag in for 'odds_information'
        for game_info in odds_info[o].findAllPrevious('a', {'class':'Score'}):

            ## If tag has score information
            if 'score' in game_info['id']:

                ## Isolate the string
                score = game_info.text.strip()
                
                ## If time refers to a 'live' event and not a game, set to -9
                if game_dict[gameid]['time'] == -9:
                    scorehome, scoreaway = -9, -9
                    break
                
                ## Else, if scores are in the string (i.e. not 'live' or 'update')
                elif score.casefold() not in miss_score_list:
                    #print("game scores string = ", game_scores)
                    scorehome = int(score[:score.find('-')]) 
                    scoreaway = int(score[score.find('-')+1:])
                    break
                
                ## Else, set to missing
                else:
                    #print("*************************** Module: get live info.\nCheck this module for the 'else' case for scores....")
                    scorehome, scoreaway = -9, -9
                    break

        dr.update(game_dict, {gameid:{'score_home':scorehome, 'score_away':scoreaway}})
                
            
    print("Processed {} 'odds information' tags.".format(o+1))   
        
    #pdb.set_trace()        
    return game_dict
    

def get_live_info_archive(soup):

    ####################################################################################
    #######  ARCHIVED 2018-04-26 - COULDN'T GET THIS WORKING!!! RRRRGGH
    ####################################################################################
    """
    This module takes soup (from BeautifulSoup (bs4)) and returns a dictionary with information on the game, team and odds.
    The dictionary is in format:
        {game_id:
            {'score_home', 'score_away', 'time'
            , team_id_X:
            {'num', 'den'}
    """

    ## Import any modules required
    import re                       ## Regular expressions
    import dict_recur as dr         ## this module is on python path
    
    ## Missing score strings (goal - when goal happens)
    miss_score_list = ['goal!', 'update', '']
    
    #print("Some teams are being missed out from live information - so some keys are missing")
    #print("***************************\nCheck get_live_info")
    ###########################################################################
    ## Create a list of all 'live events' in the web page using the soup
    ## Each event has two or more teams
    ## Each team has a score and an odds of winning
    ###########################################################################
    
    #####################
    ## Team level info ##
    #####################
    
    ## Get odds information for each event
    odds_info = soup.find_all('div', {'class':'eventprice'})

    ## Each individual team (within an event) has an ID
    ## Get the team IDs from the odds information
    team_ids = [ re.sub(r'\D', '', team['id']) for team in odds_info]

    ## Odds of winning - get each teams' odds of winning from the event level information
    odds_string = [ t.contents[0].strip() for t in odds_info ]
    
    odds_num, odds_den = [], []
    ## If odds are evens - set to 1/1
    for string in odds_string:
        if string.casefold() == 'evs':
            odds_num.append(1)
            odds_den.append(1)
            
        ## Else, get numerator and denominator
        else:
            odds_num.append( string[:string.find('/')] )
            odds_den.append( string[string.find('/')+1:] )
    
    #################################################
    ## Game level info (i.e. parent to teams) ##
    #################################################
            
    ## For each team, get the parent, game ID and current time of event in browser
    
    game_id_time = []
    tgidt = {}
    #pdb.set_trace()
    print("Looping through soup for odds information to isolate game information")
    for o in range(len(odds_info)):
        
        ## Iterate found information
        iGotInfo = False
        #print("o = {}".format(o))
        ## For each game info going up the tree
        for game in odds_info[o].findAllPrevious('a', {'class':'Score'}):
            #print(game)
            gcnt = 0
            ## If not got information already
            if iGotInfo:
                break
            else:
                gcnt += 1
                #print("gcnt = {}".format(gcnt))
                if 'start' in game['id']:
                    tgidt.update({team_ids[o]:{re.sub(r'\D', '', game['id']):game.text.strip()}})
                    
                    iGotInfo = True
                    #print("got the time for {} dictionary = {}".format(team_ids[o], tgidt))
                    #next

                
    ks = list(tgidt.keys())
    
          
    
            
    #game_id_time = [ [game for game in o.findAllPrevious('a', {'class':'Score'}) if 'start' in game['id']][0] for o in odds_info]

    
    ## Get all game IDs (i.e. the ID of the game that each team belongs to)
    print("Looping through second lot of game information to isolate game IDs.  This list has '{}'".format(len(game_id_time)))
    gidt = {}
    
    
    #game_ids = list(set(game_ids))
    
    ## Team -> Game ID dictionary 
    team_dict = {team_ids[i]:game_ids[i] for i in range(len(team_ids))}
    #pdb.set_trace
    #print(team_dict)
    #input("wait")
    
    ###################################################
    ## Create dictionary for games -> teams -> odds
    ###################################################
    
    game_odds = {}
    
    ## Initialise dictionary with game IDs
    for game in game_ids:
        game_odds.update({game:{}})

    ##############################
    ## Odds ##
    ##############################
        
    ## Then loop through each teams with numerator/denominator
    for i in range(len(team_ids)):
    
        ## Update dictionary 
        temp_dict = {team_dict[team_ids[i]]:
                     {team_ids[i]:
                      {'num':odds_num[i], 'den':odds_den[i]}
                      }
                    }
        #print(temp_dict)
        #input()
        ## Update the dictionary with the temp one (this calls the recursive dictinoary function (update))
        game_odds = dr.update(game_odds, temp_dict)
       
    ##############################
    ## Times ##
    ##############################
        
    ## Get all game times (in seconds)
    time_strings = [game.contents[0].strip() for game in game_id_time]
    
    ## Get true/false list for time_strings
    #events_to_keep = [string.strip().casefold() != 'live' for string in time_strings]
    
    event_times = []
    
    ## Get list of indices for separating out mins/seconds
    for nexttime in time_strings:
        if nexttime.casefold() == 'live':
            event_times.append(-9)
        else:
            mins = nexttime[:nexttime.find(':')]
            secs = nexttime[nexttime.find(':')+1:]
            
            ## Time in seconds
            event_times.append( int(mins) * 60 + int(secs) )
    
    
    ##############################
    ## Scores ##
    ##############################

    ## Get all scores (home/away tuple)
    
    game_scores = [ [game.text for game in o.findAllPrevious('a', {'class':'Score'}) if 'score' in game['id']][0] for o in odds_info]
    
    ## Sometimes weird font or other thigns can get into the text - to remove.
    
    ## Need a proper FOR loop as some scores may be a string (GOAL)
    scores_home, scores_away = [], []
    pdb.set_trace()   
    for i in range(len(event_times)):
        score = game_scores[i]
        ## If time refers to a 'live' event and not a game, set to -9
        if event_times[i] == -9:
            scores_home.append(-9)
            scores_away.append(-9)
            
        ## Else, if scores are in the string (i.e. not 'live' or 'update')
        elif game_scores[i].casefold() not in miss_score_list:
            #print("game scores string = ", game_scores)
            scores_home.append( int(score[:score.find('-')]) )
            scores_away.append( int(score[score.find('-')+1:]) )
        ## Else, set to missing
        else:
            #print("*************************** Module: get live info.\nCheck this module for the 'else' case for scores....")
            scores_home.append(-9)
            scores_away.append(-9)
    
    ## Now upate game dictionary       
    game_time = {game_ids[i]:
                 {'time':event_times[i]
                  , 'score_home':scores_home[i]
                  , 'score_away':scores_away[i]} for i in range(len(game_ids))}
    #pdb.set_trace()   
            
        

    ## Create dictionary with game, time and scores
    dr.update(game_odds, game_time)
    pdb.set_trace()
    ##  Finally - output dictionary 
    return game_odds




   
def get_live_time(soup):
    """
        this function has been developed to print the timer for the user - to test that the linux version can parse live information
    """
    #print(type(soup))
    #input("Wait")
    time = soup.find('a', {'class':'Score'}).text
    return time
    
    
def getliveeventinfo_sel(browser):
    """
    With browser, get all event information into dictionary
    """
    
    # from bs4 import BeautifulSoup as bs
    import re
    
    ## Score/time information (from browser)
    game_level_info = gettags(browser, 'a', 'class', 'Score')
    
    ## Initiailse event dictionary
    event_dict = {}
   
    ## Get ID for event
    event_ids = [re.sub(r'\D', "", game.attrs['id']) for game in game_level_info if game['id'].find('start') != -1]
    print("Event IDs from live info -", event_ids)
    print()
    #input()
    
    events = {}
    for event in event_ids:
    
        temp_time = -9
        score_home = -9
        score_away = -9 
        
        ######################################
        ## Get time 
        ######################################
        
        time_string = [g for g in game_level_info if g['id'].find(event) != -1 and g['id'].find('start') != -1][0].contents[0]
        temp_time_mins = int(time_string[:time_string.find(':')])
        temp_time_secs = int(time_string[time_string.find(':')+1:])
        temp_time = temp_time_mins * 60 + temp_time_secs
            
        ######################################           
        ## Get score
        ######################################
    
        score_string = [g for g in game_level_info if g['id'].find(event) != -1 and g['id'].find('score') != -1][0].contents[0]
        score_home = score_string[0:score_string.find('-')]
        score_away = score_string[score_string.find('-')+1:]
        
        ## Now with time/score - update event
        events.update({event:{'liveinfo':{'time':temp_time, 'score_home':score_home, 'score_away':score_away}}})
    
    #print("**********", events)
    return events

def getliveteaminfo_sel(browser):

    import re     
    ## Get Odds information for each event
    raw_event_info = gettags(browser, 'div', 'class', 'eventprice')
    print(raw_event_info)
    input("****..............")
    ## Initialise dictionary
    market_dict = {}
    
    ## For each event found
    for event in raw_event_info:
    
        ## Get market ID (to link back for each team)
        market_id = re.sub(r'\D', "", event.attrs['id'])
        odds_string = event.contents[0].strip()
        
        ## Initialise odds vars
        num = -1
        den = -1
        evs = 0
        
        ## If the odds provided are evens ('EVS')
        if odds_string.casefold() == 'evs':
            evs = 1
         
        else:
            num = odds_string[0:odds_string.find('/')]
            den = odds_string[odds_string.find('/')+1:]
        
        ## Update dictionary for current market
        market_dict.update({int(market_id): {'evs':evs, 'num':num, 'den':den}})
    
    ## return dictionary with ID (market_id) and odds
    return market_dict


def getliveinfo_sel(browser):

    ## Import modules
    from bs4 import BeautifulSoup as bs
    import re
    
    
    ## Init dictionary to hold information {event: {team: { time: {score, num, den}}}}
    live_info = {}
    
    ## Get team level information
    
    ## First, find each tag which has class 'eventprice'
    odds_info = gettags(browser, 'div', 'class', 'eventprice')
    
    ## Get team IDs for each tag
    team_ids = [re.sub(r'\D', '', i['id']) for i in odds_info]
    
    ## Isolate the current odds for each team
    odds_string = [i.text.strip() for i in odds_info]
    
    ## Create numerator and denominator for odds
    odds_num = [i[:i.find('/')] for i in odds_string]
    odds_den = [i[i.find('/')+1:] for i in odds_string]
   
    ############################################
    ## Event level information
    ############################################
    
    ## Time at current point
    
    ## Get event level info (of type tag) - each element of list contains a list of tags
    event_level_info = [i.findAllPrevious('a', {'class':'Score'}) for i in odds_info]
     
    ## Get event ID
    event_ids = [ re.sub(r'\D', '', i[0]['id']) for i in event_level_info if i[0]['id'].find('start') != -1]
    
    ## Time (seconds) at current point`
    
    return time_strings
    ## Score at current point
   
    ## Score string at current point
    event_scores =[re.sub(r'\D', '', i[0].text) for i in event_level_info if i['id'].find('score') != -1]
    
    ## List of integers for 'home' team scores
    score_home = [int(score[:score.find('-')]) for score in event_scores]
    
    ## List of integers for 'away' team scores
    score_away = [int(score[score.find('-')+1:]) for score in event_scores]
    
    ########################################################
    ## Now create dictionary holding event level information with team
    ########################################################
    
    #live_info = {event_ids[i]: {team_ids[i]:100} for i in range(len(team_ids))}
    return live_info
    
def process_dict(dict_in):
    for game in [g for g in dict_in if g != 'errors']:
        pass





def getgameslist(url, write_html = False, write_scripts = False):

    import requests
    from bs4 import BeautifulSoup as bs
    import json

    """
        Takes URL for William Hill website - returns a list containing
        JSON dictionaries for the events on the page
        url - url to load
    """

	
    script_string = "document.aip_list.create_prebuilt_event("      ## used to identify scripts of interest
    script_string_end = ")\n"

	
    ## Check request and provide user with info
    res = requests.Session().get(url, stream=True)
    if res.raise_for_status() != None:
            print ("Raise for status: ", res.raise_for_status())
    print("Loaded from url: ", url)

    ## Making soup
    print("Making soup.....")
    soup = bs(res.text, 'html.parser')

    if write_html:
        out_html = input("Type name of file to write HTML out to.\nwhill.txt is standard")
        
        ## Write out text file of HTML
        file = open(out_html, 'wb')
        file.write(res.text.encode('utf-8'))
        file.close()
        print("HTML data written to file: ", out_html)

    ## Create function which returns list of games for tournament in script tag

    ##
    #### Find all script objects in response - where script_string is in script
    scripts = [s for s in soup.find_all('script', {'type':'text/javascript', 'language':'Javascript'}) if script_string in s.text]

    # Write out scripts to file (if user wants)
    ##check = input("Do you want to write out all the scripts found in the soup? - Y/N")
    ##if check.upper() == 'Y':
    ##        for s in range(len(scripts)):
    ##                f = open('script_' + str(s) + '.txt', 'wt')
    ##                f.write(scripts[s].text)
    ##                f.close()
    ##                print("Written script no. " + str(s))
    ##

    ## Create empty list to hold events
    events = []
    for tournament in scripts:
            for event in tournament.text.split(';'):
                    if event.strip() != '':
                            events.append(event)

    #### User may want to output all scripts to file
    if write_scripts:
            for e in range(len(events)):
                    
                    myfile = open('event' + str(e) + '.txt', 'wt')
                    myfile.write(events[e])
                    print("Written file no. ", str(e))
                    myfile.close()

    ## Strip out the start/end strings not needed
    events = [event[event.find(script_string)+len(script_string):event.find(script_string_end)] for event in events]

    ## For each event, get all info into a single line
    events_line = [''.join([''.join(line.split()) for line in event]) for event in events]
    
    ## With each event, strip out the start and end points

    ###################################
    #### Parse scripts into JSON data
    ###################################

    ## Product a list of dictionaries holding json information
    #js_dict = [json.loads(event) for event in events_line]
    i = -1

    ## Init dictionary to output
    js_dict = {'errors':{}}
    
    ## Loop through each event in list
    for line in events_line:

        ## Iterate counter
        i += 1
        
        ## Try to encode line into json dictionary
        try:
            js_dict.update({i:json.loads(line)})
        except:
            
            ## Update dictionary holding errors
            try:
                js_dict['errors'].update({'script'+str(i):line})
            except:
                js_dict.update({'errors':{'script'+str(i):line}})
    return js_dict






def updatedb_archived(games, dbout):
    """ Archived on 2019-04-04 """ 
    """
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
                print("Game matches start date - can be updated")
                db[game].update_game(games[game])
            else:
                new_id = games[game].event + games[game].startdate.strftime('%Y_%m_%d')
                print("Games have same ID but different start date - new game will be given new ID: ", new_id)
                db[new_id] = games[game]
                
        ## Else, game can be saved as is...   
        else:
            db[str(game)] = games[game]
        
    db.close()





##############################################################
##############################################################


def get_static_events(browser
                     , soup
                     , event_exclusions_list
                     , write_html = False
                     , write_scripts = False
                     , suffix=None):

    """

        Run through browser page, and return dictionary with information
        2017-04-08- updated.
        the previous code didn't work too well.
        
    """
    
    pdb.set_trace()
    from bs4 import BeautifulSoup as bs
    import sys
    import json
    
    ## Script string - used to get the script we're interested in
    script_string = "document.aip_list.create_prebuilt_event("      ## used to identify scripts of interest
    script_string_end = ");"

    ## If no soup provided, get it from browser
    if soup == None:
        ################################
        ## Get page source
        ################################
        
        ps = browser.page_source

        ## Making soup
        print("Making soup.....")
        soup = bs(ps, 'html.parser')
        
        """  OK - Andrew added 2019-03-26
        You get soup 
        sps = soup.find_all('div', {'class':'event'})
        with sps - find all class-btmarket__selection"""

        ################################################
        ## Entire HTML - If user wants to write out html
        ################################################
        
        if write_html:
            #out_html = input("Type name of file to write HTML out to.\nwhill.txt is standard")
            #out_html = 'html_out' + str(suffix) + '.txt'
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
    #scripts = [s.text[s.text.find(script_string)+len(script_string):s.text.find(script_string_end)] for s in soup.find_all('script', {'type':'text/javascript', 'language':'Javascript'}) if script_string in s.text]
    event_scripts = [s.text for s in soup.find_all('script', {'type':'text/javascript', 'language':'Javascript'}) if script_string in s.text]
    
    ## Each event script may have one or more events - these should be extracted separately
    
    event_scripts_separated = [s.split(script_string) for s in event_scripts]
    
    ## Now remove any missing or blank space
    event_list = [ event_scripts_separated[i][j] for i in range(len(event_scripts_separated)) for j in range(len(event_scripts_separated[i])) if event_scripts_separated[i][j].strip() != '']
    
    ## With each event, remove the extra text around the start and end
    ## I.e. ready to load into JSON 
    event_list_json = [e[:e.find(script_string_end)-len(script_string_end)] for e in event_list]
    
    print("Number of scripts to turn into JSON data = ", len(event_list_json))
    dict_list = [json.loads(event) for event in event_list_json]
    
    ## Return dictionary with event ID as key
    return {dict_list[i]['event']:dict_list[i] for i in range(len(dict_list))}
    ## create dictionary with event IDs as the key
    
    
def get_static_events_201903(browser
                     , soup
                     , event_exclusions_list
                     , write_html = False
                     , write_scripts = False
                     , suffix=None):

    """

        Run through browser page, and return dictionary with information
        2017-04-08- updated.
        the previous code didn't work too well.
        
    """
    
    
    from bs4 import BeautifulSoup as bs
    import sys
    import json
    
    ## Script string - used to get the script we're interested in
    script_string = "document.aip_list.create_prebuilt_event("      ## used to identify scripts of interest
    script_string_end = ");"

    ## If no soup provided, get it from browser
    if soup == None:
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
            #out_html = 'html_out' + str(suffix) + '.txt'
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
    #scripts = [s.text[s.text.find(script_string)+len(script_string):s.text.find(script_string_end)] for s in soup.find_all('script', {'type':'text/javascript', 'language':'Javascript'}) if script_string in s.text]
    event_scripts = [s.text for s in soup.find_all('script', {'type':'text/javascript', 'language':'Javascript'}) if script_string in s.text]
    
    ### 
    
    ## Each event script may have one or more events - these should be extracted separately
    
    event_scripts_separated = [s.split(script_string) for s in event_scripts]
    
    ## Now remove any missing or blank space
    event_list = [ event_scripts_separated[i][j] for i in range(len(event_scripts_separated)) for j in range(len(event_scripts_separated[i])) if event_scripts_separated[i][j].strip() != '']
    
    ## With each event, remove the extra text around the start and end
    ## I.e. ready to load into JSON 
    event_list_json = [e[:e.find(script_string_end)-len(script_string_end)] for e in event_list]
    
    print("Number of scripts to turn into JSON data = ", len(event_list_json))
    dict_list = [json.loads(event) for event in event_list_json]
    
    ## Return dictionary with event ID as key
    return {dict_list[i]['event']:dict_list[i] for i in range(len(dict_list))}
    ## create dictionary with event IDs as the key
    




def BLAHDEBLAH20180426():
    
    
    #################################################
    ## Game level info (i.e. parent to teams) ##
    #################################################
            
    ## For each team, get the parent, game ID and current time of event in browser
    
    game_id_time = []
    tgidt = {}
    #pdb.set_trace()
    print("Looping through soup for odds information to isolate game information")
   

                
    ks = list(tgidt.keys())
    
          
    
            
    #game_id_time = [ [game for game in o.findAllPrevious('a', {'class':'Score'}) if 'start' in game['id']][0] for o in odds_info]

    
    ## Get all game IDs (i.e. the ID of the game that each team belongs to)
    print("Looping through second lot of game information to isolate game IDs.  This list has '{}'".format(len(game_id_time)))
    gidt = {}
    
    
    #game_ids = list(set(game_ids))
    
    ## Team -> Game ID dictionary 
    team_dict = {team_ids[i]:game_ids[i] for i in range(len(team_ids))}
    #pdb.set_trace
    #print(team_dict)
    #input("wait")
    
    ###################################################
    ## Create dictionary for games -> teams -> odds
    ###################################################
    
    game_odds = {}
    
    ## Initialise dictionary with game IDs
    for game in game_ids:
        game_odds.update({game:{}})


    ##############################
    ## Times ##
    ##############################
        
    ## Get all game times (in seconds)
    time_strings = [game.contents[0].strip() for game in game_id_time]
    
    ## Get true/false list for time_strings
    #events_to_keep = [string.strip().casefold() != 'live' for string in time_strings]
    
    event_times = []
    
    ## Get list of indices for separating out mins/seconds
    for nexttime in time_strings:
        if nexttime.casefold() == 'live':
            event_times.append(-9)
        else:
            mins = nexttime[:nexttime.find(':')]
            secs = nexttime[nexttime.find(':')+1:]
            
            ## Time in seconds
            event_times.append( int(mins) * 60 + int(secs) )
    
    
    ##############################
    ## Scores ##
    ##############################

    ## Get all scores (home/away tuple)
    
    game_scores = [ [game.text for game in o.findAllPrevious('a', {'class':'Score'}) if 'score' in game['id']][0] for o in odds_info]
    
    ## Sometimes weird font or other thigns can get into the text - to remove.
    
    ## Need a proper FOR loop as some scores may be a string (GOAL)
    scores_home, scores_away = [], []
    #pdb.set_trace()   
    for i in range(len(event_times)):
        score = game_scores[i]
        ## If time refers to a 'live' event and not a game, set to -9
        if event_times[i] == -9:
            scores_home.append(-9)
            scores_away.append(-9)
            
        ## Else, if scores are in the string (i.e. not 'live' or 'update')
        elif game_scores[i].casefold() not in miss_score_list:
            #print("game scores string = ", game_scores)
            scores_home.append( int(score[:score.find('-')]) )
            scores_away.append( int(score[score.find('-')+1:]) )
        ## Else, set to missing
        else:
            #print("*************************** Module: get live info.\nCheck this module for the 'else' case for scores....")
            scores_home.append(-9)
            scores_away.append(-9)
    
    ## Now upate game dictionary       
    game_time = {game_ids[i]:
                 {'time':event_times[i]
                  , 'score_home':scores_home[i]
                  , 'score_away':scores_away[i]} for i in range(len(game_ids))}
    #pdb.set_trace()   
            
        

    ## Create dictionary with game, time and scores
    dr.update(game_odds, game_time)
    pdb.set_trace()
    ##  Finally - output dictionary 
    return game_odds

   




class Game_Archive_20190404:

    """
    A William Hill Game Class
    When initialised it has a start date, sport name, event (ID number)
    
    """

    _registry = {}
    _changelist    = ['odds', 'score']
    _blacklist = []     ### Blacklisted IDs
    
    def __init__(self, static_event_info, live_event_info):

        
        """
            The Game class object
        """
          
    
        from datetime import date

        
        
        if static_event_info['selections'][0]['fb_result'] != '-':
            ## Check there is a team to update
                
            ## Set up startdate for events - to stop different events with the same ID being overwritten
            self.startdate = date.today()
        
            ## Sport name - string
            self.sport_name         = static_event_info['sport']['sport_name']
            
            ## Event ID - string - used as game level unique ID - need ot check that's OK to do
            self.event              = static_event_info['event']      ## ID for event
            
            ## Add new game to game registry for this class
            self._registry.update({self.event:self})
            
            self.tournament_id      = static_event_info['type']['type_id']
            self.tournament         = static_event_info['type']['type_name']
            self.start_time         = static_event_info['start_time']
            self.secs_to_start      = static_event_info['secs_to_start_time']
            self.selections         = static_event_info['selections']
            
            ## Each game has three teams (home/away/draw)
            self.teams              = self.initteams(static_event_info, live_event_info)
        else:
            self._blacklist.append(static_event_info['event'])
   
    def initteams(self, static_event_info, live_event_info):

        """ 
        
        Initialise team class for event
        Input static_event_info: static 'event' level information
            
        """
        #print("Teams should be a dictionary with market_id as the ID - this would avoid the need for any FOR loops when matching teams")
        return [Team(self, static_event_info, static_event_info['selections'][i]) for i in range(len(static_event_info['selections']))]

    def archive_init_events(self, events):
            """
            Using list comprehension this initialises all events into games
            """
            ## Initialises all events into 'game' objects
            #[print(type(events[i])) for i in events]
            [Game(events[i]) for i in events] 
            
    

    def checkexists(self, event_to_check):
            """
            Looks through list of events and checks whether already exists
            Returns True if already exists
            """
            output = False
            ## Loop through all in registry
            for game in self._registry:
                    ## If event id in list, stop, return True
                    if event_to_check == game.event:
                            return True


    def update_teams(self, live_event_info):
    
        """
        This function is called to update the odds and scores for each team in a game
        """
        #pdb.set_trace()
        ## Get current time (in seconds)
        time = live_event_info['time']
        #print(live_event_info)
        #print("Time = ", time)
        
        ## Iterate through each team in game
        for team in self.teams:
        
                #print("market id type", type(team.market_id))
               # [print( type(k), k) for k in live_event_info.keys()]
                
                # Update odds, if changed (or not yet initialised)
                # print(live_event_info.keys())
                # print(team.market_id, type(team.market_id))
                
                ## Only try an update if teams information in live info
                if team.market_id in live_event_info:

                    ## Update odds
                    team.update_odds(live_event_info[team.market_id], time)

                    # Update score, if changed (or not yet initialised)
                    team.update_score(time = time, live_info = live_event_info)
                            
   
    def update_game(self, new_game):
    
        """ Update DB:
               This function updates the class instance with new informatsion on odds and scores
        """
        
        import dict_recur as dr
        
        ## List of attributes
        attr_list = ['odds', 'score']
        
        ## For each team in DB
        try:
            for current_team in self.teams:
                     
                ## Match with new team to be updated
                for new_team in new_game.teams:
                    
                    ## When IDs match
                    if current_team.market_id == new_team.market_id:
                                             
                        ## Update each attribute (dictionary) 
                        for attr in attr_list:
                        
                            ## Update attribute
                            setattr(current_team, attr, current_team.update_team_attribute(new_team, attr))
                            #print("Updated team attribute: ", attr, " for team ", current_team.name, " to ", getattr(current_team, attr))
        except:
            print("There's an issue with record:", self.event, "this will need checked.")
            
            
           
            
        
    def hasstarted(self):
        """ Not sure if this function is used.  
        """
        ## If time to start is positive, game has not started
        if self.secs_to_start >= 0:
                return False
        else:
                return True

        
        
    def archive_checkchange_odds(self, dict_in):
        print("To check change in odds here\nDictionary event id = ", self.event, " and dict_in ID = ", dict_in['event'])

        ## get info to check
        for team in self.teams:
                if team.name != 'Draw':
                        print("Checkign odds for team with name", team.name)
                        team.updateodds(dict_in)
    
    def archive_checkchange_score(self, dict_in):
        pass

   
    def getgameindex(self, event_id_to_check):

        ## Init i to minus 1 (to start at zero)
        i = -1
        
        for game in self._registry:
                ## Iterate index
                i += 1
                if event_id_to_check == game.event:
                        return i
        return None

      
    def getteams(self):
        """ Returns the name of the teams with whether they are home/away"""
        teamdict = {}
        for t in self.teams:
            if t.home=='H':
                teamdict.update({'Home':t.name})
            elif t.home=='A':
                teamdict.update({'Away':t.name})
        
        return teamdict

