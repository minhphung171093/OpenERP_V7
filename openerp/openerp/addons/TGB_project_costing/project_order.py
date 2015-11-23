# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.osv import orm, fields
from openerp import netsvc
from openerp.tools.translate import _

class sale_order(orm.Model):
    _inherit = 'sale.order'


    def manual_invoice(self, cr, uid, ids, context=None):
        """ create invoices for the given sales orders (ids), and open the form
            view of one of the newly created invoices
        """
        mod_obj = self.pool.get('ir.model.data')
        wf_service = netsvc.LocalService("workflow")

        # create invoices through the sales orders' workflow
        inv_ids0 = set(inv.id for sale in self.browse(cr, uid, ids, context) for inv in sale.invoice_ids)
        for id in ids:
            wf_service.trg_validate(uid, 'sale.order', id, 'manual_invoice', cr)
        inv_ids1 = set(inv.id for sale in self.browse(cr, uid, ids, context) for inv in sale.invoice_ids)
        # determine newly created invoices
        new_inv_ids = list(inv_ids1 - inv_ids0)
        print 'new_inv_ids', new_inv_ids
        res = mod_obj.get_object_reference(cr, uid, 'TGB_project_costing', 'tgb_construction_project_billing_form_view')
        res_id = res and res[1] or False,
        if new_inv_ids:
            invoice_id = new_inv_ids[0]
            invoice = self.pool.get('account.invoice').browse(cr,uid,invoice_id)
            if invoice.origin:
                sale_id = self.search(cr,uid,[('name','=',invoice.origin)])
                if sale_id and len(sale_id)>0:
                    self.pool.get('account.invoice').write(cr,uid,invoice_id,{'sale_order_id':sale_id[0]})
        return {
            'name': _('Project Billing'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': 'account.invoice',
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': new_inv_ids and new_inv_ids[0] or False,
        }


    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = est_total_cost = est_total_profit = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                val1 += line.price_subtotal
                val += self._amount_line_tax(cr, uid, line, context=context)
                est_total_cost += line.est_total_cost
                est_total_profit += line.est_total_profit
            res[order.id]['est_total_cost'] = cur_obj.round(cr, uid, cur, est_total_cost)
            res[order.id]['est_total_cost_home'] = est_total_cost * order.exchange_rate
            res[order.id]['est_profit'] = cur_obj.round(cr, uid, cur, est_total_profit)
            res[order.id]['est_profit_home'] = est_total_profit * order.exchange_rate
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_tax_home'] = res[order.id]['amount_tax'] * order.exchange_rate
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_untaxed_home'] = res[order.id]['amount_untaxed'] * order.exchange_rate
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
            res[order.id]['amount_total_home'] = res[order.id]['amount_total'] * order.exchange_rate
            if res[order.id]['amount_total'] != 0:
                res[order.id]['profit_margin'] = res[order.id]['est_profit'] / res[order.id]['amount_total'] * 100
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    def action_button_confirm(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'sale.order', ids[0], 'order_confirm', cr)

        # redisplay the record as a sales order
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'TGB_project_costing', 'project_view_order_form')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sales Order'),
            'res_model': 'sale.order',
            'res_id': ids[0],
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }


    def action_view_invoice(self, cr, uid, ids, context=None):
        '''
        This function returns an action that display existing invoices of given sales order ids. It can either be a in a list or in a form view, if there is only one invoice to show.
        '''
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        result = mod_obj.get_object_reference(cr, uid, 'TGB_project_costing', 'tgb_construction_project_billing_action')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        #compute the number of invoices to display
        inv_ids = []
        for so in self.browse(cr, uid, ids, context=context):
            inv_ids += [invoice.id for invoice in so.invoice_ids]
        #choose the view_mode accordingly
        if len(inv_ids)>1:
            result['domain'] = "[('id','in',["+','.join(map(str, inv_ids))+"])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'TGB_project_costing', 'tgb_construction_project_billing_form_view')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = inv_ids and inv_ids[0] or False

        print 'resuslt',result
        return result


    _columns = {
        'write_uid2': fields.many2one('res.users', 'Last updated by'),
        'write_date2': fields.datetime('Last Updated Date'),
        'create_uid2': fields.many2one('res.users', 'Create By'),
        'create_date2': fields.datetime('Created Date'),
        'rev_no': fields.integer('Quotation Rev No'),
        'source_type': fields.selection([('D', 'Direct'),
                                         ('U', 'From Subcon via Project Updating'), ('Q', 'From Project Quotation')],
                                        'Source type'),
        'manager_id': fields.many2one('res.users', 'Sale Manager'),
        'site_manager_id': fields.many2one('res.users', 'Site Manager'),
        'subject': fields.text('Subject'),
        'project_start_date': fields.related('sale_project_id', 'date_start', string="Project Start Date", type='date',
                                             select=True, readonly=True),
        'project_end_date': fields.related('sale_project_id', 'date', string="Project End Date", type='date',
                                           select=True, readonly=True),
        'bill_type': fields.selection([('Pr', 'Bill By Project'),
                                       ('Ph', 'Bill By Phrase'), ('C', 'Bill By Claim'),
                                       ('D', 'Bill By Draft Bill')], 'Bill type'),
        'contract_id': fields.many2one('account.analytic.account', 'Contract'),
        'project_class': fields.many2one('project.class', 'Project Class'),
        'project_category': fields.many2one('project.category', 'Project Category'),
        'sale_tax': fields.many2one('account.tax', 'Sales Tax'),
        'retention_required': fields.boolean('Retention Required'),
        'retention_percent': fields.float('Retention Percent'),
        'retention_amount': fields.float('Retention Amount'),
        'retention_day': fields.integer('Retention Days'),
        'retention_date': fields.date('Retention Date'),
        'tolerable_percent': fields.float('Tolerable Percent'),
        'partner_po_no': fields.char('Customer Po No'),
        'warehouse_id': fields.many2one('stock.warehouse', 'Default Loading Location'),
        'exchange_rate': fields.float('Exchange Rate'),
        'operation_manager': fields.many2one('res.users', 'Operation Manager'),
        'project_manager': fields.many2one('res.users', 'Project Manager'),
        'claim_officer': fields.many2one('res.users', 'Claim Officer'),
        'project_coordinator': fields.many2one('res.users', 'Project Coordinator'),
        'resident_technical_officer': fields.many2one('res.users', 'Resident Technical Officer'),
        'head_of_department': fields.many2one('res.users', 'Head of Department'),
        'user_ids': fields.one2many('project.user.sale', 'sale_id', 'Other Member'),
        'payment_option': fields.char('Payment Option'),
        'payment_term_tenor': fields.integer('Payment Term Ternor'),
        'payment_method': fields.char('Payment Method'),
        'billing_party': fields.many2one('res.partner', 'Billing Party'),
        'billing_address': fields.many2one('res.partner', 'Billing Address'),
        'billing_contact': fields.many2one('res.partner', 'Billing Contact'),
        'scr_ids': fields.one2many('project.scr', 'sale_id', 'SCR'),
        'internal_remark_code': fields.char('Internal Remark Code'),
        'external_remark_code': fields.char('External Remark Code'),
        'internal_remark': fields.text('Internal Remark'),
        'external_remark': fields.text('External Remark'),
        'project_status': fields.char('Project Status'),
        'attachment_ids': fields.one2many('project.attachment', 'sale_id', 'Attachment'),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True),
        'total_budget':fields.float('Total budget',digits_compute=dp.get_precision('Account') ),
        'sale_project_id': fields.many2one('project.project', 'Project', readonly=True,
                                           states={'draft': [('readonly', False)]}, ),

        'est_profit': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Est. Profit',
                                      store={
                                          'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                                          'sale.order.line': (_get_order,
                                                              ['price_unit', 'tax_id', 'discount', 'product_uom_qty',
                                                               'budget_total', 'budget_profit', 'est_total_cost'], 10),
                                      },
                                      multi='sums', help="The amount without tax.", track_visibility='always'),

        'est_profit_home': fields.function(_amount_all, digits_compute=dp.get_precision('Account'),
                                           string='Est. Profit Home',
                                           store={
                                               'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                                               'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount',
                                                                                'product_uom_qty', 'budget_total',
                                                                                'budget_profit', 'est_total_cost'], 10),
                                           },
                                           multi='sums', help="The amount without tax.", track_visibility='always'),


        'est_total_cost': fields.function(_amount_all, digits_compute=dp.get_precision('Account'),
                                          string='Est. Total Cost',
                                          store={
                                              'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                                              'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount',
                                                                               'product_uom_qty', 'budget_total',
                                                                               'budget_profit', 'est_total_cost'], 10),
                                          },
                                          multi='sums', help="The amount without tax.", track_visibility='always'),

        'est_total_cost_home': fields.function(_amount_all, digits_compute=dp.get_precision('Account'),
                                               string='Est. Total Cost Home',
                                               store={
                                                   'sale.order': (
                                                   lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                                                   'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount',
                                                                                    'product_uom_qty', 'budget_total',
                                                                                    'budget_profit', 'est_total_cost'],
                                                                       10),
                                               },
                                               multi='sums', help="The amount without tax.", track_visibility='always'),


        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'),
                                          string='Total Amount',
                                          store={
                                              'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                                              'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount',
                                                                               'product_uom_qty', 'budget_total',
                                                                               'budget_profit', 'est_total_cost'], 10),
                                          },
                                          multi='sums', help="The amount without tax.", track_visibility='always'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'),
                                      string='Total Sales Tax Amt',
                                      store={
                                          'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                                          'sale.order.line': (_get_order,
                                                              ['price_unit', 'tax_id', 'discount', 'product_uom_qty',
                                                               'budget_total', 'budget_profit', 'est_total_cost'], 10),
                                      },
                                      multi='sums', help="The tax amount."),

        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
                                        store={
                                            'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                                            'sale.order.line': (_get_order,
                                                                ['price_unit', 'tax_id', 'discount', 'product_uom_qty',
                                                                 'budget_total', 'budget_profit', 'est_total_cost'],
                                                                10),
                                        },
                                        multi='sums', help="The total amount."),

        'profit_margin': fields.function(_amount_all, digits_compute=dp.get_precision('Account'),
                                         string='Profit margin %',
                                         store={
                                             'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                                             'sale.order.line': (_get_order,
                                                                 ['price_unit', 'tax_id', 'discount', 'product_uom_qty',
                                                                  'budget_total', 'budget_profit', 'est_total_cost'],
                                                                 10),
                                         },
                                         multi='sums', help="The amount without tax.", track_visibility='always'),
        'amount_untaxed_home': fields.function(_amount_all, digits_compute=dp.get_precision('Account'),
                                               string='Total Home Amt',
                                               store={
                                                   'sale.order': (
                                                   lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                                                   'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount',
                                                                                    'product_uom_qty', 'budget_total',
                                                                                    'budget_profit', 'est_total_cost'],
                                                                       10),
                                               },
                                               multi='sums', help="The amount without tax.", track_visibility='always'),
        'amount_total_home': fields.function(_amount_all, digits_compute=dp.get_precision('Account'),
                                             string='Amount Total Home',
                                             store={
                                                 'sale.order': (
                                                 lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                                                 'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount',
                                                                                  'product_uom_qty', 'budget_total',
                                                                                  'budget_profit', 'est_total_cost'],
                                                                     10),
                                             },
                                             multi='sums', help="The amount without tax.", track_visibility='always'),
        'amount_total_budget_home': fields.function(_amount_all, digits_compute=dp.get_precision('Account'),
                                                    string='Amount Budget Home',
                                                    store={
                                                        'sale.order': (
                                                        lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                                                        'sale.order.line': (_get_order,
                                                                            ['price_unit', 'tax_id', 'discount',
                                                                             'product_uom_qty', 'budget_total',
                                                                             'budget_profit', 'est_total_cost'], 10),
                                                    },
                                                    multi='sums', help="The amount without tax.",
                                                    track_visibility='always'),

        'amount_total_budget': fields.function(_amount_all, digits_compute=dp.get_precision('Account'),
                                               string='Amount Total Budget',
                                               store={
                                                   'sale.order': (
                                                   lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                                                   'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount',
                                                                                    'product_uom_qty', 'budget_total',
                                                                                    'budget_profit', 'est_total_cost'],
                                                                       10),
                                               },
                                               multi='sums', help="The amount without tax.", track_visibility='always'),
        'amount_tax_home': fields.function(_amount_all, digits_compute=dp.get_precision('Account'),
                                           string='Total Sales Tax Home Amt',
                                           store={
                                               'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                                               'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount',
                                                                                'product_uom_qty', 'budget_total',
                                                                                'budget_profit', 'est_total_cost'], 10),
                                           },
                                           multi='sums', help="The amount without tax.", track_visibility='always'),
        'state': fields.selection([
            ('draft', 'Draft Quotation'),
            ('sent', 'Quotation Sent'),
            ('cancel', 'Cancelled'),
            ('waiting_date', 'Waiting Schedule'),
            ('progress', 'Project Order'),
            ('manual', 'Project Order to Billing'),
            ('invoice_except', 'Billing Exception'),
            ('done', 'Done'),
            ], 'Status', readonly=True, track_visibility='onchange',
            help="Gives the status of the quotation or project order. \nThe exception status is automatically set when a cancel operation occurs in the processing of a document linked to the project order. \nThe 'Waiting Schedule' status is set when the invoice is confirmed but waiting for the scheduler to run on the order date.", select=True),
    }

    _defaults = {
        'exchange_rate': 1,
    }


sale_order()


class sale_order_line(osv.Model):
    _inherit = 'sale.order.line'

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {}
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.product_id,
                                        line.order_id.partner_id)
            cur = line.order_id.currency_id
            res[line.id]['price_subtotal'] = cur_obj.round(cr, uid, cur, taxes['total'])
            res[line.id]['est_total_profit'] = res[line.id]['price_subtotal'] - line.est_total_cost
        return res

    _columns = {
        'name': fields.text('Phase', required=False, readonly=True, states={'draft': [('readonly', False)]}),
        'phase_uom': fields.char('UOM', size=10),
        'budget_total': fields.float("Budget Total"),
        'budget_profit': fields.float("Budget Profit"),
        'est_total_cost': fields.float("Est. Total Cost"),
        'est_total_profit': fields.function(_amount_line, string='Est. Profit',
                                            digits_compute=dp.get_precision('Account'), multi="total_line"),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Account'),
                                          multi="total_line"),
    }


class project_user_sale(osv.Model):
    _name = 'project.user.sale'
    _columns = {
        'user_id': fields.many2one('res.users', 'User'),
        'sale_id': fields.many2one('sale.order', 'Sale'),
        'name': fields.char('Name'),
    }


class project_scr(osv.Model):
    _name = 'project.scr'
    _columns = {
        'sale_id': fields.many2one('sale.order', 'Sale'),
        'name': fields.char('SCR number'),
        'date': fields.date('Date'),
        'amount': fields.float('Amount'),
    }


class project_attachment(osv.Model):
    _name = 'project.attachment'
    _columns = {
        'sale_id': fields.many2one('sale.order', 'Sale'),
        'stock_picking_id': fields.many2one('stock.picking', 'Stock Picking'),
        'stock_picking_in_id': fields.many2one('stock.picking.in', 'Stock Picking In'),
        'stock_picking_out_id': fields.many2one('stock.picking.out', 'Stock Picking Out'),
        'name': fields.char('File name'),
        'attachment': fields.many2one('ir.attachment', 'Attachment'),
    }


class customer_purchase_order(osv.Model):
    _name = 'customer.purchase.order'
    _columns = {
        'name': fields.char('Document No'),
        'sequence': fields.integer('Seq No'),
        'project_id': fields.many2one('project.project', 'Project No', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', required=True),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True),
        'customer_job_no': fields.char('Customer Job No'),
        'subject': fields.text('Subject'),
        'customer_po_date': fields.date('Customer Po Date', required=True),
        'customer_po_no': fields.char('Customer Po No', required=True),
        'material_source': fields.many2one('construction.material.source', 'Material Source'),
        'ref_no': fields.char('Ref No'),
        'cumulative_amount': fields.float('Cumulative amount'),
        'current_po_amount': fields.float('Current Po Amount'),
        'scr_ids': fields.one2many('customer.po.scr', 'cpo_id', 'SCR'),
    }
    _defaults = {
        'customer_po_date': fields.date.context_today,
    }


class customer_purchase_order(osv.Model):
    _name = 'customer.purchase.order'
    _columns = {
        'name': fields.char('Document No'),
        'sequence': fields.integer('Seq No'),
        'project_id': fields.many2one('project.project', 'Project No', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', required=True, domain=[('customer', '=', True)]),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True),
        'customer_job_no': fields.char('Customer Job No'),
        'subject': fields.char('Subject', size=500),
        'customer_po_date': fields.date('Customer Po Date', required=True),
        'customer_po_no': fields.char('Customer Po No', required=True),
        'material_source': fields.many2one('construction.material.source', 'Material Source'),
        'ref_no': fields.char('Ref No'),
        'cumulative_amount': fields.float('Cumulative amount'),
        'current_po_amount': fields.float('Current Po Amount'),
        'scr_ids': fields.one2many('customer.po.scr', 'cpo_id', 'SCR'),
    }
    _defaults = {
        'customer_po_date': fields.date.context_today,
    }


class construction_material_source(osv.Model):
    _name = 'construction.material.source'
    _columns = {
        'name': fields.char('Name'),
    }


class project_scr(osv.Model):
    _name = 'customer.po.scr'
    _columns = {
        'cpo_id': fields.many2one('customer.purchase.order', 'Customer PO'),
        'name': fields.char('SCR number'),
        'date': fields.date('Date'),
        'amount': fields.float('Amount'),
    }


class project_cost_allowcation(osv.Model):
    _name = 'project.cost.allocation'
    _columns = {
        'name': fields.char('Voucher No'),
        'date': fields.date('Cost Allocation Date', required=True),
        'project_id': fields.many2one('project.project', 'Project No', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer'),
        'default_type': fields.char('Default Type'),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True),
        'exchange_rate': fields.char('Exchange Rate'),
        'ref_no': fields.char('Ref No'),
        'total_add_amount': fields.float('Total Add Amount'),
        'total_add_amount_home': fields.float('Total Add Amount'),
        'total_reduce_amount': fields.float('Total Add Amount'),
        'total_reduce_amount_home': fields.float('Total Add Amount'),
        'created_uid2': fields.many2one('res.users', 'Created By'),
        'created_date2': fields.date('Create Date'),
        'detail_ids': fields.one2many('project.cost.detail', 'pro_cost_id', 'Detail'),
        'internal_remark_code': fields.char('Internal Remark Code'),
        'external_remark_code': fields.char('External Remark Code'),
        'internal_remark': fields.text('Internal Remark'),
        'external_remark': fields.text('External Remark'),
    }
    _defaults = {
        'date': fields.date.context_today,
        'exchange_rate': 1,
    }


class project_type(osv.Model):
    _name = 'construction.project.type'
    _columns = {
        'name': fields.char('Type'),
    }


class project_scr(osv.Model):
    _name = 'project.cost.detail'
    _columns = {
        'name': fields.char('Name'),
        'pro_cost_id': fields.many2one('project.cost.allocation', 'Project Cost Allocation'),
        'type': fields.many2one('construction.project.type','Type'),
        'item_type': fields.char('Item Type'),
        'product_id': fields.many2one('product.product', 'Item Code/Remarks', required=True),
        'uom_id': fields.related('product_id','uom_id',type='many2one',relation='product.uom', string= 'UOM',readonly=True),
        'total_amount': fields.float('Total Amount'),
        'total_amount_home': fields.float('Total Home Amount'),
    }
