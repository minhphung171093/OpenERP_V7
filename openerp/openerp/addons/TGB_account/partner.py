# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'

    _columns = {
        'company_registry': fields.char('Company Registry', size=50, select=1),
        'gst_registry': fields.char('GST Registry', size=50, select=1),
    }
res_partner()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

