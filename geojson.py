# -*- coding: utf-8 -*-
import json
import codecs

import citycode


def main():
    citylist = citycode.getlist()

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
                pass
            else:
                if parent_code in citylist:
                    print parent_code, citylist[parent_code]['name']
                else:
                    print city_name, name


if __name__ == '__main__':
    main()


