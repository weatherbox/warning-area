# -*- coding: utf-8 -*-
import json
import codecs
import os, sys

import geojson
import shapely.geometry
import shapely.ops

import citycode


def main(pref):
    citylist = citycode.getlist()
    codes = [c for c in citylist.keys() if c[:2] == pref]

    print codes

    collection = []

    for code in codes:
        collection.append(load_geojson(code, citylist))

    print str(len(collection)) + ' features'

    with open('geojson/' + pref + '.geojson', 'w') as f:
        features = geojson.FeatureCollection(collection)
        json_str = geojson.dumps(features, ensure_ascii=False)
        f.write(json_str.encode('utf-8'))


def load_geojson(code, citylist):
    filename = 'geojson/' + code[:2] + '/' + code + '.geojson'
    with open(filename) as f:
        data = json.loads(f.read(), 'utf-8')

        if data['type'] == 'FeatureCollection':
            # qgis作成geojson
            polygons = []
            for feature in data['features']:
                if feature['geometry']['type'] == 'GeometryCollection': continue
                poly = shapely.geometry.asShape(feature['geometry'])
                polygons.append(poly)
                
            return create_city_geojson(code, polygons, citylist)

        else:
            # makegeojson.py生成
            return geojson.Feature(geometry=data['geometry'], properties=data['properties'])


def create_city_geojson(code, polygons, citylist):
    geometry = shapely.ops.cascaded_union(polygons)
    feature = geojson.Feature(geometry=geometry, properties=citylist[code])

    pref = code[:2]
    dir = 'geojson/' + pref
    if not os.path.exists(dir): os.mkdir(dir)

    with open(dir + '/' + code + '.geojson', 'w') as f:
        json_str = geojson.dumps(feature, ensure_ascii=False)
        f.write(json_str.encode('utf-8'))

    return feature

if __name__ == '__main__':
    main(sys.argv[1])

