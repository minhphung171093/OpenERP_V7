# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


class fleet_vehicle(osv.osv):
    _name = 'fleet.vehicle'
    _inherit = 'fleet.vehicle'
    _columns = {
        'assitant_id': fields.many2one('res.partner', 'Assitant', help='Assitant of the vehicle'),
    }
fleet_vehicle()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

