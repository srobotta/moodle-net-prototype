from moodlenet import MoodleNetResource

class SwitchOerResource():
    _delimiter = ';'
    _quotes = '"'
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

    def setMoodleNetResource(self, mnetResource: MoodleNetResource):
        for field in self.fields:
            setattr(self, field, '')
        self.description = mnetResource.description
        self.name = mnetResource.title
        self.language = mnetResource.language
        self.contentUrl = mnetResource.content['url'] if mnetResource.content else ''
        self.thumbnailUrl = mnetResource.image if mnetResource.image else ''
        self.licenseKey = mnetResource.license
        # We only have CC licenses with version 4.0 in MoodleNet
        if mnetResource.license.startswith('cc-'):
            self.licenseVersion = '4.0'
            self.licenseLocale = 'en-US'
            self.licenseSourceUrl = 'https://creativecommons.org/licenses/{}/4.0/'.format(
                mnetResource.license.replace('cc-', '')
            ) if mnetResource.license.startswith('cc-') else ''
        # Date only without time information
        self.datestamp = mnetResource.meta['created'][:10] if 'created' in mnetResource.meta else ''
    
    def getCsvHeader(self):
        return self._delimiter.join(key for key in self.fields)

    def toCsv(self):
        tuple = {}
        for key in self.fields:
            value = getattr(self, key)
            if value is None or (isinstance(value, str) and value.strip() == ''):
                tuple[key] = ''
            else:
                if value.find (self._delimiter) >= 0 or value.find(self._quotes) >= 0:
                    tuple[key] = self._quotes + str(value).replace(self._quotes, self._quotes*2) + self._quotes
                else:
                    tuple[key] = str(value)
        return self._delimiter.join(tuple[key] for key in self.fields)