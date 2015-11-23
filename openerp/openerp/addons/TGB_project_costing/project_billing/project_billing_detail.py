
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_billing_detail(osv.osv):
    _inherit ='account.invoice.line'
    _name='account.invoice.line'

    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            res[line.id]={
                'price_subtotal':0,
                'disc_amount':0,
            }
            price = line.price_unit * (1-(line.discount or 0.0)/100.0)
            taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
            res[line.id]['price_subtotal'] = taxes['total']
            if line.invoice_id:
                cur = line.invoice_id.currency_id
                res[line.id]['price_subtotal'] = cur_obj.round(cr, uid, cur, res[line.id]['price_subtotal'])
            res[line.id]['disc_amount']=res[line.id]['price_subtotal']*line.discount/100
        return res

    _columns = {
        'ph':fields.boolean('PH',),
        'phase_no':fields.float('Phase No',digits_compute=dp.get_precision('Account'),),
        'phase_description':fields.char('Phase Desc/Remarks',size=100,),
        'vo_type':fields.many2one('project.billing.vo.type',string='VO Type',),
        'vo_quotation_phase_no':fields.char("""VO's Quotation Phase No""",size=100,),
        'qty':fields.float('Qty',digits_compute=dp.get_precision('Account'),),
        'uom_id':fields.many2one('product.uom',string='UOM',),
        'unit_price':fields.float('Unit Price',digits_compute=dp.get_precision('Account'),),
        'disc':fields.float('Disc % ',digits_compute=dp.get_precision('Account'),),
        'disc_amount':fields.function(_amount_line, string='Disc Amount', type="float",
            digits_compute= dp.get_precision('Account'), store=False, multi="line"),
        'total_amount':fields.float('Total Amount',digits_compute=dp.get_precision('Account'),),
        'budgeted_total_cost':fields.float('Budgeted Total Cost',digits_compute=dp.get_precision('Account'),),
        'budgeted_ profit':fields.float('Budgeted Profit',digits_compute=dp.get_precision('Account'),),
        'price_subtotal': fields.function(_amount_line, string='Amount', type="float",
            digits_compute= dp.get_precision('Account'), store=False, multi="line"),
        }
    _defaults={
    }
project_billing_detail()

class project_finish_products(osv.osv):
    _inherit = 'project.finish.products'
    _columns = {
                 'product_id' : fields.many2one('product.product', 'Products',required=False),
                }

project_finish_products()




