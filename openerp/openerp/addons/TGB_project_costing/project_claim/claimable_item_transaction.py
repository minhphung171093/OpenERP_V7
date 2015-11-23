
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class claimable_item_transaction(osv.osv):
    _name='project.claimable.item.transaction.detail'
    _columns = {
        'transaction_type':fields.char('Transaction Type',size=20,),
        'source_voucher_no':fields.char('Source Voucher No.',size=20,),
        'voucher_date':fields.date('Voucher Date',),
        'period_id':fields.many2one('account.period',string='Period ',),
        'year_id':fields.many2one('account.fiscalyear',string='Year ',),
        'in_qty':fields.float('In Qty',digits_compute=dp.get_precision('Account'),),
        'out_qty':fields.float('Out Qty',digits_compute=dp.get_precision('Account'),),
        'project_claim_id':fields.many2one('project.claim',string='Project Claim',),
        }
    
    _defaults={
    }

claimable_item_transaction()
