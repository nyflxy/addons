#coding=utf-8
import datetime,pdb
import tornado
from tornado.options import options
from dxb.handler import TokenAPIHandler,APIHandler,ListCreateAPIHandler,\
    RetrieveUpdateDestroyAPIHandler
import libs.utils as utils
import libs.wslib as wslib
import libs.asynclib as asynclib
async_server = asynclib.AsyncUtils(20)
import models

class MobileCheckCode(APIHandler):
    model = models.CheckCode()

    @property
    def executor(self):
        return self.application.executor

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        result = utils.init_response_data()
        checkcode_coll = self.model.get_coll()
        try:
            mobile = self.get_argument("mobile")
            yield async_server.cmd(self.model.check_mobile, mobile)
            yield self.executor.submit(self.model.check_limit, (mobile))
            random_code = utils.get_random_num(6, mode="number")
            yield async_server.cmd(self.model.send_kaixintong_sms, mobile, random_code)
            yield self.model.save(mobile,random_code,result)
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
            if phone == "":
                raise Exception("请输入手机号！")
            elif phone_code == "":
                raise Exception("请输入验证码！")
            utils.check_code(checkcode_coll, phone, phone_code)
        except Exception, e:
            result = utils.reset_response_data(0, str(e))
        self.finish(result)

handlers = [
    (r"/api/checkcode/mobile", MobileCheckCode),
    (r"/api/mobile/check", MobileCheckCode),
]