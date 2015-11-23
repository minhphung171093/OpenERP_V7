
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class account_invoice(osv.osv):
    _name='account.invoice'
    _inherit='account.invoice'
            
    _columns = {
        'project_id':fields.many2one('project.project',string='Project No',),
        'work_order_no':fields.char('Work Order No',size=100,),
        'customer_job_no':fields.char('Customer Job No',size=100,),
        'project_type':fields.related('project_id','project_type',string='Project Type',type='many2one',relation='project.type'),
        'currency__currency':fields.many2one('res.currency',string='Currency',),
        'exch_rate':fields.float('Exch Rate',digits_compute=dp.get_precision('Account'),),
        'total_tax_amount':fields.float('Total After Tax Amount',digits_compute=dp.get_precision('Account'),),
        'total_home_amount':fields.float('Total After Tax Home Amount',digits_compute=dp.get_precision('Account'),),
        'invoice_type':fields.char('Invoice Type',size=5,),
        'billing_type':fields.char('Billing Type',size=5,),
        'claim_type':fields.char('Claim Type',size=5,),
        'project_claim_id':fields.many2one('project.claim',string='Project Claim',),
        }
    
    _defaults={
    }

account_invoice()
