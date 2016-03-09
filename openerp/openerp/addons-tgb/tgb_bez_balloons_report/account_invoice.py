# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 OpenERP SA (<http://openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from lxml import etree
import openerp.addons.decimal_precision as dp
import openerp.exceptions

from openerp import netsvc, SUPERUSER_ID
from openerp import pooler
from openerp.osv import fields, osv, orm
from openerp.tools import float_compare
from openerp.tools.translate import _

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    def invoice_print(self, cr, uid, ids, context=None):
        '''
        This function prints the invoice and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids, {'sent': True}, context=context)
        datas = {
             'ids': ids,
             'model': 'account.invoice',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'tax_invoice_sample',
            'datas': datas,
            'nodestroy' : True
        }

    _columns = {
        'appointment': fields.char('Appointment', size=1024),
        'ready_by': fields.char('Ready By', size=1024),
        'deliver_to': fields.char('Deliver to', size=1024),
        'artwork': fields.char('Artwork', size=1024),
        'customer_po': fields.char('Customer PO', size=1024),
        'balloon_color': fields.char('Balloon Color', size=1024),
        'tax_id': fields.many2one('account.tax', 'Taxes', readonly=True, states={'draft':[('readonly',False)]}),
        'discount': fields.float('Discount (%)', digits_compute= dp.get_precision('Discount'), readonly=True, states={'draft':[('readonly',False)]}),
    }
    
    def create(self, cr, uid, vals, context=None):
        new_id = super(account_invoice, self).create(cr, uid, vals, context)
        invoice = self.browse(cr, uid, new_id)
        if 'tax_id' not in vals or not vals.get('tax_id', False):
            tax_id = False
            for line in invoice.invoice_line:
                if line.invoice_line_tax_id:
                    tax_id = line.invoice_line_tax_id[0].id
                    break
            if tax_id:
                self.write(cr, uid, [invoice.id], {'tax_id':tax_id})
        else:
            invoice_line_ids = [l.id for l in invoice.invoice_line]
            self.pool.get('account.invoice.line').write(cr, uid, invoice_line_ids, {'invoice_line_tax_id': [(6,0,[vals['tax_id']])]})
            self.button_reset_taxes(cr, uid, [new_id], context)
            
        if 'discount' not in vals or not vals.get('discount', False):
            discount = False
            for line in invoice.invoice_line:
                if line.discount:
                    discount = line.discount
                    break
            if tax_id:
                self.write(cr, uid, [invoice.id], {'discount':discount})
            
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(account_invoice, self).write(cr, uid, ids, vals, context)
        if vals.get('tax_id', False):
            for invoice in self.browse(cr, uid, ids, context):
                invoice_line_ids = [l.id for l in invoice.invoice_line]
                self.pool.get('account.invoice.line').write(cr, uid, invoice_line_ids, {'invoice_line_tax_id': [(6,0,[vals['tax_id']])]})
                self.button_reset_taxes(cr, uid, [invoice.id], context)
                
        if vals.get('discount', False):
            for invoice in self.browse(cr, uid, ids, context):
                invoice_line_ids = [l.id for l in invoice.invoice_line]
                self.pool.get('account.invoice.line').write(cr, uid, invoice_line_ids, {'discount': vals['discount']})
                self.button_reset_taxes(cr, uid, [invoice.id], context)
                
        return new_write
    
account_invoice()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: