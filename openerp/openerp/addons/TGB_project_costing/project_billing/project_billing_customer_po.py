
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_billing_customer_po(osv.osv):
    _name='project.billing.customer.po'
    _columns = {
        'customer_po_no':fields.char('Customer PO No',size=20,),
        'seq_no':fields.char('Seq No',size=20,),
        'customer_po_date':fields.date('Customer PO Date',),
        'material':fields.char('Material',size=100,),
        'document_no':fields.char('Document No',size=20,),
        'reference':fields.char('Reference',size=20,),
        'cumulative_amt':fields.float('Cumulative Amt',digits_compute=dp.get_precision('Account'),),
        'project_billing_id':fields.many2one('account.invoice',string='project billing',),
        }
    
    _defaults={
    }

project_billing_customer_po()
