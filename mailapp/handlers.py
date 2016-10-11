#coding=utf-8

import json,pdb,datetime,os
import tornado,urllib
from tornado.options import options
from tornado.template import Template
from dxb.handler import TokenAPIHandler,APIHandler,ListCreateAPIHandler,\
    RetrieveUpdateDestroyAPIHandler
import libs.utils as utils
import libs.modellib as model
import models
from mail import send_email
from asynclib import AsyncUtils
async_server = AsyncUtils(20)
import reportlib

class MailListCreateHandler(ListCreateAPIHandler):
    model = models.MailModel()

class MailRetrieveUpdateDestroyHandler(RetrieveUpdateDestroyAPIHandler):
    model = models.MailModel()

class MailSendHandler(APIHandler):
    model = models.MailModel()

    def post(self):
        result = utils.init_response_data()
        try:
            to_mail_list = json.loads(self.get_argument("to_mail_list","[]"))
            theme = self.get_argument("theme","工作日报")
            template = self.get_argument("template","default")
            template_args = json.loads(self.get_argument("template_args","{}"))
            content = self.generate(template,template_args)
            attachments = []
            request_files = self.request.files
            if request_files.has_key("files"):
                files = request_files["files"]
                for file in files:
                    filename = file.get("filename","")
                    temp_filename_path = os.path.dirname(options.root_path).encode("utf-8") + u"/var/mail/" + filename + u"_" +\
                                         str(datetime.datetime.now()).replace(".","_").replace(":","_").replace(" ","_") + ".xls"
                    temp_mail_file = open(temp_filename_path,"w")
                    temp_mail_file.write(file.get("body",""))
                    attachments.append(dict(
                        filename = u"工作日报.xls",
                        data = temp_filename_path,
                    ))
            print attachments
            send_email('nj.niyoufa@dhjt.com', to_mail_list , theme, '',
                       html=content,
                       attachments=attachments)

        except Exception, e:
            result = utils.reset_response_data(0, str(e))
            self.write(result)
            self.finish()
            return
        self.finish(result)

    def generate(self,template,template_args):
        content = ""
        return content

class WorkMailSendHandler(APIHandler):
    model = models.MailModel()

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        try:
            result = utils.init_response_data()
            client = tornado.httpclient.AsyncHTTPClient()
            response = yield tornado.gen.Task(client.fetch,"http://120.26.226.63:20000/works")
            response_body = json.loads(response.body)
            data = response_body.get("data",{})
            works = data.get("works",[])

            t_s = open(os.path.dirname(options.root_path) + "/var/mail/工作日报.xls","r")
            t_s_data = t_s.read()
            t_s.close()
            to_email = ["1061794187@qq.com"]
            for work in works:
                filename = os.path.dirname(options.root_path) + "/var/mail/工作日报%s.xls"%( str(datetime.datetime.now()).\
                                                                             replace(".","_").replace(":","_").replace(" ","_") )
                w_d = open(filename,"w")
                w_d.write(t_s_data)
                w_d.close()

                copy_data = [
                    (4, 1, work.get("name", "")),
                    (4, 2, work.get("hr_analytic_timesheet_id")[1]),
                ]
                curr_time = datetime.datetime.now()
                title = "东汇集团胜众科技有限公司征信项目组%s%s年%s月%s日工作日报"%(work.get("user_id")[1],
                                                            curr_time.year,curr_time.month,curr_time.day)
                reportlib.copy_xls(filename,title,data=copy_data)
                attachments = []
                attachments.append(dict(
                    filename=u"工作日报.xls",
                    data=filename,
                ))
                from_email = "nj.niyoufa@dhjt.com"
                send_email(from_email, to_email, "工作日报", '',
                           html='',
                           attachments=attachments)

                result["data"] = works
        except Exception, e:
            result = utils.reset_response_data(0, str(e))
            self.write(result)
            self.finish()
            return

        self.finish(result)

class WorkHandler(APIHandler):
    model = models.MailModel()

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        try:
            result = utils.init_response_data()
            client = tornado.httpclient.AsyncHTTPClient()
            response = yield tornado.gen.Task(client.fetch, "http://120.26.226.63:20000/works")
            response_body = json.loads(response.body)
            data = response_body.get("data", {})
            works = data.get("works", [])
            curr_time = str(datetime.datetime.now()).split(" ")[0]
            start_time = curr_time + " " + "00:00:00.000"
            end_time = curr_time + " " + "23:59:59.999"
            result["data"] = []
            for work in works:
                username = work.get("user_id")[1]
                obj = self.model.coll.find_one({
                    "name":username,
                    "add_time":{
                        "$gte": start_time,
                        "$lte": end_time,
                    },
                })
                if obj:
                    continue
                else:
                    obj = {}
                    obj["name"] = username
                    obj["work"] = work.get("name", "")
                    obj["work_desc"] = work.get("hr_analytic_timesheet_id")[1]
                    self.model.create(**obj)
                    result["data"].append(obj)

        except Exception, e:
            result = utils.reset_response_data(0, str(e))
            self.write(result)
            self.finish()
            return

        self.finish(result)


handlers = [
    (r"/api/mail/list", MailListCreateHandler),
    (r"/api/mail", MailRetrieveUpdateDestroyHandler),
    (r"/api/mailsend", MailSendHandler),
    (r"/api/workmailsend", WorkMailSendHandler),
    (r"/api/work", WorkHandler),
]