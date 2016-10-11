#coding=utf-8

import sys, urllib, urllib2, json,pdb

import libs.modellib as model
import libs.utils as utils

class CheckCode(model.BaseModel,model.Singleton):
    __name = "dxb.checkcode"

    def __init__(self):
        model.BaseModel.__init__(self,CheckCode.__name)

    def send_106sms(self,mobile,code):
        url = 'http://apis.baidu.com/kingtto_media/106sms/106sms?mobile=%s&tag=2&content=【丁蜀镇】你的验证码是%s，有效时间30分钟，请不要告诉他人'%(mobile,code)
        req = urllib2.Request(url)

        req.add_header("apikey", "")
        resp = urllib2.urlopen(req)
        content = resp.read()
        if (content):
            print(content)
        return json.loads(content)

    def check_mobile(self,mobile):
        phoneprefix = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139', '150', '151', '152', '153',
                       '156', '158', '159', '170', '183', '182', '185', '186', '188', '189']
        if len(mobile) != 11:
            raise Exception("手机号必须是11位数字！")
        else:
            if mobile.isdigit():# 检测输入的号码是否全部是数字。
                if mobile[:3] not in phoneprefix:# 检测前缀是否是正确。
                    raise Exception("手机号无效！")
            else:
                raise Exception("手机号必须是数字！")

