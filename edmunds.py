import urllib2
import md5
import os
import json
import pdb
import time
from string import Template

cache = "cache/"
apikey = '369hxbby3j47r5hmj9pk5hg5'
vers = 'v1'
root = 'http://api.edmunds.com/'

#urls to know
findmakes = "/api/vehicle-directory-ajax/findmakes"
findmakes = "/api/vehicle/makerepository/findall"

apisuffix = "?api_key="+apikey
fmt="&fmt=json"
def fetchUrl(url):
    #hash url so we can check it later and save api hits
    hashedURL = md5.md5(url).hexdigest()    

    #check cache
    #print "is ", hashedURL, "in ", os.listdir(cache)
    if hashedURL in os.listdir(cache):
        #cache hit, return contents of that file
        f = open(cache+hashedURL, 'r')
        lines = f.readline()
        print "we got a cached url", url
        print lines
        return eval(lines)

    #cache miss, fetch the url and cache it
    fullURL = root+vers+url+apisuffix+fmt
    print "fetchURL", url, "\nfullURL", fullURL

    data = urllib2.urlopen(root+vers+url+apisuffix+fmt)
    # must not fetch more than 2x/sec, so sleep half a second
    time.sleep(.5)

    print "we got data, now save it"
    dataline = data.readline()

    dataline = dataline.replace(":null", ":\"null\"")
    dataline = dataline.replace("false", "0")
    dataline = dataline.replace("true", "1")

    #write to the file
    f = open(cache+hashedURL, 'w')
    f.write(str(dataline))
    f.close()

    return eval(dataline)

def printJson(jsonContent):
   
    print "pretty ",json.dumps(jsonContent,sort_keys=True,indent=4, separators=(',', ': '))


# To start us off, we need to fetch all of the possible makes of cars
makesAsDict = fetchUrl(findmakes)

#print makesAsDict['makes'].keys()
#printJson(makesAsDict)

#now that we have all of the makes of cars in a dict, time to iterate through them to find all of the models
results = []
for make in makesAsDict['makeHolder']:
    modelsArray = make['models']
    for model in modelsArray[2:]:
        link = model['link']
        print "link for", make['name'], model['name'],"is", link
        modelData = fetchUrl(link)
        #print modelData         
        for modelHolder in modelData['modelHolder']:
            year = modelHolder['modelYears'][0]['year']
            print year
            #if len(modelHolder['modelYears']) > 1:
                #pdb.set_trace()
            if int(year) != 2014:
                for someCategory in modelHolder['subModels'].keys():
                    print "some category is",someCategory
                    contentForSubcategories = modelHolder['subModels'][someCategory]
                    for subcategoryContent in contentForSubcategories:
                        styleIdsForThisModel = subcategoryContent['styleIds']
                        for styleId in styleIdsForThisModel:
                            d = {'style':styleId, 'zip':'94019'}
                            styleTCOUrl = Template("/api/tco/usedtruecosttoownbystyleidandzip/$style/$zip").substitute(d)
                            print "fetching", year,make['name'], model['name']
                            tcoData = fetchUrl(styleTCOUrl)
                            res = {"make":make['name'], "model":model['name'], "year":year, "tco":tcoData['value']}
                            print res
                            results.append(res) 
                            sort = sorted(results, key=lambda k: k['tco'])
                            print "sorted results"
                            print printJson(sort[:5])
  

#for makeKey in makesAsDict['makes'].keys():
    #makeLink = makesAsDict['makes'][makeKey]['link']
    #print "fetch",makeLink
    #makesContent = fetchUrl(makeLink)

