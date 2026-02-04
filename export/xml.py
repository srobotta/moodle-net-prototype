from moodlenet import MoodleNetResource

class XmlResource():
    """
    XmlResource represents a single resource in some XML format.
    """
    _originUniversity = ''
    _mnetResource = None

    def setOriginUniversity(self, university: str) -> XmlResource:
        """
        Set university string.
        
        :param university: University name
        :type university: str
        :return: self for chaining
        :rtype: XmlResource
        """
        self._originUniversity = university
        return self

    def setMoodleNetResource(self, mnetResource: MoodleNetResource) -> XmlResource:
        """
        Set an instance of MoodleNetResource to populate the SwitchOerResource fields.
        
        :param mnetResource: MoodleNetResource instance
        :type mnetResource: MoodleNetResource
        :return: self for chaining
        :rtype: XmlResource
        """
        self._mnetResource = mnetResource
        return self

    def getHeader(self) -> str:
        """
        Returns the XML header line string.

        return: XML header string and opening root tag
        retype: str
        """
        return '<?xml version="1.0" encoding="UTF-8"?>\n<resources>'

    def getResourceString(self):
        """
        Returns an XML string for the current resource.

        return: XML string
        retype: str
        """

        xml = (
            '<resource lang="{language}">\n'
            '  <name>{name}</name>\n'
            '  <type>{type}</type>\n'
            '  <contentUrl>{contentUrl}</contentUrl>\n'
            '  <thumbnailUrl>{thumbnailUrl}</thumbnailUrl>\n'
            '  <license>{licenseKey}</license>\n'
            '  <subject>{subject}</subject>\n'
            '  <originUniversity>{originUniversity}</originUniversity>\n'
            '</resource>'
        ).format(
            language = self.escape(self._mnetResource.language[0:2].upper() if self._mnetResource.language else ''),
            name = self.escape(self._mnetResource.title),
            type = self.escape(self.getResourceType()),
            contentUrl = self.escape(self._mnetResource.content['url'] if self._mnetResource.content else ''),
            thumbnailUrl = self.escape(self._mnetResource.image if self._mnetResource.image else ''),
            licenseKey = self.escape(self._mnetResource.license),
            subject = self.escape(self._mnetResource.subject),
            originUniversity = self.escape(self._originUniversity)
        )
        return xml
    
    def getFooter(self) -> str:
        """
        Returns the XML closing root tag.

        return: XML closing root tag
        retype: str
        """
        return '</resources>'
    
    def getResourceType(self) -> str:
        """
        From the MoodleNet resource type based on the suffix
        """
        name = self._mnetResource.content['name'] if self._mnetResource.content['type'] != '__link__' else self._mnetResource.content['url']
        suffix = name.split('.')[-1].lower() if name and '.' in name else ''
        return suffix
    
    def escape(self, value: str) -> str:
        """
        Escape special characters for XML.

        :param value: The string to escape
        :type value: str
        :return: The escaped string
        :rtype: str
        """
        if not value:
            return ''
        return (value.replace('&', '&amp;')
                     .replace('<', '&lt;')
                     .replace('>', '&gt;')
                     .replace('"', '&quot;')
                     .replace("'", '&apos;'))