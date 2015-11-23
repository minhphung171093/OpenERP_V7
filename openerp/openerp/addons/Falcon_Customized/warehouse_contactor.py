# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


class falcon_warehouse_contactor(osv.osv):
    _name = "falcon.warehouse.contactor"
    _description = "Warehouse Contactor"
    _columns = {
        'warehouse_contactor_id': fields.char('Contact Name', size=25),
        'name': fields.char('Contact Name', size=25),
        'tel': fields.char('Contact Telephone', size=25),
        'email': fields.char('Contact Email', size=25),
        'warehouse_contactor_ids': fields.many2many('stock.warehouse', 'warehouse_contactor_rel','warehouse_id','warehouse_contactor_id','Warehouse List'),
    }
falcon_warehouse_contactor()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

