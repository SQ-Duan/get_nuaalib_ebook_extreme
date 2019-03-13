#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
使用说明
0.  安装python3和相关库:
    widnows系统:
        在https://www.python.org/downloads/下载python3安装包，安装后再使用管理员cmd窗口执行`py -m pip install pillow requests reportlab`。
    ubuntu系统:
        使用`sudo apt install python3-pil python3-requests python3-reportlab`命令即可安装
1.  执行脚本: windows下双击执行脚本，Linux下输入命令`python3 ./get_lib_ebook.py`执行脚本
2.  打开南航的网上图书馆lib.nuaa.edu.cn
3.  搜索你想看的书籍，并在搜索结果中打开对应链接
4.  查看此书的界面内**是否有在线阅读的按钮**
5.  点击**在线阅读**按钮，将弹出的阅读界面的网址复制到命令窗口，按回车，即可。
'''

import datetime
import io
import os
import re
import sys
import time
from html.parser import HTMLParser
from queue import Queue
from threading import Thread

import requests
from PIL import Image as pilImage
from reportlab import rl_config
from reportlab.lib.boxstuff import aspectRatioFix
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import (ImageReader, _digester, import_zlib, isSeq,
                                 isStr, isUnicode)
from reportlab.pdfbase import pdfdoc
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (BaseDocTemplate, Frame, Image, PageBreak,
                                PageTemplate)

# 支持的图片类型
__allow_type = [".jpg", ".jpeg", ".bmp", ".png"]

class MyHTMLParser(HTMLParser):
    # 当进入一个script的开始结束标志
    __is_script_found = False
    __script_index = 0
    __script_data = []
    
    __is_title_found = False
    __title_data = ""

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.__is_script_found = True
            self.__script_index = self.__script_index + 1

        if tag == "title":
            self.__is_title_found = True

    def handle_endtag(self, tag):
        if tag == "script":
            self.__is_script_found = False

        if tag == "title":
            self.__is_title_found = False        

    def handle_data(self, data):
        if self.__is_script_found:
            __script_data_len = len(self.__script_data)
            for i in range(__script_data_len, self.__script_index):
                if i != self.__script_index - 1:
                    self.__script_data.append(None)
                else:
                    self.__script_data.append(data)

        if self.__is_title_found:
            self.__title_data = data

    def get_script_data(self, index):
        return self.__script_data[index]

    def get_title_data(self):
        return self.__title_data


class MyCanvas(Canvas):
    def drawImage(self, image, filename, x, y, width=None, height=None, mask=None, 
            preserveAspectRatio=False, anchor='c'):      
        self._currentPageHasImages = 1

        #imagename, use it
        s = '%s%s' % (filename, mask)
        if isUnicode(s):
            s = s.encode('utf-8')
        name = _digester(s)

        # in the pdf document, this will be prefixed with something to
        # say it is an XObject.  Does it exist yet?
        regName = self._doc.getXObjectName(name)
        imgObj = self._doc.idToObject.get(regName, None)
        if not imgObj:
            #first time seen, create and register the PDFImageXobject
            imgObj = pdfdoc.PDFImageXObject(name, mask=mask)
            ext = os.path.splitext(filename)[1].lower()
            if not(ext in ('.jpg', '.jpeg') and imgObj.loadImageFromJPEG(image)):
                if rl_config.useA85:
                    imgObj.loadImageFromA85(image)
                else:
                    imgObj.loadImageFromRaw(image)

            imgObj.name = name
            self._setXObjects(imgObj)
            self._doc.Reference(imgObj, regName)
            self._doc.addForm(name, imgObj)
            smask = getattr(imgObj,'_smask',None)
            if smask:   #set up the softmask obtained above
                mRegName = self._doc.getXObjectName(smask.name)
                mImgObj = self._doc.idToObject.get(mRegName, None)
                if not mImgObj:
                    self._setXObjects(smask)
                    imgObj.smask = self._doc.Reference(smask,mRegName)
                else:
                    imgObj.smask = pdfdoc.PDFObjectReference(mRegName)
                del imgObj._smask

        # ensure we have a size, as PDF will make it 1x1 pixel otherwise!
        x,y,width,height,scaled = aspectRatioFix(preserveAspectRatio,anchor,x,y,width,height,imgObj.width,imgObj.height)

        # scale and draw
        self.saveState()
        self.translate(x, y)
        self.scale(width, height)
        self._code.append("/%s Do" % regName)
        self.restoreState()

        # track what's been used on this page
        self._formsinuse.append(name)

        return (imgObj.width, imgObj.height)


def isAllow_file(filepath):
    """
    是否允许的文件
    :param file:
    :return:
    """
    if filepath and (os.path.splitext(filepath)[1] in __allow_type):
        return True

    return False


def validate_namer(Namer):
    valid_name_re = re.compile(r'[\\/:"*?<>|]+')
    return valid_name_re.sub('_', Namer)


def pdf_convert(save_book_name, book_w, book_h, book_pages):
    if not isinstance(book_pages, Queue):
        print("PDF队列发生错误。")
        return
    mypdf = MyCanvas(save_book_name, (book_w, book_h))
    while True:
        page_tmp = book_pages.get()
        # (None. None)为结束标志
        if page_tmp == (None, None):
            break
        else:
            with io.BytesIO(page_tmp[1]) as fp:
                mypdf.drawImage(fp, page_tmp[0], 0, 0, book_w, book_h)
                mypdf.showPage()
    mypdf.save()



def catch_n_download(Reader_URL):
    try:
        Reader_res = requests.get(Reader_URL)
        Reader_res.raise_for_status()
        
        my_html_parser = MyHTMLParser()
        my_html_parser.feed(Reader_res.text)

        Get_Image_URL_Header = my_html_parser.get_script_data(6)
        re_URL = re.compile(r"http://202.119.70.51:88/png/png.dll.*/")
        mo = re_URL.search(Get_Image_URL_Header)
        URL_IMGBEG = mo.group()
        Book_Title = validate_namer(my_html_parser.get_title_data())

        # 取自图书馆页面之逆向中的书本页面分类的文件名标志
        type_pages = ['cov%03d',
            'bok%03d',
            'leg%03d',
            'fow%03d',
            '!%05d',
            '%06d',
            'att%03d',
            'bac%03d'
            ]
        name_pages = [  '01_Cover_',
            '02_BookTi_',
            '03_Lega_',
            '04_Prefa_',
            '05_Menu_',
            '06_Text_',
            '07_Appendix_',
            '08_Back_'
            ]

        __a4_w, __a4_h = A4
        img_w, img_h = A4
        is_first_page = True
        qpages = Queue(4)
        pthread = None

        print("[*][转换PDF] : 开始. [保存路径] > [%s.pdf]。\n" % (Book_Title))
        beginTime = time.time()
        for j in range(0, 7):
            print('开始下载此书的"%s"部分。' % name_pages[j])
            for i in range(1, 999999):
                tmp_page = requests.get(URL_IMGBEG+type_pages[j]%i + '.jpg')

                while ( not ( tmp_page.status_code == 200 ) ):
                    tmp_page = requests.get(URL_IMGBEG+type_pages[j]%i + '.jpg')

                if(len(tmp_page.content) <= 200):
                    if( i ==1 ):
                        print('"本书没有%s部分。\n' % name_pages[j])
                    break

                # 当抓取到第一页时，初始化PDF
                if is_first_page:
                    is_first_page = False
                    with io.BytesIO(tmp_page.content) as fp:
                        with pilImage.open(fp) as img:
                            img_w, img_h = img.size

                            if __a4_w / img_w < __a4_h / img_h:
                                img_w = __a4_w
                                img_h = img_h * (__a4_w / img_w)
                            else:
                                img_w = img_w * (__a4_h / img_h)
                                img_h = __a4_h
                            pthread = Thread(target = pdf_convert, args = (Book_Title+".pdf", img_w, img_h, qpages), daemon = True)
                            pthread.start()

                res_type=re.split("[/;]", tmp_page.headers['Content-Type'])
                qpages.put((name_pages[j] + type_pages[5]%i + '.' + res_type[1], tmp_page.content))
            
            if( not ( i ==1 ) ):
                print('《%s》的"%s"部分已经获取完成。该部分共%d页。\n' % (Book_Title, str(name_pages[j]), i))

        qpages.put((None, None))
        pthread.join()
        print('*******************************\n* 全书下载完成；PDF生成完成。 *\n*******************************\n')
        endTime = time.time()
        print("[*][转换PDF] : 结束. [保存路径] > [%s.pdf] , 耗时 %f s。\n" % (Book_Title, (endTime - beginTime)))
    except:
        print("抓取期间出现了问题。\n")
        raise


# Main program
if __name__ == '__main__':
    if (len(sys.argv) == 2):
            Reader_URL = str(sys.argv[1])
    else:
        if(len(sys.argv) == 1):
            print("请您键入您要下载的书目在阅读器时标签栏的网址后回车。\n")
            Reader_URL = input()
            print()
        else:
            print("输入的参数不正确。")
            sys.exit()

    catch_n_download(Reader_URL)
