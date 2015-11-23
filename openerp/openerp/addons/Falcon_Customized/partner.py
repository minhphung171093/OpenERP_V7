# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _columns = {
        'falcon_partner_address': fields.one2many('falcon.partner.address','partner_id','Partner address'),
        'first_name':fields.char('First name', size=50),
    }
res_partner()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

