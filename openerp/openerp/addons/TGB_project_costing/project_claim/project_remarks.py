
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_remarks(osv.osv):
    _name='project.remark'
    _columns = {
        'remark_code':fields.char('Remarks Code',size=20,),
        'remark_description':fields.char('Description',size=100,),
        'type':fields.selection([('internal','Internal'),('external','External'),],'type',),
        }
    
    _defaults={
    }

project_remarks()
