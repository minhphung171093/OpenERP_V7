
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class res_company(osv.osv):
    _inherit='res.company'
    _columns = {
        'use_tax':fields.boolean('Use company Taxes'),
        'dk_tax_id': fields.many2many('account.tax', 'company_tax', 'company_id', 'tax_id', 'Taxes',),
        }
    _defaults={
        'use_tax' : False,
    }

res_company()

class res_partner(osv.osv):
    _inherit = 'res.partner'

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            # if record.parent_id and not record.is_company:
            #     if not context.get('no_company'):
            #         name =  "%s, %s" % (record.parent_id.name, name)
            if context.get('show_address'):
                name = name + "\n" + self._display_address(cr, uid, record, without_company=True, context=context)
                name = name.replace('\n\n','\n')
                name = name.replace('\n\n','\n')
            if context.get('show_email') and record.email:
                name = "%s <%s>" % (name, record.email)
            res.append((record.id, name))
        return res
