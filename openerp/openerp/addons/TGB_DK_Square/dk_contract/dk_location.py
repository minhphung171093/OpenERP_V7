
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class dk_location(osv.osv):
    _name='dk.location'
    _columns = {
        'code':fields.char('Code',size=20),
        'name':fields.char('Name',size=20),
        }
    
    _defaults={
    }

dk_location()
