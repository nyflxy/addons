#coding=utf-8

import urllib
import urllib2
import cookielib
import json,pdb

class CURL(object):

    @classmethod
    def post(cls,*args, **options):
        url = options.get('url', None)
        data = options.get('data', {})
        if not url:
            raise "url error"
        if type(data) != type({}):
            raise "request data error"
        try :
            opener = urllib2.build_opener()
            data = urllib.urlencode(data)
            response = opener.open(url, data).read()
            response = json.loads(response)
            if response["meta"]["code"] != 200 :
                return {"success": 0, "return_code": 'error', "error_msg": "error"}
            else :
                return {"success": 1, "return_code": 'success', "data": response["response"]["data"]}
        except Exception ,e :
            return {"success":0,"return_code":str(e),"error_msg":"error"}

    @classmethod
    def get(cls,*args, **options):
        url = options.get('url', None)
        data = options.get('data', {})
        if not url:
            raise Exception("url error")
        if type(data) != type({}):
            raise Exception("request data error")
        f = urllib.urlopen(url)
        response = json.loads(f.read())
        return response