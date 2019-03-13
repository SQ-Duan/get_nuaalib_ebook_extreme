# get_nuaalib_ebook_extreme
南航图书馆电子图书馆转PDF脚本

更改自 https://github.com/Yohoa/Download-Scanned-Book-from-the-Library-of-NUAA

## 使用说明

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
