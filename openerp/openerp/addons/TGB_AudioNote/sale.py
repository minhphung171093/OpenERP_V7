# -*- coding: utf-8 -*-
__author__ = 'Phamkr'
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, \
    float_compare
import openerp.addons.decimal_precision as dp

class sale_order(osv.osv):
    _inherit = 'sale.order'
    def make_deposit(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        """Open the partial picking wizard"""
        context.update({
            'active_model': self._name,
            'active_ids': ids,
            'active_id': len(ids) and ids[0] or False
        })
        print 'gonna return'
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'add.sale.deposit.wiz',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
            'nodestroy': True,
        }

    def deposit_trans_to_payment(self, cr, uid, ids, context=None):
        print 'check in deposit trans to payment', ids
        if context is None:
            context = {}
        """Open the partial picking wizard"""
        context.update({
            'active_model': self._name,
            'active_ids': ids,
            'active_id': len(ids) and ids[0] or False
        })
        order = self.browse(cr,uid,ids)[0]
        invoice_id = self.pool.get('account.invoice').search(cr,uid,[('origin','=',order.name),('residual','>',0)])
        check_transferred = False
        if invoice_id and len(invoice_id)>0:
            invoice_id = invoice_id[0]
            invoice_obj =self.pool.get('account.invoice').browse(cr,uid,invoice_id)
            for deposit_id in order.sale_deposit_ids:
                account_voucher_obj = self.pool.get('account.voucher')
                dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account_voucher', 'view_vendor_receipt_dialog_form')
                inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
                amount_remain = deposit_id.amount
                if not deposit_id.deposit_transferred:
                    context = {
                        'payment_expected_currency': inv.currency_id.id,
                        'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                        'default_amount': amount_remain,
                        'default_reference': inv.name,
                        'close_after_process': True,
                        'invoice_type': inv.type,
                        'invoice_id': inv.id,
                        'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                        'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                        'journal_id':deposit_id.journal_id.id,
                        'memo':'Deposit from "%s" '%order.name,
                        'deposit_id':deposit_id.id,
                        }
                    account_voucher_view = {
                        'name':_("Pay Invoice"),
                        'view_mode': 'form',
                        'view_id': view_id,
                        'view_type': 'form',
                        'res_model': 'account.voucher',
                        'type': 'ir.actions.act_window',
                        'nodestroy': True,
                        'target': 'new',
                        'domain': '[]',
                        'context':context,
                        }
                    context.update({'create_fields':True})
                    account_voucher = account_voucher_obj.create(cr,uid,{},context)
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'account.voucher', account_voucher, 'proforma_voucher', cr)
                    check_transferred = True
                    self.pool.get('sale.deposit').write(cr,uid,deposit_id.id,{'deposit_transferred':True})
            # if not check_transferred:
            #     raise osv.except_osv(_('Warning!'),
            #             _('There is no untransferred deposit ' \
            #                     'for this order: "%s" (id:%d).') % \
            #                     (order.name, order.id,))
    def register_payment(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        """Open the partial picking wizard"""
        context.update({
            'active_model': self._name,
            'active_ids': ids,
            'active_id': len(ids) and ids[0] or False
        })
        order = self.browse(cr,uid,ids)[0]
        invoice_id = self.pool.get('account.invoice').search(cr,uid,[('origin','=',order.name),('residual','>',0)])
        if invoice_id and len(invoice_id)>0:
            invoice_id = invoice_id[0]
            return self.pool.get('account.invoice').invoice_pay_customer(cr,uid,[invoice_id])
        else:
            raise osv.except_osv(_('Warning!'),
                        _('There is no unpaid invoice ' \
                                'for this order: "%s" (id:%d).') % \
                                (order.name, order.id,))

    def _amount_line_tax(self, cr, uid, line, context=None):
        val = 0.0
        for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit * (1-(line.discount or 0.0)/100.0), line.product_uom_qty, line.product_id, line.order_id.partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return val

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                val1 += line.price_subtotal
                val += self._amount_line_tax(cr, uid, line, context=context)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
            # res[order.id]['amount_total'] = res[order.id]['amount_untaxed']
        return res


    def _amount_deposit(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr,uid,ids,context=context):
            res[order.id]={
                'amount_deposit':0,
                'amount_balance':0,
            }
            total = 0
            for dep in order.sale_deposit_ids:
                total += dep.amount
            res[order.id]['amount_deposit'] = total
            res[order.id]['amount_balance'] = order.amount_total - total
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()


    def _get_sale_deposit(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.deposit').browse(cr, uid, ids, context=context):
            result[line.sale_order_id.id] = True
        return result.keys()


    def _make_invoice(self, cr, uid, order, lines, context=None):
        #Make invoice come from TGB_Sale
        inv_obj = self.pool.get('account.invoice')
        obj_invoice_line = self.pool.get('account.invoice.line')
        if context is None:
            context = {}
        invoiced_sale_line_ids = self.pool.get('sale.order.line').search(cr, uid, [('order_id', '=', order.id),
                                                                                   ('invoiced', '=', True)],
                                                                         context=context)
        from_line_invoice_ids = []
        for invoiced_sale_line_id in self.pool.get('sale.order.line').browse(cr, uid, invoiced_sale_line_ids,
                                                                             context=context):
            for invoice_line_id in invoiced_sale_line_id.invoice_lines:
                if invoice_line_id.invoice_id.id not in from_line_invoice_ids:
                    from_line_invoice_ids.append(invoice_line_id.invoice_id.id)
        for preinv in order.invoice_ids:
            if preinv.state not in ('cancel',) and preinv.id not in from_line_invoice_ids:
                for preline in preinv.invoice_line:
                    inv_line_id = obj_invoice_line.copy(cr, uid, preline.id,
                                                        {'invoice_id': False, 'price_unit': -preline.price_unit})
                    lines.append(inv_line_id)
        inv = self._prepare_invoice(cr, uid, order, lines, context=context)
        inv_id = inv_obj.create(cr, uid, inv, context=context)

        if inv_id:
            inv_obj.write(cr,uid,inv_id,{'sale_person_id':order.user_id.id})

        data = inv_obj.onchange_payment_term_date_invoice(cr, uid, [inv_id], inv['payment_term'],
                                                          time.strftime(DEFAULT_SERVER_DATE_FORMAT))
        if data.get('value', False):
            inv_obj.write(cr, uid, [inv_id], data['value'], context=context)
        inv_obj.button_compute(cr, uid, [inv_id])
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'account.invoice', inv_id, 'invoice_open', cr)
        self.deposit_trans_to_payment(cr,uid,[order.id],context)

        return inv_id




    _columns = {
        'sale_deposit_ids':fields.one2many('sale.deposit','sale_order_id','Customer deposit',readonly=True),
                'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The amount without tax.", track_visibility='always'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Taxes',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The tax amount."),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The total amount."),

        'amount_deposit': fields.function(_amount_deposit, digits_compute=dp.get_precision('Account'), string='Total Deposit',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['sale_deposit_ids'], 10),
                'sale.deposit': (_get_sale_deposit, ['amount','id'], 10),
            },
            multi='dep',help="The total deposit amount."),

        'amount_balance': fields.function(_amount_deposit, digits_compute=dp.get_precision('Account'), string='Total Balance',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['sale_deposit_ids'], 10),
                'sale.deposit': (_get_sale_deposit, ['amount','id'], 10),
            },
            multi='dep',help="The total deposit amount."),

        'payment_ids':fields.one2many('account.move.line','sale_order_id',string='Payments',readonly=True),

        'state': fields.selection([
            ('draft', 'Draft Quotation'),
            ('sent', 'Quotation Sent'),
            ('cancel', 'Cancelled'),
            ('waiting_date', 'Waiting Schedule'),
            ('progress', 'Sales Order'),
            ('manual', 'Sale to Invoice'),
            ('shipping_except', 'Shipping Exception'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ], 'Status', readonly=True, track_visibility='onchange',
            help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),

    }
    _defaults={

    }

sale_order()
