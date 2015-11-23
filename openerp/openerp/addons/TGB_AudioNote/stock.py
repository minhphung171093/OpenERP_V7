# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def _get_invoice_reference(self, cr, uid, ids, a, b, context=None):
        res = {}
        for picking in self.browse(cr, uid, ids):
            if picking.origin and len(picking.origin)>1:
                invoice_ids = self.pool.get('account.invoice').search(cr,uid,[('origin','=',picking.origin)])
                if invoice_ids and len(invoice_ids)>0:
                    res[picking.id] = self.pool.get('account.invoice').browse(cr,uid,invoice_ids[0]).number
        return res


    _columns = {
        'invoice_reference': fields.function(_get_invoice_reference, size=128, type='char', string="Invoice Ref",),
    }


stock_picking()


class stock_picking_out2(osv.osv):
    _inherit = "stock.picking.out"

    def _get_invoice_reference(self, cr, uid, ids, a, b, context=None):
        res = {}
        for picking in self.browse(cr, uid, ids):
            if picking.origin and len(picking.origin)>1:
                invoice_ids = self.pool.get('account.invoice').search(cr,uid,[('origin','=',picking.origin)])
                if invoice_ids and len(invoice_ids)>0:
                    res[picking.id] = self.pool.get('account.invoice').browse(cr,uid,invoice_ids[0]).number
        return res


    _columns = {
        'invoice_reference': fields.function(_get_invoice_reference, size=128, type='char', string="Invoice Ref",),
    }


stock_picking_out2()


class stock_picking_in2(osv.osv):
    _inherit = "stock.picking.in"

    def _get_invoice_reference(self, cr, uid, ids, a, b, context=None):
        res = {}
        for picking in self.browse(cr, uid, ids):
            if picking.origin and len(picking.origin)>1:
                invoice_ids = self.pool.get('account.invoice').search(cr,uid,[('origin','=',picking.origin)])
                if invoice_ids and len(invoice_ids)>0:
                    res[picking.id] = self.pool.get('account.invoice').browse(cr,uid,invoice_ids[0]).number
        return res


    _columns = {
        'invoice_reference': fields.function(_get_invoice_reference, size=128, type='char', string="Invoice Ref",),
    }


stock_picking_in2()






