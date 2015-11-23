
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_billing_vo_type(osv.osv):
    _name='project.billing.vo.type'
    _columns = {
        'name':fields.char('Name',size=100,),
        }
    
    _defaults={
    }

project_billing_vo_type()
