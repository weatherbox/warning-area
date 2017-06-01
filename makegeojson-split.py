# -*- coding: utf-8 -*-
import json
import codecs

import geojson
import shapely.geometry
import shapely.ops

import citycode
import estat


def main():
    #citylist = citycode.getlist()

    #cities = load_geojson(citylist)
    #output_geojson(cities, citylist)

    geojson = estat.get_geojson('01484')
    load_geojson(geojson)


def load_geojson(filename):
    with open(filename) as f:
        data = json.loads(f.read(), 'utf-8')
        areas = {}

        # append splited polygons
        for feature in data['features']:

            if feature['properties']['HCODE'] == 8154: # 水面
                continue
            
            city_name = feature['properties']['CSS_NAME']
            area_name = feature['properties']['MOJI']
            area_code = feature['properties']['KIHON1']

            print area_name, area_code




def append_geometry(cities, code, feature):
    if not code in cities:
        cities[code] = []

    poly = shapely.geometry.asShape(feature['geometry'])
    cities[code].append(poly)


def output_geojson(city_data, code, citylist):
    feature = create_city_geojson(code, city_data, citylist[code])


def create_city_geojson(code, polygons, meta):
    geometry = shapely.ops.cascaded_union(polygons)
    feature = geojson.Feature(geometry=geometry, properties=meta)

    with open('geojson/' + code + '.json', 'w') as f:
        json_str = geojson.dumps(feature, ensure_ascii=False)
        f.write(json_str.encode('utf-8'))

    return feature

if __name__ == '__main__':
    main()


