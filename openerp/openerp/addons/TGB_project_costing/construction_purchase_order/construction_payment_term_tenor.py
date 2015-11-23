
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class construction_payment_term_tenor(osv.osv):
    _name='construction.payment.term.tenor'
    _columns = {
        'name':fields.char('Name',size=100,),
        }
    
    _defaults={
    }

construction_payment_term_tenor()
