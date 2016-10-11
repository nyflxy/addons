#coding=utf-8
import datetime,pdb
from tornado.options import options
from dxb.handler import TokenAPIHandler,APIHandler,ListCreateAPIHandler,\
    RetrieveUpdateDestroyAPIHandler
import libs.utils as utils
import libs.wslib as wslib
import models

class MobileCheckCode(APIHandler):
    model = models.CheckCode()

    def get(self):
        result = utils.init_response_data()
        checkcode_coll = self.model.get_coll()
        try:
            mobile = self.get_argument("mobile")
            self.model.check_mobile(mobile)
            curr_time = datetime.datetime.now()
            if checkcode_coll.find({"mobile":mobile,"enable_flag":True}).count() > 0:
                # 验证码请求限制 每小时限制5条
                if checkcode_coll.find({"mobile":mobile,
                        "add_time":{
                            "$gte":curr_time - datetime.timedelta(hours=1),
                            "$lte":curr_time + datetime.timedelta(hours=1),
                        }
                    }).count() >= 5:
                    raise Exception("验证码请求限制，每小时限制5条！")

                cr = checkcode_coll.find({"mobile":mobile,"enable_flag":True})
                for checkcode in cr:
                    checkcode["enable_flag"] = False
                    checkcode_coll.save(checkcode)
            else:
                pass
            random_code = utils.get_random_num(6,mode="number")

            checkcode_coll.insert_one({
                "mobile":mobile,
                "enable_flag":True,
                "add_time":curr_time,
                "type":"mobile",
                "code":random_code,
            })
            # res = wslib.send_msg(mobile,"尊敬的用户您好，您本次的验证码为%s,30分钟内有效"%random_code)
            # if res != "0" :
            #     raise ValueError("错误代码：%s"%res)

            # res = self.model.send_106sms(mobile, random_code)
            # if res.get("message","") != "ok":
            #     raise Exception('短信发送失败,请联系开发人员\n错误信息：%s'%res)
            result["data"]["code"] = random_code
        except Exception, e:
            result = utils.reset_response_data(0, str(e))

        self.finish(result)

    def post(self):
        result = utils.init_response_data()
        checkcode_coll = self.model.get_coll()
        try:
            phone = self.get_argument("phone","")
            phone_code = self.get_argument("phone_code","")
            if phone != "":
                utils.check_code(checkcode_coll, phone, phone_code)
        except Exception, e:
            result = utils.reset_response_data(0, str(e))
        self.finish(result)

handlers = [
    (r"/api/checkcode/mobile", MobileCheckCode),
    (r"/api/mobile/check", MobileCheckCode),
]