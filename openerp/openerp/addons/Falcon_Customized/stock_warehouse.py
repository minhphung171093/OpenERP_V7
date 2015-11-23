# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


class stock_warehouse(osv.osv):
    _inherit = "stock.warehouse"
    _description = "Warehouse"
    _columns = {
        'warehouse_contactor_ids': fields.many2many('falcon.warehouse.contactor', 'warehouse_contactor_rel',
                                                    'warehouse_contactor_id', 'warehouse_id', 'Warehouse Contact List'),
        'address1': fields.char('Address Line', size=100),
        'address2': fields.char('Address Line 2', size=100),
        'postal_code':fields.char('Postal Code',size=10),
        'city':fields.char('City',size=25),
        'state':fields.many2one('res.country.state','State/Province'),
        'country':fields.many2one('res.country','Country'),
    }


stock_warehouse()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

