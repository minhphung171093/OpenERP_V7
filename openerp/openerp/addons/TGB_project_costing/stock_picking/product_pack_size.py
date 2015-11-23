
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class product_pack_size(osv.osv):
    _name='product.packsize'
    _inherit='stock.move'
            
    _columns = {
        'name':fields.char('Name',size=100,),
        }
    
    _defaults={
    }

product_pack_size()
