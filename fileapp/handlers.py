# -*- coding: utf-8 -*-
#
# @author: Daemon Wang
# Created on 2016-07-14
#
import json
import pdb
import os
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
                content_body = content_body.replace("${","```js").replace("}$","```")
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

handlers = [
            (r'/api/file/upload',FileUploadHandler),
            (r'/api/file/download', FileDownloadHandler),
            (r'/api/file/list', FileListHandler),
            (r'/api/download/list', FileDownloadListHandler),
            (r'/api/tool/single_document/parse',SingleDocumentParseHandler),
            (r'/api/tool/single_document/download',SingleDocumentDownloadHandler),
        ]
