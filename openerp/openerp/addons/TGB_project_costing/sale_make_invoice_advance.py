# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp import netsvc
from openerp.tools.translate import _


class sale_advance_payment_inv(osv.osv_memory):
    _inherit = "sale.advance.payment.inv"
    _description = "Sales Advance Payment Invoice"


    def open_invoices(self, cr, uid, ids, invoice_ids, context=None):
        """ open a view on one of the given invoice_ids """
        ir_model_data = self.pool.get('ir.model.data')
        form_res = ir_model_data.get_object_reference(cr, uid, 'TGB_project_costing', 'tgb_construction_project_billing_form_view')
        form_id = form_res and form_res[1] or False
        tree_res = ir_model_data.get_object_reference(cr, uid, 'TGB_project_costing', 'tgb_construction_project_billing_tree_view')
        tree_id = tree_res and tree_res[1] or False
        print 'in open invoices'
        return {
            'name': _('Advance Billing'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'account.invoice',
            'res_id': invoice_ids[0],
            'view_id': False,
            'views': [(form_id, 'form'), (tree_id, 'tree')],
            'context': "{'type': 'out_invoice'}",
            'type': 'ir.actions.act_window',
        }


    _columns = {
        'advance_payment_method':fields.selection(
            [('all', 'Bill the whole project order'),],
            'What do you want to invoice?', required=True,
            help="""Use All to create the final invoice.
                Use Percentage to invoice a percentage of the total amount.
                Use Fixed Price to invoice a specific amound in advance.
                Use Some Order Lines to invoice a selection of the project order lines."""),
        'qtty': fields.float('Quantity', digits=(16, 2), required=True),
        }



sale_advance_payment_inv()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
