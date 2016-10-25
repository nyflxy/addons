#coding=utf-8

import sys, urllib, urllib2, json,pdb, datetime
import tornado

import libs.modellib as model
import libs.utils as utils
import libs.xmllib as xmllib

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

    def send_kaixintong_sms(self,mobile,code):
        url = "http://101.201.41.194:9999/sms.aspx"
        content = u"【尚得公益】你的验证码是%s，有效时间30分钟，请不要告诉他人"%code
        data = {
            "userid":"",
            "account":"",
            "password":"",
            "mobile":mobile,
            "content":content,
            "action":"send",
        }
        data = urllib.urlencode(data)
        opener = urllib2.build_opener()
        xml_res = opener.open(url, data).read()
        res = xmllib.Xml2Json(xml_res).result
        # if res.get("returnsms", {}).get("returnstatus") != 'Success' \
        #         and res.get("returnsms", {}).get("message") != 'ok':
        #     raise Exception('短信发送失败,请联系开发人员\n错误信息：%s' % res)

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

    def check_limit(self,mobile):
        curr_time = datetime.datetime.now()
        if self.coll.find({"mobile": mobile, "enable_flag": True}).count() > 0:
            # 验证码请求限制 每小时限制5条
            if self.coll.find({"mobile": mobile,
                                    "add_time": {
                                        "$gte": curr_time - datetime.timedelta(hours=1),
                                        "$lte": curr_time + datetime.timedelta(hours=1),
                                    }
                                    }).count() >= 5:
                raise Exception("验证码请求限制，每小时限制5条！")

            # 将之前未使用的验证码设置为过期
            cr = self.coll.find({"mobile": mobile, "enable_flag": True})
            for checkcode in cr:
                checkcode["enable_flag"] = False
                self.coll.save(checkcode)

    @tornado.gen.coroutine
    def save(self,mobile,random_code,result):
        future = tornado.concurrent.Future()
        def callback(mobile,random_code):
            curr_time = datetime.datetime.now()
            res = self.coll.insert_one({
                "mobile": mobile,
                "enable_flag": True,
                "add_time": curr_time,
                "type": "mobile",
                "code": random_code,
            })
            future.set_result(res)

        tornado.ioloop.IOLoop.instance().add_callback(callback, mobile, random_code)
        result["insert"] = yield future
        result["insert"] = utils.dump(result["insert"])

