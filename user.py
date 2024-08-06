#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from arango import ArangoClient
import json
import argparse
import sys

def getCredentialsFromContig(file: str):
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

# Function to select a collection
def selectCollection(db, collection_name):
    if not db.has_collection(collection_name):
        raise Exception(f"Collection {collection_name} does not exist.")

    collection = db.collection(collection_name)
    return collection

# Function to update the displayName of a document
def updateDocumentInCollection(db, collection_name, doc_key, values):
    collection = selectCollection(db, collection_name)
    # Check if the document exists
    if not collection.has(doc_key):
        raise Exception(f"Document with _key {doc_key} does not exist.")
    
    # Retrieve the document
    document = collection.get(doc_key)
    
    # Update the displayName field
    for key, value in values.items():
        document[key] = value
    
    # Update the document in the collection
    collection.update(document)
    
    print(f"Document with _key {doc_key} updated successfully.")

def getDocumentsInCollection(db, collection_name, values={}, like=False):
    collection = selectCollection(db, collection_name)
    if len(values) == 0:
        documents = collection.all()
    else:
        aql_query = f"""
            FOR doc IN {collection_name}
                %%FILTER%%
                RETURN doc
"""
        for key, value in values.items():
            if like:
                aql_query = aql_query.replace("%%FILTER%%", f"FILTER CONTAINS(doc.{key}, '{value}') AND %%FILTER%%")
            else:
                aql_query = aql_query.replace("%%FILTER%%", f"FILTER doc.{key} == '{value}' AND %%FILTER%%")
        aql_query = aql_query.replace(" AND %%FILTER%%", "")
        cursor = db.aql.execute(aql_query)
        documents = [doc for doc in cursor]
    return documents

def getParserArgs():
    parser = argparse.ArgumentParser(
                        prog='user.py',
                        description='Handle users in MoodleNet')

    parser.add_argument('-c', '--config', type=str, help='Configuration json file of MoodleNet for DB credentials')
    parser.add_argument('-u', '--username', type=str, help='Username of the database')
    parser.add_argument('--password', type=str, help='Password of the database')
    parser.add_argument('-p', action='store_true', help='Password of the database via manual input')
    parser.add_argument('-H', '--host', type=str, help='Host of the database')
    parser.add_argument('--port', type=int, help='Port of the dasabse (default: 8529)')
    parser.add_argument('-t', '--token', type=str, help='Access token of the database if no user password is used')

    return parser.parse_args()

def getDbConnection(args):
    dbhost = 'http://localhost'
    dbuser = 'root'
    dbpass = ''
    dbtoken = None

    if args.config:
        credentials = getCredentialsFromContig(args.config)
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

    client = ArangoClient(hosts=dbhost)
    return client, dbuser, dbpass, dbtoken

def main():
    (client, dbuser, dbpass, dbtoken) = getDbConnection(getParserArgs())
    # Select the database
    db_name = 'moodlenet__web-user'
    db = client.db(db_name, user_token=dbtoken) if dbtoken else client.db(db_name, username=dbuser, password=dbpass)

    # Retrieve all documents from the collection
    #documents = getDocumentsInCollection(db, 'WebUser', {"displayName": 'Stephan'}, like=True)
    documents = getDocumentsInCollection(db, 'WebUser')

    # Print the documents
    for doc in documents:
        print(doc)

    # Optionally, you can collect all documents in a list
    print("Total documents retrieved:", len(documents))

    #updateDocumentInCollection(db, 'WebUser', '94462', {'displayName': 'John Doe'})

if __name__ == '__main__':
    main()


