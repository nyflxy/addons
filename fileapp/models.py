#coding=utf-8

import libs.modellib as model
import libs.utils as utils

# -*- coding: utf-8 -*-

"""
    alter by: daemon wnag
    alter on 2016-07-14
"""
import os,time
from bson.son import SON
import dxb.consts as consts
import dxb.libs.utils as utils
import sys
import datetime
import pdb
import dxb.libs.pdf_splite as pdf_splite

reload(sys)
sys.setdefaultencoding('utf-8')

options = utils.options

class FileModel(model.BaseModel,model.Singleton):
    __name = "dxb.file"

    def __init__(self):
        model.BaseModel.__init__(self,FileModel.__name)

    def create(self,**kwargs):
        params = ['credit_number','file_name','file_type','file_path','file_sort']
        file_save = dict([(k,v) for (k,v) in kwargs.items() for p in params if k == p])
        file_save['add_time'] = utils.get_now()
        file_save['download_count'] = 0
        file_save['enable_flag'] = 1
        file_save['logs'] = []
        file_save['logs'].append({
            "action_date":utils.get_current_time(),
            "action":"新建文件",
            "note":""
        })
        is_exist = self.get_coll().find({"file_path":file_save['file_path']}).count()
        if is_exist == 1:
            raise ValueError(u"该文件已经存在")
        credit_number = file_save.get('credit_number',None)
        if credit_number is not None:
            is_exist = self.get_coll().find({"credit_number":credit_number,"enable_flag":1}).count()
            if is_exist == 1:
                raise ValueError(u"该授权书已经存在")
        self.get_coll().save(file_save)
        return file_save

    def get_search_time(self, time_desc, start_time, end_time):
        if time_desc == "user_defined":
            if not start_time or not end_time:
                raise Exception("请选择时间！")
            # start_time = utils.strtodatetime(start_time, '%Y-%m-%d %H:%M:%S')
            # end_time = utils.strtodatetime(end_time,'%Y-%m-%d %H:%M:%S')
            start_time = utils.strtodatetime(start_time, '%Y-%m-%d %H:%M')
            end_time = utils.strtodatetime(end_time, '%Y-%m-%d %H:%M')
            return start_time, end_time
        else:
            curr_time = datetime.datetime.now()
            end_time = curr_time
            if time_desc == "nearly_three_days":
                start_time = curr_time - datetime.timedelta(days=3)
            elif time_desc == "nearly_a_week":
                start_time = curr_time - datetime.timedelta(days=7)
            elif time_desc == "nearly_a_month":
                start_time = curr_time - datetime.timedelta(days=30)
            else:
                raise Exception("查询时间未定义")
        return start_time, end_time

    def upload(self,file,file_type):
        '''
        :param upload_path: 上传路径
        :param file: self.request.files['file']的格式
        :return:
        '''
        upload_path = options.file_download_store_url + time.strftime('%Y%m%d')
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)

        file_metas=file
        if file_metas == '':
            raise ValueError(u"没有上传文件")

        for meta in file_metas:
            if file_type == "proxy":
                name = meta['filename']
                file_list,num_list =pdf_splite.pdf_splite(meta['body'],name,upload_path)
                for i in range(len(file_list)):
                    self.create(**{
                        "credit_number":num_list[i],
                        "file_name":file_list[i],
                        "file_type":file_type,
                        "file_path":os.path.join(upload_path,file_list[i]).split(utils.options.project_root_path)[1],
                        "file_sort":0,
                    })
            elif file_type == "document":
                filename = meta['filename']
                _file = self.get_coll().find_one({"file_name":filename})
                if _file is None:
                    filepath = os.path.join(upload_path,filename)
                    with open(filepath,'wb') as up:
                        up.write(meta['body'])
                    self.create(**{
                        "file_name":filename,
                        "file_type":file_type,
                        "file_path":filepath.split(utils.options.project_root_path)[1],
                        "file_sort":0,
                    })
                else:
                    filepath = utils.options.project_root_path + _file["file_path"]
                    with open(filepath,'wb') as up:
                        up.write(meta['body'])
                    _file['logs'].append({
                        "action_date":utils.get_current_time(),
                        "action":"修改文件",
                        "note":"file_path|from|%s|to|%s"%(_file['file_path'],filepath.split(utils.options.project_root_path)[1])
                    })
                    _file['file_path'] = filepath.split(utils.options.project_root_path)[1]
                    _file['enable_flag'] = 1
                    self.get_coll().save(_file)
            else:
                filename = str(utils.get_local_timestamp()) + meta['filename']
                filepath = os.path.join(upload_path,filename)
                # 有些文件需要已二进制的形式存储，实际中可以更改
                with open(filepath,'wb') as up:
                    up.write(meta['body'])
                self.create(**{
                    "file_name":filename,
                    "file_type":file_type,
                    "file_path":filepath.split(options.project_root_path)[1],
                    "file_sort":0,
                })

    def delete(self,file_id):
        file = self.get_coll().find_one({"_id":utils.create_objectid(file_id)})
        if file is None:
            raise ValueError(u"该文件不存在或已被删除")

        file['enable_flag'] = 0
        file['logs'].append({
            "action_date":utils.get_current_time(),
            "action":"删除文件",
            "note":""
        })
        self.get_coll().save(file)

    def edit(self,file_id,file):
        '''

        :param file_id: 文件id
        :param file: self.request.files['file']的格式
        :param user_id: 用户id
        :return:
        '''
        import os,time
        file_coll = self.get_coll().find_one({"_id":utils.create_objectid(file_id),"enable_flag":1})
        if file_coll is None:
            raise ValueError(u"该文件不存在或已被删除")

        upload_path=options.file_download_store_url+"%s/%s/"%(file_coll['file_type'],time.strftime('%Y/%m/%d'))

        if not os.path.exists(upload_path):
            os.makedirs(upload_path)

        file_metas=file
        if file_metas == '':
            raise ValueError(u"没有上传文件")

        for meta in file_metas:
            filename = str(utils.get_local_timestamp()) + meta['filename']
            filepath = os.path.join(upload_path,filename)
            #有些文件需要已二进制的形式存储，实际中可以更改
            with open(filepath,'wb') as up:
                up.write(meta['body'])
            file_coll['logs'].append({
                "action_date":utils.get_current_time(),
                "action":"修改文件",
                "note":"file_path|from|%s|to|%s"%(file_coll['file_path'],filepath.split(utils.options.project_root_path)[1])
            })
            file_coll['file_path'] = filepath.split(utils.options.project_root_path)[1]
            self.get_coll().save(file_coll)

    def download(self,query_dict):
        file_download = FileDownloadModel()
        file_download.create(query_dict)

class FileDownloadModel(model.BaseModel,model.Singleton):
    __name = "dxb.file_download"

    def __init__(self):
        model.BaseModel.__init__(self,FileDownloadModel.__name)

    def create(self,query_dict):
        file_model = FileModel()
        file = file_model.search(query_dict)
        if file is None:
            raise ValueError(u"文件不存在或已被删除")
        file['download_count'] += 1
        file_model.get_coll().save(file)
        file_download = {
            "file_id":file['_id'],
            "file_name":file['file_name'],
            "file_path":file['file_path'],
            "file_type":file['file_type'],
            "download_time":utils.get_now(),
        }
        self.get_coll().save(file_download)