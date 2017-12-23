#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Bot to scrape paintings from the NGA website.
NGA provides JSON these days for search so that made it a lot easier!
"""
import artdatabot
import pywikibot
import requests
import re


def getNGAGenerator(query=u''):
    '''
    Search for paintings and loop over it. Got 4118 results. Could probably use that for the paging
    '''

    baseurl = u'https://www.nga.gov/collection-search-result/jcr:content/parmain/facetcomponent/parList/collectionsearchresu.pageSize__50.pageNumber__%s.lastFacet__classification.json?classification=painting'

    for i in range(1,83):
        searchurl = baseurl % (i,)
        print searchurl
        searchPage = requests.get(searchurl)
        searchJson = searchPage.json()
        for record in searchJson.get('results'):
            metadata = {}
            ngaid = record.get('id')
            url = u'https://www.nga.gov/content/ngaweb/Collection/art-object-page.%s.html' % (ngaid,)
            metadata['url'] = url
            metadata['artworkidpid'] = u'P4683'
            metadata['artworkid'] = u'%s' % (ngaid,) # I want this to be a string

            metadata['collectionqid'] = u'Q214867'
            metadata['collectionshort'] = u'NGA'
            metadata['locationqid'] = u'Q214867'

            #No need to check, I'm actually searching for paintings.
            metadata['instanceofqid'] = u'Q3305213'

            # Get the ID. This needs to burn if it's not available
            metadata['id'] = record[u'accessionnumber']
            metadata['idpid'] = u'P217'

            if record.get('title'):
                # Chop chop, several very long titles
                if record.get('title') > 220:
                    title = record.get('title')[0:200]
                else:
                    title = record.get('title')
                metadata['title'] = { u'en' : title,
                                      }
            metadata['creatorname'] = record.get('attribution')

            metadata['description'] = { u'nl' : u'%s van %s' % (u'schilderij', metadata.get('creatorname'),),
                                        u'en' : u'%s by %s' % (u'painting', metadata.get('creatorname'),),
                                        }
            # FIXME : This will only catch oil on canvas
            if record.get('medium')==u'oil on canvas':
                metadata['medium'] = u'oil on canvas'

            # Artdatabot will take care of this
            if record.get('displaydate'):
                metadata['inception'] = record.get('displaydate')

            # Data not available
            # record.get('acquisition')

            if record.get('creditline'):
                if record.get('creditline')==u'Samuel H. Kress Collection':
                    metadata['extracollectionqid'] = u'Q2074027'
                elif record.get('creditline')==u'Andrew W. Mellon Collection':
                    metadata['extracollectionqid'] = u'Q46596638'
                elif record.get('creditline').startswith(u'Corcoran Collection'):
                    metadata['extracollectionqid'] = u'Q768446'

            # Get the dimensions
            if record.get('dimensions1'):
                regex_2d = u'overall\: (?P<height>\d+(\.\d+)?) (x|×) (?P<width>\d+(\.\d+)?) cm \([^\)]+\)$'
                regex_3d = u'overall\: (?P<height>\d+(\.\d+)?) (x|×) (?P<width>\d+(\.\d+)?) cm (x|×) (?P<depth>\d+(\.\d+)?) cm \([^\)]+\)$'
                match_2d = re.match(regex_2d, record.get('dimensions1'))
                match_3d = re.match(regex_3d, record.get('dimensions1'))
                if match_2d:
                    metadata['heightcm'] = match_2d.group(u'height')
                    metadata['widthcm'] = match_2d.group(u'width')
                elif match_3d:
                    metadata['heightcm'] = match_3d.group(u'height')
                    metadata['widthcm'] = match_3d.group(u'width')
                    metadata['depthcm'] = match_3d.group(u'depth')

            yield metadata


def main():
    dictGen = getNGAGenerator()

    #for painting in dictGen:
    #    print painting

    artDataBot = artdatabot.ArtDataBot(dictGen, create=True)
    artDataBot.run()

if __name__ == "__main__":
    main()
