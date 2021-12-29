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


import os, sys, traceback, time
import requests, re
import uuid
from urllib.parse import urljoin, urlparse
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
from requests.models import Response
from olehd_lib.postman_json import main as create_PostManJson

from .ffmpeg_lib import reset_ts_start_time 


def decrypt(data, key, iv, guest_padding_size):
    """Decrypt using AES CBC"""
    decryptor = AES.new(key, AES.MODE_CBC, IV=iv)
    # if ValueError AND has correct padding, https://github.com/Legrandin/pycryptodome/issues/10#issuecomment-354960150
    if guest_padding_size == 0: # can use as flag bcoz pad with 0 will throws modulo by zero err
        return decryptor.decrypt(data)
    else:
        return decryptor.decrypt(pad(data, guest_padding_size)) # You want pad to fill AND before decrypt, not unpad AND after decrypt. hexdump to view its last line not 16-bytes and need fill
    

def get_req(url, referer, proxies={}):
    """Get binary data from URL"""
    #print('url= '+ url)
    #data = ''
    #or chunk in requests.get(url, headers={'User-agent': 'Mozilla/5.0'}, stream=True):
    #    data += chunk
    parsed_uri=urlparse(url)
    domain = '{uri.netloc}'.format(uri=parsed_uri)
    headers = {
        'Cache-Control': 'no-cache',
        'Host': domain,
        'method': 'GET',
        'scheme': 'https',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'origin': domain,
        'referer': domain,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }    
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
            arg_proxy ='http://127.0.0.1:1080'
            if proxies== { 'http': arg_proxy, 'https': arg_proxy }:
                #response =  s.get(url, headers={'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.0.0 Safari/537.36', 'Referer': referer}, stream=True, timeout=init_t, proxies=proxies_local)
                response =  s.get(url, headers=headers, stream=True)
            else:
                response =  s.get(url, headers=headers, stream=True, proxies=proxies)
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
                    arg_proxy ='http://127.0.0.1:1080'
                    if proxies== { 'http': arg_proxy, 'https': arg_proxy }:
                        response =  s.get(url, headers=headers, stream=True)
                    else:
                        response =  s.get(url, headers=headers, stream=True, proxies=proxies)
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


def parse_url(m3u8_host, m3u8_base, url):
    if '://' in url:
        return url
    else:
        if url.startswith('/'):
            return ''.join([ m3u8_host, url[1:] ])
        else:
            return ''.join([ m3u8_base, url ])


def main(isMovie, m3u8_data, ts_path, ep_name, ep_filename, arg_from_ep, arg_to_ep,  m3u8_url, http_headers, proxies={}, skip_ad=True):
    #if isMovie:#电影
    m3u8_host = '{uri.scheme}://{uri.netloc}/'.format(uri= urlparse(m3u8_url) )
    m3u8_base = urljoin(m3u8_url, '.')

    m3u8_resolution_d = {}
    m3u8_lines = m3u8_data.split('\n')
    m3u8_lines_last_line = len(m3u8_lines) - 1
    for i, line in enumerate(m3u8_lines):
        line = line.strip()
        ni = i + 1
        if line.startswith('#') and (',RESOLUTION=' in line) and (ni <= m3u8_lines_last_line) and not m3u8_lines[ni].strip().startswith('#'):
            line_r = line.split(',RESOLUTION=')
            if len(line_r) > 1:
                x_r = line_r[1].split('x')
                if len(x_r) > 1:
                    m3u8_resolution_d[x_r[1]] = m3u8_lines[ni].strip()

    if m3u8_resolution_d:
        real_m3u8_url = ''
        real_m3u8_data = ''
        for i in sorted(list(m3u8_resolution_d.keys()), reverse=True):
            try:
                real_m3u8_url = parse_url(m3u8_host, m3u8_base, m3u8_resolution_d[i])
                print(('real m3u8 url: ' + repr(real_m3u8_url)))

                m3u8_host = '{uri.scheme}://{uri.netloc}/'.format(uri= urlparse( real_m3u8_url ) )
                m3u8_base = urljoin( real_m3u8_url, '.')

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
                        real_m3u8_data = s.get(real_m3u8_url, allow_redirects=True, headers=http_headers, timeout=init_t, proxies=proxies).text
                        #success_from_read = False
                        break
                    except requests.exceptions.ConnectTimeout:
                        init_a+=1
                    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                        success_from_read = True
                        break
                if success_from_read: # since we use Session(), so can reuse the "connected" session!
                    try:
                        real_m3u8_data = s.get(real_m3u8_url, allow_redirects=True, headers=http_headers, timeout=30, proxies=proxies).text
                    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                        print((traceback.format_exc()))

                '''if arg_debug:
                    with open(debug_path, 'a') as f:
                        f.write(real_m3u8_data)'''

            except Exception:
                print((traceback.format_exc()))
            else:
                break;
    else: # No resolution
        real_m3u8_data = m3u8_data

    sub_data = real_m3u8_data

    chunks = re.findall('#EXT-X-KEY:METHOD=AES-128,URI="(.*)",IV=(.*)\s.*\s(.*)', sub_data)

    print(('[1] chunks: ' + repr(chunks)))
    referer = m3u8_host# + 'static/player/videojs.html'

    if not chunks:
        chunks = re.findall('#EXT-X-KEY:METHOD=AES-128,URI="(.*)"', sub_data)
        print(('[2] chunks: ' + repr(chunks)))
        if chunks:
            key_url = parse_url(m3u8_host, m3u8_base, chunks[0])
            key = get_req(key_url, referer, proxies=proxies)
            iv = key
        else:
            print('No need decrypt.')
            key_url = None
            key = None
            iv = None
        chunks = []
        for d in sub_data.split('\n'):
            d = d.strip()
            if d.startswith('#EXT-X-MAP'):
                chunks.append(d.split('=')[1].replace('"',''))
            if not d.startswith('#') and d.endswith('.m4s'):
                chunks.append(d)
    else:
        chunks = chunks[0]
        key_url = parse_url(m3u8_host, m3u8_base, chunks[0])
        key = get_req(key_url, referer, proxies=proxies)
        iv = chunks[1][2:]
        for d in sub_data.split('\n'):
            d = d.strip()
            if d.startswith('#EXT-X-MAP'):
                chunks.append(d.split('=')[1].replace('"',''))
            if not d.startswith('#') and d.endswith('.m4s'):
                chunks.append(d)

    print(('key_url: ' + repr(key_url)))
    print(('key: ' + repr(key)))
    print(('iv: ' + repr(iv)))
    total_chunks = len(chunks)
    for ts_urls in enumerate(chunks):

        ts_url = f'{m3u8_base}{ts_urls[1].strip()}'
        if '://' not in ts_url:
            parsed = '+'
        else:
            parsed = ''
        s = str(ts_urls[0]+1).zfill(3)
        print('{}[{}/{}] 处理中{} {}'.format(ep_name + ' ' + ep_filename, (s), total_chunks, parsed, ts_url ), flush=True)
        final_ts_path = ts_path + "\\" + ep_name + ' ' + ep_filename + '-' + s + ".m4s"

        if os.path.isfile(final_ts_path):
            print('[{}/{}] {}已下载'.format( (s), total_chunks,  ep_name +' '+ ep_filename + '-' + s + ".m4s" ), flush=True)
            continue

        enc_ts = get_req(ts_url, referer, proxies=proxies)

        if enc_ts is None:
            print('[-] %s序号：%s下载错误，链接：%s，即将生成PostMan导入json！' %(ep_name, s, ts_url))
            if isMovie:
                create_PostManJson(isMovie, s, ts_url, ts_path, ep_name, ep_filename,  '1-'+str(total_chunks))
            else:
                create_PostManJson(isMovie, s, ts_url, ts_path, ep_name, ep_filename, str(arg_from_ep)+'-'+str(arg_to_ep))
            continue

        file_mode = 'wb'
        #测试postjson create_PostManJson(isMovie, s, ts_url, ts_path, ep_name, ep_filename,  '1-'+str(total_chunks))
        
        try:
            with open(final_ts_path, file_mode) as f:
                #with open(ts_path, 'wb') as f:
                if (key is None) and (iv is None):
                    f.write(enc_ts)
                else:
                    try:
                        dec_ts = decrypt(enc_ts, key, iv, 0)
                        f.write(dec_ts)
                        #raise ValueError # TESTING PURPOSE
                    except ValueError:
                        # BLOCK_SIZE 16 also related to crypto_py_aes.py
                        print('[i] 此段不满足 16 倍数解密。') # hang and 声音位移
                        success_pad = False
                        ts_chunk_fname = str(uuid.uuid4()) + '.m4s'
                        ts_chunk_fname_tmp = os.path.basename( '_'.join([ ts_chunk_fname, str(time.time()) + '.temp' ]) )
                        for i in range(1, 18):
                            try:
                                dec_ts = decrypt(enc_ts, key, iv, i)
                                with open(ts_chunk_fname_tmp, 'wb') as ts_cf:
                                    ts_cf.write(dec_ts)
                                    print('[+] 填充 ' + str(i) +  ' 字节成功。')
                                ts_chunk_reseted_fname, success = reset_ts_start_time(ts_chunk_fname_tmp, ts_chunk_fname)
                                with open(ts_chunk_reseted_fname, 'rb') as ts_crf:
                                    f.write(ts_crf.read())
                                if not success:
                                    raise Exception
                                try:
                                    os.remove(ts_chunk_reseted_fname)
                                except OSError:
                                    print('[+] 删除临时文件失败: ' + repr(ts_chunk_reseted_fname) )
                                success_pad = True
                                break
                            except ValueError:
                                pass
                        if not success_pad:
                            print('[-] 放弃此段。')
        except PermissionError:
            print((traceback.format_exc()))
            print('[!] 请不要一边下载加密的 .ts 视频，一边观看该视频。 请重新下载该集。')

    return True


