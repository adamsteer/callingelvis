#! /usr/bin/python3

"""
Utility functions for calling ELVIS

Adam Steer, for ANU Water and Landscape Dynamics

"""

def listcollections(elvisresponse):
    """
    Create a dictionary of 'data collections' in ELVIS.

    Input: a dictionary comprising the "available_data" element of
    an ELVIS response package

    Output: a dictionary like

    {
    0 : "NSW Government",
    1 : "ACT Government",
    ...
    7 : "Geoscience Australia"
    }

    """
    i = 0
    collections = {}
    while i < len(elvisresponse):
        collections.update( {i : elvisresponse[i]["source"] } )
        i+=1
    return collections

def pointcloudfilter(pointtype):
    """
    Create a regexp filter for finding specific point cloud types.

    Possible input values are:
    None (nonetype)
    lidar (string)
    photo (string)

    Returns a regular expression, which is applied to the 'file_url'
    field at dataset level by 'parseresponse' in anybodyhome.py

    """

    if pointtype is None:
        pointfilter = ".*"

    elif pointtype == "lidar":
        pointfilter = "-LID|lidar"

    elif pointtype == "photo":
        pointfilter = "-PHO"

    return pointfilter

def tolatlon(bbox, crs):
    """
    Use Pyproj to reproject bounding box to
    EPSG:4326, if it supplied in another CRS

    Incomplete as of April 10 2019
    """
    #create bbox corner pairs
    #xmin, ymax
    #xmax, ymax
    #xmin, ymin
    #xmax, ymin
    x = [bbox[0], bbox[2],bbox[0],bbox[2]]
    y = [bbox[3], bbox[3],bbox[1],bbox[1]]

    project = pyproj.Proj(init=crs)  # destination coordinate system

    lons, lats = project(x,y)

    bbox = [lons[0], lats[2], lons[1], lats[0]]

    return bbox
