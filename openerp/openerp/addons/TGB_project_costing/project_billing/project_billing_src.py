
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_billing_src(osv.osv):
    _name='project.billing.src'
    _columns = {
        'src_no':fields.char('SRC No',size=10,),
        'date':fields.date('Date',),
        'amount':fields.float('Amount',digits_compute=dp.get_precision('Account'),),
        'customer_po_no':fields.char('Customer PO No',size=20,),
        'seq_no':fields.float('Seq No',digits_compute=dp.get_precision('Account'),),
        'project_billing_id':fields.many2one('account.invoice',string='project Billing',),
        }
    
    _defaults={
    }

project_billing_src()
