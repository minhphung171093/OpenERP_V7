
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class phase_sequence(osv.osv):
    _name='phase.sequence'
    _columns = {
        'name':fields.char('Name',size=100,),
        }
    
    _defaults={
    }

phase_sequence()
