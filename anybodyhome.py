#! /usr/bin/python3

import requests
import json
from shapely.geometry import Polygon
from shapely.geometry import box
from shapely import wkt

import re

#not used yet
#from shapely import geometry
#import pyproj

# utilities for calling ELVIS
from callingelvis.utils import listcollections
from callingelvis.utils import pointcloudfilter

#define ELVIS URL globally
ELVISURL = "https://elvis2018-ga.fmecloud.com/fmedatastreaming/elvis_indexes/ReturnDownloadables.fmw"

#https://elvis2018-ga.fmecloud.com/fmedatastreaming/elvis_indexes/ReturnDownloadables.fmw?polygon=POLYGON((148.99281%20-35.04658%2C148.99281%20-34.67726%2C149.20017%20-34.67726%2C149.20017%20-35.04658%2C148.99281%20-35.04658))

def parseresponse(responsecontent, sourcekey, pointtype, heightref, year):
    """
    function to assemble point cloud URLS into a per-source dictionary

    """
    datadict = {}
    heightrefdict = {}
    datalist = []

    #need to decide which point clouds to look for.

    pointfilter = pointcloudfilter(pointtype)

    if "downloadables" in responsecontent[sourcekey]:
        if "Point Clouds" in responsecontent[sourcekey]["downloadables"]:
            #if no height ref is set
            if heightref is None:
                # we want to loop over each height ref dictionary
                for height in responsecontent[sourcekey]["downloadables"]["Point Clouds"]:
                    print(height)
                    # and in each height ref dict
                    for dataset in responsecontent[sourcekey]["downloadables"]["Point Clouds"][height]:
                        #loop over the list-of-dicts and construct a filtered list-of-dicts
                        if re.search(pointfilter, dataset["file_url"], re.IGNORECASE):
                            if year is not None and str(year) in dataset["file_url"]:
                                datalist.append(dataset)
                            elif year is None:
                                datalist.append(dataset)

                    if datalist:
                        datadict.update({ height : datalist })
                        datalist = []
                    else:
                        datadict = "No data"



            else:
                #if a height ref is set
                for height in responsecontent[sourcekey]["downloadables"]["Point Clouds"]:
                    # we only want to loop over the list-of-dicts in that height slot
                    if heightref in height:
                        for dataset in responsecontent[sourcekey]["downloadables"]["Point Clouds"][height]:
                            if re.search(pointfilter, dataset["file_url"], re.IGNORECASE):
                                if year is not None and str(year) in dataset["file_url"]:
                                    datalist.append(dataset)
                                elif year is None:
                                    datalist.append(dataset)

                        if datalist is not None:
                            datadict.update({ height : datalist })
                            datalist = []
                        else:
                            datadict = "No data"


        #if so, add the jurisdiction to the dict
        #datasetdict.update( { "source" : value } )
        #datasetdict.update( { "downloadables" : '' } )

        #return no data if there are no point clouds
        else:
            datadict = "No data"

    #...or no downloadables
    else:
        datadict = "No data"

    #return one dict per data source
    return datadict

def anybodyhome(bbox, pointtype=None, collection=None, year=None, heightref=None):
    """
    function to call ELVIS and return a list of datasets filtered by none, some or all of:
    - bounding box
    - point type
    - managing jurisdiction (collection)
    - year
    - height reference.

    FSDF/ELVIS only takes a bounding box:
    https://elvis2018-ga.fmecloud.com/fmedatastreaming/elvis_indexes/ReturnDownloadables.fmw?ymin=-35.02632&ymax=-35.00564&xmin=146.23878&xmax=146.27106

    We use OGC WCS crs conventions: minx,miny,maxx,maxy to set a BBOX, eg Canberra is roughly:

    [135, -36, 136, -35]

    ...so we first translate the WCS style bbox to an FSDF style query.

    The rest is parsing the response resulting from a query.

    """

    datasetdict = {}

    # elvisurl = "https://elvis2018-ga.fmecloud.com/fmedatastreaming/elvis_indexes/ReturnDownloadables.fmw"
    # ELVIS needs our WCS style bbox to become a polygon...

    bbox = box(bbox[0],bbox[1],bbox[2],bbox[3])

    querybox = wkt.dumps(Polygon(bbox), trim=True)
    querybox = querybox.replace('POLYGON ', 'POLYGON')
    querybox = querybox.replace(', ', ',')

    elvisparams = "polygon=" + querybox

    # get a JSON response from ELVIS
    apiresponse = requests.get(ELVISURL, params=elvisparams)
    print(apiresponse.url)

    responsecontent = json.loads(apiresponse.content)

    #bump off one level, we dont need it
    responsecontent = responsecontent["available_data"]

    #print(responsecontent)

    #create a dictionary of collections / data owners
    collections = listcollections(responsecontent)
    print(collections)
    # if collection is default / None, we want all the data
    if collection is None:
        # loop over each of the 8 collection agencies...
        # this sets up the {"source": ... } level
        # ...where 'source' is the jurisdiction name

        for key, value in collections.items():
            #print(key)
            #print(value)

            thedatasets = parseresponse(responsecontent, key, pointtype, heightref, year)

            datasetdict["value"] = thedatasets

    # otherwise, we want a limited subset of collections
    else:
        for key, value in collections.items():
            #print(key)
            #print(value)
            if collection in value:
                thedatasets = parseresponse(responsecontent, key, pointtype, heightref, year)
                # if there are downloadables...
                datasetdict["value"] =  thedatasets

    #how shall we return the result? A list of datasets in by-region dicts
    return datasetdict

if __name__ == "__main__":
    # cli handling parts -
    #bbox, pointtype=None, collection=None, year=None, heightref=None
    parser = ArgumentParser()
    parser.add_argument("-b", "--bounding-box",
                        help="input bounding box formatted as a WCS request [xmin, ymin, xmax, ymax]")
    parser.add_argument("-p", "--pointtype",
                        help="Define a point type - can be None to collect all point clouds; or 'lidar' to just get LiDAR sources; or 'photo' to just get photogrammetric sources",
                        default=None,
                        required=False)
    parser.add_argument("-c", "--collection",
                        help="Short unique string for collection agency, case insensitive suggest: ACT; NSW; QLD; SA; NT; TAS; WA; GEO. Applying this option restricts returned data to a single agency",
                        default=None,
                        required=False)
    parser.add_argument("-y", "--year",
                        help="four number year, eg 2014, to restrict data to a single year",
                        default=None,
                        required=False)
    parser.add_argument("-h", "--heightref",
                        help="height reference - use AHD or a substring of ellipsoidal, eg ELL",
                        default=None,
                        required=False)

    # unpack arguments
    args = parser.parse_args()

    boundingbox = vars(args)["boundingbox"]
    pointtype = vars(args)["pointtype"]
    collection = vars(args)["collection"]
    year = vars(args)["year"]
    heghtref = vars(args)["heightref"]

    callresult = anybodyhome(boundingbox,pointtype,collection,year,heightref)

    print(callresult)
