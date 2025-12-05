#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Export MoodleNet resources in Switch OER CSV format or JSON

This script reads from a MoodleNet ArangoDB database all resources and
exports them in Switch OER CSV format or as a custom JSON.
Also, single items can be exported or a list of resource IDs printed.

Requirements:
  - Python 3.x
  - python-arango package (install via pip: pip install python-arango)
  - python-slugify package (install via pip: pip install python-slugify)

Arguments:
  -c | --config <file>    : Configuration file of MoodleNet for DB credentials
  -e | --export           : Export resources in Switch OER CSV format
  -H | --host <hostname>  : Host of the database (overrides config file)
  -i | --id <id1,id2,...> : ID(s) of the resource(s) to export (comma separated)
  -j | --json             : Export resources in JSON format, only in combination with -i
  -l | --list             : List resource IDs and title
  -o | --outfile <file>   : Output CSV file (default: stdout)
  -p                      : Prompt for password of the database (overrides config file)
  --password <password>   : Password of the database (overrides config file)
  --port <port>           : Port of the database (default: 8529)
  -t | --token <token>    : Access token of the database if no user password is used
  -u | --username <user>  : Username of the database (overrides config file)

Usage examples:
  python3 export.py -c moodlenet_config.json -l -o resources_list.csv
  python3 export.py -c moodlenet_config.json -e -o resources_export.csv
  python3 export.py -c moodlenet_config.json -e -i resourceid1,resourceid2 -o resources_export.csv
  python3 export.py -c moodlenet_config.json -j -i resourceid1
  python3 export.py -H localhost -u root -p -l
  python3 export.py -H localhost -u root -p -e -o resources_export.csv
  python3 export.py -u moodlenet --password 'secret' -j -i resourceid1,resourceid2

"""

from db import MoodleNetDb
from switchoer import SwitchOerResource
from moodlenet import MoodleNetResource, MoodleNetUser
import json
import argparse
import sys
import contextlib


@contextlib.contextmanager
def openOutput(filename = None):
    if filename and filename != '-':
        fh = open(filename, 'w')
    else:
        fh = sys.stdout
    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()

def getCredentialsFromConfig(file: str):
    with open(file, 'r') as fin:
        data = json.load(fin)
    cfg = {}
    try:
        cfg['host'] = data['pkgs']['@moodlenet/arangodb']['connectionCfg']['url']
    except KeyError:
        print("No host found in the configuration file.")
    try:
        cfg['token'] = data['pkgs']['@moodlenet/arangodb']['connectionCfg']['auth']['token']
    except KeyError:
        pass
    try:
        cfg['username'] = data['pkgs']['@moodlenet/arangodb']['connectionCfg']['auth']['username']
    except KeyError:
        cfg['username'] = 'root'
    try:
        cfg['password'] = data['pkgs']['@moodlenet/arangodb']['connectionCfg']['auth']['password']
    except KeyError:
        cfg['password'] = ''
    return cfg

def getParserArgs():
    parser = argparse.ArgumentParser(
                        prog = 'export.py',
                        description = __doc__,
                        formatter_class = argparse.RawDescriptionHelpFormatter,
                        add_help = False )
    parser.add_argument('-h', '--help', action='store_true')
    parser.add_argument('-c', '--config', type=str, help='Configuration json file of MoodleNet for DB credentials')
    parser.add_argument('-u', '--username', type=str, help='Username of the database')
    parser.add_argument('--password', type=str, help='Password of the database')
    parser.add_argument('-p', action='store_true', help='Password of the database via manual input')
    parser.add_argument('-H', '--host', type=str, help='Host of the database')
    parser.add_argument('--port', type=int, help='Port of the dasabse (default: 8529)')
    parser.add_argument('-t', '--token', type=str, help='Access token of the database if no user password is used')
    parser.add_argument('-i', '--id', type=str, help='ID of the resource to export')
    parser.add_argument('-l', '--list', action='store_true', help='List resource IDs and title')
    parser.add_argument('-o', '--outfile', type=str, help='Output CSV file')
    parser.add_argument('-e', '--export', action='store_true', help='Export resources in Switch OER CSV format')
    parser.add_argument('-j', '--json', action='store_true', help='Export resources in JSON format, only in combination with -i')
    return parser.parse_args()

def getDb(args):
    dbhost = 'http://localhost'
    dbuser = 'root'
    dbpass = ''
    dbtoken = None

    if args.config:
        credentials = getCredentialsFromConfig(args.config)
        if 'token' in credentials:
            dbtoken = credentials['token']
        else:
            dbuser = credentials['username']
            dbpass = credentials['password']
        dbhost = credentials['host']

    else:
        if args.host:
            dbhost = args.host
            if dbhost[0:4].lower() != 'http':
                dbhost = 'http://' + dbhost
        dbhost += ':' + args.port if args.port else ':8529'

        if args.username:
            dbuser = args.username
        if args.password:
            dbpass = args.password
        elif args.p:
            sys.stdout.write("Enter database password: ")
            dbpass = input()

    return MoodleNetDb(dbhost, dbuser, dbpass, dbtoken)

def getMnetResource(db: MoodleNetDb, key: str) -> MoodleNetResource:
    resource = db.getResource(key)
    if resource:
        mnetResource = MoodleNetResource(resource)
        creatorDoc = db.getWebuser(mnetResource.meta['creator'].get('entityIdentifier').get('_key', ''))
        if creatorDoc:
            creator = MoodleNetUser(creatorDoc)
            mnetResource.setCreator(creator)
        return mnetResource
    else:
        return None

def main():
    args = getParserArgs()
    if args.help:
        print(__doc__)
        sys.exit(0)
    db = getDb(args)
    if args.outfile:
        fileOutName = args.outfile
        delimiter = ';'
        quotes = '"'
    else:
        fileOutName = '-'
        delimiter = ' '
        quotes = ''
    if args.list:
        if not args.outfile:
            resource_cnt = db.getResourceCnt()
            print("Total number of resources: {}".format(resource_cnt))
        resources = db.getResourcesList()
        with openOutput(fileOutName) as fout:
            print('ResourceID{}Title'.format(delimiter), file=fout)
            for resKey in resources:
                mnetResource = getMnetResource(db, resKey)
                print('{key}{delimiter}{quotes}{title}{quotes}{delimiter}'.format(
                    key=resKey, delimiter=delimiter, quotes=quotes, title=mnetResource.title.replace(quotes, quotes*2)
                ), file=fout)

    elif args.json:
        for key in args.id.split(','):
            mnetResource = getMnetResource(db, key)
            if mnetResource:
                print(mnetResource)
            else:
                print("Resource with ID {} not found.".format(key))

    elif args.export:
        resources = args.id.split(',') if args.id else list(db.getResourcesList())
        with openOutput(fileOutName) as fout:
            switchOerResource = SwitchOerResource()
            # Write CSV header
            print(switchOerResource.getCsvHeader(), file=fout)
            for resKey in resources:
                mnetResource = getMnetResource(db, resKey)
                switchOerResource.setMoodleNetResource(mnetResource)
                print(switchOerResource.toCsv(), file=fout)

if __name__ == '__main__':
    main()


