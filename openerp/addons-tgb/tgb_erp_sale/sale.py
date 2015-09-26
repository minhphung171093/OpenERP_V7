# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime
import time
from datetime import date
from datetime import timedelta
from datetime import datetime
import calendar
import openerp.addons.decimal_precision as dp
import codecs
import os
from xlrd import open_workbook,xldate_as_tuple
from openerp import modules
from openerp import netsvc


class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    _columns = {
                'cost_price': fields.float('Cost Price', required=True, digits_compute= dp.get_precision('Product Price'), readonly=True, states={'draft': [('readonly', False)]}),
    }
    
    _defaults = {
        'cost_price': 0.0,
    }
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        context = context or {}
        lang = lang or context.get('lang',False)
        if not  partner_id:
            raise osv.except_osv(_('No Customer Defined!'), _('Before choosing a product,\n select a customer in the sales form.'))
        warning = {}
        product_uom_obj = self.pool.get('product.uom')
        partner_obj = self.pool.get('res.partner')
        product_obj = self.pool.get('product.product')
        context = {'lang': lang, 'partner_id': partner_id}
        if partner_id:
            lang = partner_obj.browse(cr, uid, partner_id).lang
        context_partner = {'lang': lang, 'partner_id': partner_id}

        if not product:
            return {'value': {'th_weight': 0,
                'product_uos_qty': qty}, 'domain': {'product_uom': [],
                   'product_uos': []}}
        if not date_order:
            date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

        result = {}
        warning_msgs = ''
        product_obj = product_obj.browse(cr, uid, product, context=context_partner)

        uom2 = False
        if uom:
            uom2 = product_uom_obj.browse(cr, uid, uom)
            if product_obj.uom_id.category_id.id != uom2.category_id.id:
                uom = False
        if uos:
            if product_obj.uos_id:
                uos2 = product_uom_obj.browse(cr, uid, uos)
                if product_obj.uos_id.category_id.id != uos2.category_id.id:
                    uos = False
            else:
                uos = False
        fpos = fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position) or False
        if update_tax: #The quantity only have changed
            result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_obj.taxes_id)

        if not flag:
            result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]
            if product_obj.description_sale:
                result['name'] += '\n'+product_obj.description_sale
        domain = {}
        if (not uom) and (not uos):
            result['product_uom'] = product_obj.uom_id.id
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
                uos_category_id = product_obj.uos_id.category_id.id
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
                uos_category_id = False
            result['th_weight'] = qty * product_obj.weight
            domain = {'product_uom':
                        [('category_id', '=', product_obj.uom_id.category_id.id)],
                        'product_uos':
                        [('category_id', '=', uos_category_id)]}
        elif uos and not uom: # only happens if uom is False
            result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
            result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
            result['th_weight'] = result['product_uom_qty'] * product_obj.weight
        elif uom: # whether uos is set or not
            default_uom = product_obj.uom_id and product_obj.uom_id.id
            q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
            result['th_weight'] = q * product_obj.weight        # Round the quantity up

        if not uom2:
            uom2 = product_obj.uom_id
        # get unit price

        if not pricelist:
            warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
                    'Please set one before choosing a product.')
            warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
        else:
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                    product, qty or 1.0, partner_id, {
                        'uom': uom or result.get('product_uom'),
                        'date': date_order,
                        })[pricelist]
            if price is False:
                warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
                        "You have to change either the product, the quantity or the pricelist.")

                warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
            else:
                result.update({'price_unit': price})
        result.update({'cost_price': product_obj.standard_price or 0.0})
        if warning_msgs:
            warning = {
                       'title': _('Configuration Error!'),
                       'message' : warning_msgs
                    }
        return {'value': result, 'domain': domain, 'warning': warning}
    
    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        """Prepare the dict of values to create the new invoice line for a
           sales order line. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record line: sale.order.line record to invoice
           :param int account_id: optional ID of a G/L account to force
               (this is used for returning products including service)
           :return: dict of values to create() the invoice line
        """
        res = {}
        product_multi_company_obj = self.pool.get('product.multi.company')
        if not line.invoiced:
            if line.product_id.company_id.id != line.order_id.company_id.id:
                product_multi_company_ids = product_multi_company_obj.search(cr, uid, [('company_id','=',line.order_id.company_id.id),('product_id','=',line.product_id.id)])
                if not product_multi_company_ids:
                    raise osv.except_osv(_('Error!'),
                            _('Please define product multi company for this product: "%s" (id:%d).') % \
                                (line.product_id.name, line.product_id.id,))
                product_multi_company_id = product_multi_company_obj.browse(cr, uid, product_multi_company_ids[0])
                account_id = product_multi_company_id.income_acc_id.id
                invoice_line_tax_id = [(6, 0, [x.id for x in product_multi_company_id.customer_tax_ids])]
            else:
                invoice_line_tax_id = [(6, 0, [x.id for x in line.tax_id])]
            if not account_id:
                if line.product_id:
                    account_id = line.product_id.property_account_income.id
                    if not account_id:
                        account_id = line.product_id.categ_id.property_account_income_categ.id
                    if not account_id:
                        raise osv.except_osv(_('Error!'),
                                _('Please define income account for this product: "%s" (id:%d).') % \
                                    (line.product_id.name, line.product_id.id,))
                else:
                    prop = self.pool.get('ir.property').get(cr, uid,
                            'property_account_income_categ', 'product.category',
                            context=context)
                    account_id = prop and prop.id or False
            uosqty = self._get_line_qty(cr, uid, line, context=context)
            uos_id = self._get_line_uom(cr, uid, line, context=context)
            pu = 0.0
            if uosqty:
                pu = round(line.price_unit * line.product_uom_qty / uosqty,
                        self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Price'))
            fpos = line.order_id.fiscal_position or False
            account_id = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, account_id)
            if not account_id:
                raise osv.except_osv(_('Error!'),
                            _('There is no Fiscal Position defined or Income category account defined for default properties of Product categories.'))
            res = {
                'name': line.name,
                'sequence': line.sequence,
                'origin': line.order_id.name,
                'account_id': account_id,
                'price_unit': pu,
                'quantity': uosqty,
                'discount': line.discount,
                'uos_id': uos_id,
                'product_id': line.product_id.id or False,
                'invoice_line_tax_id': invoice_line_tax_id,
                'account_analytic_id': line.order_id.project_id and line.order_id.project_id.id or False,
            }

        return res
    
sale_order_line()    
class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
    }
    
    def init(self, cr):
#         ir_module = self.pool.get('ir.module.module')
#         module_name = 'multi_company'
#         mod_ids = ir_module.search(cr, SUPERUSER_ID, [('name', '=', module_name)])
#         record = ir_module.browse(cr, SUPERUSER_ID, mod_ids[0]) if mod_ids else None
#         to_install = [(module_name,record)]
#         action = self.pool.get('base.config.settings')._install_modules(cr, SUPERUSER_ID, to_install,context={})
        
        cr.execute(''' select res_id from ir_model_data
            where name in ('group_uom','group_multi_currency','group_multi_company')
                and model='res.groups' ''')
        implied_group = cr.fetchall()
        cr.execute(''' select res_id from ir_model_data
            where name in ('group_user') and module='base' and model='res.groups' ''')
        group = cr.fetchone()
        if implied_group and group:
            group_id = group[0]
            for implied_group in implied_group:
                implied_group_id = implied_group[0]
                self.pool.get('res.groups').write(cr, SUPERUSER_ID, [group_id], {'implied_ids': [(4, implied_group_id)]})
        
        rules = [
            {'module': 'sale','xml_id': 'sale_order_comp_rule'},
            {'module': 'sale','xml_id': 'sale_order_line_comp_rule'},
            {'module': 'account','xml_id': 'invoice_comp_rule'},
            {'module': 'account','xml_id': 'account_invoice_line_comp_rule'},
            {'module': 'account','xml_id': 'journal_comp_rule'},
            {'module': 'account','xml_id': 'tax_comp_rule'},
            {'module': 'base','xml_id': 'res_company_rule'},
            {'module': 'product','xml_id': 'product_comp_rule'},
            {'module': 'account','xml_id': 'period_comp_rule'},
            {'module': 'account','xml_id': 'account_move_line_comp_rule'},
            {'module': 'account','xml_id': 'account_move_comp_rule'},
            {'module': 'base','xml_id': 'res_users_rule'},
            {'module': 'base','xml_id': 'res_partner_rule'},
            {'module': 'account','xml_id': 'account_comp_rule'},
        ]
        for rule in rules:
            sql = '''
                update ir_rule set active='f' where id in (select res_id from ir_model_data where name='%s' and module='%s')
            '''%(rule['xml_id'],rule['module'])
            cr.execute(sql)
        return True
    
    def action_button_confirm(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        sale_line_obj = self.pool.get('sale.order.line')
        product_obj = self.pool.get('product.product')
        invoice_obj = self.pool.get('account.invoice')
        partner_multi_company_obj = self.pool.get('partner.multi.company')
        company_id = False
        for sale in self.browse(cr, uid, ids):
            invoice_line_vals = []
            for line in sale.order_line:
                if line.product_id.company_id.id != sale.company_id.id:
                    company_id = line.product_id.company_id.id
                    account_id = line.product_id.property_account_income.id
                    if not account_id:
                        account_id = line.product_id.categ_id.property_account_income_categ.id
                    if not account_id:
                        raise osv.except_osv(_('Error!'),
                                _('Please define income account for this product: "%s" (id:%d).') % \
                                    (line.product_id.name, line.product_id.id,))
                    invoice_line_vals.append((0,0,{
                        'name': line.name,
                        'sequence': line.sequence,
                        'origin': line.order_id and line.order_id.name or '',
                        'account_id': account_id,
                        'price_unit': line.cost_price,
                        'quantity': line.product_uom_qty,
                        'discount': line.discount or 0.0,
                        'uos_id': line.product_uos and line.product_uos.id or False,
                        'product_id': line.product_id and line.product_id.id or False,
                        'invoice_line_tax_id': [(6, 0, [x.id for x in line.tax_id])],
                        'account_analytic_id': line.order_id.project_id and line.order_id.project_id.id or False,
                        }))
            if invoice_line_vals:
                journal_ids = self.pool.get('account.journal').search(cr, uid,
                    [('type', '=', 'sale'), ('company_id', '=', company_id)],limit=1)
                if not journal_ids:
                    raise osv.except_osv(_('Error!'),
                        _('Please define sales journal for this company: "%s" (id:%d).') % (sale.company_id.name, sale.company_id.id))
                period_ids = self.pool.get('account.period').find(cr,uid,sale.date_order)
                period_id = self.pool.get('account.period').search(cr,uid,[('company_id','=',company_id)])[0]
                partner_multi_company_ids = partner_multi_company_obj.search(cr, uid, [('company_id','=',company_id),('partner_id','=',sale.company_id.partner_id.id)])
                if not partner_multi_company_ids:
                    raise osv.except_osv(_('Error!'),
                            _('Please define partner multi company for this partner: "%s"') % \
                                (sale.company_id.partner_id.name))
                partner_multi_company_id = partner_multi_company_obj.browse(cr, uid, partner_multi_company_ids[0])
                invoice_vals = {
                        'name': sale.client_order_ref or '',
                        'origin': sale.name,
                        'type': 'out_invoice',
                        'reference': sale.client_order_ref or sale.name,
                        'account_id': partner_multi_company_id.receivable_acc_id.id,
                        'partner_id': sale.company_id.partner_id.id,
                        'journal_id': journal_ids[0],
                        'invoice_line': invoice_line_vals,
                        'currency_id': sale.pricelist_id.currency_id.id,
                        'comment': sale.note,
                        'payment_term': sale.payment_term and sale.payment_term.id or False,
                        'fiscal_position': sale.fiscal_position.id or sale.partner_id.property_account_position.id,
                        'date_invoice': sale.date_order,
                        'company_id': company_id,
                        'user_id': sale.user_id and sale.user_id.id or False,
                        'period_id':period_id,
                        'create_invoice_auto':True
                    }
                invoice_id = invoice_obj.create(cr,uid,invoice_vals)
                wf_service = netsvc.LocalService('workflow')
                wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
                
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'sale.order', ids[0], 'order_confirm', cr)
        return True
sale_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
