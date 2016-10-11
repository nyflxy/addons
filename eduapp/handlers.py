#coding=utf-8

import datetime,pdb

from tornado.options import options
from dxb.handler import TokenAPIHandler,APIHandler,ListCreateAPIHandler,\
    RetrieveUpdateDestroyAPIHandler,ListAPIHandler
import libs.utils as utils
import libs.modellib as model
import models

class SubjectListCreateHandler(ListCreateAPIHandler):
    model = models.SubjectModel()

class SubjectRetrieveUpdateDestroyHandler(RetrieveUpdateDestroyAPIHandler):
    model = models.SubjectModel()

class UniversityListCreateHandler(ListCreateAPIHandler):
    model = models.UniversityModel()

class UniversityRetrieveUpdateDestroyHandler(RetrieveUpdateDestroyAPIHandler):
    model = models.UniversityModel()

class BookListCreateHandler(ListCreateAPIHandler):
    model = models.BookModel()

class BookRetrieveUpdateDestroyHandler(RetrieveUpdateDestroyAPIHandler):
    model = models.BookModel()

handlers = [
    (r"/api/sub/list",SubjectListCreateHandler),
    (r"/api/sub",SubjectRetrieveUpdateDestroyHandler),
    (r"/api/university/list",UniversityListCreateHandler),
    (r"/api/university",UniversityRetrieveUpdateDestroyHandler),
    (r"/api/book/list",BookListCreateHandler),
    (r"/api/book",BookRetrieveUpdateDestroyHandler),
]