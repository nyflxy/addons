#coding=utf-8

import libs.modellib as model
import libs.utils as utils

class SubjectModel(model.BaseModel,model.Singleton):
    __name = "education.subject"

    def __init__(self):
        model.BaseModel.__init__(self,SubjectModel.__name)

class UniversityModel(model.BaseModel,model.Singleton):
    __name = "education.university"

    def __init__(self):
        model.BaseModel.__init__(self,UniversityModel.__name)

class BookModel(model.BaseModel,model.Singleton):
    __name = "education.book"

    def __init__(self):
        model.BaseModel.__init__(self,BookModel.__name)