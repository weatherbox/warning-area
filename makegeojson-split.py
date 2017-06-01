# -*- coding: utf-8 -*-
import json
import codecs

import geojson
import shapely.geometry
import shapely.ops

import citycode
import estat

citylist = citycode.getlist()

def split01484(name, code):
    if name[2:4] == u'焼尻' or name[2:4] == u'天売':
        return '0148402' # 天売焼尻
    else:
        return '0148401' # 羽幌町

def split01206(name, code):
    if name[:3] == u'阿寒町':
        return '0120602'
    elif name[:3] == u'音別町':
        return '0120603'
    else:
        return '0120601' # 釧路市釧路

def split01208(name, code):
    if int(code) > 1200: # 北見市常呂
        return '0120802'
    else:
        return '0120801' # 北見市北見

split_areas = [
    #['01484', split01484],
    #['01206', split01206],
    ['01208', split01208],
]

def main():
    for area in split_areas:
        geojson = estat.get_geojson(area[0])
        load_geojson(geojson, area[1])




def load_geojson(filename, split_func):
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

            if area_name[-4:] == u'（湖面）':
                continue

            print area_name, area_code
            code = split_func(area_name, area_code)
            append_geometry(areas, code, feature)

        output_geojson(areas)


def append_geometry(areas, code, feature):
    if not code in areas:
        areas[code] = []

    poly = shapely.geometry.asShape(feature['geometry'])
    areas[code].append(poly)


def output_geojson(areas):
    for code in areas.keys():
        feature = create_city_geojson(code, areas[code], citylist[code])


def create_city_geojson(code, polygons, meta):
    geometry = shapely.ops.cascaded_union(polygons)
    feature = geojson.Feature(geometry=geometry, properties=meta)

    with open('geojson-split/' + code + '.json', 'w') as f:
        json_str = geojson.dumps(feature, ensure_ascii=False)
        f.write(json_str.encode('utf-8'))

    return feature

if __name__ == '__main__':
    main()


