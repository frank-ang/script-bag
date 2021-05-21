#!/usr/bin/env python3
# Download "ts" media segments from m3u8 url, including variant streams from master m3u8
# Adapted from https://gist.github.com/anonymouss/5293c2421b4236fc1a38705fefd4f2e7

import os
import urllib.request
import argparse

def readDataFromUrl(url: str, referer: str) -> bytes:

    headers = {'Referer': referer}
    req = urllib.request.Request(url=url, data=None, headers=headers)
    with urllib.request.urlopen(req) as response:
        data = response.read()
    return data


def writeFile(path: str, filename: str, data: bytes) -> None:
    fullPath = os.path.join(path, filename)
    with open(fullPath, 'wb') as file:
        file.write(data)
    return None


def parseM3U8(baseDir: str, baseUrl: str, data: bytes, referer: str) -> None:
    for line in data.splitlines():
        line = line.strip()
        extension = os.path.splitext(line)[1]
        if extension.lower() == b'.ts' or extension.lower() == b'.aac':
            tsUrl = baseUrl + '/' + line.decode()
            print('downloading ', tsUrl)
            tsData = readDataFromUrl(tsUrl, referer)
            writeFile(baseDir, line.decode(), tsData)
        elif extension.lower() == b'.m3u8':
            simpleUrl = baseUrl + '/' + line.decode()
            binDir = os.path.join(baseDir, simpleUrl.split('/')[-2])
            m3u8Name = os.path.basename(simpleUrl)
            print('In master m3u8, processing ', simpleUrl)
            if not os.path.exists(binDir):
                try:
                    os.mkdir(binDir)
                except Exception as e:
                    print(e, ' Create ', binDir, ' failed, exit.')
                    return
            m3u8Data = readDataFromUrl(simpleUrl, referer)
            writeFile(binDir, m3u8Name, m3u8Data)
            parseM3U8(binDir, os.path.dirname(simpleUrl), m3u8Data, referer)


def fetchData(m3u8url: str, referer: str):

    prefixDir='out.gitignore' 
    baseUrl = os.path.dirname(m3u8url)
    m3u8Name = os.path.basename(m3u8url)

    curPath = os.path.abspath(os.curdir)
    binDir = os.path.join(curPath, prefixDir, m3u8url.split('/')[-2])
    print(curPath, baseUrl, binDir)

    if not os.path.exists(prefixDir):
        os.mkdir(prefixDir)

    if not os.path.exists(binDir):
        try:
            os.mkdir(binDir)
        except Exception as e:
            print(e, ' Create ', binDir, ' failed, exit.')
            return False
    m3u8Data = readDataFromUrl(m3u8url, referer)
    writeFile(binDir, m3u8Name, m3u8Data)
    parseM3U8(binDir, baseUrl, m3u8Data, referer)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="m3u/m3u8 url", type=str)
    parser.add_argument("referer", help="Referrer HTTP header", type=str)
    args = parser.parse_args()
    m3u8url=args.url
    referer=args.referer
    fetchData(m3u8url, referer)