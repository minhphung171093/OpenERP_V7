
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_shipment_term(osv.osv):
    _name='project.shipment.term'
    _columns = {
        'name':fields.char('name',size=20,),
        }
    
    _defaults={
    }

project_shipment_term()
