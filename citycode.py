# -*- coding: utf-8 -*-
import codecs
import re


def getlist():
    with codecs.open('jma-definition/CityCode.csv', encoding='utf-8') as f:
        f.readline() # header
        data = {}

        for line in f:
            row = line.split(',')

            if row[5] == '1': # 気象警報で使用
                split = re.match(u"気象庁予報警報規程別表", row[1]) is not None
                data[row[0]] = {
                    'name': row[2],
                    'parentArea': row[4],
                    'splitArea': split
                }

        return data



if __name__ == '__main__':
    print getlist()


