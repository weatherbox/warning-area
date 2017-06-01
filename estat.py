# -*- coding: utf-8 -*-
import requests
import json
import zipfile
import re
import os

list_url = 'http://e-stat.go.jp/SG2/eStatGIS/Service.asmx/GetDownloadStep4ListTokeiTag'
file_url = 'http://e-stat.go.jp/SG2/eStatGIS/downloadfile.ashx'

def get(code):
    id = get_id(code)
    filename = download_file(code, id)
    path = unzip(filename)
    print path

def download_file(code, id):
    payload = {
        'state': '',
        'pdf': 0,
        'id': id,
        'cmd': 'D001',
        'type': 5,
        'tcode': 'A002005212010',
        'acode': '',
        'ccode': code
    }
    req = requests.post(file_url, data=payload, stream=True)

    filename = 'data/census-2010-' + code + '.zip'
    with open(filename, 'wb') as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()

    return filename


def get_id(code):
    payload = {
        'censusId': 'A002005212010',
        'statIds': 'T000572',
        'cityIds': code,
        'forHyou': False
    }
    req = requests.post(list_url, data=payload)

    for match in re.finditer(r"dodownload\(0,'(\d+)','(\d)',.*?\)", req.text):
        id = match.group(1)
        type = match.group(2)

        if type == '5':
            return id

def unzip(filename):
    path = filename[:-4]
    os.mkdir(path)

    zfile = zipfile.ZipFile(filename)
    zfile.extractall(path)

    return path

if __name__ == '__main__':
    get('01484')


