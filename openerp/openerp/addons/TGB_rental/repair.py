# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
import netsvc
import datetime
import openerp.addons.decimal_precision as dp
import time
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from dateutil.relativedelta import relativedelta
import pytz

class repair_order(osv.osv):
    _name = 'repair.order'
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('repair.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_total': 0.0,
            }
            sub_price = 0
            for line in order.repair_lines:
                sub_price += line.subprice
            res[order.id]['amount_total'] = sub_price
        return res
    def to_quarantine(self,cr,uid,ids,context={}):
        self.write(cr,uid,ids,{'state':'quarantine','done_date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        for order in self.browse(cr,uid,ids,context=context):
            if order.product_serial:
                self.pool.get('product.product.serial').write(cr,uid,[order.product_serial.id],{'rental_product_id':None,
                                                                                                'sale_product_id':None,
                                                                                                'repair_product_id':order.product_id.id,})
        return True
    def return_product(self,cr,uid,ids,context={}):
        self.write(cr,uid,ids,{'state':'done','done_date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        self.action_create_invoice(cr,uid,ids,False,context=context)
        self.create_picking(cr,uid,ids,context=context)
        return True
    def confirm_order(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{'state':'confirm'})
        self.create_order_picking(cr,uid,ids,context=context)
        return True
    def set_done(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{'state':'done','done_date':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return True
    def cancel_order(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{'state':'cancel'})
        self.action_cancel(cr,uid,ids,context=context)
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for order in self.browse(cr, uid, ids, context=context):
            for pick in order.picking_ids:
                self.pool.get('stock.picking').action_cancel(cr,uid,[pick.id])
            for invoice in order.invoice_ids:
                self.pool.get('account.invoice').action_cancel(cr,uid,[invoice.id])
        return True

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        if context is None:
            context = {}
        journal_ids = self.pool.get('account.journal').search(cr, uid,
            [('type', '=', 'sale'), ('company_id', '=', order.company_id.id)],
            limit=1)
        if not journal_ids:
            raise osv.except_osv(_('Error!'),
                _('Please define sales journal for this company: "%s" (id:%d).') % (order.company_id.name, order.company_id.id))
        invoice_vals = {
            'name': '',
            'origin': order.name,
            'type': 'out_invoice',
            'reference': order.name,
            'account_id': order.partner_id.property_account_receivable.id,
            'partner_id': order.partner_id.id,
            'journal_id': journal_ids[0],
            'invoice_line': [(6, 0, lines)],
            'currency_id': order.pricelist_id.currency_id.id,
            'comment': order.note,
            'payment_term':False,
            'fiscal_position': order.partner_id.property_account_position.id,
            'date_invoice': context.get('date_invoice', False),
            'company_id': order.company_id.id,
            'user_id': False,
            'repair_order_id':order.id,
        }

        # Care for deprecated _inv_get() hook - FIXME: to be removed after 6.1
#        invoice_vals.update(self._inv_get(cr, uid, order, context=context))
        return invoice_vals
    def _make_invoice(self, cr, uid, order, lines, context=None):
        inv_obj = self.pool.get('account.invoice')
        obj_invoice_line = self.pool.get('account.invoice.line')
        if context is None:
            context = {}
        invoiced_sale_line_ids = self.pool.get('repair.order.line').search(cr, uid, [('order_id', '=', order.id)], context=context)
        from_line_invoice_ids = []
        for invoiced_sale_line_id in self.pool.get('repair.order.line').browse(cr, uid, invoiced_sale_line_ids, context=context):
            for invoice_line_id in invoiced_sale_line_id.invoice_line_ids:
                if invoice_line_id.invoice_id.id not in from_line_invoice_ids:
                    from_line_invoice_ids.append(invoice_line_id.invoice_id.id)
        for preinv in order.invoice_ids:
            if preinv.state not in ('cancel',) and preinv.id not in from_line_invoice_ids:
                for preline in preinv.invoice_line:
                    inv_line_id = obj_invoice_line.copy(cr, uid, preline.id, {'invoice_id': False, 'price_unit': -preline.price_unit})
                    lines.append(inv_line_id)
        inv = self._prepare_invoice(cr, uid, order, lines, context=context)
        inv_id = inv_obj.create(cr, uid, inv, context=context)
        data = inv_obj.onchange_payment_term_date_invoice(cr, uid, [inv_id], inv['payment_term'], time.strftime(DEFAULT_SERVER_DATE_FORMAT))
        if data.get('value', False):
            inv_obj.write(cr, uid, [inv_id], data['value'], context=context)
        inv_obj.button_compute(cr, uid, [inv_id])
        return inv_id

    def action_create_invoice(self, cr, uid, ids,date_invoice = False, context=None):
        res = False
        invoices = {}
        invoice_ids = []
        invoice = self.pool.get('account.invoice')
        obj_repair_order_line = self.pool.get('repair.order.line')
        partner_currency = {}
        if context is None:
            context = {}
        # If date was specified, use it as date invoiced, usefull when invoices are generated this month and put the
        # last day of the last month as invoice date
        if date_invoice:
            context['date_invoice'] = date_invoice
        for o in self.browse(cr, uid, ids, context=context):
            currency_id = o.pricelist_id.currency_id.id
            if (o.partner_id.id in partner_currency) and (partner_currency[o.partner_id.id] <> currency_id):
                raise osv.except_osv(
                    _('Error!'),
                    _('You cannot group sales having different currencies for the same partner.'))

            partner_currency[o.partner_id.id] = currency_id
            lines = []
            for line in o.repair_lines:
                lines.append(line.id)
            created_lines = obj_repair_order_line.invoice_line_create(cr, uid, lines)
            if created_lines:
                invoices.setdefault(o.partner_id.id, []).append((o, created_lines))
        if not invoices:
            for o in self.browse(cr, uid, ids, context=context):
                for i in o.invoice_ids:
                    if i.state == 'draft':
                        return i.id
        for val in invoices.values():
            for order, il in val:
                res = self._make_invoice(cr, uid, order, il, context=context)
                invoice_ids.append(res)
                #cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (order.id, res))
        return res

    def date_to_datetime(self, cr, uid, userdate, context=None):
        user_date = datetime.datetime.strptime(userdate, DEFAULT_SERVER_DATE_FORMAT)
        if context and context.get('tz'):
            tz_name = context['tz']
        else:
            tz_name = self.pool.get('res.users').read(cr, 1, uid, ['tz'])['tz']
        if tz_name:
            utc = pytz.timezone('UTC')
            context_tz = pytz.timezone(tz_name)
            user_datetime = user_date + relativedelta(hours=12.0)
            local_timestamp = context_tz.localize(user_datetime, is_dst=False)
            user_datetime = local_timestamp.astimezone(utc)
            return user_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return user_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def _prepare_order_picking(self, cr, uid, order,type, context=None):
        if type == 'out':
             pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
        else:
            pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in')
        date = self.date_to_datetime(cr, uid, order.order_create_date, context)
        return {
            'name': pick_name,
            'origin': order.name,
            'date': date,
            'type':type,
            'state': 'auto',
            #'move_type': order.picking_policy,
            'repair_order_id': order.id,
            'partner_id': order.partner_id.id,
            'note': order.note,
            'invoice_state':'none',
            'company_id': order.company_id.id,
        }

    def _prepare_order_line_move(self, cr, uid, order, line, picking_id, date_planned, context=None):
        location_id = order.shop_id.warehouse_id.lot_stock_id.id
        output_id = order.shop_id.warehouse_id.lot_output_id.id
        return {
            'name': line.product_id.name,
            'picking_id': picking_id,
            'product_id': line.product_id.id,
            'date': date_planned,
            'date_expected': date_planned,
            'product_qty': line.product_uom_qty,
            'product_uom': line.product_uom.id,
            'product_uos_qty': line.product_uom_qty,
            'product_uos':  line.product_uom.id,
           # 'product_packaging': line.product_packaging.id,
            'partner_id': order.partner_id.id,
            'location_id': location_id,
            'location_dest_id': output_id,
            'repair_line_id': line.id,
            'tracking_id': False,
            'state': 'draft',
            #'state': 'waiting',
            'company_id': order.company_id.id,
            'price_unit': line.price
        }
    def _prepare_order_picking_move(self, cr, uid, order,picking_id, date_planned,type='out',context=None):
        if type == 'out':
            output_id = order.shop_id.warehouse_id.lot_stock_id.id
            location_id = order.shop_id.warehouse_id.lot_output_id.id
        else:
            location_id = order.shop_id.warehouse_id.lot_stock_id.id
            output_id = order.shop_id.warehouse_id.lot_output_id.id
        return {
            'name': order.product_id.name,
            'picking_id': picking_id,
            'product_id': order.product_id.id,
            'date': date_planned,
            'date_expected': date_planned,
            'product_qty': 1,
            'product_uom': order.product_id.uom_id.id,
            'product_uos_qty': 1,
            'product_uos':  order.product_id.uom_id.id,
           # 'product_packaging': line.product_packaging.id,
            'partner_id': order.partner_id.id,
            'location_id': location_id,
            'location_dest_id': output_id,
            'tracking_id': False,
            'state': 'draft',
            #'state': 'waiting',
            'company_id': order.company_id.id,
           # 'price_unit': line.price
        }
    def create_picking(self, cr, uid,ids,  context=None):
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        for order in self.browse(cr,uid,ids,context=context):
            picking_id = False
            for line in order.repair_lines:
                date_planned = order.order_create_date
                if line.product_id:
                    if line.product_id.type in ('product', 'consu'):
                        if not picking_id:
                            picking_id = picking_obj.create(cr, uid, self._prepare_order_picking(cr, uid, order,'out', context=context))
                        move_obj.create(cr, uid, self._prepare_order_line_move(cr, uid, order, line, picking_id, date_planned,context=context))
            move_obj.create(cr, uid, self._prepare_order_picking_move(cr, uid, order, picking_id, date_planned,'in',context=context))
            wf_service = netsvc.LocalService("workflow")
            if picking_id:
                wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
        return True
    def create_order_picking(self, cr, uid,ids,context=None):
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        for order in self.browse(cr,uid,ids,context=context):
            picking_id = False
            date_planned = order.order_create_date
            if order.product_id:
                if order.product_id.type in ('product', 'consu'):
                    if not picking_id:
                        picking_id = picking_obj.create(cr, uid, self._prepare_order_picking(cr, uid, order,'in', context=context))
                    move_obj.create(cr, uid, self._prepare_order_picking_move(cr, uid, order,picking_id, date_planned,'out',context=context))
            wf_service = netsvc.LocalService("workflow")
            if picking_id:
                wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
        return True

    def _get_default_shop(self, cr, uid, context=None):
        company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        shop_ids = self.pool.get('sale.shop').search(cr, uid, [('company_id','=',company_id)], context=context)
        if not shop_ids:
            raise osv.except_osv(('Error!'), ('There is no default shop for the current user\'s company!'))
        return shop_ids[0]
    def onchange_shop_id(self, cr, uid, ids, shop_id, context=None):
        v = {}
        if shop_id:
            shop = self.pool.get('sale.shop').browse(cr, uid, shop_id, context=context)
            if shop.pricelist_id.id:
                v['pricelist_id'] = shop.pricelist_id.id
        return {'value': v}

    _columns = {
        'partner_id':fields.many2one('res.partner','Customer',required=True,readonly=True,states={'draft': [('readonly', False)],}),
        'product_id':fields.many2one('product.product','Repair Products',required=True,readonly=True,states={'draft': [('readonly', False)],}),
        'product_serial':fields.many2one('product.product.serial','Repair Products Serial',required=True,readonly=True,states={'draft': [('readonly', False)],}),
        'repair_lines':fields.one2many('repair.order.line','order_id','repair Products',readonly=False,states={'done': [('readonly', True)],'quarantine': [('readonly', True)]}),
        'order_create_date':fields.date('Create date',readonly=True,states={'draft': [('readonly', False)],}),
        'done_date':fields.date('Finish date',readonly=True),
        'invoice_ids':fields.one2many('account.invoice','repair_order_id','Invoice Ids',readonly=True,states={'draft': [('readonly', False)],}),
        'picking_ids':fields.one2many('stock.picking','repair_order_id','Picking Ids',readonly=True,states={'draft': [('readonly', False)],}),
        'amount_total': fields.function(_amount_all, digits=(16,2), string='Total',
            store={
                'repair.order': (lambda self, cr, uid, ids, c={}: ids, ['repair_lines','from_date','to_date'], 10),
                'repair.order.line': (_get_order, ['price'], 10),
            },
            multi='sums'),
        'name': fields.char('Order Reference', size=64, required=True,
            readonly=True, states={'draft': [('readonly', False)]}, select=True),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Pricelist for current sales order."),
        'shop_id': fields.many2one('sale.shop', 'Shop', required=True, readonly=True, states={'draft': [('readonly', False)]}),
         'company_id': fields.related('shop_id','company_id',type='many2one',relation='res.company',string='Company',store=True,readonly=True),
         'state': fields.selection([
            ('draft', 'Draft Quotation'),
            ('confirm', 'Confirm'),
            ('cancel', 'Cancelled'),
            ('repair','Wait for return'),
            ('quarantine','To quarantine'),
            ('done', 'Done'),
            ], 'Status', readonly=True, track_visibility='onchange',),
          'note': fields.text('Remarks'),
    }
    _defaults = {
        'state':'draft',
        'order_create_date':fields.date.context_today,
        'shop_id': _get_default_shop,
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'repair.order'),
    }
    _order = 'id desc'
repair_order()

class repair_order_line(osv.osv):
    _name = 'repair.order.line'
    def _get_line_qty(self, cr, uid, line, context=None):
        return line.product_uom_qty

    def _get_line_uom(self, cr, uid, line, context=None):
        return line.product_uom.id

    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
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
            pu = round(line.price * line.product_uom_qty / uosqty,
                    self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Price'))
        fpos = False
        account_id = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, account_id)
        if not account_id:
            raise osv.except_osv(_('Error!'),
                        _('There is no Fiscal Position defined or Income category account defined for default properties of Product categories.'))
        res = {
            'name': line.product_id.name,
            #'sequence': line.sequence,
            'origin': line.order_id.name,
            'account_id': account_id,
            'price_unit': pu,
            'quantity': uosqty,
           # 'discount': line.discount,
            'uos_id': uos_id,
            'product_id': line.product_id.id or False,
            #'invoice_line_tax_id': [(6, 0, [x.id for x in line.tax_id])],
            'account_analytic_id': False,
        }

        return res
    def invoice_line_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        create_ids = []
        sales = set()
        for line in self.browse(cr, uid, ids, context=context):
            vals = self._prepare_order_line_invoice_line(cr, uid, line, False, context)
            if vals:
                inv_id = self.pool.get('account.invoice.line').create(cr, uid, vals, context=context)
                self.write(cr, uid, [line.id], {'invoice_lines': [(4, inv_id)]}, context=context)
                sales.add(line.order_id.id)
                create_ids.append(inv_id)
        return create_ids

    def onchange_product_id(self, cr, uid, ids, product_id,price=0,product_uom_qty=1, context=None):
        if not product_id:
            return {'value': {'price': 0, 'product_serial': False,}}
        product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
        if not price:
            price = product.list_price
        val = {
            'subprice': price*product_uom_qty,
            'price':price,
            'product_uom':product.uom_id.id,
        }
        return {'value': val}

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.price * line.product_uom_qty
        return res

    _columns = {
        'product_id':fields.many2one('product.product','Repair Products',required=True),
        'product_uom_qty': fields.float('Quantity', digits_compute= dp.get_precision('Product UoS'), required=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure ', required=True),
        'price':fields.float('Price',digits=(16,2)),
        'order_id':fields.many2one('repair.order','Order ID',required=True),
        'move_ids':fields.one2many('stock.move','repair_line_id','Stock moves'),
        'invoice_line_ids':fields.one2many('account.invoice.line','repair_line_id','Invoice lines'),
        'subprice': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
    }
    _defaults = {
        'product_uom_qty':1,
    }
repair_order_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
