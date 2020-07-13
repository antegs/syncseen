import requests
import ast
import re
import sys
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-np", action="store_false",
                    help="no progress output")
parser.add_argument("-shost", dest="shost",
                    help="source host url")
parser.add_argument("-skey", dest="skey",
                    help="source api key")
parser.add_argument("-dhost", dest="dhost",
                    help="destination host url")
parser.add_argument("-dkey", dest="dkey",
                    help="destination api key")
parser.add_argument("-o", dest="outfile",
                    help="write data to FILE", metavar="FILE")
parser.add_argument("-i", dest="infile",
                    help="read data from file", metavar="FILE")
parser.add_argument("-u", dest="userlist",
                    help="comma seperated user list")
parser.add_argument("-t", dest="itemtypes",
                    help="comma seperated list of item types")
parser.add_argument("-s", choices=['mirror', 'playedonly', 'unplayedonly'], default='mirror',
                    help="sync strategy (mirror is default)")
parser.add_argument("--listusers", action="store_true",
                    help="only get the user list")
parser.add_argument("--stats", action="store_true",
                    help="print some stats")
args = parser.parse_args()

if len(sys.argv) == 1:
    parser.print_help()
    quit()

nosource = True;
if (args.shost != None and args.skey != None):
    nosource = False;
nodest = True;
if (args.dhost != None and args.dkey != None):
    nodest = False;

if nosource and nodest:
    print("Need at least source host and key OR destination host and key.")
    quit()

if args.outfile != None and nosource:
    print("Source host and key are needed to create output file.")
    quit()
if args.infile != None and nodest:
    print("Destination host and key are needed to read input file.")
    quit()

itemTypes="movie,episode,video,musicvideo"
if args.itemtypes != None:
    itemTypes = args.itemtypes

usersRequested = None
if args.userlist != None:
    usersRequested = args.userlist.split(",")

if args.outfile != None and args.infile != None:
    print("Cannot use both input and output file.")
    quit()

def update(key, userid, itemid):
    if key in loadedusers:
        URL = args.dhost+"/Users/"+userid+"/PlayedItems/"+itemid+"?api_key="+args.dkey
        played = loadedusers[key]
        if played and (args.s == "mirror" or args.s == "playedonly"):
            # make post request (played)
            PARAMS = {'DatePlayed':20200101000000}
            r = requests.post(url = URL, params = {})
            if r.status_code != 200:
                print(r)
        if not played and (args.s == "mirror" or args.s == "unplayedonly"):
            # make delete request (not played)
            r = requests.delete(url = URL, params = {})
            if r.status_code != 200:
                print(r)
    else:
        print("Item not in source: %s"%(key))

def process(calltype, callhost, callkey):
    URL = callhost+"/Users?api_key="+callkey
    r = requests.get(url = URL, params = {})
    usersdb = r.json()
    users={}

    if args.listusers:
        print("--- " + calltype + " Users:")
        for usr in usersdb:
            print(usr['Name'])
    else:
        URL = callhost+"/Library/PhysicalPaths?api_key="+callkey
        r = requests.get(url = URL, params = {})
        pathsdb = r.json()

        userCount = 0
        movieCount = 0
        episodeCount = 0
        videoCount = 0
        playedList = {}

        for usr in usersdb:
            userid = usr['Id']
            username = usr['Name']
            if usersRequested == None or username in usersRequested:
                userCount += 1
                if userCount == 1:
                    print("--- Processing " + calltype)

                startindex = 0
                itemlimit = 100
                keepgoing = True
                while keepgoing:
                    if args.np:
                        print(username + " " + str(startindex))
                    URL = callhost+"/Users/"+userid+"/Items?IncludeItemTypes="+itemTypes+"&Recursive=true&StartIndex="+str(startindex)+"&Limit="+str(itemlimit)+"&api_key="+callkey
                    r = requests.get(url = URL, params = {})
                    itemsdb = r.json()

                    if len(itemsdb['Items']) < itemlimit:
                        keepgoing = False
                    else:
                        startindex += itemlimit
                        keepgoing = True

                    for item in itemsdb['Items']:
                        itemid = item['Id']
                        itemplayed = item['UserData']['Played']

                        URL = callhost+"/Users/"+userid+"/Items/"+itemid+"?api_key="+callkey
                        r = requests.get(url = URL, params = {})
                        itemdb = r.json()

                        if itemdb['MediaSources'][0]['Type'] == "Default":
                            if item['Type'] == "Episode":
                                episodeCount += 1
                                key = username + ':' + item['Type']  + ':' + str(itemplayed)
                            elif item['Type'] == "Movie":
                                movieCount += 1
                                key = username + ':' + item['Type'] + ':' + str(itemplayed)
                            elif item['Type'] == "Video" or item['Type'] == "MusicVideo":
                                videoCount += 1
                                key = username + ':Video:' + str(itemplayed)
                            if key in playedList:
                                playedList[key] = playedList[key]+1
                            else:
                                playedList[key] = 1

                            if not args.stats:
                                itempath = itemdb['Path']
                                itempath = re.sub("^smb://.*?/", "/", itempath)
                                itempathbefore = itempath
                                for path in pathsdb:
                                    if itempath.startswith(path) and itempath[len(path):len(path)+1] == "/":
                                        itempath = itempath[len(path)+1:]
                                        exit
                                if itempathbefore == itempath:
                                    print("Paths not corrected.")
                                    continue

                                key = username + ':' + itempath
                                if calltype == "Source":
                                    if key in users:
                                        print("Key already in users: " + key)
                                    else:
                                        users[key] = itemplayed
                                else:
                                    update(key, userid, itemid)

        if calltype == "Source" and args.outfile != None:
            file = open(args.outfile, 'w')
            file.write(str(users))
            file.close()
            quit()

        if args.stats:
            print("--- " + calltype + " stats:")
            if userCount != 0:
                print("Users: %s\nTotal Movies: %s\nTotal Episodes: %s\nTotal Videos: %s"%(
                userCount,movieCount,episodeCount,videoCount))
            for key, value in sorted(playedList.items()):
                print("%s: %s"%(key.replace(":False", ":NotPlayed").replace(":True", ":Played"), value))
        return users

if args.infile == None:
    if not nosource:
        loadedusers = process("Source", args.shost, args.skey)
else:
    with open(args.infile, 'r') as content_file:
        loadedusers = ast.literal_eval(content_file.read().strip())

if not nodest:
    process("Destination", args.dhost, args.dkey)
