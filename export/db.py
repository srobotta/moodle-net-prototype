
from arango import ArangoClient

class MoodleNetDb:
    _db = None
    _client = None
    _username = None
    _password = None
    _token = None

    def __init__(self, host: str, username: str, password: str, token: str = None):
        self._client = ArangoClient(hosts=host)
        self._username = username
        self._password = password
        self._token = token

    def _getDb(self, db_name: str):
        if self._token:
            return self._client.db(db_name, user_token=self._token)
        else:
            return self._client.db(db_name, username=self._username, password=self._password)
    
    def _getDocumentsInCollection(self, collection_name, filter = {}, like = False, return_fields = []):
        aql_query = f"""
            FOR doc IN @@collection_name
                %%FILTER%%
                RETURN doc
"""
        for key, value in filter.items():
            if like:
                aql_query = aql_query.replace("%%FILTER%%", f"FILTER CONTAINS(doc.{key}, '{value}') AND %%FILTER%%")
            else:
                aql_query = aql_query.replace("%%FILTER%%", f"FILTER doc.{key} == '{value}' AND %%FILTER%%")
        aql_query = aql_query.replace(" AND %%FILTER%%", "").replace("%%FILTER%%", "")

        if len(return_fields) > 0:
            return_aql = 'doc.' + return_fields[0] if len(return_fields) == 1 else '{' + ', '.join([f"doc.{key}" for key in return_fields]) + '}'
            aql_query = aql_query.replace("RETURN doc", f"RETURN {return_aql}")

        cursor = self._db.aql.execute(aql_query, bind_vars={"@collection_name": collection_name})
        documents = [doc for doc in cursor]
        return documents

    def _selectCollection(self, collection_name):
        if not self._db.has_collection(collection_name):
            raise Exception(f"Collection {collection_name} does not exist.")
        return self._db.collection(collection_name)

    def getResourceCnt(self) -> int:  # Number of resources
        self._db = self._getDb('moodlenet__system-entities')
        return len(list(self._selectCollection('moodlenet__ed-resource__Resource').keys()))
    
    def getResource(self, id: str) -> dict:  # Get resource by id
        self._db = self._getDb('moodlenet__system-entities')
        documents = list(self._getDocumentsInCollection('moodlenet__ed-resource__Resource', {"_key": id}))
        return documents[0] if len(documents) > 0 else None
    
    def getResourcesList(self) -> list:  # Get list of resource ids
        self._db = self._getDb('moodlenet__system-entities')
        #documents = list(self._getDocumentsInCollection('moodlenet__ed-resource__Resource', {}, False, ["_key"]))
        documents = self._selectCollection('moodlenet__ed-resource__Resource').keys()
        return documents

    def getWebuser(self, id: str) -> dict:  # Get webuser(profile) by id
        self._db = self._getDb('moodlenet__system-entities')
        documents = list(self._getDocumentsInCollection('moodlenet__web-user__Profile', {"_key": id}))
        return documents[0] if len(documents) > 0 else None