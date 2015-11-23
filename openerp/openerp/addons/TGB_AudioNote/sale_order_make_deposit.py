# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class add_sale_deposit_wiz(osv.osv_memory):
    _name='add.sale.deposit.wiz'

    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(add_sale_deposit_wiz, self).default_get(cr, uid, fields, context=context)
        sale_order_id = context.get('active_id')
        if isinstance(sale_order_id, list):
            purchase_order_id = sale_order_id[0]
        active_model = context.get('active_model')
        assert active_model in ('sale.order'), 'Bad context propagation'
        if 'sale_order_id' in fields:
            res.update(sale_order_id=sale_order_id)
        return res

    def confirm(self, cr, uid, ids, context=None):
        for track in self.browse(cr,uid,ids):
            print 'conttext', context
            order_id = self.pool.get('sale.order').browse(cr,uid,context.get('active_id'))
            customer_id = order_id.partner_id.id
            new_track  = self.pool.get('sale.deposit').create(cr,uid,{
                                                                    'customer_id':customer_id,
                                                                    'amount':track.amount,
                                                                    'period_id':track.period_id.id,
                                                                    'journal_id':track.journal_id.id,
                                                                    'sale_order_id':order_id.id,
                                                                        })
        return new_track
    _columns={
        'customer_id':fields.many2one('res.partner','Customer'),
        'amount': fields.float('Total', digits_compute=dp.get_precision('Account'), required=True, ),
        'period_id': fields.many2one('account.period', 'Period', required=True, ),
        'partner_id':fields.many2one('res.partner', 'Partner', change_default=1, readonly=True, ),
        'journal_id':fields.many2one('account.journal', 'Payment Method', required=True, domain=[('type','in',['bank','cash'])]),
        'date':fields.date('Date', readonly=True, select=True, help="Effective date for accounting entries"),
        'sale_order_id':fields.many2one('sale.order','Sale',required=True),
        'cheque_no':fields.char('Cheque No',size=100,),
    }

    def _get_period(self, cr, uid, context=None):
        if context is None: context = {}
        if context.get('period_id', False):
            return context.get('period_id')
        ctx = dict(context, account_period_prefer_normal=True)
        periods = self.pool.get('account.period').find(cr, uid, context=ctx)
        return periods and periods[0] or False
    _defaults={
        'period_id': _get_period,
    }
add_sale_deposit_wiz()