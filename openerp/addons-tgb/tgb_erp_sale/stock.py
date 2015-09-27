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
import openerp.addons.decimal_precision as dp
import os
from openerp import modules

class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def _prepare_invoice_line(self, cr, uid, group, picking, move_line, invoice_id,
        invoice_vals, context=None):
        """ Builds the dict containing the values for the invoice line
            @param group: True or False
            @param picking: picking object
            @param: move_line: move_line object
            @param: invoice_id: ID of the related invoice
            @param: invoice_vals: dict used to created the invoice
            @return: dict that will be used to create the invoice line
        """
        product_multi_company_obj = self.pool.get('product.multi.company')
        if group:
            name = (picking.name or '') + '-' + move_line.name
        else:
            name = move_line.name
        origin = move_line.picking_id.name or ''
        if move_line.picking_id.origin:
            origin += ':' + move_line.picking_id.origin

        if invoice_vals['type'] in ('out_invoice', 'out_refund'):
            account_id = move_line.product_id.property_account_income.id
            if not account_id:
                account_id = move_line.product_id.categ_id.\
                        property_account_income_categ.id
        else:
            account_id = move_line.product_id.property_account_expense.id
            if not account_id:
                account_id = move_line.product_id.categ_id.\
                        property_account_expense_categ.id
        
        #Phung them tinh nang kiem tra company de set account cho dung company
        if move_line.product_id.company_id.id != picking.company_id.id and invoice_vals['type'] in ('out_invoice', 'out_refund'):
            product_multi_company_ids = product_multi_company_obj.search(cr, uid, [('company_id','=',picking.company_id.id),('product_id','=',move_line.product_id.id)])
            if not product_multi_company_ids:
                raise osv.except_osv(_('Error!'),
                        _('Please define product multi company for this product: "%s" (id:%d).') % \
                            (move_line.product_id.name, move_line.product_id.id,))
            product_multi_company_id = product_multi_company_obj.browse(cr, uid, product_multi_company_ids[0])
            account_id = product_multi_company_id.income_acc_id.id
            invoice_line_tax_id = [(6, 0, [x.id for x in product_multi_company_id.customer_tax_ids])]
        else:
            invoice_line_tax_id = [(6, 0, self._get_taxes_invoice(cr, uid, move_line, invoice_vals['type']))]
        #END Phung
        
        if invoice_vals['fiscal_position']:
            fp_obj = self.pool.get('account.fiscal.position')
            fiscal_position = fp_obj.browse(cr, uid, invoice_vals['fiscal_position'], context=context)
            account_id = fp_obj.map_account(cr, uid, fiscal_position, account_id)
        # set UoS if it's a sale and the picking doesn't have one
        uos_id = move_line.product_uos and move_line.product_uos.id or False
        if not uos_id and invoice_vals['type'] in ('out_invoice', 'out_refund'):
            uos_id = move_line.product_uom.id
        
        return {
            'name': name,
            'origin': origin,
            'invoice_id': invoice_id,
            'uos_id': uos_id,
            'product_id': move_line.product_id.id,
            'account_id': account_id,
            'price_unit': self._get_price_unit_invoice(cr, uid, move_line, invoice_vals['type']),
            'discount': self._get_discount_invoice(cr, uid, move_line),
            'quantity': move_line.product_uos_qty or move_line.product_qty,
            'invoice_line_tax_id': invoice_line_tax_id,
            'account_analytic_id': self._get_account_analytic_invoice(cr, uid, picking, move_line),
        }
    
stock_picking()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
