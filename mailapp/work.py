#coding=utf-8
import sys,platform,os,pdb
import json,datetime,pymongo
import tornado
from mail import send_email
from asynclib import AsyncUtils
async_server = AsyncUtils(20)
import reportlib
import curl

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding('utf-8')

root_path = "/home/dhui100/develop/tornado_base_server"

class WorkReport(object):

    @classmethod
    def send_work_email(cls):
        host = "localhost"
        port = 27017
        db_client = pymongo.MongoClient(host, port)
        db = db_client["dxb"]
        coll = db.mail
        get_params = {"url":"http://120.26.226.63:20000/works"}
        response = curl.CURL.get(**get_params)
        data = response.get("data", {})
        works = data.get("works", [])
        curr_time = str(datetime.datetime.now()).split(" ")[0]
        start_time = curr_time + " " + "00:00:00.000"
        end_time = curr_time + " " + "23:59:59.999"
        for work in works:
            username = work.get("user_id")[1]
            obj = coll.find_one({
                "name": username,
                "add_time": {
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
                obj["add_time"] = str(datetime.datetime.now())
                coll.insert_one(obj)
                print obj
                cls.send_email_func(work)

    @classmethod
    def send_email_func(cls,work):
        t_s = open(root_path + "/var/mail/工作日报.xls", "r")
        t_s_data = t_s.read()
        t_s.close()
        to_email = ["1061794187@qq.com"]

        filename =root_path +"/var/mail/工作日报%s.xls" % (str(datetime.datetime.now()).replace(".", "_").replace(":","_").replace(" ", "_"))

        w_d = open(filename, "w")
        w_d.write(t_s_data)
        w_d.close()

        copy_data = [
            (4, 1, work.get("name", "")),
            (4, 2, work.get("hr_analytic_timesheet_id")[1]),
        ]
        username = work.get("user_id")[1]
        curr_time = datetime.datetime.now()
        title = "东汇集团胜众科技有限公司征信项目组%s%s年%s月%s日工作日报" % (username,
                                                      curr_time.year, curr_time.month, curr_time.day)
        reportlib.copy_xls(filename, title, data=copy_data)
        attachments = []
        attachments.append(dict(
            filename=u"%s工作日报.xls"%username,
            data=filename,
        ))
        from_email = "nj.niyoufa@dhjt.com"
        send_email(from_email, to_email, u"%s工作日报"%username, '',
                   html='',
                   attachments=attachments)

if __name__ == "__main__":
    WorkReport.send_work_email()

