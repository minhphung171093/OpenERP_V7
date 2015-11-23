
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class requisition_type(osv.osv):
    _name='requisition.type'
    _columns = {
        'name':fields.char('Name',size=20,),
        }
    
    _defaults={
    }

requisition_type()
