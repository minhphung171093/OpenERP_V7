# -*- coding: utf-8 -*-
##############################################################################
#
#
##############################################################################

import time
from datetime import datetime
from osv import fields, osv
from tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import decimal_precision as dp
from tools.translate import _
from openerp import SUPERUSER_ID
from openerp import netsvc

class edit_invoice(osv.osv_memory):
    _name = "edit.invoice"
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(edit_invoice, self).default_get(cr, uid, fields, context=context)
        invoice_obj = self.pool.get('account.invoice')
        invoice_ids = context.get('active_ids')
        for invoice in invoice_obj.browse(cr, uid, invoice_ids):
            edit_invoice_line = []
            for line in invoice.invoice_line:
                edit_invoice_line.append((0,0,{
                    'name': line.name,
                    'uos_id': line.uos_id and line.uos_id.id or False,
                    'product_id': line.product_id and line.product_id.id or False,
                    'account_id': line.account_id and line.account_id.id or False,
                    'price_unit': line.price_unit,
                    'quantity': line.quantity,
                    'invoice_line_tax_id': [(6,0,[l.id for l in line.invoice_line_tax_id])],
                    'company_id': line.company_id and line.company_id.id or False,
                    'invoice_line_id': line.id,
                }))
            res.update({'edit_invoice_line': edit_invoice_line})
        return res
    
    _columns = {
        'edit_invoice_line': fields.one2many('edit.invoice.line', 'edit_invoice_id', 'Edit Invoice Line'),
    }
    
    def update_invoice_line(self, cr, uid, ids, context=None):
        invoice_line_obj = self.pool.get('account.invoice.line')
        invoice_obj = self.pool.get('account.invoice')
        wf_service = netsvc.LocalService('workflow')
        for ei in self.browse(cr, uid, ids):
            for line in ei.edit_invoice_line:
                invoice_id = line.invoice_line_id.invoice_id.id
                invoice_line_obj.write(cr, uid, [line.invoice_line_id.id], {
                    'price_unit': line.price_unit,
                    'quantity': line.quantity,
                    'invoice_line_tax_id': [(6,0,[l.id for l in line.invoice_line_tax_id])],
                })
            invoice_obj.button_reset_taxes(cr, uid, [invoice_id], context)
            wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_cancel', cr)
            invoice_obj.action_cancel_draft(cr, uid, [invoice_id], [])
            wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
        return {'type': 'ir.actions.act_window_close'}
    
edit_invoice()

class edit_invoice_line(osv.osv_memory):
    _name = "edit.invoice.line"
    
    _columns = {
        'edit_invoice_id': fields.many2one('edit.invoice', 'Edit Invoice',ondelete='cascade'),
        'name': fields.text('Description', readonly=True),
        'uos_id': fields.many2one('product.uom', 'Unit of Measure',readonly=True),
        'product_id': fields.many2one('product.product', 'Product',readonly=True),
        'account_id': fields.many2one('account.account', 'Account',readonly=True),
        'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Product Price')),
        'quantity': fields.float('Quantity', digits_compute= dp.get_precision('Product Unit of Measure'), required=True),
        'invoice_line_tax_id': fields.many2many('account.tax', 'edit_invoice_line_tax_ref', 'edit_invoice_line_id', 'tax_id', 'Taxes', domain=[('parent_id','=',False)]),
        'company_id': fields.many2one('res.company', 'Company'),
        'invoice_line_id': fields.many2one('account.invoice.line', 'Invoice Line Reference'),
     }
    
edit_invoice_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
