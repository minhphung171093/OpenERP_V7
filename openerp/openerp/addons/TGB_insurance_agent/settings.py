# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


class TGB_insurance_setting(osv.osv):
    _name = 'tgb.insurance.setting'
    _columns = {
        'key': fields.char('Key', size=256, select=1,required=True),
        'value':fields.char('Value', size=256, select=1,required=True),
    }
    _sql_constraints = [
        ('key_uniq', 'unique(key)', 'Key must be unique.')
    ]
TGB_insurance_setting()




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

