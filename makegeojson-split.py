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

def split01233(name, code):
    if int(code) > 400: # 伊達市大滝
        return '0123302'
    else:
        return '0123301' # 伊達市伊達

def split01601(name, code):
    if int(code) <= 40 :
        return '0160101' # 日高町日高
    else:
        return '0160102' # 日高町門別

def split01346(name, code):
    if name[:2] == u'熊石':
        return '0134602' # 八雲町熊石
    else:
        return '0134601' # 八雲町八雲

def split04421(name, code):
    seibu = [u'宮床', u'吉岡', u'吉田']
    if name[:2] in seibu or code == '0090' or code == '0060':
        return '0442102' # 大和町西部
    else:
        return '0442101' # 大和町東部

def split04215(name, code):
    if name[:3] == u'岩出山' or name[:2] == u'鳴子':
        return '0421502' # 大崎市西部
    else:
        return '0421501' # 大崎市東部

def split04213(name, code):
    west = [u'一迫', u'鶯沢', u'栗駒', u'花山']
    if name[:2] in west:
        return '0421302' # 栗原市西部
    else:
        return '0421301' # 栗原市東部


def split23211(name, code):
    # source: https://ja.wikipedia.org/wiki/%E8%B1%8A%E7%94%B0%E5%B8%82%E3%81%AE%E7%94%BA%E5%90%8D%E3%81%AE%E4%B8%80%E8%A6%A7#.E8.B6.B3.E5.8A.A9.E5.9C.B0.E5.8C.BA
    if int(code) >= 3290:
        return '2321102' # 豊田市東部
    else:
        return '2321101' # 豊田市西部

def split25201(name, code):
    # xxx: not all
    north = [u'小野', u'葛川', u'木戸', u'小松', u'和邇', u'朝日', u'水明', u'湖青']
    if name[:2] in north or name[:3] == u'伊香立':
        return '2520102' # 大津市北部
    else:
        return '2520101' # 大津市南部

def split29207(name, code):
    if name[:3] == u'大塔町':
        return '2920702' # 五條市南部
    else:
        return '2920701' # 五條市北部

def split30206(name, code):
    if name is None: # 無人島? 
        return '3020601' # 田辺
    elif name[:2] == u'龍神':
        return '3020602' # 龍神
    elif name[:3] == u'中辺路':
        return '3020603' # 中辺路
    elif name[:2] == u'大塔':
        return '3020604' # 大塔 xxx
    elif name[:2] == u'本宮':
        return '3020605' # 本宮
    else:
        return '3020601' # 田辺

def split31201(name, code):
    south = [u'河原町', u'用瀬町', u'佐治町']
    if name[:3] in south:
        return '3120102' # 鳥取市南部
    else:
        return '3120101' # 鳥取市北部


split_areas = [
    #['01484', split01484],
    #['01206', split01206],
    #['01208', split01208],
    #['01233', split01233],
    #['01601', split01601],
    #['01346', split01346],
    #['04421', split04421],
    #['04215', split04215],
    #['04213', split04213],

    #['23211', split23211],
    #['25201', split25201],
    #['29207', split29207],
    #['30206', split30206],
    ['31201', split31201],
]

def main():
    for area in split_areas:
        areas = {}
        geojson = estat.get_geojson(area[0])
        load_geojson(geojson, area[1], areas)
        output_geojson(areas)


def split_sendai():
    areas = {}

    geojson1 = estat.get_geojson('04101')
    load_geojson(geojson1, split04101, areas)

    geojson2 = estat.get_geojson('04102')
    load_geojson(geojson2, split0410001, areas)

    geojson3 = estat.get_geojson('04103')
    load_geojson(geojson3, split0410001, areas)

    geojson4 = estat.get_geojson('04104')
    load_geojson(geojson4, split04104, areas)

    geojson5 = estat.get_geojson('04105')
    load_geojson(geojson5, split0410002, areas)

    output_geojson(areas)


def split04101(name, code): # 青葉区
    # 宮城総合支所
    # source http://www.city.sendai.jp/aoba-kusesuishin/aobaku/shokai/profile/shokankuiki.html
    miyagi = [u'赤坂', u'愛子中央', u'愛子東', u'芋沢', u'大倉', u'落合', u'上愛子', u'国見ケ丘', u'熊ケ根', u'栗生', u'郷六', u'作並', u'下愛子', u'高野原', u'中山台', u'中山台西', u'中山吉成', u'錦ケ丘', u'ニツカ', u'新川', u'南吉成', u'みやぎ台', u'向田', u'吉成', u'吉成台', u'臨済院']

    if name in miyagi:
        return '0410002' # 仙台市西部

    elif name[-2:] == u'丁目' and name[:-3] in miyagi:
        return '0410002' # 仙台市西部

    else:
        return '0410001' # 仙台市東部

def split04104(name, code): # 太白区
    # 秋保総合支所
    if name[:3] in u'秋保町':
        return '0410002' # 仙台市西部

    else:
        return '0410001' # 仙台市東部

def split0410001(name, code): # 宮城野区, 若林区
    return '0410001' # 仙台市東部

def split0410002(name, code): # 泉区
    return '0410002' # 仙台市西部



def load_geojson(filename, split_func, areas):
    with open(filename) as f:
        data = json.loads(f.read(), 'utf-8')

        sort = False
        codes = {}

        # append splited polygons
        for feature in data['features']:

            if feature['properties']['HCODE'] == 8154: # 水面
                continue
            
            city_name = feature['properties']['CSS_NAME']
            area_name = feature['properties']['MOJI']
            area_code = feature['properties']['KIHON1']

            if area_name is not None and area_name[-4:] == u'（湖面）':
                continue

            if not sort:
                print area_name, area_code
                code = split_func(area_name, area_code)
                append_geometry(areas, code, feature)
            else:
                codes[area_code] = [area_name, feature]

        if sort:
            for code in sorted(codes.keys()):
                print code, codes[code][0]


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
    #split_sendai()


