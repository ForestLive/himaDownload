# -*- coding: utf-8 -*-
import urllib.request
import time
import json
import re
import socket
import os
import sys
import datetime

import subprocess

def moviePageId(url):
    # はてなのログインURL
    LOAD_URL = url
    SEARCH_KEY = "\d+"
    linkList = []
    # urlopenのdata引数を指定するとHTTP/POSTを送信できる
    with urllib.request.urlopen(url=LOAD_URL,data=None,timeout=socket._GLOBAL_DEFAULT_TIMEOUT) as page:
        # WebページのURLを取得する
        # print(page.geturl())
        # infoメソッドは取得したページのメタデータを返す
        # print(page.info())
        # readlinesでWebページを取得する

        for line in page.readlines():
            line = line.decode('utf-8')
            if "nofollow" in str(line):
                match = re.search(SEARCH_KEY, line)
                if match:
                    if match.group() in linkList:
                        pass
                    elif len(match.group()) > 1:
                        linkList.append(match.group())

    return linkList

def movieIdList(accessUrl):
    print("access : " + accessUrl)

    movieTitle = ""
    topMovieUrl = ""
    movieUrlList = []


    with urllib.request.urlopen(accessUrl,data=None,timeout=socket._GLOBAL_DEFAULT_TIMEOUT) as page:
        for line in page.readlines():
            line = line.decode('utf-8')

            if 'ary_spare_sources = {[' in line:
                if not '{"spare":[]}' in line:
                    print("json create line ",line)
                    data = json.loads(line[line.index('{"spare"'):line.index('"}]};')+4])
                    for movieUrlSize in range(0,len(data['spare'])):
                        movieUrl = data['spare'][movieUrlSize]['src'].replace('%3A',':').replace('%2F','/').replace('%3F','?')
                        movieUrlList.append(movieUrl)



            if "var display_movie_url" in line:
                spList = line.split("\'")
                topMovieUrl = spList[len(spList) - 2].replace('%3A',':').replace('%2F','/').replace('%3F','?').replace('%25','?').replace('external:','')

            if "og:title" in line:
                spList = line.split("\"")
                movieTitle = spList[len(spList) - 2].replace(' - ひまわり動画','')
                movieTitle = movieTitle.replace("/","_")


    return movieTitle,topMovieUrl,movieUrlList

def saveMovie(title,topMovieUrl,movieUrlList,folderPathDate):

    folderPath = "/Users/yukimori/Movies/himawari/" + folderPathDate
    folderTitle = "/Users/yukimori/Movies/himawari/" + folderPathDate + "/" + title
    infoJsonPath = folderTitle + "/info.json"
    moviePath = folderTitle + "/" + title + ".mp4"

    print("folderPath : " + folderPath,)
    print("folderTitle : " + folderTitle,)
    print("infoJsonPath : " + infoJsonPath,)

    # 日付フォルダの判別
    if not os.path.exists(folderPath):
        os.mkdir(folderPath)
        pass

    # タイトルフォルダの判別
    if not os.path.exists(folderTitle):
        os.mkdir(folderTitle)
        pass

    if not os.path.exists(folderTitle):
        os.mkdir(folderTitle)
        pass

    if os.path.exists(moviePath):
        if os.path.getsize(moviePath) > 40000000:
            print("ファイルは存在しています",)
            return

    # Json作成
    file = open(infoJsonPath, 'a')
    file.write("{")
    file.write("\"title\":" + "\"" + title + "\"" + ",")
    file.write("\"topMovieUrl\":" + "\"" + topMovieUrl + "\"" + ",")
    file.write("\"subUrl\":[")

    for urlDate in movieUrlList:
        file.write("{")
        file.write("\"url\":" + "\"" + urlDate + "\"")
        file.write("}")

        if not urlDate == movieUrlList[len(movieUrlList)-1]:
            file.write(",")

    file.write("]")
    file.write("}")
    file.close()

    MAX_FILE_SIZE = 0
    MAX_FILE_SERVER = ""
    FILE_NUMBER = 0
    NOT_DOWNLOAD = True

    SERVER_BLACK_LIST_SEREVER = "YouTubeFrontEnd"
    SERVER_BLACK_LIST_CONTENT_TYPE = "text/html"


    if len(movieUrlList) > 0:

        # リストを反転にする
        movieUrlList.reverse()

        count = 0
        for urlDate in movieUrlList:
            print("MAX_FILE_SIZE_URL : ", urlDate,)
            try:
                response = urllib.request.urlopen(url=topMovieUrl,data=None,timeout=socket._GLOBAL_DEFAULT_TIMEOUT)

                NOT_DOWNLOAD = False
                MAX_FILE_SIZE_URL = urlDate
                FILE_NUMBER = count

                if not response.info()["Server"] == None:
                    print("Not Server Name",)
                    MAX_FILE_SERVER = response.info()["Server"]
                    break

                count += 1

            except ValueError as e:
                print(u"Error ", e)
    else:
        try:
            print("url : ",topMovieUrl)
            response = urllib.request.urlopen(url=topMovieUrl,data=None,timeout=socket._GLOBAL_DEFAULT_TIMEOUT)

            NOT_DOWNLOAD = False
            MAX_FILE_SIZE_URL = topMovieUrl
            FILE_NUMBER = -1

            if not response.info()["Server"] == SERVER_BLACK_LIST_SEREVER:
                MAX_FILE_SERVER = response.info()["Server"]

        except urllib.error.HTTPError as e:
            print("単体：",e,)
        except IOError:
            print("IOError",)
        except ValueError:
            print("ValueErrorこれ？",)

    if not NOT_DOWNLOAD:
        print("URL : ", MAX_FILE_SIZE_URL)
        try:
            if MAX_FILE_SERVER == "YouTubeFrontEnd":
                # コマンドでダウンロード
                print("Youtubeは除外")
                pass
            else:
                urllib.request.urlretrieve(MAX_FILE_SIZE_URL, moviePath)
        except urllib.error.HTTPError as e:
            print("IOError2",)
        except IOError:
            print("IOError",)
        except ValueError:
            print("ValueErrorここ？",)
    pass


if __name__ == '__main__':

    print("Hi! Himawari Download System",)
    print("Select Himawari page",)
    print("0 : TOP PAGE",)
    print("1 : New Upload",)
    print("2 : Ranking",)

    HIMAWARI_DOMAIN = "http://himado.in/"
    HIMAWARI_PARAM_NEW_PAGE = "?sort=movie_id&page="
    idList = []

    inputVal = input()

    if inputVal == "0":
        idList = moviePageId(HIMAWARI_DOMAIN)
    elif inputVal == "1":
        print("load page size",)
        pageSize = input()

        for pageCount in range(0,int(pageSize)):
            idList.extend(moviePageId(HIMAWARI_DOMAIN + HIMAWARI_PARAM_NEW_PAGE + str(pageSize)))
    elif inputVal == "2":
        print("あとで",)
        exit
    else:
        exit

    todaydetail = datetime.datetime.today()
    folderPathDate = todaydetail.strftime("%Y%m%d")

    print(idList)

    if len(idList) > 0:
        for movieId in idList:
           title,topMovieUrl,movieUrlList = movieIdList("http://himado.in/" + movieId)

           saveMovie(title,topMovieUrl,movieUrlList,folderPathDate)

        #    print("################")
        #    print(title)
        #    print(topMovieUrl)
        #    print(movieUrlList)
        #    print("################")
    pass