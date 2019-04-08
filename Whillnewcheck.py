import os
import sys
import shelve
import pdb

##whpath = os.path.join('sports-scraping')
##sys.path.append(whpath)
##

import classes_whill_sel

## Open new DB
db = shelve.open(os.path.join('whilldb'))
ks = list(db.keys())

print("There are {} games".format(len(db)))
db1 = db[ks[0]]

### Get all odds (team 0)
odds1 = [db[ks[i]].teams[0].odds for i in range(len(db))]
lens1 = [len(o) for o in odds1]
print("Odds:\n{}".format(lens1))
oddsCK = [db[ks[i]].teams[0].odds for i in range(len(lens1)) if lens1[i]>3]

## print odds

# get times
times = [list(o.keys()) for o in oddsCK]

## Sort times in ascending order
[t.sort() for t in times]

##for t1 in times:
##    print("")
##    for t in t1:
##        print("{} --> {} --> {:4%}".format(t, t1[t], t1[t]['prob']))

odds2 = [db[ks[i]].teams[1].odds for i in range(len(db))]
lens2 = [len(o) for o in odds2]

scores1= [db[ks[i]].teams[0].score for i in range(len(db))]
lens3 = [len(s) for s in scores1]
print("Scores:\n{}".format(lens3))

## Which games have length> 1 (score)




