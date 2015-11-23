
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_billing_party(osv.osv):
    _name='project.billing.party'
    _columns = {
        'name':fields.char('Name',size=100,),
        'code':fields.char('Code',size=20,),
        }
    
    _defaults={
    }

project_billing_party()
