
import os
import hashlib
import qrcode
import io
import fitz
import time
import difflib
from aip import AipOcr
import string
from zhon.hanzi import punctuation
import cv2
import numpy as np
from lxml import html
from lxml.html import tostring
try:
    from win32com.client import constants, gencache
except ImportError:
    constants = None
    gencache = None
import pythoncom    # word-pdf 用于多线程

# __all__ = ['DB','UPLOAD_BASE_PATH','word_to_pdf','pics_to_pdf','sort_for_up_pdf']


"""百度ocr接口信息"""
APP_ID = '22858422'  # 'App ID'
API_KEY = 'VqOVEi9IQa2NyNnGl0dWY1yG'  # 'Api Key'
SECRET_KEY = 'WkYdayFh9Ycm4iE3kGOPl1xNnSyYSXMR'  # 'Secret Key'
CLIENT = AipOcr(APP_ID, API_KEY, SECRET_KEY)
def get_equal_rate(str1, str2):
    return difflib.SequenceMatcher(None, str1, str2).quick_ratio()

def get_content_ocr(ocrObject):
    strs = ''
    try:
        for item in ocrObject['words_result']:
            strs +=item['words'] + '\n'
        return strs
    except:
        return ''

def sort_for_up_pdf(src_pdf_path,upload_pic_path):
    doc = fitz.open(src_pdf_path)
    valid_pdf_img = [item.getPixmap() for item in doc]
    doc.close()
    src_pdf_text = [get_content_ocr(CLIENT.basicAccurate(item.getImageData(output='png'))) for item in valid_pdf_img] 
    upload_img = []
    for i in os.listdir(upload_pic_path):
        with open(upload_pic_path+'/'+i,'rb') as f:
            upload_img.append(f.read())
    upload_text = [get_content_ocr(CLIENT.basicAccurate(item)) for item in upload_img]
    upload_index_sort = []
    up_load_txt = []
    for src_text in src_pdf_text:
        similaritys = []
        for usr_text in upload_text:
            similarity = get_equal_rate(src_text,usr_text)
            similaritys.append(similarity)
        index = [i for (i,item) in enumerate(similaritys) if item==max(similaritys)][0]
        upload_index_sort.append(index)
        up_load_txt.append(upload_text[index])
    print(upload_index_sort)

    compare_tables = ''
    for src_txt,up_txt in zip(src_pdf_text,up_load_txt):
            # src_remove_char, up_remove_char= compares(src_txt), compares(up_txt)
            # similarity_remove = get_equal_rate(src_remove_char, up_remove_char)
            # compare_sum +=similarity_remove
            diff = difflib.HtmlDiff()
            # result = diff.make_file(src_txt.split('\n'), up_txt.split('\n'))
            result = diff.make_table(src_txt.split('\n'), up_txt.split('\n'))
            compare_tables+=result+'\n' 
    
    with open('compare.txt',mode='w',encoding='utf8') as f:
        f.write(compare_tables)

    with open('src_pdf.txt',mode='w',encoding='utf8') as f:
        f.write('\n'.join(src_pdf_text))
    with open('up_img.txt',mode='w',encoding='utf8') as f:
        f.write('\n'.join(up_load_txt))

    diff = difflib.HtmlDiff()
    # result = diff.make_table(''.join(src_pdf_text).split('\n'), ''.join(up_load_txt).split('\n'))
    result = diff.make_table(src_pdf_text[1].split('\n'), up_load_txt[1].split('\n'))

    compare_html = 'diffs_2.html'
    # fd_diff = open(compare_html, "a", encoding='utf-8')
    # fd_diff.write(result)
    # fd_diff.close()

    # return upload_index_sort
def compare():
    src_txt,up_txt = '',''
    with open('src_pdf.txt',mode='r',encoding='utf8') as f:
        src_txt = f.readlines()

    print('#'*50)

    with open('up_img.txt',mode='r',encoding='utf8') as f:
        up_txt = f.readlines()
    x = difflib.context_diff(src_txt[0],up_txt[0])    
    diff = difflib.Differ()
    df1 = difflib.HtmlDiff()
    r1 = df1.make_table(src_txt[0].split('\n'),up_txt[0].split('\n'))
    r = diff.compare(src_txt,up_txt)
    # print(src_txt)
    for i in r1:
        print(i)
    # print(next(x))

if __name__ == "__main__":
    sort_for_up_pdf('./测试合同.pdf','pics')
    # compare()