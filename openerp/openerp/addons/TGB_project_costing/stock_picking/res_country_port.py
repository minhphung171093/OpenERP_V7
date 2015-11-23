
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class res_country_port(osv.osv):
    _name='res.country.port'
    _inherit='stock.picking.out'
            
    _columns = {
        'country_id':fields.many2one('res.country',string='Country',),
        'port_code':fields.char('Port Code',size=20,),
        'port_name':fields.char('Port Name',size=100,),
        }
    
    _defaults={
    }

res_country_port()
