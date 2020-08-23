# get_nuaalib_ebook_extreme

**图书馆已采用邮箱申请PDF方式，此脚本作废，仅供参考学习**

南航图书馆电子图书馆转PDF脚本

更改自 https://github.com/Yohoa/Download-Scanned-Book-from-the-Library-of-NUAA

## Features

1. 抓取到的图片片不再采用本地存储的方式，采用内存存储
2. 网络请求和PDF存储分别不同线程，无需等待全部内容下载完，边下载边存储，速度更快

## 使用说明

0.  安装python3和相关库:  
    widnows系统:在`https://www.python.org/downloads/`下载python3安装包，安装后再使用管理员cmd窗口执行`py -m pip install pillow requests reportlab`。  
    ubuntu系统:使用`sudo apt install python3-pil python3-requests python3-reportlab`命令即可安装  
1.  执行脚本: windows下双击执行脚本，或在当前目录下用cmd或powershell中执行`py get_lib_ebook_extreme.py`  
    Linux下在当前目录输入命令`python3 get_lib_ebook_extreme.py`执行脚本  
2.  打开南航的网上图书馆`lib.nuaa.edu.cn`  
3.  搜索你想看的书籍，并在搜索结果中打开对应链接  
4.  查看此书的界面内**是否有在线阅读的按钮**  
5.  点击**在线阅读**按钮，将弹出的阅读界面的网址复制到命令窗口，按回车，即可。  
