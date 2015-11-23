
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class request_for_customer_po_top_up(osv.osv):
    _name='request.for.customer.po.top.up'
    _columns = {
        'project_no':fields.many2one('project.project',string='Project No',),
        'customer_name':fields.many2one('res.partner',string='Customer Name',),
        'customer_job_no':fields.char('Customer Job No',size=20,),
        'customer_po_no':fields.char('Customer PO No',size=20,),
        'seq_no':fields.char('Seq No',size=20,),
        'material':fields.char('Material',size=100,),
        'total billed_billable_amt':fields.float('Total Billed &Billable Amt',digits_compute=dp.get_precision('Account'),),
        'cusomter_po_amt':fields.float('Customer PO Amt',digits_compute=dp.get_precision('Account'),),
        'untomter_src_amt':fields.float('Untagged SRC Amt',digits_compute=dp.get_precision('Account'),),
        'tagged_amt':fields.float('Tagged Amt',digits_compute=dp.get_precision('Account'),),
        'balance amt_to_issued':fields.float('Balance Amt To Issued',digits_compute=dp.get_precision('Account'),),
        }
    
    _defaults={
    }

request_for_customer_po_top_up()
