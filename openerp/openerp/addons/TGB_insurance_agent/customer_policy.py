# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


class TGB_customer_policy(osv.osv):
    _name = 'tgb.customer.policy.alert'
    _columns = {
        'partner_id':fields.many2one('res.partner','Customer'),
        'date_of_alert':fields.date('Day of Alert'),
        'remark':fields.char('Remark',size=100),
    }
TGB_customer_policy()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

