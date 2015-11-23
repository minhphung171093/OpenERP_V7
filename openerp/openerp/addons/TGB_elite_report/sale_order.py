# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
        'tgb_price_term':fields.char('Price Term',size=255),
        'tgb_validity':fields.date('Validity'),
        'tgb_delivery':fields.char('Delivery',size=255),
        'tgb_specification':fields.char('Specification',size=255),
        'tgb_warranty':fields.char('Warranty',size=255),
        }

sale_order()




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

