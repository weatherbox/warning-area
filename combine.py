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

    if not pref == 'all':
        codes = [c for c in citylist.keys() if c[:2] == pref]
        print codes

    else:
        codes = citylist.keys()

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
                
            return create_geojson(code, 'geojson/' + code[:2], polygons, citylist[code])

        else:
            # makegeojson.py生成
            return geojson.Feature(geometry=data['geometry'], properties=data['properties'])


def create_geojson(code, dir, polygons, properties):
    geometry = shapely.ops.cascaded_union(polygons)
    feature = geojson.Feature(geometry=geometry, properties=properties)

    if not os.path.exists(dir): os.mkdir(dir)

    with open(dir + '/' + code + '.geojson', 'w') as f:
        json_str = geojson.dumps(feature, ensure_ascii=False)
        f.write(json_str.encode('utf-8'))

    return feature


def load_geometry(code):
    filename = 'geojson/' + code[:2] + '/' + code + '.geojson'
    with open(filename) as f:
        data = json.loads(f.read(), 'utf-8')
        return shapely.geometry.asShape(data['geometry'])

def load_feature(file):
    with open(file) as f:
        data = json.loads(f.read(), 'utf-8')
        return geojson.Feature(geometry=data['geometry'], properties=data['properties'])

def create_division_geojson():
    divisionlist = citycode.getdivisionlist()
    collection = []

    for dcode in divisionlist.keys():
        division = divisionlist[dcode]
        features = []

        print dcode, division

        for code in division['codes']:
            features.append(load_geometrye(code))

        feature = create_geojson(dcode, 'geojson/division', features, division)
        collection.append(feature)


def create_all_division_geojson():
    divisionlist = citycode.getdivisionlist()
    collection = []

    for dcode in divisionlist.keys():
        collection.append(load_feature('geojson/division/' + dcode + '.geojson'))

    print str(len(collection)) + ' features'

    with open('geojson/division-all.geojson', 'w') as f:
        features = geojson.FeatureCollection(collection)
        json_str = geojson.dumps(features, ensure_ascii=False)
        f.write(json_str.encode('utf-8'))


if __name__ == '__main__':
    if sys.argv[1] == 'division':
        #create_division_geojson()
        create_all_division_geojson()

    else:
        main(sys.argv[1])

