
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class dk_contract_type(osv.osv):
    _name='dk.contract.type'

    # def name_get(self, cr, uid, ids, context=None):
    #     if not ids:
    #         return []
    #     if isinstance(ids, (int, long)):
    #                 ids = [ids]
    #     reads = self.read(cr, uid, ids, ['name', 'description'], context=context)
    #     res = []
    #     for record in reads:
    #         name = record['name']
    #         if record['description']:
    #             name = record['description']
    #         res.append((record['id'], name))
    #     return res

    _columns = {
        'name':fields.char('Name',size=20,),
        'description':fields.char('Description',size=100,),
        }
    
    _defaults={
    }

    _sql_constraints = [
        ('name_uiquie', 'unique (name)', 'The code of this type already existed !')
    ]


dk_contract_type()
