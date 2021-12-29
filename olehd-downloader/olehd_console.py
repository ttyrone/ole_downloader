# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) 2019 ttyronehank@gmail.com
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

__author__ = 'Tyrone Hank'
__copyright__ = 'Copyright 2021'
__credits__ = ['Lim Kok Hole Links']
__license__ = 'MIT'
__version__ = 1.0
__maintainer__ = 'Tyrone Hank'
__email__ = 'ttyronehank@gmail.com'
__status__ = 'Production'

'''
from slimit import ast
from slimit.parser import Parser
from slimit.visitors import nodevisitor
'''

import sys, os, traceback
import requests
from urllib.parse import urlparse
from olehd_lib.ts_operate import combinets as combinets
from olehd_lib.ts_operate import deletets as deletets
import json
import re 
import subprocess
ffmpeg_path = 'ffmpeg'
try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    base_path = sys._MEIPASS
    #print('done base_path: ' + repr(base_path))
except Exception:
    #print('use abs path')
    base_path = os.path.abspath(".")
ffmpeg_full_path = '"' + os.path.join(base_path, os.path.join('olehd_lib', ffmpeg_path) ) + '"'

PY3 = sys.version_info[0] >= 3
if not PY3:
    print('\n[!]中止! 请使用 python 3。')
    sys.exit(1)

import tqdm
from bs4 import BeautifulSoup

#try: from urllib.request import urlopen #python3
#except ImportError: from urllib2 import urlopen #python2

# RIP UA, https://groups.google.com/a/chromium.org/forum/m/#!msg/blink-dev/-2JIRNMWJ7s/yHe4tQNLCgAJ
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
#from termcolor import cprint
#import colorama
#from colorama import Style, Fore, Back
#colorama.init() # Windows need this
#BOLD_ONLY = ['bold']

# https://github.com/limkokhole/calmjs.parse
import calmjs # Used in `except calmjs...:`
from calmjs.parse import es5
# ~/.local/lib/python3.6/site-packages/calmjs/parse/walkers.py
from calmjs.parse.asttypes import Assign as CalmAssign
from calmjs.parse.asttypes import Identifier as CalmIdentifier
from calmjs.parse.asttypes import String as CalmString
from calmjs.parse.asttypes import VarDecl as CalmVar
from calmjs.parse.walkers import Walker as CalmWalker
from calmjs.parse.parsers.es5 import Parser as CalmParser

from olehd_lib.m3u8_decryptor import main as m3u8_decryptopr_main
from olehd_lib.m3u8_decryptor_export import main as m3u8_decryptopr_export_main
from olehd_lib.ts_operate import fix as mp4_fix
from olehd_lib.ffmpeg_lib import remux_ts_to_mp4 
from olehd_lib.crypto_py_aes import main as crypto_py_aes_main

import logging, http.client
import datetime
import time
import argparse
from argparse import RawTextHelpFormatter
arg_parser = argparse.ArgumentParser(
    description='欧乐影院下载器v1.0', formatter_class=RawTextHelpFormatter)

def quit(msgs, exit=True):
    if not isinstance(msgs, list):
        msgs = [msgs]
    # 搞笑 bug: 之前无意中移除 exit=True，导致我系统有默认 exit 没问题，别人却有问题。
    if exit: #避免只看见最后一行“中止。”而不懂必须滚上查看真正错误原因。
        msgs[-1]+= '中止。'
    for msg in msgs:
        if msg == '\n': # Empty line without bg color
            print('\n')
        else:
            #cprint(msg, 'white', 'on_red', attrs=BOLD_ONLY)
            print(msg)
    # Should not do this way, use return instead to support gui callback
    #if exit:
    #    #cprint('Abort.', 'white', 'on_red', attrs=BOLD_ONLY)
    #    sys.exit()


def get_req(url, proxies={}):
    """Get binary data from URL"""
    print('url= '+ url)
    #data = ''
    #or chunk in requests.get(url, headers={'User-agent': 'Mozilla/5.0'}, stream=True):
    #    data += chunk
    init_t = 0.3
    init_a = 0
    total_t = 0
    s = requests.Session()
    success_from_read = False
    while 1:
        try:
            if total_t >= 120:
                return None
            if ( (init_a % 6) == 0) and (init_t < 30):
                init_t+=0.3
            total_t+=init_t
            response =  s.get(url,  proxies=proxies)
            if response.status_code == 200:
                return response.content
            else:
                return None
            #success_from_read = False
        except requests.exceptions.ConnectTimeout:
            init_a+=1
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            success_from_read = True
            for t in (10, 20, 30, 60):
                try:
                    #return s.get(url, headers={'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.0.0 Safari/537.36', 'Referer': referer}, stream=True, timeout=t, proxies=proxies).content
                    response =  s.get(url, proxies=proxies)
                    if response.status_code == 200:
                        return response.content
                    else:
                        return None
                except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                    pass
            return None

    #return requests.get(url, headers={'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.0.0 Safari/537.36'}, stream=False, proxies=proxies).content #tested 1 proxy not able use stream=False
    #if r.status_code == 200:
    #    #r.raw.decode_content = True
    #    #return r.raw
    #    return r
    #return None


#arg_parser.add_argument('-t', '--video-type', dest='video_type', action='store_true', help='Specify movie instead of cinemae')
arg_parser.add_argument('-d', '--dir', help='用来储存连续剧/综艺的目录名 (非路径)。')
arg_parser.add_argument('-f', '--file', help='用来储存电影的文件名。请别加后缀 .mp4。')
#from/to options should grey out if -f selected:
arg_parser.add_argument('-da', '--downloadall', help='下载全集')
arg_parser.add_argument('-from-ep', '--from-ep', dest='from_ep', default=1, type=int, help='从第几集开始下载。')
arg_parser.add_argument('-to-ep', '--to-ep', dest='to_ep',
                        type=int, help='到第几集停止下载。')
arg_parser.add_argument('-p', '--proxy', help='https 代理(如有)')

arg_parser.add_argument('-g', '--debug', action='store_true', help='储存 olehd_epN.log 日志附件， 然后你可以在 https://github.com/limkokhole/olehd-downloader/issues 报告无法下载的问题。')
arg_parser.add_argument('url', nargs='?', help='下载链接。')
args, remaining = arg_parser.parse_known_args()

def main(isMovie, arg_file, arg_url, arg_from_ep, arg_to_ep, custom_stdout, arg_debug, arg_proxy={}, downloadAll=False):

    try:
        sys.stdout = custom_stdout
           
        if not arg_url:
            print('main arg_url: {}'.format(repr(arg_url)))
            return quit('[!] [e1] 请用该格式  https://www.olehd.com/index.php/vod/detail/id/32220.html 的链接。')
        
        parsed_uri=urlparse(arg_url)
        domain = '{uri.netloc}'.format(uri=parsed_uri)
        domain_full = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)


        preresponse = get_req(arg_url, arg_proxy)
        
        if preresponse is not None:
            soup = BeautifulSoup(preresponse,'html.parser')
            ep_name = soup.title.text.split(' - 欧乐影院')[0].split('_')[0]
            try:
                cinema_id = int(arg_url.split('.html')[0].split('/id/')[1])
            except ValueError as ve:
                print(ve)
                #return quit('[!] [e3] Please specify cinema url in https://www.fanstui.com/voddetail-300.html. Abort.')
                return quit('[!] [e3] 请用该格式  https://www.olehd.com/index.php/vod/detail/id/32220.html 的链接。')



            if not isMovie:
                playlist = []
                for ultag in soup.find_all('ul', {'class': 'content_playlist clearfix'}):
                    for litag in ultag.find_all('li'):
                        playlist.append(litag.find('a')['href'])
                if downloadAll:
                    arg_from_ep = 1
                    arg_to_ep = len(playlist)

            arg_file = os.path.abspath(arg_file)

            if not isMovie and not downloadAll:
                for ii in range(arg_from_ep, arg_to_ep+1):
                    try:
                        ep_url= f'{domain_full}{playlist[ii-1]}'
                    except Exception:
                        print('第'+str(arg_to_ep)+'集不存在！')
                        continue
                    #print('还要处理ep_filename，下载以后的合并文件名是错的，自动修复和删除临时文件都不成功')
                    ep_filename =''
                    try:
                        downloadm4s(isMovie, arg_file, ep_url, ep_name, ep_filename, arg_from_ep, arg_to_ep, custom_stdout, arg_debug, arg_proxy, downloadAll)
                        continue
                    except Exception:  
                        print('%s 下载失败！'.format(ep_name))
                        continue
                        #在playlist中循环出正确的html给downloadm4s即可
                os.startfile(f'{arg_file}{ep_name}')
            else:
                for ultag in soup.find_all('ul', {'class': 'content_playlist clearfix'}):
                    for litag in ultag.find_all('li'):
                        #电影播放页面的url
                        ep_filename = ''
                        url_path = litag.find('a')['href']
                        ep_url= f'{domain_full}{url_path}'
                        if litag.find('a').string != '在线播放' and litag.find('a').string != '高清播放':
                            ep_filename =litag.find('a').string
                        #循环下载init.mp4和m4s
                        #D:\长津湖\长津湖 上集_fix.mp4
                                            
                        linksy = '\\'
                        tmp = f'{arg_file}{ep_name}{linksy}{ep_name} {ep_filename}{"_fix.mp4"}'
                        if not os.path.isfile(tmp):
                            downloadm4s(isMovie, arg_file, ep_url, ep_name, ep_filename, arg_from_ep, arg_to_ep, custom_stdout, arg_debug, arg_proxy, downloadAll)
                        else:
                            print(f'{ ep_name} {ep_filename}{"已下载！"}')
                            continue
                os.startfile(f'{arg_file}{ep_name}')
        else:
            return quit('[i] 请求失败，请重试！ ')
    except Exception:
        try:
            print(traceback.format_exc())
        except UnicodeEncodeError:
            print('[!] 出现错误。')
    
    
    try:
        print('[😄] 全部下载工作完毕。您已可以关闭窗口, 或下载别的视频。')
    except UnicodeEncodeError:
        print('[*] 全部下载工作完毕。您已可以关闭窗口, 或下载别的视频。')

#ep_name 长津湖
#ep_filename 上集，如果只有一集的就是空
def downloadm4s(isMovie, arg_file, arg_url, ep_name, ep_filename, arg_from_ep, arg_to_ep, custom_stdout, arg_debug, arg_proxy={}, downloadAll=False):
    try:
        arg_file = f'{arg_file}{ep_name}'

        if '://' not in arg_url:
            arg_url = 'https://' + arg_url
            print('arg_url= '+ arg_url)
        dir_path_m = os.path.abspath(arg_file)
        if not os.path.isdir(dir_path_m):
            try:
                os.makedirs(dir_path_m)
            except OSError:
                return quit('[i] 无法创建目录。或许已有同名文件？ ')

        if isMovie:
            json_path= dir_path_m + "\\" + ep_name + ' ' + ep_filename + " import.json"
        else:
            json_path= dir_path_m + "\\" + ep_name + ' ' + ep_filename + str(arg_from_ep)+'-'+str(arg_to_ep)  + " import.json"

        if os.path.isfile(json_path):
            os.remove(json_path)


        # https://stackoverflow.com/questions/10606133/sending-user-agent-using-requests-library-in-python
        http_headers = {
            'User-Agent': UA,
            'method': 'GET',
            'scheme': 'https',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }

        def calm_assign(node):
            return isinstance(node, CalmAssign)

        def calm_id(node):
            return isinstance(node, CalmIdentifier)

        def calm_str(node):
            return isinstance(node, CalmString)

        def calm_var(node):
            return isinstance(node, CalmVar)

        CP = CalmParser()
        walker = CalmWalker()
        
        
        # 获取第一个m3u8文件

        print('[...] 尝试 URL: ' + arg_url)
        
        try:
            init_t = 1
            init_a = 0
            total_t = 0
            s = requests.Session()
            success_from_read = False
            while 1:
                try:
                    if total_t >= 120:
                        return None
                    if ( (init_a % 6) == 0) and (init_t < 30):
                        init_t+=1
                    total_t+=init_t
                    r = s.get(arg_url, allow_redirects=True, headers=http_headers, timeout=init_t, proxies=arg_proxy)
                    #success_from_read = False
                    break
                except requests.exceptions.ConnectTimeout:
                    init_a+=1
                except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                    success_from_read = True
                    break
            if success_from_read: # since we use Session(), so can reuse the "connected" session!
                try:
                    r = s.get(arg_url, allow_redirects=True, headers=http_headers, timeout=30, proxies=arg_proxy)
                except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                    print('[!A] 失败。')

        except requests.exceptions.ConnectionError:
            print('\n[!] 你的网络出现问题，也可能是网站的服务器问题。\n', flush=True)

        soup = BeautifulSoup(r.text, 'html.parser')
        if ep_filename =='':
            ep_filename = soup.title.text.split(' - 欧乐影院')[0].split('_')[1]
            if os.path.isfile(dir_path_m+'\\' + ep_name + ' ' + ep_filename + '_fix.mp4'):
                print (ep_name + ' ' + ep_filename+'已下载！！')
                return

        try:
            pattern = re.compile(r"var player_aaaa=", re.MULTILINE | re.DOTALL) 
            script = soup.find("script", text=pattern) 
            m3u8_url = json.loads(script.text.replace('var player_aaaa=',''))["url"]#第一个m3u8文件
        except IndexError:
            print('获取m3u8文件失败: ')
            
        ct_b64 = '' #reset
        passwd = '' #reset

        printed_err = False
        got_ep_url = False

        

        if m3u8_url and dir_path_m:
            got_ep_url = True
            print('m3u8头文件 url: ' + m3u8_url)
            print('下载的 mp4 路径: ' + dir_path_m)

            init_t = 1
            init_a = 0
            total_t = 0
            s = requests.Session()
            success_from_read = False
            while 1:
                try:
                    if total_t >= 120:
                        return None
                    if ( (init_a % 6) == 0) and (init_t < 30):
                        init_t+=1
                    total_t+=init_t
                    r = s.get(m3u8_url, allow_redirects=True, headers=http_headers, timeout=init_t, proxies=arg_proxy)
                    #success_from_read = False
                    break
                except requests.exceptions.ConnectTimeout:
                    init_a+=1
                except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                    success_from_read = True
                    break
            if success_from_read: # since we use Session(), so can reuse the "connected" session!
                try:
                    r = s.get(m3u8_url, allow_redirects=True, headers=http_headers, timeout=30, proxies=arg_proxy)
                except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                    print('[!C] 失败。')
            
            #if isMovie:#电影
            if not os.path.isfile(dir_path_m+'\\' + ep_name + ' ' + ep_filename + '_fix.mp4'):
                #将真实init.mp4和m4s文件的地址传过去下载
                if m3u8_decryptopr_main(isMovie, r.text, dir_path_m,  ep_name, ep_filename, arg_from_ep, arg_to_ep,  m3u8_url, http_headers, proxies=arg_proxy):
                    if not os.path.isfile(dir_path_m+ "\\" + ep_name + ' ' + ep_filename +" import.json"):
                        #remux_ts_to_mp4(ep_ts_path, ep_mp4_path)
                        if combinets(isMovie, ep_name, ep_filename, dir_path_m, ep_name):#print('合并成MP4')区分电影和电视剧
                            if mp4_fix(isMovie, ffmpeg_full_path,ep_name, ep_filename, dir_path_m, ep_name) :
                                print('[!] {}修复MP4完毕，'.format(ep_name ))
                            else:
                                print('[!] {}修复MP4失败，不影响观看，但无法拖动，介意请自行用命令：ffmpeg -i 下载待修复.mp4 -c copy 下载待修复_fix.mp4。'.format(ep_name ))
                            if not deletets(isMovie, ep_name, ep_filename, dir_path_m, ep_name):#print('如果合并成功就删除临时文件')
                                print('[!] {}删除临时文件失败，请手动删除，命令：del {}*.ts 或在资源管理器中选择删除。'.format(dir_path_m, ep_name))
                            else:
                                print('[!] {}删除临时文件完毕。'.format(dir_path_m, ep_name))
                        else:
                            print('[!] {}合并MP4失败，请手动合并，命令：copy /b {}*.m4s xxx.mp4。'.format(dir_path_m, ep_name))
                    else:
                        file = open(json_path,encoding='utf-8', errors='ignore')
                        file_lines = file.read()
                        file.close()
                        file_json = json.loads(file_lines)
                        n = len(file_json['item'])
                        print('{} {} 共有{}个下载错误的ts文件需要重新下载，请将{}导入到postman，逐个下载文件，并命名为请求名.ts（如：请求名为第xx集-002，下载文件就命名为第xx集-002.ts），然后将所有下载文件拷回到{}并替换原有文件，然后按名称顺序排序，进行合并即可（合并命令：copy /b {}*.m4s {}.mp4），合并后请自行删除相关的ts文件'.format(ep_name, ep_filename, str(n), json_path, json_path, ep_filename, ep_filename))
                    #打开下载目录
                    
                else: 
                    print('[!] {} ts文件下载失败，请再试一次。'.format(ep_name + ' ' + ep_filename))
            else:
                print('%s 已下载' %(ep_name + ' ' + ep_filename ))
            

            #source_url = "https://tv2.xboku.com/20191126/wNiFeUIj/index.m3u8"
            #https://stackoverflow.com/questions/52736897/custom-user-agent-in-youtube-dl-python-script
            #youtube_dl.utils.std_headers['User-Agent'] = UA
            #try: # This one shouldn't pass .mp4 ep_path
            #    youtube_dl.YoutubeDL(params={'-c': '', '-q': '', '--no-mtime': '',
            #                                 'outtmpl': ep_path + '.%(ext)s'}).download([ep_url])
            #except youtube_dl.utils.DownloadError:
            #    print(traceback.format_exc())
            #    print(
            #        'Possible reason is filename too long. Please retry with -s <maximum filename size>.')
            #    sys.exit()

        #print(walker.extract(tree, assignment))


        if not got_ep_url:
            if not printed_err:
                if arg_file:
                    print('[!] 不存在该部影片。')
                else:
                    print('[!] 不存在该部影片。')

    except Exception:
        try:
            print(traceback.format_exc())
        except UnicodeEncodeError:
            print('[!] 出现错误。')



def export(isMovie, arg_file, arg_url, arg_from_ep, arg_to_ep, custom_stdout, arg_debug, arg_proxy={}, downloadAll=False):

    try:
        sys.stdout = custom_stdout
           
        if not arg_url:
            print('main arg_url: {}'.format(repr(arg_url)))
            return quit('[!] [e1] 请用该格式  https://www.olehd.com/index.php/vod/detail/id/32220.html 的链接。')
        
        parsed_uri=urlparse(arg_url)
        domain = '{uri.netloc}'.format(uri=parsed_uri)
        domain_full = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)


        preresponse = get_req(arg_url, arg_proxy)
        
        if preresponse is not None:
            soup = BeautifulSoup(preresponse,'html.parser')
            ep_name = soup.title.text.split(' - 欧乐影院')[0].split('_')[0]
            try:
                cinema_id = int(arg_url.split('.html')[0].split('/id/')[1])
            except ValueError as ve:
                print(ve)
                #return quit('[!] [e3] Please specify cinema url in https://www.fanstui.com/voddetail-300.html. Abort.')
                return quit('[!] [e3] 请用该格式  https://www.olehd.com/index.php/vod/detail/id/32220.html 的链接。')



            if not isMovie:
                if downloadAll:
                    playlist = []
                    for ultag in soup.find_all('ul', {'class': 'content_playlist clearfix'}):
                        for litag in ultag.find_all('li'):
                            playlist.append(litag.find('a')['href'])
                    arg_from_ep = 1
                    arg_to_ep = len(playlist)

            arg_file = os.path.abspath(arg_file)

            if not isMovie:
                playlist = []
                for ultag in soup.find_all('ul', {'class': 'content_playlist clearfix'}):
                    for litag in ultag.find_all('li'):
                        playlist.append(litag.find('a')['href'])
                if downloadAll:
                    arg_from_ep = 1
                    arg_to_ep = len(playlist)

            arg_file = os.path.abspath(arg_file)

            if not isMovie and not downloadAll:
                for ii in range(arg_from_ep, arg_to_ep+1):
                    try:
                        ep_url= f'{domain_full}{playlist[ii-1]}'
                    except Exception:
                        print('第'+str(arg_to_ep)+'集不存在！')
                        continue
                    #print('还要处理ep_filename，下载以后的合并文件名是错的，自动修复和删除临时文件都不成功')
                    ep_filename =''
                    try:
                        exportm4s(isMovie, arg_file, ep_url, ep_name, ep_filename, arg_from_ep, arg_to_ep, custom_stdout, arg_debug, arg_proxy, downloadAll)
                        continue
                    except Exception:  
                        print('%s 下载失败！'.format(ep_name))
                        continue
                        #在playlist中循环出正确的html给downloadm4s即可
                os.startfile(f'{arg_file}{ep_name}')
            else:
                for ultag in soup.find_all('ul', {'class': 'content_playlist clearfix'}):
                    for litag in ultag.find_all('li'):
                        #电影播放页面的url
                        ep_filename = ''
                        url_path = litag.find('a')['href']
                        ep_url= f'{domain_full}{url_path}'
                        if litag.find('a').string != '在线播放' and litag.find('a').string != '高清播放':
                            ep_filename =litag.find('a').string
                        #循环下载init.mp4和m4s
                        #D:\长津湖\长津湖 上集_fix.mp4
                        linksy = '\\'
                        tmp = f'{arg_file}{ep_name}{linksy}{ep_name} {ep_filename}{"-download_list.txt"}'
                        if not os.path.isfile(tmp):
                            exportm4s(isMovie, arg_file, ep_url, ep_name, ep_filename, arg_from_ep, arg_to_ep, custom_stdout, arg_debug, arg_proxy, downloadAll)
                        else:
                            print(f'{ ep_name} {ep_filename}{"已下载！"}')
                            continue
            os.startfile(f'{arg_file}{ep_name}')
        else:
            return quit('[i] 请求失败，请重试！ ')
    except Exception:
        try:
            print(traceback.format_exc())
        except UnicodeEncodeError:
            print('[!] 出现错误。')
    
    
    try:
        print('[😄] 全部导出工作完毕。您已可以导入其他下载软件进行下载。')
    except UnicodeEncodeError:
        print('[*] 全部导出工作完毕。您已可以导入其他下载软件进行下载。')

            
def exportm4s(isMovie, arg_file, arg_url, ep_name, ep_filename, arg_from_ep, arg_to_ep, custom_stdout, arg_debug, arg_proxy={}, downloadAll=False):
    try:
        arg_file = f'{arg_file}{ep_name}'

        if '://' not in arg_url:
            arg_url = 'https://' + arg_url
            print('arg_url= '+ arg_url)
        dir_path_m = os.path.abspath(arg_file)
        if not os.path.isdir(dir_path_m):
            try:
                os.makedirs(dir_path_m)
            except OSError:
                return quit('[i] 无法创建目录。或许已有同名文件？ ')

        if isMovie:
            json_path= dir_path_m + "\\" + ep_name + ' ' + ep_filename + "-download_list.txt"
        else:
            json_path= dir_path_m + "\\" + ep_name + ' ' + ep_filename + str(arg_from_ep)+'-'+str(arg_to_ep)  + "-download_list.txt"

        if os.path.isfile(json_path):
            os.remove(json_path)


        # https://stackoverflow.com/questions/10606133/sending-user-agent-using-requests-library-in-python
        http_headers = {
            'User-Agent': UA,
            'method': 'GET',
            'scheme': 'https',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }

        def calm_assign(node):
            return isinstance(node, CalmAssign)

        def calm_id(node):
            return isinstance(node, CalmIdentifier)

        def calm_str(node):
            return isinstance(node, CalmString)

        def calm_var(node):
            return isinstance(node, CalmVar)

        CP = CalmParser()
        walker = CalmWalker()
        
        
        # 获取第一个m3u8文件

        print('[...] 尝试 URL: ' + arg_url)
        
        try:
            init_t = 1
            init_a = 0
            total_t = 0
            s = requests.Session()
            success_from_read = False
            while 1:
                try:
                    if total_t >= 120:
                        return None
                    if ( (init_a % 6) == 0) and (init_t < 30):
                        init_t+=1
                    total_t+=init_t
                    r = s.get(arg_url, allow_redirects=True, headers=http_headers, timeout=init_t, proxies=arg_proxy)
                    #success_from_read = False
                    break
                except requests.exceptions.ConnectTimeout:
                    init_a+=1
                except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                    success_from_read = True
                    break
            if success_from_read: # since we use Session(), so can reuse the "connected" session!
                try:
                    r = s.get(arg_url, allow_redirects=True, headers=http_headers, timeout=30, proxies=arg_proxy)
                except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                    print('[!A] 失败。')

        except requests.exceptions.ConnectionError:
            print('\n[!] 你的网络出现问题，也可能是网站的服务器问题。\n', flush=True)

        soup = BeautifulSoup(r.text, 'html.parser')

        if ep_filename =='':
            ep_filename = soup.title.text.split(' - 欧乐影院')[0].split('_')[1]
            if os.path.isfile(dir_path_m+'\\' + ep_name + ' ' + ep_filename + str(arg_from_ep)+'-'+str(arg_to_ep)  + '-download_list.txt'):
                print (ep_name + ' ' + ep_filename+'已导出下载列表！！')
                return
        try:
            pattern = re.compile(r"var player_aaaa=", re.MULTILINE | re.DOTALL) 
            script = soup.find("script", text=pattern) 
            m3u8_url = json.loads(script.text.replace('var player_aaaa=',''))["url"]#第一个m3u8文件
        except IndexError:
            print('获取m3u8文件失败: ')
            
        ct_b64 = '' #reset
        passwd = '' #reset

        printed_err = False
        got_ep_url = False

        

        if m3u8_url and dir_path_m:
            got_ep_url = True
            print('m3u8头文件 url: ' + m3u8_url)
            print('下载的 mp4 路径: ' + dir_path_m)

            init_t = 1
            init_a = 0
            total_t = 0
            s = requests.Session()
            success_from_read = False
            while 1:
                try:
                    if total_t >= 120:
                        return None
                    if ( (init_a % 6) == 0) and (init_t < 30):
                        init_t+=1
                    total_t+=init_t
                    r = s.get(m3u8_url, allow_redirects=True, headers=http_headers, timeout=init_t, proxies=arg_proxy)
                    #success_from_read = False
                    break
                except requests.exceptions.ConnectTimeout:
                    init_a+=1
                except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                    success_from_read = True
                    break
            if success_from_read: # since we use Session(), so can reuse the "connected" session!
                try:
                    r = s.get(m3u8_url, allow_redirects=True, headers=http_headers, timeout=30, proxies=arg_proxy)
                except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                    print('[!C] 失败。')
            
            if not os.path.isfile(json_path):
                #将真实init.mp4和m4s文件的地址传过去下载
                if m3u8_decryptopr_export_main(isMovie, r.text, dir_path_m, ep_name, ep_filename, m3u8_url, http_headers, proxies=arg_proxy):
                    print('%s 下载列表已导出' %(ep_name + ' ' + ep_filename ))
                else: 
                    print('[!] {} 下载列表导出失败，请再试一次。'.format(ep_name + ' ' + ep_filename))
            else:
                print('%s 下载列表已导出' %(ep_name + ' ' + ep_filename ))
            

            #source_url = "https://tv2.xboku.com/20191126/wNiFeUIj/index.m3u8"
            #https://stackoverflow.com/questions/52736897/custom-user-agent-in-youtube-dl-python-script
            #youtube_dl.utils.std_headers['User-Agent'] = UA
            #try: # This one shouldn't pass .mp4 ep_path
            #    youtube_dl.YoutubeDL(params={'-c': '', '-q': '', '--no-mtime': '',
            #                                 'outtmpl': ep_path + '.%(ext)s'}).download([ep_url])
            #except youtube_dl.utils.DownloadError:
            #    print(traceback.format_exc())
            #    print(
            #        'Possible reason is filename too long. Please retry with -s <maximum filename size>.')
            #    sys.exit()

        #print(walker.extract(tree, assignment))


        if not got_ep_url:
            if not printed_err:
                if arg_file:
                    print('[!] 不存在该部影片。')
                else:
                    print('[!] 不存在该部影片。')

    except Exception:
        try:
            print(traceback.format_exc())
        except UnicodeEncodeError:
            print('[!] 出现错误。')


def combine(isMovie, arg_file, custom_stdout):

    try:
        sys.stdout = custom_stdout
        
        file_path = os.path.abspath(arg_file)
        '''if not os.path.isfile(arg_file):
            print('[!] [e1] 所选路径不存在。')
            return quit('[!] [e1] 所选路径不存在。')'''

        
        dir_arr =[]

        for root, dirs, files in os.walk(file_path):
            #print('root_dir:', root)  # 当前目录路径
            #print('sub_dirs:', dirs)  # 当前路径下所有子目录
            #print('files:', files)  # 当前路径下所有非目录子文件
            for i in dirs:
                dir_arr.append(i)

        for dirname in dir_arr:
            all_ts = os.listdir(arg_file+'/'+dirname)

        #循环取得所有的文件夹名
        
            temp_ts = []
            init_mp4 = ''
            for j in all_ts:
                if os.path.splitext(j)[1].endswith('.m4s'):
                    temp_ts.append(j)
            for k in all_ts:
                if os.path.splitext(k)[1].endswith('.mp4'):
                    init_mp4= k
                    break

            needed_ts = []

            temp_ts.sort(key=lambda x: int(x.split('seg-')[1].split('-v1-a1.m4s')[0]))

            for i in temp_ts:
                needed_ts.append(i)

            needed_ts.insert(0,init_mp4)

            #print(time.mktime(datetime.datetime.now().timetuple()))
            hebing_path = f'{arg_file}{"/"}{dirname}{"/"}{dirname}{".mp4"}'
            try:
                if not os.path.isfile(hebing_path):
                    with open(hebing_path, 'wb+') as f:
                        for ii in range(len(needed_ts)):
                            ts_video_path = os.path.join(arg_file+'/'+dirname, needed_ts[ii])
                            f.write(open(ts_video_path, 'rb').read())
                    print("%s 合并完成，即将删除下载的m4s文件！！" %(dirname+'.mp4'))
                    try:
                        if os.path.exists(arg_file+'/'+dirname):
                            os.chdir(arg_file+'/'+dirname)
                            file_list = os.listdir()
                            for file in file_list:
                                if file.startswith('seg-') and file.endswith('.m4s'):
                                    os.remove(arg_file+'/'+dirname+'/'+file)
                            os.remove(arg_file+'/'+dirname+'/init-v1-a1.mp4')
                            print(" %s 临时文件删除完毕！" %(arg_file+'/'+dirname ))
                            continue
                    except Exception as e:
                        print("%s 临时文件删除失败，请手动删除！！" %(dirname))
                        continue
                    continue
                else:
                    continue
            except Exception as e:
                print("%s 合并失败，请手动合并！！" %(dirname+'.mp4'))
                continue
                #不需要修复也能拖动，，
                # 删除临时文件，




        
        
  
    except Exception:
        try:
            print(traceback.format_exc())
        except UnicodeEncodeError:
            print('[!] 出现错误。')

    try:
        print('[😄] 全部合并工作完毕。')
    except UnicodeEncodeError:
        print('[*] 全部合并工作完毕。')




def fixfile(arg_file):

    try:
        if not arg_file:
            print('待修复视频: {}'.format(repr(arg_file)))
            return quit('[!] [e1] 请选择要修复的视频。')
        
        if not os.path.isfile(arg_file):
            print('视频文件不存在: {}'.format(repr(arg_file)))
            return quit('[!] [e1] 请选择要修复的视频。')
        
        print('即将开始修复视频文件：%s。' %(arg_file))

        filearr = arg_file.split('/')
        count = len(filearr)-1
        filename= filearr[count]
        download_path =''
        for index in range(count):
             download_path += filearr[index]+'/'


        new_filename = filename.split('.mp4')[0]+'_fix.mp4'
        new_path = '"'+download_path+new_filename+'"'
        arg_file_final = '"'+arg_file+'"'
        if os.path.isfile(new_path):
            print('视频文件已修复: {}，无须重复修复。'.format(repr(new_path)))
        else:
            #ffmpeg -i 2.mp4 -vcodec copy -strict -2 video_out.mp4
            fix_cmd = f'{ffmpeg_full_path} {"-i"} {arg_file_final} {"-c copy"} {new_path}'
            try:
                result=subprocess.Popen(fix_cmd,shell=False)
                return_code=result.wait()
                if return_code==0:
                    print('[😄] 修复完毕。')
                    os.remove(arg_file)
                else:
                    print('[!] 出现错误。')
            except Exception as e:
                print('[!] 出现错误。')
        
        os.startfile(download_path)

    except Exception:
        try:
            print(traceback.format_exc())
        except UnicodeEncodeError:
            print('[!] 出现错误。')


    '''
    #slimit, https://stackoverflow.com/questions/44503833/python-slimit-minimizer-unwanted-warning-output
    parser = Parser()
    tree = parser.parse(script.text)
    for node in nodevisitor.visit(tree):
        if isinstance(node, ast.Assign):
            print(666)
    '''

if __name__ == "__main__":
    main(args.dir, args.file, args.from_ep, args.to_ep, args.url, sys.stdout, args.debug, args.proxy, args.proxy_local, args.downloadAll)
