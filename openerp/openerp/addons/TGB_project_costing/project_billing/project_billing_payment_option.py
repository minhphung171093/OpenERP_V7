
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_billing_payment_option(osv.osv):
    _name='project.billing.payment.option'
    _columns = {
        'name':fields.char('Name',size=20,),
        'description':fields.text('Description',),
        }
    
    _defaults={
    }

project_billing_payment_option()
