
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class ar_credit_note(osv.osv):
    _name='ar.credit.note'
    _columns = {
        'service_code':fields.many2one('product.product','Service Code',required=True),
        'description':fields.char('Description',size=100,),
        'amount':fields.float('Amount',digits_compute=dp.get_precision('Account'),),
        'project_claim_id':fields.many2one('project.claim',string='Project Claim',),
        }
    
    _defaults={
    }

ar_credit_note()
