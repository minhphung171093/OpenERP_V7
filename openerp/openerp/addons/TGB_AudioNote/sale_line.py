# -*- coding: utf-8 -*-
__author__ = 'Phamkr'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, \
    float_compare


class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'


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
        if not line.invoiced:
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
                pu = line.price_unit * line.product_uom_qty / uosqty
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
                'invoice_line_tax_id': [(6, 0, [x.id for x in line.tax_id])],
                'account_analytic_id': line.order_id.project_id and line.order_id.project_id.id or False,
            }

        return res



    def _product_available(self,cr,uid,ids,a,b,context={}):
        res = {}
        for line in self.browse(cr,uid,ids):
            product_id  = line.product_id
            qty_on_hand = self.pool.get('product.product').get_product_available(cr,uid,[product_id.id])
            if qty_on_hand:
                res[line.id] = qty_on_hand[product_id.id]
            else:
                res[line.id] = 0
        return res

    # def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
    #     tax_obj = self.pool.get('account.tax')
    #     cur_obj = self.pool.get('res.currency')
    #     res = {}
    #     if context is None:
    #         context = {}
    #     for line in self.browse(cr, uid, ids, context=context):
    #         res[line.id]={
    #             'price_subtotal':0,
    #             'taxed_subtotal':0,
    #         }
    #         price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
    #         taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.product_id, line.order_id.partner_id)
    #         cur = line.order_id.pricelist_id.currency_id
    #         res[line.id]['price_subtotal'] = cur_obj.round(cr, uid, cur, taxes['total'])
    #         res[line.id]['taxed_subtotal'] = cur_obj.round(cr, uid, cur, line.product_uom_qty*line.price_taxed)
    #     return res


    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.product_id, line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id]= cur_obj.round(cr, uid, cur, taxes['total'])
            print 'taxes', taxes
            self.write(cr,uid,line.id,{'subtotal_template':res[line.id],
                                       'total_temp':taxes['total_included']})
        return res


    # def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
    #     tax_obj = self.pool.get('account.tax')
    #     cur_obj = self.pool.get('res.currency')
    #     res = {}
    #     if context is None:
    #         context = {}
    #     for line in self.browse(cr, uid, ids, context=context):
    #         if line.inclusive and line.tax_id:
    #             price = (line.price_unit * (1 - (line.discount or 0.0) / 100.0))  / (1+line.tax_id[0].amount)
    #             taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.order_id.partner_invoice_id.id, line.product_id, line.order_id.partner_id)
    #         else:
    #             price = (line.price_unit * (1 - (line.discount or 0.0) / 100.0))
    #             taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.order_id.partner_invoice_id.id, line.product_id, line.order_id.partner_id)
    #         cur = line.order_id.pricelist_id.currency_id
    #         res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
    #     return res



    # def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
    #         uom=False, qty_uos=0, uos=False, name='', partner_id=False,
    #         lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
    #     print 'check in our on change product'
    #     context = context or {}
    #     lang = lang or context.get('lang',False)
    #     if not  partner_id:
    #         raise osv.except_osv(_('No Customer Defined!'), _('Before choosing a product,\n select a customer in the sales form.'))
    #     warning = {}
    #     product_uom_obj = self.pool.get('product.uom')
    #     partner_obj = self.pool.get('res.partner')
    #     product_obj = self.pool.get('product.product')
    #     context = {'lang': lang, 'partner_id': partner_id}
    #     if partner_id:
    #         lang = partner_obj.browse(cr, uid, partner_id).lang
    #     context_partner = {'lang': lang, 'partner_id': partner_id}
    #
    #     if not product:
    #         return {'value': {'th_weight': 0,
    #             'product_uos_qty': qty}, 'domain': {'product_uom': [],
    #                'product_uos': []}}
    #     if not date_order:
    #         date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
    #
    #     result = {}
    #     warning_msgs = ''
    #     product_obj = product_obj.browse(cr, uid, product, context=context_partner)
    #
    #     uom2 = False
    #     if uom:
    #         uom2 = product_uom_obj.browse(cr, uid, uom)
    #         if product_obj.uom_id.category_id.id != uom2.category_id.id:
    #             uom = False
    #     if uos:
    #         if product_obj.uos_id:
    #             uos2 = product_uom_obj.browse(cr, uid, uos)
    #             if product_obj.uos_id.category_id.id != uos2.category_id.id:
    #                 uos = False
    #         else:
    #             uos = False
    #     fpos = fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position) or False
    #     if update_tax: #The quantity only have changed
    #         result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_obj.taxes_id)
    #
    #     if not flag:
    #         result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]
    #         if product_obj.description_sale:
    #             result['name'] += '\n'+product_obj.description_sale
    #     domain = {}
    #     if (not uom) and (not uos):
    #         result['product_uom'] = product_obj.uom_id.id
    #         if product_obj.uos_id:
    #             result['product_uos'] = product_obj.uos_id.id
    #             result['product_uos_qty'] = qty * product_obj.uos_coeff
    #             uos_category_id = product_obj.uos_id.category_id.id
    #         else:
    #             result['product_uos'] = False
    #             result['product_uos_qty'] = qty
    #             uos_category_id = False
    #         result['th_weight'] = qty * product_obj.weight
    #         domain = {'product_uom':
    #                     [('category_id', '=', product_obj.uom_id.category_id.id)],
    #                     'product_uos':
    #                     [('category_id', '=', uos_category_id)]}
    #     elif uos and not uom: # only happens if uom is False
    #         result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
    #         result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
    #         result['th_weight'] = result['product_uom_qty'] * product_obj.weight
    #     elif uom: # whether uos is set or not
    #         default_uom = product_obj.uom_id and product_obj.uom_id.id
    #         q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
    #         if product_obj.uos_id:
    #             result['product_uos'] = product_obj.uos_id.id
    #             result['product_uos_qty'] = qty * product_obj.uos_coeff
    #         else:
    #             result['product_uos'] = False
    #             result['product_uos_qty'] = qty
    #         result['th_weight'] = q * product_obj.weight        # Round the quantity up
    #
    #     if not uom2:
    #         uom2 = product_obj.uom_id
    #     # get unit price
    #
    #     if not pricelist:
    #         warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
    #                 'Please set one before choosing a product.')
    #         warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
    #     else:
    #         price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
    #                 product, qty or 1.0, partner_id, {
    #                     'uom': uom or result.get('product_uom'),
    #                     'date': date_order,
    #                     })[pricelist]
    #         product_uom_qty = result.get('product_uom_qty') or False
    #         price_taxed = price
    #
    #         if result.get('tax_id'):
    #             for c in self.pool.get('account.tax').compute_all(cr, uid, self.pool.get('account.tax').browse(cr,uid,result['tax_id']),price,1, product_uom_qty, product, partner_id)['taxes']:
    #                 price_taxed += c.get('amount', 0.0)
    #
    #         result.update({'price_taxed': price_taxed})
    #         if price is False:
    #             warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
    #                     "You have to change either the product, the quantity or the pricelist.")
    #
    #             warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
    #         else:
    #             result.update({'price_unit': price})
    #
    #     if warning_msgs:
    #         warning = {
    #                    'title': _('Configuration Error!'),
    #                    'message' : warning_msgs
    #                 }
    #     return {'value': result, 'domain': domain, 'warning': warning}

    def _tax_reverse(self,cr,uid,taxed_price,taxes):
        percent_amount = 0
        fixed_amount = 0
        for tax in taxes:
            if tax.type=='percent':
                percent_amount += tax.amount

            elif tax.type=='fixed':
                fixed_amount += tax.amount
        unit_price = (taxed_price-fixed_amount)/(1+percent_amount)
        return unit_price

    def taxed_price_change(self, cr, uid, ids, taxed_price,price_unit, tax_id,context=None):
        if tax_id:
            tax_obj = self.pool.get('account.tax').browse(cr,uid,tax_id[0][2])
            unit_price = self._tax_reverse(cr,uid,taxed_price,tax_obj)
            if round(unit_price,1)!=round(price_unit,1):
                return {'value':{'price_unit':unit_price}}
        return True

    def price_unit_change(self, cr, uid, ids, price_unit,taxed_price,tax_id,product_uom_qty,product_id,partner_id,context=None):
        price_taxed = price_unit
        if tax_id and price_unit!=0:
            tax_obj = self.pool.get('account.tax').browse(cr,uid,tax_id[0][2])
            for c in self.pool.get('account.tax').compute_all(cr, uid, tax_obj,price_unit,1, product_uom_qty, product_id, partner_id)['taxes']:
                price_taxed += c.get('amount', 0.0)
            if round(price_taxed,1)!=round(taxed_price,1):
                print 'return value', price_taxed, taxed_price
                return {'value':{'price_taxed':price_taxed}}
        return True

    def price_unit_change2(self, cr, uid, ids, price_unit,tax_id,product_uom_qty,product_id,partner_id,discount,currency_id,context=None):
        subtotal_template=0
        tax_ids = tax_id[0][2]
        if price_unit and tax_id:
            cur_obj = self.pool.get('res.currency')
            tax_obj = self.pool.get('account.tax')
            price = price_unit * (1 - (discount or 0.0) / 100.0)
            taxes = tax_obj.compute_all(cr, uid, tax_obj.browse(cr,uid,tax_ids), price, product_uom_qty, product_id, partner_id)
            cur = cur_obj.browse(cr,uid,currency_id)
            subtotal_template= cur_obj.round(cr, uid, cur, taxes['total'])
        return {'value':{'subtotal_template':subtotal_template}}

    def subtotal_template_change(self, cr, uid, ids, subtotal_template,tax_id,product_uom_qty,product_id,partner_id,discount,currency_id,context=None):
        tax_ids = tax_id[0][2]
        price = subtotal_template/product_uom_qty
        if len(tax_ids)>1:
            raise osv.except_osv(_('Too many taxes!'),_("Manual subtotal only valid with 1 working tax!"))
        print 'tax_id', tax_id, 'whatttttttttt theeeeeeeeeeeeeee fuckkkkkkkkkkkkkkkkkkkkkk'
        if subtotal_template and len(tax_ids)>0:
            cur_obj = self.pool.get('res.currency')
            tax_obj = self.pool.get('account.tax')
            tax = tax_obj.browse(cr,uid,tax_ids[0])
            tax_inclusive = tax.price_include
            tax_type = tax.type
            if tax_type=='percent':
                if tax_inclusive:
                    price = float(subtotal_template)*(1+tax.amount)/float(product_uom_qty)
                    print 'price', price
                else:
                    price = (float(subtotal_template)/float(product_uom_qty))/(1+tax.amount)
                    print 'price', price
            elif tax_type=='fixed':
                price = float(subtotal_template)/float(product_uom_qty) - tax.amount*product_uom_qty
            else:
                raise osv.except_osv(_('Unsupported Taxes!'),_("Manual subtotal only supported for percentage and fixed taxes !"))
        else:
            price = float(subtotal_template)/float(product_uom_qty)
            print 'price', price, subtotal_template
        return {'value':{'price_unit':price}}


    def total_temp_change(self, cr, uid, ids, total_temp,tax_id,product_uom_qty,product_id,partner_id,discount,currency_id,context=None):
        tax_ids = tax_id[0][2]
        price = total_temp/product_uom_qty
        if len(tax_ids)>1:
            raise osv.except_osv(_('Too many taxes!'),_("Manual subtotal only valid with 1 working tax!"))
        print 'tax_id', tax_id, 'whatttttttttt theeeeeeeeeeeeeee fuckkkkkkkkkkkkkkkkkkkkkk'
        if total_temp and len(tax_ids)>0:
            tax_obj = self.pool.get('account.tax')
            tax = tax_obj.browse(cr,uid,tax_ids[0])
            tax_inclusive = tax.price_include
            tax_type = tax.type
            if tax_type=='percent':
                if tax_inclusive:
                    price = float(total_temp)/float(product_uom_qty)
                else:
                    price = (float(total_temp)/float(product_uom_qty))/(1+tax.amount)
            elif tax_type=='fixed':
                price = float(total_temp)/float(product_uom_qty) - tax.amount*product_uom_qty
            else:
                raise osv.except_osv(_('Unsupported Taxes!'),_("Manual subtotal only supported for percentage and fixed taxes !"))
        else:
            price = float(total_temp)/float(product_uom_qty)
            print 'price', price, total_temp
        return {'value':{'price_unit':price}}



    def inclusive_change(self, cr, uid, ids,inclusive,tax_id):
        # print "inclusive change", inclusive, tax_id
        # for taxes in tax_id:
        #     for tax in taxes:
        #         if type(tax) == list:
        #             tax_id = tax
        # print 'tax', tax_id
        # if inclusive:
        #     tax_write = self.pool.get('account.tax').write(cr,uid,tax_id,{'price_include':True})
        # else:
        #     self.pool.get('account.tax').write(cr,uid,12,{'price_include':False})
        return True

    _columns = {
        'qty_available': fields.function(_product_available,
            type='float',  digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Quantity On Hand',
            help="Current quantity of products.\n"
                 "In a context with a single Stock Location, this includes "
                 "goods stored at this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods stored in the Stock Location of this Warehouse, or any "
                 "of its children.\n"
                 "In a context with a single Shop, this includes goods "
                 "stored in the Stock Location of the Warehouse of this Shop, "
                 "or any of its children.\n"
                 "Otherwise, this includes goods stored in any Stock Location "
                 "with 'internal' type."),
        'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal',
                                          digits_compute=dp.get_precision('Sale Price')),
        # 'taxed_subtotal': fields.function(_amount_line, method=True, string='Taxed Subtotal',
        #                                   digits_compute=dp.get_precision('Sale Price'),multi='subtotal'),
        'price_unit': fields.float('Unit Price', required=True, readonly=True,digits=(16,12), states={'draft': [('readonly', False)]}),

        'price_taxed': fields.float('Taxed Price', digits_compute= dp.get_precision('Product Price'), readonly=True, states={'draft': [('readonly', False)]}),
        'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], change_default=True),
        'tgb_length':fields.related('product_id','tgb_length',type='char',size=20,string='Length',readonly=True),
        'inclusive': fields.boolean( 'Tax Inclusive',),
        'subtotal_template':fields.float('Subtotal'),
        'total_temp':fields.float('Total'),
        'suggested_price':fields.related('product_id','suggested_price',type='float',readonly=True,string='Suggested Price'),

    }
    _defaults={
        'inclusive':False,
    }

sale_order_line()
