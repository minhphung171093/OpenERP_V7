
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_claim_detail(osv.osv):
    _name='project.claim.detail'
    _columns = {
        'phase_description_remrks':fields.char('Phase Description Remarks',size=100,),
        'vo_type':fields.char('VO Type',size=20,),
        'qty':fields.float('Qty',digits_compute=dp.get_precision('Account'),),
        'uom_id':fields.many2one('product.uom',string='UOM',),
        'unit_price':fields.float('Unit Price',digits_compute=dp.get_precision('Account'),),
        'disc_amount_percent':fields.float('Disc%/Amount',digits_compute=dp.get_precision('Account'),),
        'total_amount':fields.float('Total Amount',digits_compute=dp.get_precision('Account'),),
        'claim_option':fields.selection([('qty','Qty'),
                                        ('amount','Amount'),
                                         ('dimensions','Dimensions'),
                                         ('fraction','Fraction'),],'Claim Option',),
        'curren_cumulative_claim_amount':fields.float('Current Cumulative Claim Amount',digits_compute=dp.get_precision('Account'),),
        'curren_cumulative_certified_amount':fields.float('Current Cumulative Certified Amount',digits_compute=dp.get_precision('Account'),),
        'this cumulative_claim_amount':fields.float('This Cumulative Claim Amount',digits_compute=dp.get_precision('Account'),),
        'this_claim_amount':fields.float('This Claim Amount',digits_compute=dp.get_precision('Account'),),
        'remarks':fields.text('Remarks',),
        'project_claim_id':fields.many2one('project.claim',string='Project Claim',),
        }
    
    _defaults={
    }

project_claim_detail()
