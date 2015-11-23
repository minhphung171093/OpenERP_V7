
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_category(osv.osv):
    _name='project.category'
    _columns = {
        'name':fields.char('Name',size=100,),
        }
    
    _defaults={
    }

project_category()
