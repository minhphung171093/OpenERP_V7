
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_type(osv.osv):
    _name='project.type'
    _columns = {
        'name':fields.char('Name',size=20,),
        'description':fields.char('Description',size=100,),
        }
    
    _defaults={
    }

project_type()
