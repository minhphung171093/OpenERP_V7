# -*- coding: utf-8 -*-

from openerp.osv import fields, osv

class res_users(osv.osv):
    _inherit = 'res.users'

    _columns = {
        'user_code': fields.char('User Code',size=25),
    }
res_users()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

