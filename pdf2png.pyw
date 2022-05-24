#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os

from tkinter import *
import tkinter.filedialog as filedialog
import tkinter.messagebox as msgbox
import tkinter.ttk as ttk

from tkinter import font

importFlag = 0

try:
    import fitz
except:
    importFlag +=1

try:
    from PIL import Image
except:
    importFlag +=2

if importFlag > 0:

    if importFlag ==1:
        errmsg = "载入 pymupdf 库失败，请用 pip install pymupdf 命令进行安装。"
    elif importFlag ==2:
        errmsg = "载入 PIL 库失败，请用 pip install pillow 命令进行安装。"
    else:
        errmsg = "pymupdf 和 PIL 库载入失败，请用 pip install pymupdf pillow 命令进行安装。"
    
    msgbox.showerror("错误",errmsg)
    quit()

#-------------------------------------

def textSelectAll(event):
    try:
        event.widget.tag_add('sel', '1.0', 'end')
    except:
        event.widget.select_range(0,'end')

def select_file():
    filename = filedialog.askopenfilename(filetypes=(("pdf文件", "*.pdf"),),initialdir=os.getcwd(),title="请选择一个PDF文件")
    if filename:
        nameVar.set(filename)
        path=os.path.dirname(filename)
        if path:
            pathVar.set(path)
            os.chdir(path)

def select_dir():
    dirname = filedialog.askdirectory(mustexist=True,initialdir=os.getcwd(),title="选择输出文件存放位置")
    if dirname:
        pathVar.set(dirname)

def set_mod_multi():
    btnMultiPics.configure(relief="sunken",bg="powder blue")
    btnMergePic.configure(relief="groove",bg=DEFAULT_BUTTON_COLOR)
    inputPrefix.configure(state="normal")
    inputPicName.configure(state="disabled")
    modeVar.set(True)

def set_mod_long():
    btnMultiPics.configure(relief="groove",bg=DEFAULT_BUTTON_COLOR)
    btnMergePic.configure(relief="sunken",bg="powder blue")
    inputPrefix.configure(state="disabled")
    inputPicName.configure(state="normal")
    modeVar.set(False)


def start_convert():
    inputFile = nameVar.get()
    outputPath = pathVar.get()
    convertMode = modeVar.get()
    picPrefix = prefixVar.get()
    picName = picnameVar.get()

    
    if os.path.isfile(inputFile) and os.path.exists(outputPath):
        if inputFile.split(".")[-1].lower() != 'pdf':
            msgbox.showerror("错误","读取文件须为PDF格式")
            return None
        os.chdir(outputPath)
        imagedata = pdf2png(inputFile,convertMode,picPrefix)

        if not convertMode:
            mergePic(imagedata,True,picName)
            msgbox.showinfo("完成",f"已生成{picName}.png。")
        else:
            msgbox.showinfo("完成",f"已导出{len(imagedata)}张图片。")


#----- core convert function -------

def pdf2png(file,save2file=False,filename="page"):
    data=[]
    with fitz.open(file) as doc:
        for page in doc:
            pix = page.get_pixmap()
            imgdata = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            data.append(imgdata)
            if save2file:
                pix.save(f"{filename}-{page.number+1:02}.png")

    return data
    
def mergePic(data,save2file=False,filename='合并长图'):
    total = len(data)
    x,y = data[0].size
    print('  首张图片尺寸：',x,y)
    toImage = Image.new('RGBA',(x,y*total))
    for i in range(total):
        toImage.paste(data[i],(0,y*i))
        
    if save2file:
        toImage.save(f'{filename}.png')

    return toImage

#-------------------------------------


root = Tk()
root.bind_class("Text","<Control-a>", textSelectAll)  #覆盖原有的 Ctrl+a
root.title("PDF 转图片工具 v0.2 by 欧剃")

#字体和尺寸

LARGE_FONT=16
MON_FONTSIZE = 13
SMALL_FONT=10

#可自行更换字体
FONT_NAME = "等距更纱黑体 T SC" if "等距更纱黑体 T SC" in font.families() else "Sans-Serif"
FONT_NAME = "霞鹜文楷" if "霞鹜文楷" in font.families() else "Sans-Serif"

default_font = font.nametofont("TkDefaultFont")
default_font.configure(family=FONT_NAME,size=MON_FONTSIZE)
btnFont = font.Font(family=FONT_NAME, size=SMALL_FONT)

style = ttk.Style()

root.geometry("508x350+500+300")

#------- 全局参数

modeVar = BooleanVar()
nameVar = StringVar()
pathVar = StringVar()
prefixVar = StringVar()
picnameVar = StringVar()
multiPicIcon = PhotoImage(file="multipics.png")
longPicIcon =  PhotoImage(file="longpic.png")

modeVar.set(True)

#------- root ------------------

frameLeft  = ttk.Frame(root,padding=8,relief="groove",borderwidth=1)
frameRight = ttk.Frame(root,padding=8,relief="groove",borderwidth=1)

label1 = ttk.Label(root,text="读取文件：")
label2 = ttk.Label(root,text="输出位置：")
label3 = ttk.Label(frameLeft,text="前缀名称：")
label4 = ttk.Label(frameRight,text="图片名称：")
label5 = ttk.Label(root,text="选择转换模式：")

inputFileName = ttk.Entry(root, width=48, textvariable = nameVar)
inputOutPath  = ttk.Entry(root, width=48, textvariable = pathVar)
inputPrefix   = ttk.Entry(frameLeft,width=19, textvariable = prefixVar)
inputPicName  = ttk.Entry(frameRight,width=19,state="disabled", textvariable = picnameVar)

prefixVar.set("页面")
picnameVar.set("长图")

btnOpen      = Button(root,text="浏览...", font=btnFont, command=select_file)
btnDir       = Button(root,text="浏览...", font=btnFont, command=select_dir)
btnMultiPics = Button(frameLeft,text="生成多张图片",
                      font=btnFont,relief="sunken",bg="powder blue",
                      image=multiPicIcon,compound =BOTTOM,
                      command=set_mod_multi)
btnMergePic  = Button(frameRight,text="合并成长图",
                      font=btnFont,relief="groove",
                      image=longPicIcon,compound =BOTTOM,
                      command=set_mod_long)
btnStart     = Button(root,text="开始转换",width=30, command=start_convert)

DEFAULT_BUTTON_COLOR = btnStart['bg']
#-------- packing

label1.place(x=5,y=5)
label2.place(x=5,y=35)

inputFileName.place(x=90,y=8)
inputOutPath.place(x=90,y=38)

btnOpen.place(x=440,y=5)
btnDir.place(x=440,y=35)

frameLeft.place(x=5,y=88)
frameRight.place(x=255,y=88)

label5.place(x=12,y=72)

btnStart.pack(side=BOTTOM,padx=5,pady=10)

#--- frame grid---

btnMultiPics.grid(row=0,column=0,columnspan=2, padx=5, pady=5,sticky="nesw")
btnMergePic.grid(row=0,column=0,columnspan=2, padx=5, pady=5,sticky="nesw")

label3.grid(row=1,column=0, pady=5,sticky="w")
label4.grid(row=1,column=0, pady=5,sticky="w")

inputPrefix.grid(row=1,column=1, pady=5,sticky="we")
inputPicName.grid(row=1,column=1, pady=5,sticky="we")

#-------- grid config

frameLeft.grid_columnconfigure('all', weight=0)
frameRight.grid_columnconfigure('all', weight=0)

#-------------------------------

root.resizable(False,False)  #阻止窗口缩放
root.mainloop()

