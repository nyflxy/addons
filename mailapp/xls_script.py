#coding=utf-8

import xlsxwriter,xlrd
import xlutils
from xlutils.copy import copy
oldwb = xlrd.open_workbook("test1.xls",formatting_info=True)
newwb = copy(oldwb)
newwb.get_sheet(0).write(0,1,"foo")
newwb.save("test1.xls")