"""
    公共库
"""
import os
import hashlib
from .tools import connectSqlite
import qrcode
import io
import fitz
import time
import difflib
from aip import AipOcr
import string
from zhon.hanzi import punctuation
from lxml import html
from lxml.html import tostring
try:
    from win32com.client import constants, gencache
except ImportError:
    constants = None
    gencache = None
import pythoncom    # word-pdf 用于多线程
import json


__all__ = ['dir_init','DB','UPLOAD_BASE_PATH','word_to_pdf','pics_to_pdf','sort_for_up_pdf']



# UPLOAD_BASE_PATH = os.path.abspath(__name__)
global baseconfig
_path = os.path.abspath(__name__)
with open(os.path.join(os.path.split(_path)[0],'baseconfig.json'),'r',encoding='utf8')as fp:
    baseconfig = json.load(fp)
# /attach/  静态目录配置 = UPLOAD_BASE_PATH
# UPLOAD_BASE_PATH = baseconfig['UPLOAD_BASE_PATH']
UPLOAD_BASE_PATH = os.path.abspath(os.path.curdir).replace('\\','/')

DATABASE_PATH = baseconfig['DATABASE_PATH']
ATTACHMENT = baseconfig['ATTACHMENT']

"""百度ocr接口信息"""

APP_ID = baseconfig['APP_ID']  # 'App ID'
API_KEY = baseconfig['API_KEY']  # 'Api Key'
SECRET_KEY = baseconfig['SECRET_KEY']  # 'Secret Key'

CLIENT = AipOcr(APP_ID, API_KEY, SECRET_KEY)
DB = connectSqlite(DATABASE_PATH,os.path.exists(DATABASE_PATH))

def dir_init():
    for dir_pre in ['src','pics','diff','thumb','pdf']:
        os.makedirs(os.path.join(UPLOAD_BASE_PATH,ATTACHMENT,dir_pre),exist_ok=True)

def md5(strings):
    return hashlib.md5(strings.encode(encoding='UTF-8')).hexdigest()

"""
    @param:
        encrypts:strings info
    return:  ByteArr
"""
def qrcode_Bytes(encrypts:str):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4, )
    qr.add_data(encrypts)
    qr.make(fit=True)
    img = qr.make_image()
    imgByteArr = io.BytesIO()
    img.save(imgByteArr, format='PNG')
    imgByteArr = imgByteArr.getvalue()

    return imgByteArr

# win
# return pdf_path
def word_to_pdf(word_path,encrypts):
    pythoncom.CoInitialize()
    word_path = os.path.abspath(word_path)
    word = gencache.EnsureDispatch('Word.Application')
    doc = word.Documents.Open(word_path, ReadOnly=1)

    word_name = os.path.basename(word_path)
    file_name,ext = os.path.splitext(word_name)
    pdfPath = os.path.join(UPLOAD_BASE_PATH,ATTACHMENT,'src','pdf')
    os.makedirs(pdfPath,exist_ok=True)
    pdf_path = os.path.join(pdfPath,file_name+'.pdf')
    doc.ExportAsFixedFormat(pdf_path,
                            constants.wdExportFormatPDF,
                            Item=constants.wdExportDocumentWithMarkup,
                            CreateBookmarks=constants.wdExportCreateHeadingBookmarks)
    pdf_path, thumb_path, page_num = img_insert_pdf(pdf_path,qrcode_Bytes(encrypts))
    # word.Quit(constants.wdDoNotSaveChanges)   # 保存错误
    return pdf_path,thumb_path,page_num

# 加入防伪码
def img_insert_pdf(pdf_path,imgbytes):
    doc = fitz.open(pdf_path)
    rect = fitz.Rect(500, 50, 570, 120)
    page_num = len(doc)
    for page in doc:
        page.insertImage(rect,stream=imgbytes)
        break
    # 保存缩略图
    mat = fitz.Matrix(0.2, 0.2)
    thumbnail_path = os.path.join(UPLOAD_BASE_PATH,'assets','thumb')
    pdf_name = os.path.basename(pdf_path)
    file_name,ext = os.path.splitext(pdf_name)

    thumb_path = os.path.join(thumbnail_path,file_name+'_thumb.png')
    doc[0].getPixmap(matrix=mat).writePNG(thumb_path)
    
    pdf_path,thumb_path = pdf_path.replace('\\','/'),thumb_path.replace('\\','/')
    pdf_path = pdf_path.replace('src/','')

    doc.save(pdf_path)
    doc.close()

    contract_url,thumb_url = pdf_path.replace(UPLOAD_BASE_PATH+'/',''), thumb_path.replace(UPLOAD_BASE_PATH+'/','')
    return contract_url,thumb_url,page_num

def compares(s1):
    remove = string.punctuation + string.whitespace + punctuation
    table = str.maketrans('', '', remove)
    return s1.translate(table)

def get_content_ocr(ocrObject):
    strs = ''
    try:
        for item in ocrObject['words_result']:
            strs +=item['words'] + '\n'
        return strs
    except:
        import traceback
        traceback.print_exc()
        print(ocrObject)
        return ''

# 返回去除标点样式的html
def remove_punctuation(html_content):
    response = html.fromstring(html_content)
    span_lists = response.xpath('//span/text()')
    span_class_lists = response.xpath('//span')
    remove = string.punctuation + string.whitespace + punctuation   # flag
    for span_list, span_class_list in zip(span_lists, span_class_lists):
        if span_list in remove:
            span_class_list.attrib.pop('class')
    return tostring(response, encoding='utf-8').decode('utf-8')

# 排序
def sort_for_up_pdf(src_pdf_path,upload_pic_path):
    doc = fitz.open(src_pdf_path)
    valid_pdf_img = [item.getPixmap() for item in doc]
    doc.close()
    src_pdf_text = [get_content_ocr(CLIENT.basicAccurate(item.getImageData(output='png'))) for item in valid_pdf_img] 
    
    # src_pdf_text = []
    # for item in valid_pdf_img:
    #     src_pdf_text.append(get_content_ocr(CLIENT.basicAccurate(item.getImageData(output='png'))))
    #     time.sleep(0.5)
    
    upload_img = []
    for i in os.listdir(upload_pic_path):
        with open(upload_pic_path+'/'+i,'rb') as f:
            upload_img.append(f.read())
    upload_text = [get_content_ocr(CLIENT.basicAccurate(item)) for item in upload_img]
    # upload_text = []
    # for item in upload_img:
    #     upload_text.append(get_content_ocr(CLIENT.basicAccurate(item)))
    #     time.sleep(0.5)
    


    upload_index_sort = []
    for src_text in src_pdf_text:
        similaritys = []
        for usr_text in upload_text:
            similarity = get_equal_rate(src_text,usr_text)
            similaritys.append(similarity)
        index = [i for (i,item) in enumerate(similaritys) if item==max(similaritys)][0]
        upload_index_sort.append(index)
    # print(upload_index_sort)
    return upload_index_sort

def pics_to_pdf(upload_index_sort,imgdir='./pics'):
    doc = fitz.open()  # PDF with the pictures
    imglist = os.listdir(imgdir)  # list of them

    for i in upload_index_sort:
        f = imglist[i]
        img = fitz.open(os.path.join(imgdir, f))  # open pic as document
        rect = img[0].rect  # pic dimension
        pdfbytes = img.convertToPDF()  # make a PDF stream
        img.close()  # no longer needed
        imgPDF = fitz.open("pdf", pdfbytes)  # open stream as PDF
        page = doc.newPage(width = rect.width,  # new page with ...
                        height = rect.height)  # pic dimension
        page.showPDFpage(rect, imgPDF, 0)  # image fills the page
        # psg.EasyProgressMeter("Import Images",  # show our progress
        #     i+1, imgcount)
    base_path,cname = os.path.split(imgdir)
    up_pdf_path= os.path.join(imgdir,cname+'.pdf').replace('\\','/')
    thumb_path = os.path.join(base_path,cname+'.png').replace('\\','/')
    doc.save(up_pdf_path)

    # 保存缩略图
    mat = fitz.Matrix(0.5, 0.5)
    doc[0].getPixmap(matrix=mat).writePNG(thumb_path)

    doc.close()

    up_pdf_path,thumb_path = up_pdf_path.replace(UPLOAD_BASE_PATH,'attach'),thumb_path.replace(UPLOAD_BASE_PATH,'attach')
    return up_pdf_path,thumb_path

def valid(pdf_path,upload_pics='.'):
    # 使用原合同进行鉴定
    pdf_path = pdf_path.replace('/pdf/','/src/pdf/')

    compare_html_path = os.path.join(UPLOAD_BASE_PATH,'assets','diff')
    # pdf_path = '2020劳动合同范文.pdf.pdf'

    doc = fitz.open(pdf_path)
    valid_pdf_img = [item.getPixmap() for item in doc]
    doc.close()
    # src_pdf_text = [get_content_ocr(CLIENT.basicAccurate(item.getImageData(output='png'))) for item in valid_pdf_img] 
    # 每页原pdf的识别文字
    # src_pdf_text = ['\n'.join([text['words'] for text in CLIENT.basicAccurate(item.getImageData(output='png'))['words_result']]) for item in valid_pdf_img] 
    src_pdf_text = [get_content_ocr(CLIENT.basicAccurate(item.getImageData(output='png'))) for item in valid_pdf_img] 
    # src_pdf_text = []
    # for item in valid_pdf_img:
    #     src_pdf_text.append(get_content_ocr(CLIENT.basicAccurate(item.getImageData(output='png'))))
    #     time.sleep(0.5)

    upload_img = []
    for i in os.listdir(upload_pics):
        if not i.endswith('.pdf'):
            with open(upload_pics+'/'+i,'rb') as f:
                upload_img.append(f.read())
    upload_text = [get_content_ocr(CLIENT.basicAccurate(item)) for item in upload_img]
    # upload_text = []
    # for item in upload_img:
    #     upload_text.append(get_content_ocr(CLIENT.basicAccurate(item)))
    #     time.sleep(0.5)

    # 排序
    upload_text_sort = []
    sort_index = []
    for src_text in src_pdf_text:
        similaritys = []
        for usr_text in upload_text:
            similarity = get_equal_rate(src_text,usr_text)
            similaritys.append(similarity)
        index = [i for (i,item) in enumerate(similaritys) if item==max(similaritys)][0]
        sort_index.append(index)
        upload_text_sort.append(upload_text[index])
    
    print(sort_index)

    compare_sum = 0
    base_name = os.path.basename(upload_pics)
    # compare_html = os.path.join(compare_html_path,base_name+'_diff.html')
    ## w
    compare_tables_txt = os.path.join(compare_html_path,base_name+'_diff.txt')
    compare_tables = ''
    similaritys = []
    # fd_diff = open(compare_html, "w", encoding='utf-8')
    for src_txt,up_txt in zip(src_pdf_text,upload_text_sort):
        src_remove_char, up_remove_char= compares(src_txt), compares(up_txt)
        similarity_remove = get_equal_rate(src_remove_char, up_remove_char)
        #if int(similarity_remove)<1:
        similaritys.append(f'{similarity_remove:.2%}')
        compare_sum +=similarity_remove
        diff = difflib.HtmlDiff()
        # result = diff.make_file(src_txt.split('\n'), up_txt.split('\n'))
        result = diff.make_file(src_txt.split('\n'), up_txt.split('\n'))
        result = remove_punctuation(result)
        try:
            # if similarity_remove < 1:
            compare_tables +=remove_punctuation(diff.make_table(src_txt.split('\n'), up_txt.split('\n')))+r"&#*&"
                # fd_diff.write(result)
            #else:
                #pass
        except Exception as e:
            import traceback
            traceback.print_exc()
    # fd_diff.close()
    
    # print(compare_tables)
    with open(compare_tables_txt,"w", encoding='utf-8') as f:
        f.write(compare_tables)

    similarity_avg =f'{compare_sum/len(src_pdf_text):.2%}'
    # compare_html = compare_html.replace(UPLOAD_BASE_PATH,'attach')
    compare_tables_txt= compare_tables_txt.replace(UPLOAD_BASE_PATH,'attach')
    compare_tables_txt =compare_tables_txt.replace('\\','/')
    return similarity_avg,compare_tables_txt,similaritys

def get_equal_rate(str1, str2):
    return difflib.SequenceMatcher(None, str1, str2).quick_ratio()
