# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp import netsvc
from openerp.tools.translate import _


class sale_advance_payment_inv(osv.osv_memory):
    _inherit = "sale.advance.payment.inv"
    _description = "Sales Advance Payment Invoice"

    def _create_invoices_auto_validate(self, cr, uid, inv_values, sale_id, context=None):
        inv_values['is_fixed']=True
        wf_service = netsvc.LocalService('workflow')
        inv_obj = self.pool.get('account.invoice')
        sale_obj = self.pool.get('sale.order')
        inv_id = inv_obj.create(cr, uid, inv_values, context=context)
        inv_obj.button_reset_taxes(cr, uid, [inv_id], context=context)
        # add the invoice to the sales order's invoices
        cr.execute("DELETE FROM account_invoice_tax WHERE invoice_id=%s", (inv_id,))
        for line in self.pool.get('account.invoice').browse(cr,uid,inv_id).invoice_line:
            self.pool.get('account.invoice.line').write(cr,uid,line.id,{'invoice_line_tax_id':[(6,0,[])]})

        sale_obj.write(cr, uid, sale_id, {'invoice_ids': [(4, inv_id)]}, context=context)
        wf_service.trg_validate(uid, 'account.invoice', inv_id, 'invoice_open', cr)
        return inv_id


    def create_invoices(self, cr, uid, ids, context=None):
        print 'check in create invoice'
        wf_service = netsvc.LocalService('workflow')
        """ create invoices for the active sales orders """
        sale_obj = self.pool.get('sale.order')
        act_window = self.pool.get('ir.actions.act_window')
        wizard = self.browse(cr, uid, ids[0], context)
        sale_ids = context.get('active_ids', [])
        if wizard.advance_payment_method == 'all':
            # create the final invoices of the active sales orders
            res = sale_obj.manual_invoice(cr, uid, sale_ids, context)
            inv_id = res.get('res_id')
            if inv_id:
                if self.pool.get('account.invoice').browse(cr,uid,inv_id).state=='draft':
                    wf_service.trg_validate(uid, 'account.invoice', inv_id, 'invoice_open', cr)
            if context.get('open_invoices', False):
                return res
            return {'type': 'ir.actions.act_window_close'}

        if wizard.advance_payment_method == 'lines':
            # open the list view of sales order lines to invoice
            no_fixed = True
            exist_inv_ids = []
            for order in sale_obj.browse(cr,uid,sale_ids):
                exist_inv_ids.extend(self.pool.get('account.invoice').search(cr,uid,[('origin','=',order.name)]))
            for inv in self.pool.get('account.invoice').browse(cr,uid,exist_inv_ids):
                if inv.is_fixed:
                    no_fixed = False
            if not no_fixed:
                raise osv.except_osv(_('UserError'), _('Can not create invoice for invoiced order'))
            res = act_window.for_xml_id(cr, uid, 'sale', 'action_order_line_tree2', context)
            res['context'] = {
                'search_default_uninvoiced': 1,
                'search_default_order_id': sale_ids and sale_ids[0] or False,
            }
            return res
        assert wizard.advance_payment_method in ('fixed', 'percentage')

        inv_ids = []
        for sale_id, inv_values in self._prepare_advance_invoice_vals(cr, uid, ids, context=context):
            inv_ids.append(self._create_invoices_auto_validate(cr, uid, inv_values, sale_id, context=context))

        if context.get('open_invoices', False):
            return self.open_invoices(cr, uid, ids, inv_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}


sale_advance_payment_inv()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
