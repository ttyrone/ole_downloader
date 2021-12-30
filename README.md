# ole_downloader欧乐下载器
复制粘贴链接，自定义下载第几集的欧乐视频
https://www.olehd.com/index.php/vod/detail/id/32437.html 粘贴这样的网址

---
### 使用说明:

1. 电影和“连续剧/综艺/动漫”的URL要分开粘贴
2. 电影下载根据网站的格式有可能分为上下集
3. “连续剧/综艺/动漫”支持选择下载集数，也支持下载全集（连续剧网址粘贴在电影页面时实际就是下载全集）
4. 支持导出下载列表，用其他下载软件（如迅雷）下载后再进行合并。
5. 支持将其他下载软件下载的m4s文件合并
6. 支持修复合并的视频
7. 支持代理，默认设置下，对于翻墙用户，只在解析m3u8文件之前需要用到代理，后续的下载没有走代理流量。
---
### 注意事项:

1. 下载过程是先下载多段 .m4s 文件，单个 .m4s 文件单独保存， 完成后才转换 .mp4。
2. 如果没有自动转换为mp4，表示有m4s文件下载失败，重新运行一次，会重新下载丢失的m4s，如果多次下载错误才有可能是被ban了，将下载目录里的xxxxx import.json文件，导到postman里看能不能下（点send and download）。该文件为postman的collection文件，将该文件导入postman进行下载操作，逐个下载文件，并命名为请求名.m4s（如：请求名为第xx集-002，下载文件就命名为第xx集-002.m4s），然后将所有下载文件拷回到下载目录，然后按名称顺序排序，进行合并即可（合并命令：copy /b 第xx集*.m4s 第xx集.mp4），合并后请自行删除相关的m4s文件，当然，如果不介意丢帧可以直接合并。
3. 重复下载剧集不会覆盖目录下的同名 .m4s/.mp4，这样能节约下载时间，如果想要重新下载请先删除原来的.m4s/.mp4。
4. 网络有时候慢或操作频繁导致下载失败， 就停止等一阵子才尝试。 
5. 导出下载列表，用其他下载工具下载，然后用合并mp4合并，合并后修复，每集导出一个txt，迅雷里每个txt都合并为任务组，以txt的文件名来命名任务组，迅雷有点问题，链接不一样，后缀一样的也会提示下载列表已存在相同任务，所以下完一集后要删除这个下载任务（彻底删除，但不要删除下载文件）再下第二集（假设每一集下载列表的文件夹都在D:\迅雷下载\下载列表 下,确保这个文件夹只有存放m4s文件的文件夹）
全部下载完后，合并MP4选择D:\迅雷下载\下载列表，程序会按目录循环将所有m4s文件合并，每个文件夹下的最终mp4文件都以该文件夹命名（D:\迅雷下载\下载列表\第1集下的MP4就是D:\迅雷下载\下载列表\第1集\第1集.mp4）
6. 如果合并后的视频不能拖动，可以用修复MP4进行修复
7. 只测试了一部电影和一部电视剧。

---
### 普通用户:
Windows (64-bit) 用户，只需要下载 "[欧乐下载器_win_64_exe.zip](https://www.aliyundrive.com/s/MQan7K5YU4o)",  双击 "欧乐下载器 win_64 v1.0.exe" 文件执行。 

---
### python 3 用户:

下载代码后，请自行下载ffmpeg.exe(https://www.aliyundrive.com/s/KG3JFxHjCAo)，放到.\olehd-downloader\olehd_lib目录下，修复视频功能才可以使用
只适用于windows用户。

使用 `python3 ole_gui.py` 打开图形界面，或 `python3 ole_console.py -选项` 使用命令行界面。

python3 用户必须先执行命令 `python3 -m pip install beautifulsoup4==4.7.1` 才能正常使用。其余 `pip` 的依赖请参考 requirements_py3_gui.txt(图形界面) 或 requirements_py3_console.txt(命令行) 文件。如使用 socks ，需要 `python3 -m pip install pysocks` 及 `python3 -m pip install -U requests[socks]`。


###### 打包exe:
在虚拟环境下打包，这样文件比较小
在管理员模式下运行
1. pip install pipenv
2. cd D:\pythonenv #新建pythonenv目录，在这个目录下进行后续操作
3. pipenv install --python 3.7 这个库适用3.7
4. pipenv shell
5. pipenv install pyinstaller
6. 把要打包的文件夹拷到D:\pythonenv下，本例是win_64_source
7. cd D:\pythonenv\win_64_source
8. pipenv install -r requirements_py3_console.txt
9. pipenv install -r requirements_py3_gui.txt
10. (pythonenv-X-dP51br) D:\pythonenv\win_64_source>pyinstaller -F -w -i olehd_small.ico  olehd_gui.py --add-binary=".\\olehd_lib\\ffmpeg.exe;.\\olehd_lib" 把ffmpeg打包进exe文件
11. exe在D:\pythonenv\win_64_source\dist下

###### 待解决问题：
1. 调用的ffmpeg太大
2. ffmpeg执行时会弹cmd黑框
