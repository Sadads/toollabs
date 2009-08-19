#!/usr/bin/python
# -*- coding: utf-8  -*-
'''
http://wikipedia.ramselehof.de/flinfo.php
https://fisheye.toolserver.org/browse/Magnus/flickr2commons.php?r=HEAD
'''
import sys, urllib
sys.path.append("/home/multichill/pywikipedia")
import wikipedia, config, query

import flickrapi
import xml.etree.ElementTree
api_key = 'e3df7868503946355dae7a1c6a1bd8fd'

allowed_tags =	[   u'gama',
		    u'vanmourik',
                    u'twentsewelle',
                    u'kunsthal',
                    u'nemo',
                    u'thermenmuseum',
                    u'gemeentemuseum',
                    u'vincent van gogh',
                    u'nbm',
                    u'textielmuseum',
                    u'naturalis',
                    u'sieboldhuis',
                    u'vanabbemuseum',
                    u'rmo',
                    u'openluchtmuseum',
                    u'visserijmuseum',
                    u'catharijneconvent',
                    u'aardewerkmuseum',
                    u'zeeuwsmuseum',
                    u'rmt',
                    u'nai',
                    u'admiraliteitshuis',
                    u'loevestein',
                    u'tropenmuseum',
                    u'historischetuin',
                    u'friesmuseum',
                    u'nimk',
                    u'boijmans',
                    u'glaspaleis',
                    u'maritiem',
                    u'princessehof',
                    u'friesmuseum',
                    u'franshals',
                    u'vermeerdelft',
		]

waiting_tags =	[   u'museumhilversum',
		    u'jhm',
		    u'allardpierson',
		    u'havenmuseum',
		    u'vrijthof',
		    u'verzetsmuseum',
		    u'volkenkunde',
		]

denied_tags =	[   u'ing',	    # Ing needs OTRS
		    u'gdm',	    # Derivative works, not free
		    u'nocommons',   # Dont upload to Commons
		    u'nowcommons',  # Is already uploaded
		]

def getPhotosInGroup(flickr=None, group_id=''):
    '''
    Get a list of photo id's
    '''
    result = []
    #First get the total number of photo's in the group
    photos = flickr.groups_pools_getPhotos(group_id=group_id, per_page='100', page='1')
    pages = photos.find('photos').attrib['pages']
    
    for i in range(1, int(pages)):
        for photo in flickr.groups_pools_getPhotos(group_id=group_id, per_page='100', page=i).find('photos').getchildren():
            print photo.attrib['id']
            yield photo.attrib['id']

def getPhotos(flickr=None, photoIds=[]):
    result = []
    for photo_id in photoIds:
        result.append(getPhoto(flickr=flickr, photo_id=photo_id))
    return

def getPhoto(flickr=None, photo_id=''):
    photoInfo = flickr.photos_getInfo(photo_id=photo_id)
    #xml.etree.ElementTree.dump(photoInfo)
    photoSizes = flickr.photos_getSizes(photo_id=photo_id)
    #xml.etree.ElementTree.dump(photoSizes)
    return (photoInfo, photoSizes)

def isAllowedLicense(photoInfo=None):
    license = photoInfo.find('photo').attrib['license']
    if (license=='4' or license=='5'):
	#Is cc-by or cc-by-sa
	return True
    else:
	#We don't accept other licenses
	return False

def getTags(photoInfo=None):
    result = []
    for tag in photoInfo.find('photo').find('tags').findall('tag'):
	result.append(tag.text.lower())
    return result

def photoCanUpload(tags=[]):
    foundAllowed = False
    #xml.etree.ElementTree.dump(photoInfo)
    for tag in tags:
	if tag in denied_tags:
	    return False
	elif tag in allowed_tags:
	    foundAllowed = True
	print tag
    if foundAllowed:
	print 'Foundallowed'
	return True
    else:
	#Didn't find an allowed tag
	return False

def getFlinfoDescription(photoId=0):
    '''
    Get the description from http://wikipedia.ramselehof.de/flinfo.php?id=3691355871&raw=on&user_lang=
    '''
    parameters = urllib.urlencode({'id' : photoId, 'raw' : 'on'})
    
    print 'Flinfo gaat nu aan de slag'
    rawDescription = urllib.urlopen("http://wikipedia.ramselehof.de/flinfo.php?%s" % parameters).read()
    #print rawDescription.decode('utf-8')
    return rawDescription.decode('utf-8')

def getTagDescription(tags=[]):
    description = u''
    template = u'User:Multichill/WLANL/descriptions'
    for tag in tags:
	description = description + expandTemplates(template=template, parameter=tag)
    #print 'De tag based description is:'
    #print description.strip()
    return description.strip()

def getTagCategories(tags=[]):
    categories = u''
    template = u'User:Multichill/WLANL/museums'
    for tag in tags:
	categories = categories + expandTemplates(template=template, parameter=tag)
    #print 'De tag categories zijn:'
    #print categories.strip()
    return categories.strip()

def getFilename(photoInfo=None):
    '''
    Build a good filename for the upload
    '''
    username = photoInfo.find('photo').find('owner').attrib['username']
    title = photoInfo.find('photo').find('title').text

    return u'WLANL - %s - %s.jpg' % (username, title)

def buildDescription(flinfoDescription=u'', tagDescription=u'', tagCategories=u''):
    '''
    Build the final description for the image
    '''
    description = u''
    if not(tagDescription==u''):
	description = flinfoDescription.replace(u'|Description=', u'|Description=' + tagDescription + u' ')
    else:
	description = flinfoDescription
    description = description + tagCategories
    # Add WLANL template
    description = description.replace(u'{{flickrreview}}', u'{{WLANL}}\n{{flickrreview}}')
    # Mark as flickr reviewed
    description = description.replace(u'{{flickrreview}}', u'{{flickrreview|Multichill|{{subst:CURRENTYEAR}}-{{subst:CURRENTMONTH}}-{{subst:CURRENTDAY2}}}}')
    # Filter the categories
    print description
    return description
    
def prepareUpload(photoInfo=None, photoSizes=None):

    return 0

def cleanUpCategories(description =''):

    return ''

def expandTemplates(template='', parameter=''): # should be dict
    text = u'{{' + template + u'|' + parameter + u'}}'

    params = {
	'action'    : 'expandtemplates',
	'text'	    : text
    }

    data = query.GetData(params, wikipedia.getSite(), useAPI = True, encodeTitle = False)
    # Beware, might be some encoding issues!
    return data['expandtemplates']['*']
    return 0


def main():
    site = wikipedia.getSite(u'commons', u'commons')
    wikipedia.setSite(site)

    flickr = flickrapi.FlickrAPI(api_key)
    groupId = '1044478@N20'
    #photos = flickr.flickr.groups_search(text='73509078@N00', per_page='10') = 1044478@N20
    for photoId in getPhotosInGroup(flickr=flickr, group_id=groupId):
        (photoInfo, photoSizes) = getPhoto(flickr=flickr, photo_id=photoId)
	if isAllowedLicense(photoInfo=photoInfo):
	    tags=getTags(photoInfo=photoInfo)
	    if photoCanUpload(tags=tags):
		flinfoDescription = getFlinfoDescription(photoId=photoId)
		tagDescription = getTagDescription(tags=tags)
		tagCategories = getTagCategories(tags)
		filename = getFilename(photoInfo=photoInfo)
		print filename
		photoDescription = buildDescription(flinfoDescription, tagDescription, tagCategories)
		#(photoUrl, filename, photoDescription) = prepareUpload(photoInfo=photoInfo, photoSizes=photoSizes)
		#Do the actual upload
		print 'bla'
        
    #photos = getPhotos(flickr=flickr, photoIds=photoIds)
    #photos = flickr.groups_pools_getPhotos(group_id=group_id, per_page='10', page='1')
    #xml.etree.ElementTree.dump(photos)

    print 
    
    for item in photos.getchildren():
        print item.attrib
        for photo in item.getchildren():
            print photo.attrib
    #print photos
    
if __name__ == "__main__":
    try:
        main()
    finally:
        print 'done'
        #wikipedia.stopme()
