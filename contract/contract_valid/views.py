from django.shortcuts import render
from django.http import HttpResponse
import json
import os
from os import path
# from .share import 
from .share import dir_init,baseconfig,UPLOAD_BASE_PATH,md5,DB,qrcode_Bytes,word_to_pdf,img_insert_pdf,valid,pics_to_pdf,sort_for_up_pdf
from .tools import connectSqlite
import time,sys
# cbv
# Create your views here.
sys.path.append('.')


dir_init()

def login(request):
    result = """{
                "data":{"isAssgin":%s,"msg":"%s","username":"%s"}
                }"""
    isAssgin = 1
    msg = '用户名/密码错误'
    username = ""

    if request.method == 'POST':
        login_name = request.POST.get('user')
        pwd = request.POST.get('password')
        data = DB.fetchall_table("select user_name from user \
                            where login_name='%s'"%(login_name))
        if data:
            isAssgin = 0
            msg = '验证成功'
            username = list(data)[0][0]
        else:
            isAssgin = 1
    result = result%(isAssgin,msg,username)           
    print(result)
    return HttpResponse(json.dumps(result),content_type="application/json")

def upload(request):

    state = 1
    msg = '上传失败'

    if request.method == 'POST':
        info_data = json.loads(request.POST.get('info_data'))
        print(info_data)
        for index in range(len(info_data)):
            print(request.FILES)
            _file = request.FILES.get('file'+str(index))
            title = str(_file.name)
            md5_id = md5(title)
            data = info_data[md5_id]
            upload_name, upload_date, company_name, contract_name =  data['upload_name'],data['upload_date'],data['company_name'],data['contract_name']
            mkdir_path = path.join(UPLOAD_BASE_PATH,'assets')
            os.makedirs(mkdir_path,exist_ok=True)
            file_save_base_path = path.join(mkdir_path,'src')
            os.makedirs(file_save_base_path,exist_ok=True)
            file_save_path = path.join(file_save_base_path,title)
            if path.exists(file_save_path):
                file_save_path = path.join(file_save_base_path,str(int(time.time()))+'_'+title)
            with open(file_save_path,mode='wb+') as destination:
                try: 
                    for chunk in _file.chunks():      # 分块写入文件  
                        destination.write(chunk)
                except:
                    import traceback
                    traceback.print_exc()
            encrypts = md5(str(int(time.time()))+contract_name)
            contract_url, thumb_url, page_num= word_to_pdf(file_save_path,encrypts)
            
            sql = """INSERT INTO contract_info ('upload_name','upload_date','company_name','contract_name','uuid','contract_pdf_url','contract_thumb_url','contract_page_num') values ('%s','%s','%s','%s','%s','%s','%s','%s')"""%(upload_name,upload_date,company_name,contract_name,encrypts,contract_url,thumb_url,page_num)
            print(sql)
            is_ok = DB.insert_update_table(sql)
            if is_ok:
                state = 0
                msg = '上传成功'
            else:
                state = 1
                msg = '失败'
                break

    result  = """
                {"data":"{"info":%s}","success":%s}
            """%(msg,state)
    print(result)
    return HttpResponse(json.dumps(result),content_type="application/json")
            
def get_info(request):
    # print(baseconfig)
    print(UPLOAD_BASE_PATH)
    
    search_info = ''
    like_search = "contract_name like '%%%s%%' or upload_name like '%%%s%%' or \
                    company_name like '%%%s%%' or upload_date like '%%%s%%'"%(search_info,search_info,search_info,search_info)
    sql = """select company_name,'<a class="'||uuid||'" href="attach/'||contract_pdf_url||'" style="color:red" target="_blank">'||contract_name||'</a>',upload_name,upload_date,'<button style="border-radius:25px" class="btn btn-primary valid"  cno="'||uuid||'" contract_thumb_url="attach/'||contract_thumb_url||'" page_num="'||contract_page_num||'">鉴伪</button>' from contract_info
            where %s 
        """%like_search
    # print(DB.fetchall_table(sql))
    
    data = DB.fetchall_table(sql)
    if not data:
        data = []
    # print(json.dumps(data))
    result = """{"data":{"info":%s},"success":0}"""%json.dumps(data)
    return HttpResponse(result,content_type="application/json")

def pre_upload(request):
    if request.method == 'POST':
        cno = request.POST.get('cno')
        sql = """select contract_pdf_url,contract_name from contract_info where uuid='%s'
            """%(cno)
        data = DB.fetchall_table(sql)
        cname = list(data)[0][1]

        upload_pic_base_path = path.join(UPLOAD_BASE_PATH,'assets','pics',cname)
        os.makedirs(upload_pic_base_path,exist_ok=True)
        for index in range(len(request.FILES)):
            _file = request.FILES.get('file'+str(index))
            title = str(_file.name)
            file_name,ext = os.path.splitext(title)
            with open(path.join(upload_pic_base_path,title),mode='wb+') as destination:
                try: 
                    for chunk in _file.chunks():      # 分块写入文件  
                        destination.write(chunk)
                except:
                    import traceback
                    traceback.print_exc()
        src_pdf_path = os.path.join(UPLOAD_BASE_PATH,list(data)[0][0])
        print(UPLOAD_BASE_PATH,list(data)[0][0])
        upload_index_sort = sort_for_up_pdf(src_pdf_path,upload_pic_base_path)
        up_pdf_path,thumb_path = pics_to_pdf(upload_index_sort,upload_pic_base_path)

        result = """
                    {"data":{"up_pdf_url":"%s","thumb_url":"%s"},"success":0}
                """%(up_pdf_path,thumb_path)
        # print(result)
        return HttpResponse(result)

# 1.1 
def valid_contract_info(request):
        cno = request.POST.get('cno')

        sql = """select contract_pdf_url,contract_name from contract_info where uuid='%s'
            """%(cno)

        data = DB.fetchall_table(sql)
        ##  data None exception
        cname = list(data)[0][1]
        pdf_path = list(data)[0][0]
        
        pdf_path = os.path.join(UPLOAD_BASE_PATH,pdf_path).replace('\\','/')
        upload_pic_base_path = path.join(UPLOAD_BASE_PATH,'assets','pics',cname)
        similarity_avg ,compare_tables_txt,similaritys= valid(pdf_path,upload_pic_base_path)
        
        ## 鉴伪结果

        ##
        
        result = """
                    {"data":{"similarity":"%s","compare_tables_url":"%s","similaritys":%s},"success":0}
                """%(similarity_avg,compare_tables_txt,json.dumps(similaritys))
        print(result)
        return HttpResponse(result)

# 1.0
def valid_contract(request):
    if request.method == 'POST':
        print(len(request.FILES))
        cno = request.POST.get('cno')

        sql = """select contract_url,contract_name from contract where uuid='%s'
            """%(cno)

        data = DB.fetchall_table(sql)
        cname = list(data)[0][1]
        url_path = list(data)[0][0]

        upload_pic_base_path = path.join(UPLOAD_BASE_PATH,'assets','pics',cname)
        os.makedirs(upload_pic_base_path,exist_ok=True)
        for index in range(len(request.FILES)):
            _file = request.FILES.get('file'+str(index))
            title = str(_file.name)
            file_name,ext = os.path.splitext(title)
            with open(path.join(upload_pic_base_path,title),mode='wb+') as destination:
                try: 
                    for chunk in _file.chunks():      # 分块写入文件  
                        destination.write(chunk)
                except:
                    import traceback
                    traceback.print_exc()
        pdf_url = url_path.replace('assets',UPLOAD_BASE_PATH+'/assets').replace('//','/')
        diff_html_url,similarity_avg,compare_tables_txt = valid(pdf_url,upload_pic_base_path)
        diff_html_url = diff_html_url.replace('\\','/')
        result = """
                    {"data":{"diff_url":"%s"},"success":0}
                """%diff_html_url
        print(result)
        return HttpResponse(result)