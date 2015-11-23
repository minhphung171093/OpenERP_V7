__author__ = 'Son'
# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp


class account_invoice(osv.osv):
    _inherit='account.invoice'
    _columns={
        'total_payment_fee':fields.float('Total Payment Fee', digits_compute=dp.get_precision('Account') ,readonly=True),
        'tax_line': fields.one2many('account.invoice.tax', 'invoice_id', 'Tax Lines', readonly=False, states={'draft':[('readonly',False)]}),
        'sale_person_id':fields.many2one('res.users','Sale Person in Charge')
    }

    _defaults={
        'total_payment_fee':0,
    }

account_invoice()



class account_invoice_line(osv.osv):
    _inherit='account.invoice.line'
    _columns={
        'price_unit': fields.float('Unit Price', required=True, digits=(16,12)),
    }
account_invoice_line()

