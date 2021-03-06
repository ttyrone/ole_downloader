import json
from re import T
import  os
from urllib.parse import urlparse

def main(isMovie, s, url, download_path, ep_name, ep_filename, ep_num_origin):
  json_path= download_path + "\\" + ep_name +' '+ ep_filename + " import.json"

  parsed_uri=urlparse(url)
  domain = '{uri.netloc}'.format(uri=parsed_uri)
  path = '{uri.path}'.format(uri=parsed_uri)
  host_split = domain.split('.')
  path_split = path.split('/')
  #filePath = str(filePath, "utf-8")
  if not os.path.isfile(json_path):
    json_info = {}
    data = json.loads(json.dumps(json_info))
    json_main_info = {
    '_postman_id':'',
    'name': ep_name + ' ' + ep_filename,
    'schema':'https://schema.getpostman.com/json/collection/v2.1.0/collection.json',
    }
    data['info'] = json_main_info
    data['item'] = [{
      'name': ep_name + ' ' + ep_filename +'-'+ s,
      'protocolProfileBehavior': {
        'disabledSystemHeaders': {
          'connection': True,
          'user-agent': True
        }
      },
      'request': {
        'method': 'GET',
        'header': [
          {
            'key': 'method',
            'value': 'GET',
            'type': 'text'
          },
          {
            'key': 'scheme',
            'value': 'https',
            'type': 'text'
          },
          {
            'key': 'accept-language',
            'value': 'zh-CN,zh;q=0.9,en;q=0.8',
            'type': 'text'
          },
          {
            'key': 'origin',
            'value': domain,
            'type': 'text'
          },
          {
            'key': 'referer',
            'value': domain,
            'type': 'text'
          },
          {
            'key': 'user-agent',
            'value': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'type': 'text'
          }
        ],
        'url': {
          'raw': url,
          'protocol': 'https',
          'host': [
            host_split[0],
            host_split[1],
            host_split[2]
          ],
          'path': [
            path_split[1],
            path_split[2],
            path_split[3],
            path_split[4],
            path_split[5],
            path_split[6]
          ]
        }
      },
      'response': []
    }]
    postmanjson = json.dumps(data, indent = 4, ensure_ascii=False)
    with open(json_path, 'w', encoding='utf-8') as file:
      #file.write(json.dumps(postmanjson, indent = 4))
      file.write(postmanjson)
      file.close()
    #print('???????????????????????????????????????postman?????????json??????????????????postman?????????????????????json???????????????'+ download_path +'???????????????import.json????????????????????????postman???collection????????????????????????002.ts??????????????????????????????ts?????????'+ download_path +'?????????????????????????????????????????????????????????????????????copy /b '+ file_prefix + '*.ts xxx.mp4???')
  else:
    #new = json.dumps({**json.loads(json_path), **{"new_key": "new_value"}})
    file = open(json_path,encoding='utf-8', errors='ignore')
    file_lines = file.read()
    file.close()
    file_json = json.loads(file_lines)
    new_item = {
          'name': ep_name+ ' ' + ep_filename +'-'+s,
          'protocolProfileBehavior': {
            'disabledSystemHeaders': {
              'connection': True,
              'user-agent': True
            }
          },
          'request': {
            'method': 'GET',
            'header': [
              {
                'key': 'method',
                'value': 'GET',
                'type': 'text'
              },
              {
                'key': 'scheme',
                'value': 'https',
                'type': 'text'
              },
              {
                'key': 'accept-language',
                'value': 'zh-CN,zh;q=0.9,en;q=0.8',
                'type': 'text'
              },
              {
                'key': 'origin',
                'value': domain,
                'type': 'text'
              },
              {
                'key': 'referer',
                'value': domain,
                'type': 'text'
              },
              {
                'key': 'user-agent',
                'value': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
                'type': 'text'
              }
            ],
            'url': {
              'raw': url,
              'protocol': 'https',
              'host': [
                host_split[0],
                host_split[1],
                host_split[2]
              ],
              'path': [
                path_split[1],
                path_split[2],
                path_split[3],
                path_split[4],
                path_split[5],
                path_split[6]
              ]
            }
          },
          'response': []
        }
    file_json['item'].append(new_item)
    postmanjson = json.dumps(file_json, indent = 4, ensure_ascii=False)
    with open(json_path, 'w', encoding='utf-8') as file:
      #file.write(json.dumps(postmanjson, indent = 4))
      file.write(postmanjson)
      file.close()
 