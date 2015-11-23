
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class hr_time_table(osv.osv):
    _name='hr.time.table'
    _columns = {
        'shift_no':fields.integer('Shift No',required=True),
        'am_in':fields.float('Morning In'),
        'am_out':fields.float('Morning Out'),
        'pm_in':fields.float('Afternoon In'),
        'pm_out':fields.float('Afternoon Out'),
        'ot_in':fields.float('OT In'),
        'ot_out':fields.float('OT Out'),
        }

    _defaults={
    }

    _sql_constraints = [
        ('shift_no_uniq', 'unique (shift_no)', 'The shift already defined !')
    ]


hr_time_table()
