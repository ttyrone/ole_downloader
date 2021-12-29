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

__author__ = ''
__copyright__ = 'Copyright 2021'
__credits__ = ['Lim Kok Hole']
__license__ = 'MIT'
__version__ = 1.0
__maintainer__ = 'Tyrone Hank'
__email__ = 'ttyronehank@gmail.com'
__status__ = 'Production'

import sys, os, logging, traceback
PY3 = sys.version_info[0] >= 3
if not PY3:
    print('\n[!]中止! 请使用 python 3。')
    sys.exit(1)

from logging.handlers import QueueHandler, QueueListener

from PySide2 import QtCore
from PySide2.QtCore import Qt, Slot, QProcess
from PySide2.QtWidgets import (QApplication, QCheckBox, QMainWindow,
                                QLayout, QHBoxLayout, QVBoxLayout,
                                QWidget, QLabel, 
                                QSpinBox, QRadioButton, QPushButton,
                                QLineEdit, QPlainTextEdit, 
                                QFileDialog)
                               
import multiprocessing

def worker_init(q):
    qh = QueueHandler(q)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    #logger.setLevel(logging.DEBUG)
    logger.addHandler(qh)

class LogEmitterOtherProces(QtCore.QObject):
    sigLog = QtCore.Signal(str)

class LogEmitter(QtCore.QObject):
    sigLog = QtCore.Signal(logging.LogRecord)

class LogHandler(logging.Handler):

    def __init__(self):
        super().__init__()
        self.emitter = LogEmitter()

    def emit(self, record):
        msg = self.format(record)
        self.emitter.sigLog.emit(msg)

class LogHandlerOtherProcess(logging.Handler):

    def __init__(self):
        super().__init__()
        self.emitter =  LogEmitterOtherProces()

    def emit(self, record):
        msg = self.format(record)
        self.emitter.sigLog.emit(msg)

class LoggerWriterOtherProcess():

    def write(self, msg):
        logging.info(msg.strip())
        #logging.debug(msg.strip())

    def flush(self): 
        pass

class LoggerWriter(logging.Handler):

    emitter = LogEmitter()

    def write(self, msg):
        self.emitter.sigLog.emit(msg.strip())

    def flush(self): 
        pass

    def emit(self, record):
        msg = self.format(record)
        self.emitter.sigLog.emit(msg)

class Widget(QWidget):

    cinema_url_label_text = "粘贴欧乐影院的连续剧/综艺/动漫 URL: "
    movie_url_label_text = "粘贴欧乐影院的电影 URL: "

    #cinema_dest_label_text = "输入连续剧/综艺/动漫名 (用来命名下载的目录): "
    #movie_dest_label_text = "输入电影名 (用来命名下载的文件): "

    def __init__(self):
        QWidget.__init__(self)

        self.q = None
        self.pool = None

        self.top = QHBoxLayout()
        self.top.setMargin(10)

        self.radioButtonMov = QRadioButton("电影")
        self.radioButtonCinema = QRadioButton("连续剧/综艺/动漫")

        self.top.addWidget(self.radioButtonMov)
        self.top.addWidget(self.radioButtonCinema)
        
        self.middle = QVBoxLayout()
        self.middle.setMargin(10)

        self.url_label = QLabel()
        self.url = QLineEdit()
        self.url_label.setBuddy(self.url)
        self.middle.addWidget(self.url_label)
        self.middle.addWidget(self.url)

        self.browse_folder_label = QLabel("下载到：")
        self.browseFolder = QPushButton("选择目录(将在此目录下创建以剧名命名的文件夹用于存放临时文件和视频文件)")
        self.browse_folder_label.setBuddy(self.browseFolder)
        self.middle.addWidget( self.browse_folder_label)
        self.middle.addWidget( self.browseFolder)
        self.browse_folder_value = ""
  
        #self.dest_file_label = QLabel()
        # "输入电影/电视剧名 (用来命名下载的文件/目录): " title set by choose_movie_widgets() later
        '''
        self.folder_or_filename = QLineEdit()
        self.dest_file_label.setBuddy(self.folder_or_filename)
        self.middle.addWidget(self.dest_file_label)
        self.middle.addWidget(self.folder_or_filename)
        '''

        self.downloadAll = QCheckBox('下载全集')
        self.middle.addWidget(self.downloadAll)

        self.bk_cinemae_spin_from = 1
        self.bk_cinemae_spin_to = 1
        self.fromEpSpinBox = QSpinBox()
        self.fromEpSpinBox.setMinimum(1)
        self.fromEpSpinBox.setMaximum(2147483647)
        self.fromEpLabel = QLabel("&从第几集开始下载：")
        self.fromEpLabel.setBuddy(self.fromEpSpinBox)

        self.toEpSpinBox = QSpinBox()
        self.toEpSpinBox.setMinimum(1)
        self.toEpSpinBox.setMaximum(2147483647)
        self.toEpLabel = QLabel("&到第几集停止下载：")
        self.toEpLabel.setBuddy(self.toEpSpinBox)

        self.cinema_ly = QHBoxLayout()
        #self.cinema_ly.setMargin(10)
        self.cinema_ly.addWidget(self.fromEpLabel)
        self.cinema_ly.addWidget(self.fromEpSpinBox)
        self.cinema_ly.addWidget(self.toEpLabel)
        self.cinema_ly.addWidget(self.toEpSpinBox)
        self.middle.addLayout(self.cinema_ly)

        self.proxy_label = QLabel("（如有）代理（非翻墙用户请去掉默认设置，或填写实际代理）：")
        self.proxy = QLineEdit('http://127.0.0.1:1080')
        self.proxy_label.setBuddy(self.proxy)
        self.middle.addWidget(self.proxy_label)
        self.middle.addWidget(self.proxy)

        self.add = QPushButton("开始下载")
        self.add.setEnabled(False)
        self.middle.addWidget(self.add)

        self.stop_me = QPushButton("停止下载")
        self.stop_me.setEnabled(False)
        self.middle.addWidget(self.stop_me)

        self.export = QPushButton("导出下载列表")
        self.export.setEnabled(False)
        self.middle.addWidget(self.export)

        self.combine = QPushButton("合并MP4")
        self.combine.setEnabled(False)
        self.middle.addWidget(self.combine)

        self.combine_folder_label = QLabel("待合并视频文件夹：")
        self.combineFolder = QPushButton("选择目录(选择m4s文件夹的上级目录,确保这个文件夹只有存放m4s文件的文件夹)")
        self.combine_folder_label.setBuddy(self.combineFolder)
        self.middle.addWidget( self.combine_folder_label)
        self.middle.addWidget( self.combineFolder)
        self.combine_folder_value = ""


        self.fixfile = QPushButton("修复MP4")
        self.fixfile.setEnabled(False)
        self.middle.addWidget(self.fixfile)

        self.fixfile_folder_label = QLabel("待修复视频：")
        self.fixfileFolder = QPushButton("选择待修复视频")
        self.fixfile_folder_label.setBuddy(self.fixfileFolder)
        self.middle.addWidget( self.fixfile_folder_label)
        self.middle.addWidget( self.fixfileFolder)
        self.fixfile_folder_value = ""

        self.log_area = QPlainTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumBlockCount(1000)
        self.middle.addWidget(self.log_area)

        #self.table_view.setSizePolicy(size)
        #self.layout.addWidget(self.table)
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.top)
        self.layout.addLayout(self.middle)
        self.setLayout(self.layout)

        self.radioButtonMov.toggled.connect(self.choose_movie_widgets)
        self.radioButtonCinema.toggled.connect(self.choose_cinema_widgets)
        self.url.textChanged[str].connect(self.check_disable_download)
        self.browseFolder.clicked.connect(self.add_folder)
        self.combineFolder.clicked.connect(self.add_combine_folder)
        self.fixfileFolder.clicked.connect(self.add_fixfile)
        #self.folder_or_filename.textChanged[str].connect(self.check_disable_download)
        self.export.clicked.connect(self.start_export)
        self.combine.clicked.connect(self.start_combine)
        self.fixfile.clicked.connect(self.start_fixfile)
        self.add.clicked.connect(self.start_download)
        self.stop_me.clicked.connect(self.stop_download)

        self.radioButtonMov.setChecked(True) #set default only after .connect above

        # TESTING PURPOSE
        
        '''self.radioButtonMov.setChecked(True)
        self.url.setText('https://www.olehd.com/index.php/vod/detail/id/32191.html')#'https://m.olehd.fun/voddetail/2485.html'
        self.browse_folder_value = ''
        '''


        #set current process (not queue that one) log handler:
        logger = logging.getLogger(__name__)
        handler2 = LoggerWriter()
        logger.addHandler(handler2)
        logger.setLevel(logging.INFO) #DEBUG
        handler2.emitter.sigLog.connect(self.log_area.appendPlainText)
        sys.stdout = handler2 #LoggerWriter()
        #sys.stderr = handler2 #Seems no difference
        #handler2.emitter.sigLog.emit('hihi')

    @Slot()
    def choose_movie_widgets(self):

        if self.radioButtonMov.isChecked():

            self.url_label.setText(self.movie_url_label_text)
            #self.dest_file_label.setText(self.movie_dest_label_text)

            self.fromEpLabel.setDisabled(True)
            self.toEpLabel.setDisabled(True)

            self.fromEpSpinBox.setDisabled(True)
            self.toEpSpinBox.setDisabled(True)

            self.bk_cinemae_spin_from = self.fromEpSpinBox.value()
            self.bk_cinemae_spin_to = self.toEpSpinBox.value()
            self.fromEpSpinBox.setValue(1)
            self.toEpSpinBox.setValue(1)

    @Slot()
    def choose_cinema_widgets(self):

        if self.radioButtonCinema.isChecked():

            self.url_label.setText(self.cinema_url_label_text)
            #self.dest_file_label.setText(self.cinema_dest_label_text)

            self.fromEpLabel.setEnabled(True)
            self.toEpLabel.setEnabled(True)

            self.fromEpSpinBox.setEnabled(True)
            self.toEpSpinBox.setEnabled(True)

            self.fromEpSpinBox.setValue(self.bk_cinemae_spin_from)
            self.toEpSpinBox.setValue(self.bk_cinemae_spin_to)


    @Slot()
    def add_folder(self, s):

        #fname = QFileDialog.getOpenFileName(self, 'Open file', "c:\'", "Image files (*.jpg *.gif)")
        #fname = QFileDialog.getOpenFileName(self, 'Open file', '', QFileDialog.ShowDirsOnly)
        fname = QFileDialog.getExistingDirectory(self, '选择下载至什么目录', '', QFileDialog.ShowDirsOnly)
        #print('repr: ' + repr(fname))
        if fname and fname.strip():
            fname = fname.strip()
            self.browse_folder_value = fname
            #if getOpenFileName, will return ('/home/xiaobai/Pictures/disco.jpg', 'Image files (*.jpg *.gif)')
            #, while if getExistingDirectory, will return single path string only
            self.browseFolder.setText(fname)
            self.check_disable_download(fname)
        #else:
        #    print('User cancel')

    @Slot()
    def add_combine_folder(self, s):

        #fname = QFileDialog.getOpenFileName(self, 'Open file', "c:\'", "Image files (*.jpg *.gif)")
        #fname = QFileDialog.getOpenFileName(self, 'Open file', '', QFileDialog.ShowDirsOnly)
        fname = QFileDialog.getExistingDirectory(self, '选择目录', '', QFileDialog.ShowDirsOnly)
        #print('repr: ' + repr(fname))
        if fname and fname.strip():
            fname = fname.strip()
            self.combine_folder_value = fname
            #if getOpenFileName, will return ('/home/xiaobai/Pictures/disco.jpg', 'Image files (*.jpg *.gif)')
            #, while if getExistingDirectory, will return single path string only
            self.combineFolder.setText(fname)
            self.check_disable_download(fname)
            self.combine.setEnabled(True)
        #else:
        #    print('User cancel')
        #   
        else:
            print('未选择目录')
            self.combine.setEnabled(False)
        
    @Slot()
    def add_fixfile(self, s):

        fname = QFileDialog.getOpenFileName(self, '选择待修复视频', "c:\'", "Vedio files (*.mp4)")
        #fname = QFileDialog.getOpenFileName(self, 'Open file', '', QFileDialog.ShowDirsOnly)
        #fname = QFileDialog.getExistingDirectory(self, '选择待修复视频', '', QFileDialog.ShowDirsOnly)
        #print('repr: ' + repr(fname))
        if fname[0] != '':
            filepathname = fname[0].strip()
            self.fixfile_folder_value = filepathname
            #if getOpenFileName, will return ('/home/xiaobai/Pictures/disco.jpg', 'Image files (*.jpg *.gif)')
            #, while if getExistingDirectory, will return single path string only
            self.fixfileFolder.setText(filepathname)
            self.fixfile.setEnabled(True)
            print('待修复视频：%s' % filepathname)
            #self.check_disable_download(fname)
        else:
            print('无待修复视频')
            self.fixfile.setEnabled(False)

    @Slot()
    def check_disable_download(self, s):

        if self.url.text().strip() and self.browse_folder_value:
            self.add.setEnabled(True)
            self.export.setEnabled(True)
        else:
            self.add.setEnabled(False)
            self.export.setEnabled(False)

    def task_done(self, retVal):
        self.add.setEnabled(True)
        self.stop_me.setEnabled(False)
        self.combine.setEnabled(True)
        self.export.setEnabled(True)

    @Slot()
    def stop_download(self):
        if self.q:
            self.q.close()
        if self.pool:
            self.pool.terminate()
        self.add.setEnabled(True)
        self.stop_me.setEnabled(False)
        print('下载停止。')

    @Slot()
    def start_download(self):

        if self.fromEpSpinBox.value() > self.toEpSpinBox.value():
            self.log_area.setPlainText('[!] 从第几集必须小于或等于到第几集。')
            return

        #No need worry click twice too fast, it seems already handle by PySide2
        self.add.setEnabled(False)
        self.stop_me.setEnabled(True)
        self.log_area.clear()

        dest_full_path = os.path.join(self.browse_folder_value)
        '''
        print('dest_full_path: ' + repr(dest_full_path))
        print('self.url.text(): ' + repr(self.url.text()))
        print('self.fromEpSpinBox.value(): ' + repr(self.fromEpSpinBox.value()))
        print('self.toEpSpinBox.value(): ' + repr(self.toEpSpinBox.value()))
        '''

        import olehd_console

        #Windows can't set like that bcoz not update for args.url, must put explicitly
        #olehd_console.redirect_stdout_to_custom_stdout(arg_url, ...etc, LoggerWriter())

        #failed other process
        handler = LogHandlerOtherProcess()
        handler.emitter.sigLog.connect(self.log_area.appendPlainText)

        ''' #ref current process:
        logger = logging.getLogger(__name__)
        handler2 = LoggerWriter()
        logger.addHandler(handler2)
        logger.setLevel(logging.DEBUG)
        handler2.emitter.sigLog.connect(self.log_area.appendPlainText)
        sys.stdout = handler2 #LoggerWriter()
        #handler2.emitter.sigLog.emit('hihi')
        '''

        #handler = LoggerWriter()
        #handler.emitter.sigLog.connect(self.log_area.appendPlainText)

        self.q = multiprocessing.Queue()
        self.ql = QueueListener(self.q, handler)
        self.ql.start()

        self.pool = multiprocessing.Pool(1, worker_init, [self.q])
        arg_proxy =self.proxy.text().strip()
        if arg_proxy:
            if '://' not in arg_proxy:
                arg_proxy = 'https://' + arg_proxy
            proxies = { 'http': arg_proxy, 'https': arg_proxy }
            print('[...] 尝试代理: ' + proxies['https'])
        else:
            proxies = {}
            print('[...] 无代理。')
            
        if self.radioButtonMov.isChecked():
            self.pool.apply_async(olehd_console.main, args=(True, dest_full_path,
                    self.url.text().strip(), self.fromEpSpinBox.value(), self.toEpSpinBox.value(), LoggerWriterOtherProcess(), False, proxies, self.downloadAll.isChecked()), callback=self.task_done)
        else:
            self.pool.apply_async(olehd_console.main, args=(False, dest_full_path, 
                    self.url.text().strip(), self.fromEpSpinBox.value(), self.toEpSpinBox.value(), LoggerWriterOtherProcess(), False, proxies, self.downloadAll.isChecked()), callback=self.task_done)
    @Slot()
    def start_export(self):

        if self.fromEpSpinBox.value() > self.toEpSpinBox.value():
            self.log_area.setPlainText('[!] 从第几集必须小于或等于到第几集。')
            return

        #No need worry click twice too fast, it seems already handle by PySide2
        self.add.setEnabled(False)
        self.export.setEnabled(False)
        self.stop_me.setEnabled(False)
        self.log_area.clear()

        dest_full_path = os.path.join(self.browse_folder_value)
        '''
        print('dest_full_path: ' + repr(dest_full_path))
        print('self.url.text(): ' + repr(self.url.text()))
        print('self.fromEpSpinBox.value(): ' + repr(self.fromEpSpinBox.value()))
        print('self.toEpSpinBox.value(): ' + repr(self.toEpSpinBox.value()))
        '''

        import olehd_console

        #Windows can't set like that bcoz not update for args.url, must put explicitly
        #olehd_console.redirect_stdout_to_custom_stdout(arg_url, ...etc, LoggerWriter())

        #failed other process
        handler = LogHandlerOtherProcess()
        handler.emitter.sigLog.connect(self.log_area.appendPlainText)

        ''' #ref current process:
        logger = logging.getLogger(__name__)
        handler2 = LoggerWriter()
        logger.addHandler(handler2)
        logger.setLevel(logging.DEBUG)
        handler2.emitter.sigLog.connect(self.log_area.appendPlainText)
        sys.stdout = handler2 #LoggerWriter()
        #handler2.emitter.sigLog.emit('hihi')
        '''

        #handler = LoggerWriter()
        #handler.emitter.sigLog.connect(self.log_area.appendPlainText)

        self.q = multiprocessing.Queue()
        self.ql = QueueListener(self.q, handler)
        self.ql.start()

        self.pool = multiprocessing.Pool(1, worker_init, [self.q])
        arg_proxy =self.proxy.text().strip()
        if arg_proxy:
            if '://' not in arg_proxy:
                arg_proxy = 'https://' + arg_proxy
            proxies = { 'http': arg_proxy, 'https': arg_proxy }
            print('[...] 尝试代理: ' + proxies['https'])
        else:
            proxies = {}
            print('[...] 无代理。')
            
        if self.radioButtonMov.isChecked():
            self.pool.apply_async(olehd_console.export, args=(True, dest_full_path,
                    self.url.text().strip(), self.fromEpSpinBox.value(), self.toEpSpinBox.value(), LoggerWriterOtherProcess(), False,  proxies, self.downloadAll.isChecked()), callback=self.task_done)
        else:
            self.pool.apply_async(olehd_console.export, args=(False, dest_full_path,
                    self.url.text().strip(), self.fromEpSpinBox.value(), self.toEpSpinBox.value(), LoggerWriterOtherProcess(), False,  proxies, self.downloadAll.isChecked()), callback=self.task_done)

    @Slot()
    def start_combine(self):

        self.add.setEnabled(False)
        self.export.setEnabled(False)
        self.combine.setEnabled(False)
        self.stop_me.setEnabled(False)
        self.log_area.clear()

        dest_full_path = os.path.join(self.combine_folder_value)

        import olehd_console

        handler = LogHandlerOtherProcess()
        handler.emitter.sigLog.connect(self.log_area.appendPlainText)

        ''' #ref current process:
        logger = logging.getLogger(__name__)
        handler2 = LoggerWriter()
        logger.addHandler(handler2)
        logger.setLevel(logging.DEBUG)
        handler2.emitter.sigLog.connect(self.log_area.appendPlainText)
        sys.stdout = handler2 #LoggerWriter()
        #handler2.emitter.sigLog.emit('hihi')
        '''

        #handler = LoggerWriter()
        #handler.emitter.sigLog.connect(self.log_area.appendPlainText)

        self.q = multiprocessing.Queue()
        self.ql = QueueListener(self.q, handler)
        self.ql.start()

        self.pool = multiprocessing.Pool(1, worker_init, [self.q])
            
        if self.radioButtonMov.isChecked():
            self.pool.apply_async(olehd_console.combine, args=(True, dest_full_path, LoggerWriterOtherProcess()), callback=self.task_done)
        else:
            self.pool.apply_async(olehd_console.combine, args=(False, dest_full_path, LoggerWriterOtherProcess()), callback=self.task_done)


    @Slot()
    def start_fixfile(self):

        self.add.setEnabled(False)
        self.export.setEnabled(False)
        self.stop_me.setEnabled(False)
        self.log_area.clear()

        dest_full_path = os.path.join(self.fixfile_folder_value)
        import olehd_console
        olehd_console.fixfile( dest_full_path)
       
class MainWindow(QMainWindow):
    def __init__(self, widget):
        QMainWindow.__init__(self)
        self.setWindowTitle("欧乐影院下载器v1.0")
        self.setCentralWidget(widget)
        self.widget = widget

    def closeEvent(self, event):
        if self.widget.q:
            self.widget.close()
        if self.widget.pool:
            # To avoid child process olehd_console still running
            self.widget.pool.terminate()
        QMainWindow.closeEvent(self, event)

if __name__ == "__main__":

    PY3 = sys.version_info[0] >= 3
    if not PY3:
        print('请使用 python 3。中止。')
        sys.exit(1)

    # Prevent closing pyside2 window then automatically re-open until closed console window
    # https://stackoverflow.com/questions/24944558/pyinstaller-built-windows-exe-fails-with-multiprocessing
    # On Windows calling this function is necessary.
    multiprocessing.freeze_support()

    app = QApplication(sys.argv)
    widget = Widget()
    window = MainWindow(widget)
    #window.setStyleSheet('* { font-family: "Times New Roman", Times, serif;}')
    # Better look of chinese character:
    window.setStyleSheet('* { font-family: Tahoma, Helvetica, Arial, "Microsoft Yahei","微软雅黑", STXihei, "华文细黑", sans-serif;}')
    window.show()
    sys.exit(app.exec_())
