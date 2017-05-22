# -*- coding: utf-8 -*-
import codecs
import re
import copy

def getlist():
    arealist = getarealist()

    with codecs.open('jma-definition/CityCode.csv', encoding='utf-8') as f:
        f.readline() # header
        data = {}

        for line in f:
            row = line.split(',')

            if row[5] == '1': # 気象警報で使用
                split = re.match(u"気象庁予報警報規程別表", row[1]) is not None

                code = str(row[0])
                data[code] = copy.deepcopy(arealist[row[4]])

                data[code]['name'] = row[2]
                data[code]['splitArea'] = split

        return data


def getarealist():
    '''
    prefecture 府県予報区
    distlict   一次細分
    division   市町村等をまとめた地域
    city       二次細分
    '''
    with codecs.open('jma-definition/AreaForecastLocal.csv', encoding='utf-8') as f:
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

if __name__ == '__main__':
    cities = getlist()
    for l in cities.keys():
        c = cities[l]
        print ','.join([l, c['name'], str(c['splitArea']), c['divisionName'], c['distlictName'], c['prefName']])


