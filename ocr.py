# encoding:utf-8

import requests
import base64


def ocr(path):

    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
    # 二进制方式打开图片文件
    f = open(path, 'rb')
    img = base64.b64encode(f.read())

    params = {"image":img}
    access_token = '[24.a759b6f5779a442a934c4121dfa05f2e.2592000.1613054170.282335-23532324]'
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    if response:
        return (response.json())
    else:
        raise ValueError("cannot get json")
    
    
