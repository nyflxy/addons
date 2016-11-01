#coding=utf-8

import libs.modellib as model
import libs.utils as utils

class LinkModel(model.BaseModel,model.Singleton):
    __name = "newbie.link"

    def __init__(self):
        model.BaseModel.__init__(self,LinkModel.__name)

class SubjectModel(model.BaseModel,model.Singleton):
    __name = "newbie.subject"

    def __init__(self):
        model.BaseModel.__init__(self,SubjectModel.__name)