# olehd_downloader欧乐影院下载器
## 原作者仓库：https://github.com/limkokhole/olehd-downloader
复制粘贴链接，自定义下载第几集的欧乐影院视频
https://m.olehd.fun/voddetail/2485.html 粘贴这样的网址

---
### 功能:

1. 默认下载连续剧/综艺/动漫，而不是电影。 
2. 选择目录后不需要手工输入剧名，将在选择的目录下创建所下载的剧名的文件夹，临时文件和最终的视频文件都存放在这里。
3. 新增本机代理设置：对于ssr用户，这个选项可大幅减少丢帧现象，代理脚本地址可以在设置-网络和Internet-代理下的脚本地址处获得。
4. 改变下载和保存的模式：每个ts文件单独保存，全部下载完成后自动合并视频并删除相关ts临时文件。具体操作参见注意事项。
5. 增加了下载全集功能，勾选之后会自动下载全集，无须再去选择开始结束集数。 
6. 下载完成后会自动打开下载目录

---
### 注意事项:

1. 下载过程是先下载多段 .ts 文件，单个 .ts 文件单独保存， 完成后才转换 .mp4。
2. 如果没有自动转换为mp4，表示有ts文件下载失败，重新运行一次，会重新下载丢失的ts，如果多次下载错误才有可能是被ban了，将下载目录里的xxxxx import.json文件， 导到postman里看能不能下（点send and download）。该文件为postman的collection文件，将该文件导入postman进行下载操作，逐个下载文件，并命名为请求名.ts（如：请求名为第xx集-002，下载文件就命名为第xx集-002.ts），然后将所有下载文件拷回到下载目录，然后按名称顺序排序，进行合并即可（合并命令：copy /b 第xx集*.ts 第xx集.mp4），合并后请自行删除相关的ts文件，当然，如果不介意丢帧可以直接合并。
3. 重复下载剧集不会覆盖目录下的同名 .ts/.mp4，这样能节约下载时间，如果想要重新下载请先删除原来的.ts/.mp4。
4. 网络有时候慢或操作频繁导致下载失败， 就停止等一阵子才尝试。 
5. 只用雪中悍刀行做了测试。

---
### 普通用户:
Windows (64-bit) 用户，只需要下载 "[欧乐影院下载器_win_64_exe.zip](https://www.aliyundrive.com/s/mLp4GwuzpKt)",  双击 "欧乐影院下载器win_64 v1.1.exe" 文件执行。 
### 示范视频参见原作者视频 (点击图片会在 YouTube 打开):
[![watch in youtube](https://i.ytimg.com/vi/eejUgl7Ku8E/hqdefault.jpg)](https://www.youtube.com/watch?v=eejUgl7Ku8E "欧乐影院下载器")

---
### python 3 用户:

只适用于windows用户。

使用 `python3 olehd_gui.py` 打开图形界面，或 `python3 olehd_console.py -选项` 使用命令行界面。

python3 用户必须先执行命令 `python3 -m pip install beautifulsoup4==4.7.1` 才能正常使用。其余 `pip` 的依赖请参考 requirements_py3_gui.txt(图形界面) 或 requirements_py3_console.txt(命令行) 文件。如使用 socks ，需要 `python3 -m pip install pysocks` 及 `python3 -m pip install -U requests[socks]`。


###### 打包exe:
在虚拟环境下打包，这样文件比较小
1. pip install pipenv
2. cd D:\pythonenv #新建pythonenv目录，在这个目录下进行后续操作
3. pipenv install --python 3.7 这个库适用3.7
4. pipenv shell
5. pipenv install pyinstaller
6. 把要打包的文件夹拷到D:\pythonenv下，本例是win_64_source
7. cd D:\pythonenv\win_64_source
8. pipenv install -r requirements_py3_console.txt
9. pipenv install -r requirements_py3_gui.txt
10. (pythonenv-X-dP51br) D:\pythonenv\win_64_source>pyinstaller -F -w -i olehd_small.ico olehd_gui.py
11. exe在D:\pythonenv\win_64_source\dist下 这样打出来的包只有40多m，直接打包有120多m。
