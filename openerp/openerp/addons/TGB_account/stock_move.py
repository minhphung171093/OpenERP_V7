# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


class stock_move(osv.osv):
    _name = 'stock.move'
    _inherit = 'stock.move'
    _columns = {
        'place': fields.char('Place', size=50, select=1),
    }


stock_move()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

