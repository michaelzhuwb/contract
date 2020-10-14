import os
from os import path

if __name__ == "__main__":
    abs_cur_path = os.path.abspath(os.path.curdir)
    nginx_conf = path.join(abs_cur_path,'nginx','conf')
    strs = ''
    with open(path.join(nginx_conf,'nginx.conf'),'r',encoding='utf8') as f:
        txt = f.read()
        strs = txt.replace('html_abs_path',path.join(abs_cur_path,'contract','html','src','contract_p').replace('\\','/'))
        strs = txt.replace('contract_file_abs_path;',path.join(abs_cur_path,'contract').replace('\\','/'))
    with open(path.join(nginx_conf,'nginx.conf'),'w',encoding='utf8') as f:
        f.write(strs)

    