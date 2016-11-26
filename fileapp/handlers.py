# -*- coding: utf-8 -*-
#
# @author: Daemon Wang
# Created on 2016-07-14
#
import json
import pdb
import os
import shutil
import tornado.web
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import time

from dxb.handler import APIHandler,ListAPIHandler
import dxb.libs.utils as utils
import models
from pinyin import PinYin
pinyin_obj = PinYin()
pinyin_obj.load_word()

options = utils.options

class FileUploadHandler(APIHandler):
    model = models.FileModel()

    #上传文件接口
    def post(self):
        result = utils.init_response_data()
        try:
            file_type = self.get_argument("file_type",'normal')
            file = self.request.files['file']
            self.model.upload(file,file_type)
        except StandardError,e:
            result = utils.reset_response_data(0,str(e))

        self.finish(result)

class FileDownloadHandler(APIHandler):
    model = models.FileModel()

    #文件下载
    def get(self):
        options = utils.options
        try:
            file_query = {}
            file_query['file_name'] = self.get_argument("file_name",'')
            file_query['file_path'] = self.get_argument("file_path",'')
            file_query['enable_flag'] = 1

            res = self.model.get_coll().find_one(file_query)
            if res is None:
                raise ValueError(u"文件不存在或已被删除")

            self.model.download(file_query)
            url = options.project_root_path + res['file_path']

            filename = os.path.split(url)[1]
            self.set_header ('Content-Type', 'application/octet-stream')
            self.set_header ('Content-Disposition', 'attachment; filename='+filename)
            with open(url, 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    self.write(data)
            self.finish()
        except StandardError,e:
            self.write("<html><head><meta charse='UTF-8'></head>")
            self.write(str(e))
            self.write("</html>")

class FileListHandler(ListAPIHandler):
    model = models.FileModel()

class FileDownloadListHandler(ListAPIHandler):
    model = models.FileDownloadModel()

class SingleDocumentParseHandler(APIHandler):

    def post(self):
        result = utils.init_response_data()
        try:
            filename = self.get_argument("filename")
            download_format = self.get_argument("download_format","md")
            contents = self.request.files['file']
            for content in contents[0:1]:
                print content.keys()
                content_body = content.get("body","")
                content_body = content_body.replace("${","```js").replace("}$","```").replace("<<<","```js").replace(">>>","```")
                filename_words = pinyin_obj.hanzi2pinyin(string=filename)
                filename_pinyin = "_".join(filename_words)
                url = "/tmp/" + filename_pinyin + "." +download_format
                with open(url, 'wb') as f:
                        f.write(content_body)
                paras = content_body.split("#")
                result["data"].update(dict(
                    filename=filename,
                    paras=paras,
                ))
        except StandardError,e:
            result = utils.reset_response_data(0,str(e))

        self.finish(result)

class SingleDocumentDownloadHandler(tornado.web.RequestHandler):

    def get(self):
        result = utils.init_response_data()
        try:
            filename = self.get_argument("filename")
            download_format = self.get_argument("download_format","md")
            filename_words = pinyin_obj.hanzi2pinyin(string=filename)
            filename_pinyin = "_".join(filename_words)
            url = "/tmp/" + filename_pinyin + "." + download_format
            self.set_header ('Content-Type', 'application/octet-stream')
            self.set_header ('Content-Disposition', 'attachment; filename='+filename_pinyin + "." + download_format)
            with open(url, 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    self.write(data)
        except StandardError,e:
            result = utils.reset_response_data(0,str(e))
            self.finish(result)

        self.finish()

class APIDocumentParseHanlder(APIHandler):
    def post(self):
        result = utils.init_response_data()
        try:
            contents = self.request.files['file']
            _folder_names = self.get_argument("folder_names","[]")
            folder_names = json.loads(_folder_names)
            if not type(folder_names) ==  list:
                raise Exception("params folder_names error!")
            elif len(folder_names) == 0:
                self.folder_names_flag = True
            else:
                self.folder_names_flag = False
            # path = self.get_argument("path", "/tmp/")
            path = "/home/nyf/develop/python_api_document/"
            for content in contents[0:1]:
                # ['body', 'content_type', 'filename']
                body = content.get("body","{}")
                body = json.loads(body)

                if len(body) != 0:
                    body_name = body.get("name","")
                    body_description = body.get("description","")

                    requests = body.get("requests",[])
                    requests_dict = {}
                    for request in requests:
                        id = request.get("id")
                        requests_dict[id] = dict(
                            url = request.get("url",""),
                            method = request.get("method",""),
                            name = request.get("name",""),
                            description = request.get("description",""),
                        )

                    folders = body.get("folders", [])
                    temp_folders = []
                    for folder in folders:
                        name = folder.get("name")
                        description = folder.get("description","")
                        order = folder.get("order",[])

                        temp_requests = []
                        for id in order:
                            request = requests_dict.get(id)
                            temp_requests.append(request)
                        if name in folder_names or self.folder_names_flag:
                            temp_folders.append(dict(
                                name = name,
                                description = description,
                                requests = temp_requests
                            ))

                self.summary = ""
                self.summary_index = 1
                self.parse_folders(path, body_name, body_description, temp_folders)
                with open(path + "SUMMARY.md","wb") as f:
                    f.write(self.summary)
                result["data"] = dict(
                    path = path,
                    body_name = body_name,
                    body_description = body_description,
                    folders = temp_folders,
                    summery = self.summary
                )

        except StandardError,e:
            result = utils.reset_response_data(0,str(e))

        self.finish(result)

    def parse_folders(self, folders_path, folders_name, folders_description, folders):
        if not os.path.isdir(folders_path):
            os.mkdir(folders_path)
        folders_name_words = pinyin_obj.hanzi2pinyin(string=folders_name)
        folders_name_pinyin = "_".join(folders_name_words)
        path = folders_path + folders_name_pinyin
        if os.path.isdir(path):
            shutil.rmtree(path)
            os.mkdir(path)
        else:
            os.mkdir(path)
        path_file = path + "/" + folders_name_pinyin + ".md"
        self.summary += "* [%s](%s/%s.md)\n"%(folders_name, folders_name_pinyin, folders_name_pinyin)
        with open(path_file, "wb") as f:
            f.write("#" + folders_name + "\n" + "#" + folders_description + "\n\n")

        parent_path = folders_name_pinyin + "/"
        for folder in folders:
            folder_name = folder.get("name", "")
            folder_description = folder.get("folder_description", "")
            requests = folder.get("requests", [])
            self.parse_folder(path, folder_name, folder_description, requests, parent_path)

    def parse_folder(self, path, folder_name, folder_description, requests, parent_path):
        folder_name_words = pinyin_obj.hanzi2pinyin(string=folder_name)
        folder_name_pinyin = "_".join(folder_name_words)
        folder_path = path + "/" + folder_name_pinyin
        if not os.path.isdir(folder_path):
            os.mkdir(folder_path)
        folder_path_file = folder_path + "/" + folder_name_pinyin + ".md"
        self.summary += "* [%s %s](%s/%s.md)\n" %(self.summary_index, folder_name, parent_path + folder_name_pinyin, folder_name_pinyin)
        self.summary_index += 1
        with open(folder_path_file, "wb") as f:
            f.write("#" + folder_name + "\n" + "#" + folder_description + "\n\n")

        for request in requests:
            request_name = request.get("name", "")
            request_name_words = pinyin_obj.hanzi2pinyin(string=request_name)
            request_name_pinyin = "_".join(request_name_words)
            request_method = request.get("method","")
            request_url = request.get("url","")
            request_description = request.get("description","")
            request_file_path = folder_path + "/" + request_name_pinyin + ".md"
            self.summary += "* [%s](%s/%s.md)\n" % (request_name, parent_path + folder_name_pinyin, request_name_pinyin)
            request_description = self.parse_single_document(request_name, request_description)
            with open(request_file_path, "wb") as f:
                f.write("#接口名：%s\n地址：%s\n方法类型：%s\n%s"%(request_name, request_url.split("?")[0], request_method, request_description))

    def parse_single_document(self, filename, content, download_format="md"):
        filename_words = pinyin_obj.hanzi2pinyin(string=filename)
        filename_pinyin = "_".join(filename_words)
        content_bocontentdy = content.replace("${", "```js").replace("}$", "```").replace("<<<", "```js").replace(
            ">>>", "```")
        return content_bocontentdy

handlers = [
            (r'/api/file/upload',FileUploadHandler),
            (r'/api/file/download', FileDownloadHandler),
            (r'/api/file/list', FileListHandler),
            (r'/api/download/list', FileDownloadListHandler),
            (r'/api/tool/single_document/parse',SingleDocumentParseHandler),
            (r'/api/tool/single_document/download',SingleDocumentDownloadHandler),
            (r'/api/tool/apidocument/parse', APIDocumentParseHanlder),
        ]
