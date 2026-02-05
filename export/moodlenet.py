import json
import re
from slugify import slugify

class MoodleNetEntity:
    _wwwroot = ''
    _webpath = ''
    _id = ''
    _key = ''
    _rev = ''

    def __init__(self, instanceDomain: str, document: dict):
        self._wwwroot = instanceDomain if instanceDomain.startswith('http') else 'https://' + instanceDomain
        self._id = document.get('_id', '')
        self._key = document.get('_key', '')
        self._rev = document.get('_rev', '')

    def _getWebLink(self, directAccessId: str, webpath: str = '') -> str:
        return self._wwwroot + '/' + (webpath if webpath else self._webpath) + '/' + directAccessId
        
    def _slug(self, title: str = '') -> str:
        if title == '':
            title = self.title if 'title' in self.__dict__ else ''
        title = self.__dict__['title']
        return slugify(title, lowercase=True)

class MoodleNetResource(MoodleNetEntity):
    _webpath = '.pkg/@moodlenet/ed-resource/public'
    description = ''
    title = ''
    image = None
    published = False
    license = ''
    subject = ''
    language = ''
    level = ''
    date = ''
    type = ''
    learningOutcomes = []
    content = None
    meta = {
        "created": "",
        "creator": {},
        "updated": ""
    }
    link = ''

    def __init__(self, instanceDomain: str, document: dict):
        super().__init__(instanceDomain, document)
        self.description = document.get('description', '')
        self.title = document.get('title', '')
        self.link = self._wwwroot + '/resource/' + self._key + '/' + self._slug()
        image = document.get('image', None)
        if image and image.get('kind', '') == 'file':
            self.image = self._getWebLink(image.get('directAccessId', ''))
        self.published = document.get('published', False)
        self.license = document.get('license', '')
        self.subject = document.get('subject', '')
        self.language = document.get('language', '')
        self.level = document.get('level', '')
        self.date = '{}-{}-01T00:00:00.000Z'.format(document.get('year', ''), document.get('month', ''))
        self.type = document.get('type', '')
        self.learningOutcomes = document.get('learningOutcomes', [])
        content = document.get('content', None)
        if content:
            if content.get('kind', '') == 'file':
                self.content = {
                    "url": self._getWebLink(
                        content['fsItem']['rpcFile']['name'],
                        self._webpath.replace('public', 'dl/ed-resource/' + self._key)
                    ),
                    "name": content['fsItem']['rpcFile']['name'],
                    "type": content['fsItem']['rpcFile']['type'],
                    "size": content['fsItem']['rpcFile']['size']
                }
            elif content.get('kind', '') == 'link':
                self.content = {
                    "url": content['url'],
                    "name": '',
                    "type": '__link__',
                    "size": 0
                }
        self.meta = document.get('_meta', {
            "created": "",
            "creator": {},
            "updated": ""
        })

    def setCreator(self, creator: MoodleNetUser) -> MoodleNetResource:
        self.meta['creator'] = dict()
        for key, value in creator.__dict__().items():
            self.meta['creator'][key] = value
        return self

    def __str__(self):
        return json.dumps(self.__dict__, indent = 2)

class MoodleNetUser(MoodleNetEntity):
    _webpath = '.pkg/@moodlenet/web-user/public'
    id = ''
    name = ''
    slug = ''
    about = ''
    avatar = None

    def __init__(self, instanceDomain: str, document: dict):
        super().__init__(instanceDomain, document)
        self.name = document.get('displayName', '')
        self.about = document.get('aboutMe', '')
        self.slug = document.get('webslug', '')
        self.id = self._key
        avatar = document.get('avatarImage', None)
        if avatar and avatar.get('kind') == 'file':
            self.avatar = self._getWebLink(avatar.get('directAccessId', ''))

    def __dict__(self):
        all_attrs = super().__dir__()
        return {attr: getattr(self, attr) for attr in all_attrs if not attr.startswith("_")}