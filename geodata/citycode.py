# -*- coding: utf-8 -*-
import codecs
import re
import copy
import json

def getlist():
    arealist = getarealist()

    with codecs.open('../jma-definition/CityCode.csv', encoding='utf-8') as f:
        f.readline() # header
        data = {}

        for line in f:
            row = line.split(',')

            if row[5] == '1': # 気象警報で使用
                split = re.match(u"気象庁予報警報規程別表", row[1]) is not None

                code = str(row[0])
                data[code] = copy.deepcopy(arealist[row[4]])

                data[code]['name'] = row[2]
                data[code]['code'] = code
                #data[code]['splitArea'] = split

        return data


def getarealist():
    '''
    prefecture 府県予報区
    distlict   一次細分
    division   市町村等をまとめた地域
    city       二次細分
    '''
    with codecs.open('../jma-definition/AreaForecastLocal.csv', encoding='utf-8') as f:
        f.readline() # header
        area = {}

        for line in f:
            row = line.split(',')

            area[row[0]] = {
                'divisionCode': row[0],
                'divisionName': row[1],
                'distlictCode': row[2],
                'distlictName': row[3],
                'prefCode': row[4],
                'prefName': row[5],
            }

        return area


def getdivisionlist():
    arealist = getarealist()

    with codecs.open('../jma-definition/CityCode.csv', encoding='utf-8') as f:
        f.readline() # header
        data = {}
        codelist = {}

        for line in f:
            row = line.split(',')

            if row[5] == '1': # 気象警報で使用
                citycode = str(row[0])
                dcode = str(row[4])

                if dcode in data:
                    codelist[dcode].append(citycode)

                else:
                    data[dcode] = copy.deepcopy(arealist[dcode])
                    codelist[dcode] = [citycode]

        return data, codelist


def getdistlictlist():
    arealist = getarealist()

    with codecs.open('../jma-definition/CityCode.csv', encoding='utf-8') as f:
        f.readline() # header
        data = {}
        codelist = {}

        for line in f:
            row = line.split(',')

            if row[5] == '1': # 気象警報で使用
                citycode = str(row[0])
                dcode = str(row[4])
                code = arealist[dcode]['distlictCode']

                if code in data:
                    codelist[code].append(citycode)

                else:
                    d = arealist[dcode]
                    data[code] = {
                        'distlictCode': d['distlictCode'],
                        'distlictName': d['distlictName'],
                        'prefCode': d['prefCode'],
                        'prefName': d['prefName'],
                    }
                    codelist[code] = [citycode]

        return data, codelist


def getpreflist():
    arealist = getarealist()

    with codecs.open('../jma-definition/CityCode.csv', encoding='utf-8') as f:
        f.readline() # header
        data = {}
        codelist = {}

        for line in f:
            row = line.split(',')

            if row[5] == '1': # 気象警報で使用
                citycode = str(row[0])
                dcode = str(row[4])
                code = arealist[dcode]['prefCode']

                if code in data:
                    codelist[code].append(citycode)

                else:
                    d = arealist[dcode]
                    data[code] = {
                        'prefCode': d['prefCode'],
                        'prefName': d['prefName'],
                    }
                    codelist[code] = [citycode]

        return data, codelist


def createlistjson():
    citylist = getlist()
    jsondata = {}

    for citycode in citylist.keys():
        d = citylist[citycode]

        if not d['prefCode'] in jsondata:
            jsondata[d['prefCode']] = {
                'name': d['prefName'],
                'data': {}
            }

        prefdata = jsondata[d['prefCode']]['data']
        if not d['distlictCode'] in prefdata:
            prefdata[d['distlictCode']] = {
                'name': d['distlictName'],
                'data': {}
            }

        distlictdata = prefdata[d['distlictCode']]['data']
        if not d['divisionCode'] in distlictdata:
            distlictdata[d['divisionCode']] = {
                'name': d['divisionName'],
                'data': {}
            }

        divisiondata = distlictdata[d['divisionCode']]['data']
        divisiondata[d['code']] = { 'name': d['name'] }


    with open('list.json', 'w') as f:
        json_str = json.dumps(jsondata, ensure_ascii=False)
        f.write(json_str.encode('utf-8'))


if __name__ == '__main__':
    createlistjson()

