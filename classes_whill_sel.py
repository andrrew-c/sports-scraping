import pdb
import json


class Game:

    """
    A William Hill Game Class
    When initialised it has a start date, sport name, event (ID number)
    
    """

    _registry = {}
    _changelist    = ['odds', 'score']
    _blacklist = []     ### Blacklisted IDs
    
    def __init__(self, gameid, live_event_info, iterNum):

        
        """
            The Game class object
        """


        ## Init delete flag to false
        self.delete = False

        #if gameid == 'OB_EV14427415':
        #    pdb.set_trace()
          
    
        from datetime import date

        #pdb.set_trace()

        ## If current time is live skip this event
        if live_event_info['currentTime'] == 'Live':
            return None
            
        
    #if static_event_info['selections'][0]['fb_result'] != '-':
        ## Check there is a team to update
            
        ## Set up startdate for events - to stop different events with the same ID being overwritten
        self.startdate = live_event_info['startTime'][:10]

        ## Keep a note of when last seen in live event information
        self.lastseen = datetime.now()
    
        ## Sport name - string
        #self.sport_name         = static_event_info['sport']['sport_name']
        self.sport_name = 'Football'
        
        ## Event ID - string - used as game level unique ID - need ot check that's OK to do
        self.event              = gameid    #static_event_info['event']      ## ID for event
        
        ## Add new game to game registry for this class
        self._registry.update({self.event:self})

        if not 'tournamentID' in live_event_info:
            print("No tournament ID for ID {}".format(self.event))
            #return None
        else:
            self.tournament_id      = live_event_info['tournamentID']   #static_event_info['type']['type_id']
            self.tournament         = live_event_info['tournament']     #static_event_info['type']['type_name']
        self.start_time         = live_event_info['startTime']      #static_event_info['start_time']
        #self.secs_to_start      = static_event_info['secs_to_start_time']
        #self.selections         = static_event_info['selections']
        
        ## Each game has three teams (home/away/draw)
        self.teams              = self.initteams(gameid, live_event_info, iterNum)

        ## If one of the keys are missing - delete this
        if self.teams == None:

            #pdb.set_trace()
            self.delete = True
        
    
    def initteams(self, gameid, live_event_info, iterNum):

        import os
        import shelve

        """ 
        
        Initialise team class for event
        Input static_event_info: static 'event' level information
            
        """

        ## Path for shelve object to hold missing teams information
        pathmissingTeams = os.path.join('..', '..', 'whill', 'missingteamsdb')

            ## Iterate over home, draw and away
        for key in ['H', 'D', 'A']:

            ## Check if any of the keys are not in the DB

            if not key in live_event_info:
                print("Event with ID {} missing key '{}'".format(gameid, key))
                
                ## Let's add them to a shelve object, i'll sort it out later
                #db = shelve.open(pathmissingTeams)
                #db[gameid] = live_event_info
                #print("DB now has {} entries".format(len(db)))
                #db.close
                return None
            
        ## If program has got this far - then all 3 teams exist.        
        return [Team(self, gameid, live_event_info['currentTime'], key, live_event_info[key], iterNum) for key in ['H', 'D', 'A']]

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


    def update_teams(self, live_event_info, iterNum):
    
        """
        This function is called by the main engine to update the odds and scores for each team in a game
        """


        """

"""
        ## Keep a note of when this game is being updated
        self.lastseen = datetime.now()
        
        ## Get current time (in seconds)
        #pdb.set_trace()
        time1 = live_event_info['currentTime']
        time2 = int(time1[:2])*60 + int(time1[4:5])
        
        if not hasattr(self, 'teams'):
            pdb.set_trace()
            #tnames = [t.name for t in self.teams]
            print("Event {} has no teams attribute 'teams'".format(self.event))
            
            return None
        
        else:
            
            ## Iterate through each team in game
            for team in self.teams:

                ## If team's home status (i.e. 'H', 'A' or 'D') in live data
                if team.home in live_event_info:
         
                    ## Only try an update if teams information in live info
                    if team.market_id in live_event_info[team.home].values():

                        ## Update odds
                        team.update_odds(time2, live_event_info[team.home], iterNum)

                        
                        # Update score, if changed (or not yet initialised)
                        team.update_score(time2, live_event_info[team.home])
            
                    
   
    def update_game(self, new_game):
    
        """ Update DB:
               This function updates the class instance with new informatsion on odds and scores
        """

        testID = ''#'OB_EV14441124'
        
        import dict_recur as dr

        if new_game.event == testID:
            pdb.set_trace()
        
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
                            
                            if new_game.event == testID:
                                print("Jobby")
                                pdb.set_trace()
                        break
        
                            
                            #print("Updated team attribute: ", attr, " for team ", current_team.name, " to ", getattr(current_team, attr))
        
        except AttributeError as e:
            print("Attribute error with event ID '{}'\n{}".format(self.event, e))
            

        except:
            print("There's an issue with record:", self.event, "this will need checked.")
            raise
        
            
            
           
            
        
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



####################################################
####################################################
                
class Team:
        """The team class has a number of properties and methods:

            -----------------------------
            -- Properties --
            -----------------------------
            
            parent    - game the team belongs to
            name      - name of the team
            home      - 'A' for away team, 'H' for home team and 'D' for draw (third team)
            scoretype - text description of the team's score (home away, etc.)
            market_id - ID used to identify the team's 'market' ID - used for betting
            odds      - dictionary holding all recorded odds with time in seconds
            score     - dictionary holding all recorded scores (time in seconds)

            -----------------------------
            -- Methods --
            -----------------------------
            
            getselection
            gettime
            update_score
            update_odds
            update_team_attribute

            get_score
            getodds_component
            getodds
            getprob: Return most recent probability of team winning
            add_odds: Each team can have many sets of odds
                        Odds may change so the numerator, denominator and the time of the
                        change should be recorded.
        """

        ## String to pull out score differs for home / away teams
        _score_lookup = {'H':'score_home', 'A':'score_away', 'D':''}

        def __init__(self, parent, gameid, currentTime, homeflag, d_in_team, iterNum):

            """
                Inputs:
                    parent: parent (game) object
                    gameid: ID for game
                    currentTime:  Current time in "01:23" format
                    homeflag:     'A' for away and 'H' for home, etc.
                    d_in_team:    Dictionary holding game information
                This program will update the attributes as follows:
                self.parent - set a reference to the parent (game) object
                self.name     - team name
                self.home     - string holding information on whether home, away or draw
                self.scoretype    - This uses the team dictionary (_score_lookup) to map the home, away, etc. to 'score_home' or 'score_away'.  Not sure where this is used (2019-04-06)
                self.market_id    - ID for team (this was developed to only look at the team 'winning' as a market.
                self.odds, self.score - Dictionary holding score and odds in format {'time':score} or {'time:num=, den=, prob=}
                    Time should be in seconds
                    
            """
            #pdb.set_trace()
            self.parent = parent
            self.name = d_in_team['data-name']
            self.home = homeflag # d_in_team['fb_result']
            
            ## Score type - string for score type (e.g. 'comp1_score')
            
            self.scoretype = Team._score_lookup[self.home]             ## String to hold score type
            
            ## market ID is required to get odds from page source
            #team_selection = self.getselection(d_in_event)
            self.market_id = d_in_team['id'] #team_selection['ev_oc_id']
            
            ## Initialise odds and score dictionary for this team
            self.odds = {}
            self.score = {}

            ## time in seconds
            timesecs = int(currentTime[:2])*60 + int(currentTime[4:5])
            #pdb.set_trace()
            self.update_score(timesecs, d_in_team)
            self.update_odds(timesecs, d_in_team, iterNum)
            #pdb.set_trace() 
            
     
        def update_score(self, time, live_info):

            """
                Update score (self.score) information for team if there are changes.
                First checks for 'home'/'away' teams (rather than draw)
                
            """
    
            ## Get current score
            current_score = self.get_score()
            
            ## Only process 'home' and 'away teams'li
            if self.home in ['H', 'A']:
                
                ## Get score for this team from live information
                new_score = int(live_info['score'])
                          
                ## If the team is not 'draw' and the new score is different
                if current_score != new_score:
                        
                    ## Create dictionary with new score for this team
                    new_score_dict = {time:new_score}
                    
                    ## Update score dictionary with new score
                    self.score.update(new_score_dict)
                    
        def update_odds(self, time, live_info, iterNum):
            """
            Update odds (self.odds) for each team
            """
        
            ## Only process if time is not missing (perhaps a live event?)
            if time != -9:

                ## From live data - Get odds for correct selection (matching on team name)
                num = live_info['data-num']
                den = live_info['data-denom']

                ## Check if odds are 'evens'
                if live_info['data-odds'].casefold() == 'evs':
                    prob = 0.5
                else:
                    
                    ## Calculate pseudo probability based on odds
                    prob = round(float(den) / (float(num) + float(den)), 3)

                ## Create dictionary to update the team's info
                new_odds = {time: {'num':num, 'den':den, 'prob':prob}}
                    
                ## Get current numerator and denominator (most recent)
                current_num = self.getodds_component('num')
                current_den = self.getodds_component('den')
                                
                ## Check whether num/den have changed
                if current_num != num or current_den != den:

                    if iterNum > 1:
                        pass
                        #print("Iteration number: {} team name: {} with currrent odds '{}' and new odds '{}'".format(iterNum, self.name, self.odds, new_odds))
                        #pdb.set_trace()
                    
                    ####################################################
                    # Update odds
                    ####################################################
                    
                    self.odds.update(new_odds)
                   
            ## Else, time information is not ok
            else:
                pass
                print("*"*30, "Update odds - not processing team ID:", self.market_id)
                
            
        def getselection(self, d_in_event):
            """
            Returns a sub-dictionary with the selection for the team
            """
            """ Returns the dictionary for this team's selection """
            for sel in d_in_event['selections']:
           
                if self.home == sel['fb_result']:
                    return sel
                

        def gettime(self, d_in_event):
            """
            Returns integer of time
            self - team object
            d_in_event - dictionary 
            """
            return -int(d_in_event['secs_to_start_time'])

        def update_team_attribute(self, new_game, attr):
            """
                For a given team, update the attribute specified in the string attr
            """
            import dict_recur as dr
            
            ## Get values of current and new
            current = getattr(self, attr)
            new     = getattr(new_game, attr)
            
            ## If current blank, return new
            if current == {}:
                #print("Current attr ", attr, "value was blank, so updating with new", new)
                return new
            ## Else, update dictionary
            else:
                #print("Current attr ", attr, "was not blank - currently", current, "but adding new: ", new, "final value should be ", dr.update(current, new))
                
                return dr.update(current, new)
                    
        def update_odds_archive(self, d_in_event):

                ## time saved in seconds until game start - negative
                time = str(self.gettime(d_in_event))
                
                ## Get odds for correct selection (matching on team name)
                for sel in d_in_event['selections']:
                        #print( "self.home and fb result", self.home, sel['fb_result'] )
                        if self.home == sel['fb_result']:
                                num = sel['lp_num']
                                den = sel['lp_den']

                ## Calculate pseudo probability based on odds
                prob = round(int(den) / (int(num) + int(den)), 3)

                ## Create dictionary to update odds dictionary
                new_odds = {time: {'num':num, 'den':den, 'prob':prob}}

                ## if lenght zero, initialise dictionary
                # if len(self.odds) == 0:
                        # print("Initialised odds")
                        # self.odds.update(new_odds)
                             
                ## Else, if odds have changed update
                if self.getodds_component('num') != num or self.getodds_component('den') != den:
                    ## Update odds
                    self.odds.update(new_odds)
                    print("Updated odds for ", self.name, "!")

        def get_score(self):
                try:
                        return int(self.score[max(self.score.keys())])
                except:
                        return None

        def getodds_component(self, component):
                if self.odds != {}:
                    recent_time = max(self.odds.keys())
                    return self.odds[max(self.odds.keys())][component]
                else:
                    None
                        
        
        def getodds(self):
            """ Method that return most recent odds for this team
            """
                
            cur_idx = len(self.odds) - 1
            
            if cur_idx == -1:
                    return None
            else:
                    return str(self.odds[cur_idx]['num']) + '/' + str(self.odds[cur_idx]['den'])

        def getprob(self):
            """ Return most recent probability of team winning
            """
            cur_idx = len(self.odds) - 1
            
            if cur_idx == -1:
                    return None
            else:
                    return self.odds[cur_idx]['prob']
         
        def add_odds(self, num, den, time):
            """
                    Each team can have many sets of odds
                    Odds may change so the numerator, denominator and the time of the
                    change should be recorded.
            """
            odds_string = num + '/' + den
##                print("odds_string=", odds_string)
##                print(self.get_odds())
            if odds_string != self.get_odds():
            
                ## calculate pseudo-probability
                prob = round(int(den) / (int(num) + int(den)), 3)
                num = int(num)
                den = int(den)
                
                self.odds.append({'time':time, 'num':num, 'den':den, 'prob':prob})


                        
                        
class WHillBrowser:
    
    def __init__(self, browser, write_html = False, write_scripts = False, suffix = None):
    
        self.new_events = self.getgameslist_sel(self, write_html, write_scripts, suffix)
        self.live_event_info = self.getliveeventinfo_sel(browser)
        self.live_team_info = self.getliveteaminfo_sel(browser)
    
   
    def getgameslist_sel(browser
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
            out_html = input("Type name of file to write HTML out to.\nwhill.txt is standard")
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
        scripts = [s for s in soup.find_all('script', {'type':'text/javascript', 'language':'Javascript'}) if script_string in s.text]

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
        events = [event[event.find(script_string)+len(script_string):len(event)-3] for event in events]

        ## For each event, get all info into a single line
        events_line = [''.join([''.join(line.split()) for line in event]) for event in events]

        ## With each event, strip out the start and end points

    ##    i = 0
    ##    for line in events_line:
    ##        i += 1
    ##        f = open('single_'+str(i)+'.txt', 'w')
    ##        f.write(line)
    ##        f.close()

        ###################################
        #### Parse scripts into JSON data
        ###################################

        ## Product a list of dictionaries holding json information
        #js_dict = [json.loads(event) for event in events_line]
        i = -1

        ## Init dictionary to output
        js_dict = {}

        ## Init errors key
        js_dict.update({'errors':{}})

        ## check json has been loaded
        if 'json' not in sys.modules:
            print("json module has not been loaded.  please check code")

        ## Otherwise, ok to proceed
        else:
            ## Loop through each event in list
            for line in events_line:

                ## Iterate counter
                i += 1
                
                ## Try to encode line into json dictionary
                try:
                    js_dict.update({i:json.loads(line)})
                except:
                    js_dict.update({'errors':{i}})


        return js_dict

    
    def gettags(browser, tag, myclass, myclassstring):
        """
            Returns list matching tag, myclass, myclasstring
        """
        
        from bs4 import BeautifulSoup as bs
        import re
        
        
        ## make soup from items
        soup = bs(browser.page_source, 'html.parser')
        
        if myclass != None:
            return soup.find_all(tag, {myclass:myclassstring})
        else:
            return soup.find_all(tag)
    
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
        print(event_ids)
        input()
        
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
            events.update({event:{'time':temp_time, 'score_home':score_home, 'score_away':score_away}})
        
        
        return events

    def getliveteaminfo_sel(browser):

        import re
        
        ## Get Odds information for each event
        raw_event_info = gettags(browser, 'div', 'class', 'eventprice')
        
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



