
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_customer_contract(osv.osv):
    _name='project.customer.contract'
    _columns = {
        'customer_id':fields.many2one('res.partner',string='Customer',),
        'description':fields.text('Description',),
        'name':fields.char('Name',size=20,),
        }
    
    _defaults={
    }

project_customer_contract()
