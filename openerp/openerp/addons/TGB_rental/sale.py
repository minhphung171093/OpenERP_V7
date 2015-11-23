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
class sale_order(osv.osv):
    _inherit = 'sale.order'
    def _prepare_order_picking(self, cr, uid, order, context=None):
        res = super(sale_order,self)._prepare_order_picking(cr,uid,order,context=context)
        res['contact_address'] = order.partner_shipping_id.contact_address
        return res
    _columns = {
       'state': fields.selection([
            ('draft', 'Draft Quotation'),
            ('sent', 'Quotation Sent'),
            ('cancel', 'Cancelled'),
            ('waiting_date', 'Waiting Schedule'),
            ('progress', 'Sales Order'),
            ('manual', 'Sale to Invoice'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ], 'Status', readonly=True, track_visibility='onchange',
            help="Gives the status of the quotation or sales order. \nThe exception status is automatically set when a cancel operation occurs in the processing of a document linked to the sales order. \nThe 'Waiting Schedule' status is set when the invoice is confirmed but waiting for the scheduler to run on the order date.", select=True,

            states={'draft': [('readonly', False)]}),
    }
    def create(self,cr,uid,vals,context={}):
        ids = super(sale_order,self).create(cr,uid,vals,context=context)
        wf_service = netsvc.LocalService("workflow")
        if vals.get('state') in ['manual','done','progress']:
            #self.action_ship_create(cr,uid,[ids],context=context)
            wf_service.trg_validate(uid, 'sale.order', ids, 'order_confirm', cr)
        return ids
sale_order()

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    _columns = {
        'state': fields.selection([('cancel', 'Cancelled'),('draft', 'Draft'),('confirmed', 'Confirmed'),('exception', 'Exception'),('done', 'Done')], 'Status', required=True, readonly=True,states={'draft': [('readonly', False)]},
                help='* The \'Draft\' status is set when the related sales order in draft status. \
                    \n* The \'Confirmed\' status is set when the related sales order is confirmed. \
                    \n* The \'Exception\' status is set when the related sales order is set as exception. \
                    \n* The \'Done\' status is set when the sales order line has been picked. \
                    \n* The \'Cancelled\' status is set when a user cancel the sales order related.'),
    }

sale_order_line()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _columns = {
        'contact_address': fields.char(string="Delivery Address"),
        }
stock_picking()
class stock_picking(osv.osv):
    _inherit = 'stock.picking.out'
    _columns = {
        'contact_address': fields.char(string="Delivery Address"),
        }
stock_picking()
class stock_picking(osv.osv):
    _inherit = 'stock.picking.in'
    _columns = {
        'contact_address': fields.char(string="Delivery Address"),
        }
stock_picking()

class product_product_serial(osv.osv):
    _name = 'product.product.serial'
    def _get_product_id(self, cr, uid, ids, field_name, args, context=None):
        res = dict.fromkeys(ids, False)
        for this in self.browse(cr, uid, ids, context=context):
            if this.sale_product_id:
                 res[this.id] = this.sale_product_id.id
            elif this.rental_product_id:
                 res[this.id] = this.rental_product_id.id
            elif this.repair_product_id:
                 res[this.id] = this.repair_product_id.id
        return res
    _columns = {
        'sale_product_id': fields.many2one('product.product','Sale products'),
        'rental_product_id': fields.many2one('product.product','Rental products'),
        'repair_product_id': fields.many2one('product.product','Repair products'),
        'product_id': fields.function(_get_product_id, string='Invoiced', type='many2one',relation="product.product",
            store={
                'product.product.serial': (lambda self,cr,uid,ids,ctx=None: ids, ['sale_product_id','rental_product_id','repair_product_id'], 10)}),
        'name':fields.char('Serial Number',size=128),
        'warranty_number':fields.char('Serial Number',size=128),
        'state':fields.selection([('available','Available'),('unavailable','Unavailable')],'State')
        }
    def create(self,cr,uid,vals,context=None):
        if context.get('rental_product_id'):
            vals['rental_product_id'] = context.get('rental_product_id')
        return super(product_product_serial,self).create(cr,uid,vals,context=context)
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name'], context=context)
        res = []
        for record in reads:
            res.append((record['id'], record['name']))
        return res
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Serial Number have to be unique!'),
    ]
product_product_serial()

class product_product(osv.osv):
    _inherit = 'product.product'
    def _get_not_available_serial(self,cr,uid,product_id,from_date,to_date,order_id=False):
        not_available_serial = self.pool.get('rental.order.line').search(cr,uid,[('product_id','=',product_id),
                                                                                 ('order_id.id','!=',order_id),
                                                                                 ('order_id.state','!=','draft'),
                                                                                ('order_id.from_date','<=',to_date),
                                                                                 ('order_id.to_date','>=',from_date)])
        #ids = self.pool.get('product.product.serial').search(cr,uid,[('rental_product_id','=',product_id),
        #                                                             ('id','not in',not_available_serial)])
        return [line.product_serial.id for line in self.pool.get('rental.order.line').browse(cr,uid,not_available_serial)]
    _columns = {
        'sale_product_ids': fields.one2many('product.product.serial','sale_product_id','Sale products'),
        'rental_product_ids': fields.one2many('product.product.serial','rental_product_id','Rental products'),
        'repair_product_ids': fields.one2many('product.product.serial','repair_product_id','Repair products'),
        'rental_price':fields.one2many('product.product.rentalprice','product_id','Rental Price')
        }
product_product()

class product_product_rentalprice(osv.osv):
    _name = 'product.product.rentalprice'
    _columns = {
        'product_id':fields.many2one('product.product','Product Id'),
        'days':fields.integer('Number of day'),
        'price':fields.float('Price',digits=(16,0)),
    }
    _order = "days"
product_product_rentalprice()

class rental_order(osv.osv):
    _name = 'rental.order'
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('rental.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'number_of_day': 0,
                'amount_total': 0.0,
            }
            sub_price = 0
            from_date = datetime.datetime.strptime(order.from_date,"%Y-%m-%d")
            to_date = datetime.datetime.strptime(order.to_date,"%Y-%m-%d")
            for line in order.rental_lines:
                sub_price += line.price
            res[order.id]['number_of_day'] = (to_date-from_date).days+1
            res[order.id]['amount_total'] = sub_price * res[order.id]['number_of_day']
        return res

    def onchange_day(self,cr,uid,ids,from_date,to_date,context={}):
        val = {}
        if from_date and to_date:
            from_date = datetime.datetime.strptime(from_date,"%Y-%m-%d")
            to_date = datetime.datetime.strptime(to_date,"%Y-%m-%d")
            number_of_day = (to_date-from_date).days+1
            val['number_of_day'] = number_of_day
        return {'value':val}

    def confirm_order(self,cr,uid,ids,context=None):
        for order in self.browse(cr,uid,ids,context=context):
            self.check_available(cr,uid,ids,order.from_date,order.to_date,context=context)
        self.write(cr,uid,ids,{'state':'manual'})
        self.create_picking(cr,uid,ids,'out',context=context)
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
            'rental_order_id':order.id,
        }

        # Care for deprecated _inv_get() hook - FIXME: to be removed after 6.1
#        invoice_vals.update(self._inv_get(cr, uid, order, context=context))
        return invoice_vals
    def _make_invoice(self, cr, uid, order, lines, context=None):
        inv_obj = self.pool.get('account.invoice')
        obj_invoice_line = self.pool.get('account.invoice.line')
        if context is None:
            context = {}
        invoiced_sale_line_ids = self.pool.get('rental.order.line').search(cr, uid, [('order_id', '=', order.id)], context=context)
        from_line_invoice_ids = []
        for invoiced_sale_line_id in self.pool.get('rental.order.line').browse(cr, uid, invoiced_sale_line_ids, context=context):
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

    def action_create_invoice(self, cr, uid, ids,date_invoice = False,number_of_date=1, context=None):
        res = False
        invoices = {}
        invoice_ids = []
        invoice = self.pool.get('account.invoice')
        obj_rental_order_line = self.pool.get('rental.order.line')
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
            for line in o.rental_lines:
                lines.append(line.id)
            created_lines = obj_rental_order_line.invoice_line_create(cr, uid, lines,number_of_date)
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
    def create_invoice(self,cr,uid,ids,context=None):
        for order in self.browse(cr,uid,ids,context=context):
            self.write(cr,uid,[order.id],{'state':'wait','invoiced_date':order.to_date})
            self.action_create_invoice(cr,uid,ids,date_invoice=False,number_of_date=order.number_of_day,context=context)
        return True
    def check_available(self,cr,uid,ids,from_date,to_date,context={}):
        for order in self.browse(cr,uid,ids,context=context):
            for line in order.rental_lines:
                res = self.pool.get('product.product')._get_not_available_serial(cr,uid,line.product_id.id,from_date,to_date,order.id)
                if line.product_serial.id in res:
                    raise osv.except_osv(_('Error'),_('Serial is not available'))
        return True
    def extend_order(self,cr,uid,ids,context=None):
        for order in self.browse(cr,uid,ids,context=context):
            self.check_available(cr,uid,ids,order.from_date,order.extend_date,context=context)
            if order.state not in ['wait','manual']:
                raise osv.except_osv(('Error'),('Can only extend confirmed order'))
            if order.extend_date and order.extend_date > order.to_date:
                from_date = datetime.datetime.strptime(order.to_date,"%Y-%m-%d")
                to_date = datetime.datetime.strptime(order.extend_date,"%Y-%m-%d")
                number_of_date = (to_date-from_date).days
                if not order.invoice_ids:
                    from_date = datetime.datetime.strptime(order.from_date,"%Y-%m-%d")
                    number_of_date = (to_date-from_date).days+1
                self.write(cr,uid,[order.id],{'state':'wait','to_date':order.extend_date,'invoiced_date':order.extend_date,})
            else:
                raise osv.except_osv(('Error'),('Extend date can not be earlier than current due date'))
            self.action_create_invoice(cr,uid,ids,date_invoice=order.extend_date,number_of_date=number_of_date,context=context)
        return True

    def receive_product(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{'state':'done'})
        self.create_picking(cr,uid,ids,'in',context=context)
        return True
    def date_to_datetime(self, cr, uid, userdate, context=None):
        """ Convert date values expressed in user's timezone to
        server-side UTC timestamp, assuming a default arbitrary
        time of 12:00 AM - because a time is needed.

        :param str userdate: date string in in user time zone
        :return: UTC datetime string for server-side use
        """
        # TODO: move to fields.datetime in server after 7.0
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
        if type == 'out':
            date = self.date_to_datetime(cr, uid, order.from_date, context)
        else:
            date = self.date_to_datetime(cr, uid, order.to_date, context)
        return {
            'name': pick_name,
            'origin': order.name,
            'date': date,
            'type':type,
            'state': 'auto',
            #'move_type': order.picking_policy,
            'rental_order_id': order.id,
            'partner_id': order.partner_id.id,
            'note': order.note,
            'invoice_state':'none',
            'company_id': order.company_id.id,
        }
    def _prepare_order_line_move(self, cr, uid, order, line, picking_id, date_planned,type='out', context=None):
        if type=='out':
            location_id = order.shop_id.warehouse_id.lot_stock_id.id
            output_id = order.shop_id.warehouse_id.lot_output_id.id
        else:
            output_id = order.shop_id.warehouse_id.lot_stock_id.id
            location_id = order.shop_id.warehouse_id.lot_output_id.id
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
            'rental_line_id': line.id,
            'tracking_id': False,
            'state': 'draft',
            #'state': 'waiting',
            'company_id': order.company_id.id,
            'price_unit': line.price
        }
    def create_picking(self, cr, uid,ids, type='out', context=None):
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        for order in self.browse(cr,uid,ids,context=context):
            picking_id = False
            for line in order.rental_lines:
                date_planned = order.from_date
                if line.product_id:
                    if line.product_id.type in ('product', 'consu'):
                        if not picking_id:
                            picking_id = picking_obj.create(cr, uid, self._prepare_order_picking(cr, uid, order,type, context=context))
                        move_obj.create(cr, uid, self._prepare_order_line_move(cr, uid, order, line, picking_id, date_planned,type, context=context))
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
        'rental_lines':fields.one2many('rental.order.line','order_id','Rental Products',readonly=True,states={'draft': [('readonly', False)],}),
        'order_create_date':fields.date('Create date',readonly=True,states={'draft': [('readonly', False)],}),
        'from_date':fields.date('From date',required=True,readonly=True,states={'draft': [('readonly', False)],}),
        'to_date':fields.date('To date',required=True,readonly=True,states={'draft': [('readonly', False)],}),
        'extend_date':fields.date('Extend date',readonly=False,states={'done': [('readonly', True)],}),
        'number_of_day':fields.function(_amount_all,type='integer',size=12,string='Number of day',
                     store={
                'rental.order': (lambda self, cr, uid, ids, c={}: ids, ['from_date','to_date'], 10),
            },multi='sums'),
        'invoiced_date':fields.date('Invoiced date',readonly=True),
        'invoice_ids':fields.one2many('account.invoice','rental_order_id','Invoice Ids',readonly=True,states={'draft': [('readonly', False)],}),
        'picking_ids':fields.one2many('stock.picking','rental_order_id','Picking Ids',readonly=True,states={'draft': [('readonly', False)],}),
         'amount_total': fields.function(_amount_all, digits=(16,2), string='Total',
            store={
                'rental.order': (lambda self, cr, uid, ids, c={}: ids, ['rental_lines','from_date','to_date'], 10),
                'rental.order.line': (_get_order, ['price'], 10),
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
            ('manual', 'Rental to Invoice'),
            ('wait','Wait for return'),
            ('done', 'Done'),
            ], 'Status', readonly=True, track_visibility='onchange',),
          'note': fields.text('Remarks'),
    }
    _defaults = {
        'state':'draft',
        'order_create_date':fields.date.context_today,
        'shop_id': _get_default_shop,
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'rental.order'),
    }
    _order = 'id desc'
rental_order()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _columns = {
        'rental_order_id':fields.many2one('rental.order','Rental Order Id'),
        'repair_order_id':fields.many2one('repair.order','Repair Order Id'),
    }
stock_picking()
class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
        'rental_order_id':fields.many2one('rental.order','Rental Order Id'),
        'repair_order_id':fields.many2one('repair.order','Repair Order Id'),
    }
account_invoice()
class rental_order_line(osv.osv):
    _name = 'rental.order.line'
    def _get_line_qty(self, cr, uid, line, context=None):
        return line.product_uom_qty

    def _get_line_uom(self, cr, uid, line, context=None):
        return line.product_uom.id

    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False,number_of_date=1, context=None):
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
            'price_unit': pu*number_of_date,
            'quantity': uosqty,
           # 'discount': line.discount,
            'uos_id': uos_id,
            'product_id': line.product_id.id or False,
            #'invoice_line_tax_id': [(6, 0, [x.id for x in line.tax_id])],
            'account_analytic_id': False,
            'rental_line_id':line.id,
        }

        return res
    def invoice_line_create(self, cr, uid, ids,number_of_date, context=None):
        if context is None:
            context = {}

        create_ids = []
        sales = set()
        for line in self.browse(cr, uid, ids, context=context):
            vals = self._prepare_order_line_invoice_line(cr, uid, line, False,number_of_date, context)
            if vals:
                inv_id = self.pool.get('account.invoice.line').create(cr, uid, vals, context=context)
                self.write(cr, uid, [line.id], {'invoice_lines': [(4, inv_id)]}, context=context)
                sales.add(line.order_id.id)
                create_ids.append(inv_id)
        return create_ids
    def onchange_product_id(self, cr, uid, ids, product_id,number_of_day=1,from_date=False,to_date=False,product_uom_qty=1, context=None):
        if not product_id:
            return {'value': {'price': 0, 'product_serial': False,}}
        product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
        best_days = 0
        best_price = 0
        for price in product.rental_price:
            if price.days <= number_of_day and best_days <= price.days:
                best_days = price.days
                best_price = price.price
        product_serial_available = self.pool.get('product.product')._get_not_available_serial(cr,uid,product_id,from_date,to_date)
        domain = {'product_serial':[('rental_product_id','=',product_id),
                                    ('id','!=',product_serial_available),
                                    ]}
        print 'best_price',best_price, 'number of day',number_of_day
        val = {
            'price': best_price*number_of_day*product_uom_qty,
            'product_serial':False,
            'product_uom':product.uom_id.id,
        }
        return {'value': val,'domain':domain}
    _columns = {
        'product_id':fields.many2one('product.product','Rental Products',required=True),
        'product_serial':fields.many2one('product.product.serial','Product Serial',required=True),
        'product_uom_qty': fields.float('Quantity', digits_compute= dp.get_precision('Product UoS'), required=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure ', required=True),
        'price':fields.float('Price',digits=(16,2)),
        'order_id':fields.many2one('rental.order','Order ID',required=True),
        'move_ids':fields.one2many('stock.move','rental_line_id','Stock moves'),
        'invoice_line_ids':fields.one2many('account.invoice.line','rental_line_id','Invoice lines'),
    }
    _defaults = {
        'product_uom_qty':1,
    }
rental_order_line()
class stock_move(osv.osv):
    _inherit = 'stock.move'
    _columns = {
        'rental_line_id':fields.many2one('rental.order.line','Rental Line Id'),
        'repair_line_id':fields.many2one('repair.order.line','Rental Line Id'),
    }
stock_move()
class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'
    _columns = {
        'rental_line_id':fields.many2one('rental.order.line','Rental Line Id'),
        'repair_line_id':fields.many2one('repair.order.line','Rental Line Id'),
    }
account_invoice_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
