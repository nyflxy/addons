#coding=utf-8

import libs.modellib as model
import libs.utils as utils

#coding=utf-8

import libs.modellib as model
import libs.utils as utils

class MailModel(model.BaseModel,model.Singleton):
    __name = "dxb.mail"

    def __init__(self):
        model.BaseModel.__init__(self,MailModel.__name)

