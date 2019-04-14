import os
import sys
import shelve
import pdb

import classes_whill_sel

## Open new DB
db = shelve.open(os.path.join('whilldb'))
ks = list(db.keys())

print("There are {} games".format(len(db)))
#db1 = db[ks[0]]

print("Checking teams")
i = 0 
for k in ks:
    i = i + 1
    
    hasteam = hasattr(db[k], 'teams')
    if not hasteam:
        print("game {}, start date = {}, id '{}' has NO teams = {}".format(i, db[k].startdate, k, hasteam))

       

### Get all odds (team 0)
odds1 = [db[ks[i]].teams[0].odds for i in range(len(db))]
score1 = [db[ks[i]].teams[0].score  for i in range(len(db))]
lens1 = [len(o) for o in odds1]
lens2 = [len(s) for s in score1]
print("Odds:\n{}\n".format(lens1))
print("Score:\n{}\n".format(lens2))
print("You can view odds for team1")
team1 = db[ks[0]].teams[0]
oddsCK = [db[ks[i]].teams[0].odds for i in range(len(lens1)) if lens1[i]>3]

# db[ks[226]].teams[0].name
##
##dates = [db[i].startdate for i in db]
##def PrintLengths(dates, lens1):
##        for i in range(len(dates)):
##            print("i = {} date = {} and len of odds = {}".format(i, dates[i], lens1[i]))
####PrintLengths(dates, lens1)
##
##print("Load up games from 2019-04-09")
##db2 = [db[i] for i in db if db[i].startdate == '2019-04-09']
##ks2 = [i.event for i in db2]
##
##names = [(t[0].name, t[0].parent.event) for t in [db[g].teams for g in db]]
##blah  = db[ks[0]].teams[0].odds
##
###db.close()
