# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _columns = {
        'ic_no':fields.char('I/C No', size=50),
        'gender': fields.selection( [ ('m','M'),('f','F')],'Gender'),
    }
res_partner()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

