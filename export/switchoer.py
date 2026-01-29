from moodlenet import MoodleNetResource
import json
import os
class SwitchOerResource():
    """
    SwitchOerResource represents a single resource in the Switch OER CSV export format.
    """
    _delimiter = ';'
    _quotes = '"'
    _originUniversity = ''
    _resourceTypeMapping = None
    # all fields according to https://docs.edu-sharing.com/de/edu-sharing-documentation/9.1/bulkimport-excel
    fields = [
        'catalog',
        'identifier',
        'datestamp',
        'name',
        'title',
        'language',
        'description',
        'keyword',
        'context',
        'educationalIntendedenduserrole',
        'educationalTypicalAgeRangeFrom',
        'educationalTypicalAgeRangeTo',
        'educationalTypicalAgeRange',
        'lifeCycleContributerAuthor',
        'lifeCycleContributerPublisher',
        'metadataContributerProvider',
        'metadataContributerCreator',
        'technicalFormat',
        'technicalLocation',
        'wwwurl',
        'contentUrl',
        'educationalLearningResourceType',
        'RightsCopyrightAndOtherRestrictions',
        'RightsDescription',
        'thumbnailUrl',
        'taxonId',
        'taxonEntry',
        'licenseKey',
        'licenseVersion',
        'licenseLocale',
        'licenseSourceUrl',
        'licenseTitleOfWork',
        'licenseTo',
        'licenseValid',
        'originUniversity',
        'metadataset',
        'oeh_widgets'
    ]

    def setOriginUniversity(self, university: str):
        self._originUniversity = university
        return self

    def setMoodleNetResource(self, mnetResource: MoodleNetResource):
        """
        Set an instance of MoodleNetResource to populate the SwitchOerResource fields.
        
        :param mnetResource: MoodleNetResource instance
        :type mnetResource: MoodleNetResource
        """
        for field in self.fields:
            setattr(self, field, '')
        self.description = mnetResource.description
        self.name = mnetResource.title
        self.language = mnetResource.language[0:2].upper() if mnetResource.language else ''
        self.contentUrl = mnetResource.content['url'] if mnetResource.content else ''
        self.thumbnailUrl = mnetResource.image if mnetResource.image else ''
        self.licenseKey = mnetResource.license
        # We only have CC licenses with version 4.0 in MoodleNet
        if mnetResource.license.startswith('cc-'):
            self.licenseVersion = '4.0'
            self.licenseLocale = ''
            self.licenseSourceUrl = 'https://creativecommons.org/licenses/{}/4.0/'.format(
                mnetResource.license.replace('cc-', '')
            ) if mnetResource.license.startswith('cc-') else ''
        # Date only without time information
        self.datestamp = mnetResource.meta['created'][:10] if 'created' in mnetResource.meta else ''
        self.originUniversity = self._originUniversity
        self.educationalLearningResourceType = self.mapRessourceType(mnetResource)

    def getCsvHeader(self) -> str:
        """
        Returns the CSV header line string.

        return: CSV header line
        retype: str
        """
        return self._delimiter.join(key for key in self.fields)

    def toCsv(self):
        """
        Returns a csv line string for the current resource, escaping fields as needed.

        return: CSV line
        retype: str
        """
        tuple = {}
        for key in self.fields:
            value = getattr(self, key)
            if value is None or (isinstance(value, str) and value.strip() == ''):
                tuple[key] = ''
            else:
                if value.find (self._delimiter) >= 0 or value.find(self._quotes) >= 0 or value.find('\n') >= 0:
                    tuple[key] = self._quotes + str(value).replace(self._quotes, self._quotes*2) + self._quotes
                else:
                    tuple[key] = str(value)
        return self._delimiter.join(tuple[key] for key in self.fields)
    
    def mapRessourceType(self, mnetResource: MoodleNetResource) -> str:
        """
        From the MoodleNet resource type and content type, map to the Switch OER educationalLearningResourceType.
        
        :param mnetResource: MoodleNetResource instance
        :type mnetResource: MoodleNetResource
        :return: Description
        :rtype: str
        """
        # Load mapping only once
        if self._resourceTypeMapping is None:
            self._resourceTypeMapping = json.loads(open(os.path.dirname(__file__) + '/content_type_mapping.json', 'r').read())
        
        mainType = mnetResource.type
        # If no mapping found, return 'other', that should not happen.
        if mainType not in self._resourceTypeMapping:
            return 'https://w3id.org/edu-sharing/vocabs/switch/hcrt/other'
        # If the type is a link we check for typical video domains and return the video type.
        if mnetResource.content['type'] == '__link__':
            for domain in [
                "youtube.com",
                "vimeo.com",
                "mediaspace.bfh.ch"
            ]:
                if domain in mnetResource.content['url']:
                    return "https://w3id.org/edu-sharing/vocabs/switch/hcrt/video"
        # Now check if we have no subtypes via file suffix defined, thus return the direct mapping.
        if 'suffix' not in self._resourceTypeMapping[mainType]:
            return self._resourceTypeMapping[mainType]
        # Check the suffix mapping (there is always a default defined when no specific suffix match is found)
        subTypes = self._resourceTypeMapping[mainType]['suffix']
        name = mnetResource.content['name'] if mnetResource.content['type'] != '__link__' else mnetResource.content['url']
        suffix = name.split('.')[-1].lower() if name and '.' in name else ''
        mnetType = subTypes[suffix] if suffix in subTypes else subTypes['default']
        return mnetType