# -*- coding: utf-8 -*-
import json
import codecs
import os

import geojson
import shapely.geometry
import shapely.ops

import citycode


def main():
    citylist = citycode.getlist()

    cities = load_geojson(citylist)
    output_geojson(cities, citylist)

def load_geojson(citylist):
    with open('data/N03-170101_GML/japan2016.json') as f:
        data = json.loads(f.read(), 'utf-8')
        cities = {}

        # append splited polygons
        for feature in data['features']:
            
            city_name = feature['properties']['N03_003']
            name = feature['properties']['N03_004']
            code = feature['properties']['N03_007']

            if code is None:
                continue

            jma_code = str(code) + '00'

            #append_geometry(cities, code, feature)

            if jma_code in citylist:
                #append_geometry(cities, jma_code, feature)
                pass

            else:
                parent_code = get_parent_code(str(code))
                if parent_code in citylist:
                    append_geometry(cities, parent_code, feature)

                else:
                    #print city_name, name
                    pass

        return cities

def get_parent_code(code):
    '''
    政令指定都市 区がある
    '''

    second_designated_city = [
        '1413', # 川崎市
        '1415', # 相模原市
        '2714', # 堺市
        '4010', # 北九州市
        '4013', # 福岡市
    ]

    if code[:4] in second_designated_city:
        return code[:4] + '000'

    elif code[:4] == '2213': # 浜松市
        if code == '22137':
            return '2213002' # 浜松市北部
        else:
            return '2213001' # 浜松市南部

    else: # first designated city
        return code[:3] + '0000'


def output_geojson(cities, citylist):
    print 'cities:' + str(len(cities))
    #collection = []

    for code in cities.keys():
        feature = create_city_geojson(code, cities[code], citylist)
        #collection.append(feature)

    '''
    with open('geojson/04.json', 'w') as f:
        features = geojson.FeatureCollection(collection)
        json_str = geojson.dumps(features, ensure_ascii=False)
        f.write(json_str.encode('utf-8'))
    '''

def append_geometry(cities, code, feature):
    if not code in cities:
        cities[code] = []

    poly = shapely.geometry.asShape(feature['geometry'])
    cities[code].append(poly)


def create_city_geojson(code, polygons, citylist):
    geometry = shapely.ops.cascaded_union(polygons)
    feature = geojson.Feature(geometry=geometry, properties=citylist[code])

    pref = code[:2]
    dir = 'geojson3/' + pref
    if not os.path.exists(dir): os.mkdir(dir)

    with open(dir + '/' + code + '.geojson', 'w') as f:
        json_str = geojson.dumps(feature, ensure_ascii=False)
        f.write(json_str.encode('utf-8'))

    return feature

if __name__ == '__main__':
    main()


