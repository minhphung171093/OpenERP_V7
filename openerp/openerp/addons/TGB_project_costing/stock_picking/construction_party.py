
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class construction_party(osv.osv):
    _name='construction.party'
    _inherit='stock.picking.out'
            
    _columns = {
        'party_code':fields.char('Party Code',size=20,),
        'party_name':fields.char('Party Name',size=20,),
        }
    
    _defaults={
    }

construction_party()
