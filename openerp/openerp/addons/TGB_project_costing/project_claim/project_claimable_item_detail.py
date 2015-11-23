
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_claimable_item_detail(osv.osv):
    _name='project.claimable.item.detail'
    _columns = {
        'project_claim_id':fields.many2one('project.claim',string='Project Claim ID',),
        'product_id':fields.many2one('product.product',string='Item Code',),
        'product_description':fields.related('product_id','description',string='Item Description',type='char',readonly=True),
        'qty':fields.float('Qty',digits_compute=dp.get_precision('Account'),),
        }
    
    _defaults={
    }

project_claimable_item_detail()
