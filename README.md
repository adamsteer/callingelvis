# Calling Elvis

***Calling Elvis... is anybody home?***

-- Mark Knopfler/Dire Straits, 1991

Using Python to query the Geoscience Australia ELVIS system, for ANU WALD (http://wald.anu.edu.au).

## API documentation

No formal query API exists. The code here uses the FME cloud endpoint behind the ELVIS front end, and parses the response.

## Proposed usage

The most basic queries use just a bounding box, which is **required**:

`python anybodyhome.py -b [xmin, ymin, xmax, ymax]`

...or:

```
from callingelvis.anybodyhome import anybodyhome

queryresult = anybodyhome(bbox)
```

Filters for jurisdiction / collection, year, point type, and height reference can be added.

These filters only operate on the data package returned from an ELVIS query - ELVIS itself only accepts a bounding box. It may be wise in future to add a method for caching queries in a specific bounding box, unless we know new data have been added.

A full filter set looks like this:

```
from callingelvis.anybodyhome import anybodyhome

bbox = [xmin, ymin, xmax, ymax]
queryresult = anybodyhome(bbox, collection="ACT", pointtype="lidar", year=2015, heightref="AHD" )
```

...however any subset of filters can be applied, since they all default to `None` and handlers for the case of no filter exist.

The results of this function can be exported to JSON using:

```
with open('output.json', 'w') as outfile:
    json.dump(queryresult, outfile)
```

*Note - the output of anybodyhome is not standard GeoJSON*

## Proposed output

A list of datasets organised into dictionaries by data source and height reference, for example:

```
{
        {"ACT Government" :
            { "AHD" : [ {
                        'index_poly_name': '6586070',
                        'file_name': 'ACT2015_4ppm-C3-AHD_6586070_55_0002_0002.zip',
                        'file_url': 'https://s3-ap-southeast-2.amazonaws.com/act.elvis/Lidar/z55/ACT2015_4ppm-C3-AHD_6586070_55_0002_0002.zip',
                        'file_size': '196205608',
                        'file_last_modified': '20170616',
                        'bbox': '148.74207269637532,-35.50100460313498,148.76372090731323,-35.48265938553811'
                        },
                        ...                                
                        ],
         "Ellipsoidal" : [ {
                            'index_poly_name': '6606054',
                            'file_name': 'ACT2015_4ppm-C3-ELL_6606054_55_0002_0002.zip',
                            'file_url': 'https://s3-ap-southeast-2.amazonaws.com/act.elvis/Lidar/z55/ACT2015_4ppm-C3-ELL_6606054_55_0002_0002.zip',
                            'file_size': '656868607',
                            'file_last_modified': '20170619',
                            'bbox': '148.76728008939003,-35.644880907252094,148.78895968493913,-35.626530623629115'
                            },
                            ...
                            ]
            }
        },
        {
        "NSW Government" : "No Data"
        }
    }
```
