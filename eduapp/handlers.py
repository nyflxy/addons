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

    def get(self):
        result = utils.init_response_data()
        try:
            keyword = self.get_argument("keyword", "")
            if keyword != "":
                self.mg_query_params.update({
                    "name": {"$regex": keyword}
                })
            self.mg_sort_params = {
                "city": -1,
            }
        except Exception, e:
            result = utils.reset_response_data(0, str(e))
            self.write(result)
            self.finish()
            return
        ListCreateAPIHandler.get(self)

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