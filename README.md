# syncseen
A python script to sync played/unplayed status of media across Emby and/or Jellyfin instances.

You will need the API key for the two servers which can be generated in the Admin section of each server.  This script can be used to sync two Emby servers, two Jellyfin servers, or an Emby and a Jellyfin server.

## Basic operation
The most basic operation will sync the played and unplayed status of all movies, tv series, and videos from the host server to the destination server for all users.  This assumes that both servers have the same media and users
```
python syncseen.py -shost=<source URL> -skey=<source API key> -dhost=<destination URL> -dkey=<destination API key>
```
A user list can be passed to select only some users to sync. User names are case sensitive
```
python syncseen.py -shost=<source URL> -skey=<source API key> -dhost=<destination URL> -dkey=<destination API key> -u Admin,Kids
```

## Find existing users
To find the exact user names to use when syncing use the --listusers option
```
python syncseen.py -shost=<source URL> -skey=<source API key> -dhost=<destination URL> -dkey=<destination API key> --listusers
```
This can be run for only the source server
```
python syncseen.py -shost=<source URL> -skey=<source API key> --listusers
```
or only the destination server
```
python syncseen.py -dhost=<destination URL> -dkey=<destination API key> --listusers
```

## Write and read data from file
For systems where the source server and the destination server cannot be accessed at the same time, it is possible to first save the played/unplayed statuses in a file and then read that file in a separate action
```
python syncseen.py -shost=<source URL> -skey=<source API key> -o savedstatuses.txt
python syncseen.py -dhost=<destination URL> -dkey=<destination API key> -i savedstatuses.txt
```

## Specify media types
The default media types processed are movie, episode (for series), and video.  The "-t ITEMTYPES" option allows for finer control
```
python syncseen.py -shost=<source URL> -skey=<source API key> -dhost=<destination URL> -dkey=<destination API key> -t movie,episode
```

## Choose sync strategy
The default sync strategy is to update both played and unplayed items from the source server to the destination server, creating a mirror setup. But it is possible to update only the played items found on the source server
```
python syncseen.py -shost=<source URL> -skey=<source API key> -dhost=<destination URL> -dkey=<destination API key> -s playedonly
```
or only the unplayed items found on the source server
```
python syncseen.py -shost=<source URL> -skey=<source API key> -dhost=<destination URL> -dkey=<destination API key> -s unplayedonly
```

## Get some statistics about the media
To find the total number of movies and tv series, as well as the number of played and unplayed items for each user, use the --stats option
```
python syncseen.py -shost=<source URL> -skey=<source API key> -dhost=<destination URL> -dkey=<destination API key> --stats
```
This can be run for only the source or destination server
```
python syncseen.py -shost=<source URL> -skey=<source API key> --stats
python syncseen.py -dhost=<destination URL> -dkey=<destination API key> --stats
```

## Misc
* Running the script without arguments shows the help text
```
python syncseen.py
```
```
usage: syncseen.py [-h] [-np] [-shost SHOST] [-skey SKEY] [-dhost DHOST]
                   [-dkey DKEY] [-o FILE] [-i FILE] [-u USERLIST]
                   [-t ITEMTYPES] [-s {mirror,playedonly,unplayedonly}]
                   [--listusers] [--stats]

 optional arguments:
  -h, --help            show this help message and exit
  -np                   no progress output
  -shost SHOST          source source URL
  -skey SKEY            source api key
  -dhost DHOST          destination source URL
  -dkey DKEY            destination api key
  -o FILE               write data to FILE
  -i FILE               read data from file
  -u USERLIST           comma seperated user list
  -t ITEMTYPES          comma seperated list of item types
  -s {mirror,playedonly,unplayedonly}
                        sync strategy (mirror is default)
  --listusers           only get the user list
  --stats               print some stats
```

* Most operations show a progress indicator for every few media items. This can be suppressed with the -np argument
```
python syncseen.py -shost=<source URL> -skey=<source API key> --stats -np
```

* Many options can be combined
```
python syncseen.py -shost=<source URL> -skey=<source API key> -u Kids -t movie -np -o savedstatuses.txt
```

* A concrete command would look something like this
```
python syncseen.py -shost="http://192.168.1.100:8096" -skey="5c500d1715374703946bb187d993d507" -dhost="http://192.168.1.101:8096" -dkey="7bbd4a7c76c84530888d86ef70642550" -u Kids
```

## Future
* Currently the users have to be the same in both servers.  It might be helpful to add some functionality where users can be mapped between the two servers.  For now this is possible by saving a user to a file, and then using an text editor to rename all user instances, before importing to the destination server.

* The next major Jellyfin release is planning an API overhaul which might make this tool unusable for Jellyfin instances.
