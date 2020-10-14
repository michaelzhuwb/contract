import fitz
import os,io
from aip import AipOcr
import difflib
import glob
import string
from zhon.hanzi import punctuation

def ocr_pdf():
    # file_path = '2020劳动合同范文.pdf.pdf'
    file_path = 'all-my-pics.pdf'

    doc = fitz.open(file_path)

    with open('src.text',mode='w',encoding='utf8') as f:
        for page in doc:
            x = page.getText()
            f.write(x)
            print(x)

def pics_to_pdf(imgdir='./pics'):
    doc = fitz.open()  # PDF with the pictures
    imglist = os.listdir(imgdir)  # list of them
    imgcount = len(imglist)  # pic count

    for i, f in enumerate(imglist):
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
    print(len(doc))

    # 保存缩略图
    mat = fitz.Matrix(0.5, 0.5)
    doc[0].getPixmap(matrix=mat).writePNG(thumb_path)

    doc.close()

    return up_pdf_path,thumb_path
def get_equal_rate(str1, str2):
    return difflib.SequenceMatcher(None, str1, str2).quick_ratio()



def compares(s1):
    remove = string.punctuation + string.whitespace + punctuation
    table = str.maketrans('', '', remove)
    return s1.translate(table)

def valid(upload_pics='.'):
    def get_content_ocr(ocrObject):
        strs = ''
        try:
            for item in ocrObject['words_result']:
                strs +=item['words'] + '\n'
            return strs
        except:
            return ''
    pdf_path = '2020劳动合同范文.pdf.pdf'
    doc = fitz.open(pdf_path)
    # x = doc[0].getImageList()
    x = doc[0].getPixmap()
    valid_pdf_img = [item.getPixmap() for item in doc]
    doc.close()
    # src_pdf_text = [get_content_ocr(client.basicAccurate(item.getImageData(output='png'))) for item in valid_pdf_img] 
    # 每页原pdf的识别文字
    # src_pdf_text = ['\n'.join([text['words'] for text in client.basicAccurate(item.getImageData(output='png'))['words_result']]) for item in valid_pdf_img] 
    src_pdf_text = [get_content_ocr(client.basicAccurate(item.getImageData(output='png'))) for item in valid_pdf_img] 
    
    upload_img = []
    for i in os.listdir('./pics'):
        with open('pics/'+i,'rb') as f:
            upload_img.append(f.read())
    upload_text = [get_content_ocr(client.basicAccurate(item)) for item in upload_img]


    # 排序
    upload_text_sort = []
    for src_text in src_pdf_text:
        similaritys = []
        for usr_text in upload_text:
            similarity = get_equal_rate(src_text,usr_text)
            similaritys.append(similarity)
        index = [i for (i,item) in enumerate(similaritys) if item==max(similaritys)][0]
        upload_text_sort.append(upload_text[index])

    compare_html = os.path.join('.', 'diff.html')


    compare_sum = 0
    print(len(src_pdf_text))
    # src_pdf_text, upload_text_sort = src_pdf_text[0].split('\n'),upload_text_sort[0].split('\n')
    for src_txt,up_txt in zip(src_pdf_text,upload_text_sort):
        print('#'*35)
        print('src_txt:',src_txt)
        src_remove_char, up_remove_char= compares(src_txt), compares(up_txt)
        similarity_remove = get_equal_rate(src_remove_char, up_remove_char)
        compare_sum +=similarity_remove
        diff = difflib.HtmlDiff()
        result = diff.make_file(src_txt.split('\n'), up_txt.split('\n'))
        try:
            if similarity_remove < 1:
                fd_diff = open(os.path.join('.', 'diff.html'), "a", encoding='utf-8')
                fd_diff.write(result)
                fd_diff.close()
            else:
                pass
        except Exception as e:
            import traceback
            traceback.print_exc()
    # res =  client.basicAccurate(upload_img[1])
    # print(upload_text)

    # print(data)
    
    # print(doc.extractImage(3))

    # img_byte = io.BytesIO()
    # x[1].writePNG(img_byte)
    # print(res)
    # doc.save("all-my-pics.pdf")
if __name__ == "__main__":
    pics_to_pdf()
    # ocr_pdf()
    """百度ocr接口信息"""
    APP_ID = '22823124'  # 'App ID'
    API_KEY = 'FQDaVPxo5NaF8w2e0lEtlvO0'  # 'Api Key'
    SECRET_KEY = '1k2Rqrl4LFAced97QGpZLgUee5oreRHu'  # 'Secret Key'
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    # valid()
