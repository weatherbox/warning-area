# -*- coding: utf-8 -*-
import json
import codecs

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
            parent_code = str(code[:3]) + '0000'

            if jma_code in citylist:
                append_feature(cities, jma_code, feature)

            else:
                if parent_code in citylist:
                    append_feature(cities, parent_code, feature)

                else:
                    #print city_name, name
                    pass

        return cities

def output_geojson(cities, citylist):
    print 'cities:' + str(len(cities))
    for code in cities.keys():
        if code == '0120200':
            create_geojson(code, cities[code])


def append_feature(cities, code, feature):
    if not code in cities:
        cities[code] = []

    cities[code].append(feature)


def create_geojson(code, feature):
    geojson = {
        'type': 'FeatureCollection',
        'features': feature
    }

    with open(code + '.json', 'w') as f:
        json_str = json.dumps(geojson, ensure_ascii=False)
        f.write(json_str.encode('utf-8'))


if __name__ == '__main__':
    main()


