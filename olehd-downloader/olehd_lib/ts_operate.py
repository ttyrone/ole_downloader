import subprocess
from re import T
import  os
from urllib.parse import urlparse


from calmjs.parse.asttypes import Catch

def combinets(isMovie, ep_name, ep_filename, download_path, file_prefix):
  try:
    print('%s 下载完成，即将开始合并视频文件。' %(ep_name + ' ' + ep_filename ))
    #hebing_path = download_path+ '\\' + file_prefix + '.mp4'
    all_ts = sorted(os.listdir(download_path))
    final_ts = []
    para1,para2 = '\\','.mp4'
    hebing_path = f'{download_path}{para1}{ep_name} {ep_filename}{para2}'
    for file in all_ts:
      if file.startswith(ep_name+ ' ' + ep_filename) and file.endswith('.m4s'):
        final_ts.append(file)
    if not os.path.isfile(hebing_path):
      with open(hebing_path, 'wb+') as f:
          for ii in range(len(final_ts)):
              ts_video_path = os.path.join(download_path, final_ts[ii])
              f.write(open(ts_video_path, 'rb').read())
      print("%s %s 合并完成！！" %(ep_name, ep_name + ' ' + ep_filename))
    return True
  except Exception as e:
    return False
 

def fix(isMovie, ffmpeg_exe_path, ep_name, ep_filename, download_path, file_prefix):
  print('%s 合并完成，即将开始修复视频文件。' %(ep_name+' '+ ep_filename))
  new_filename = ep_name+' '+ ep_filename+'_fix.mp4'
  new_path = '"' + download_path+'\\'+new_filename+ '"' 
  if os.path.isfile(new_path):
    return True
  else:
    old_filename = ep_name+' '+ ep_filename + '.mp4' 
    old_path = '"' + download_path+'\\'+old_filename + '"' 
    
    #ffmpeg -i 2.mp4 -vcodec copy -strict -2 video_out.mp4
    fix_cmd = f'{ffmpeg_exe_path} {"-i"} {old_path} {"-c copy"} {new_path}'
    try:
      result=subprocess.Popen(fix_cmd,shell=False)
      return_code=result.wait()
      if return_code==0:
        return True
      else:
        return False
    except Exception as e:
      return False
   

def deletets(isMovie, ep_name, ep_filename, download_path,file_prefix):

  try:
    if os.path.exists(download_path):
      os.chdir(download_path)
      file_list = os.listdir()
      for file in file_list:
        if file.startswith(ep_name + ' ' + ep_filename) and file.endswith('.m4s'):
          os.remove(download_path+'\\'+file)
      os.remove(download_path+'\\'+ep_name + ' ' + ep_filename+'.mp4')
      print("%s %s 临时文件删除完毕！" %(ep_name , ep_name + ' ' + ep_filename ))
    return True
  except Exception as e:
    return False
  