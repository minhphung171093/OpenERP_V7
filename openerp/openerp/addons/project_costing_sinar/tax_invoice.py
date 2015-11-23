from osv import fields, osv
from tools.translate import _
import netsvc
import openerp.addons.decimal_precision as dp

class tax_invoice(osv.osv):
    _name = "tax.invoice"
    _description = "tax.invoice table"
    
    def _calculate_lst_amount(self, cr, uid, ids, prop, unknow_none, context=None):
        res, li = {}, []
        tax_obj = self.browse(cr, uid, ids)
        for tax in tax_obj:
            for td in tax.luxury_sale_ids:
                li.append(td.lst)
            res[tax.id] = sum(li)
        return res
    
    _columns = {
        'inv_id' : fields.many2one("account.invoice", 'Invoice Number', readonly=True),
        'company_id' : fields.many2one("res.company", 'Company', readonly=True),
        'partner_id': fields.many2one('res.partner', 'Customer', readonly=True),
        'currency_id': fields.many2one('res.currency', 'Currency', readonly=True),
        'date_invoice': fields.date('Invoice Date', readonly=True),
        'tax_invoice_code' : fields.char("Tax Invoice Code"),
        'vat_number' : fields.char("Taxable VAT entity confirm number"),
        'inv_line' : fields.one2many('tax.invoice.line','invoice_id','Invoice Lines', readonly=True),
        'inv_line_tax_id': fields.many2many('account.tax', 'account_invoice_tax_rel', 'invoice_line_id', 'tax_id', 'Taxes', readonly=True),
        'disc': fields.float('Discount (%)', digits_compute= dp.get_precision('Discount'), readonly=True),
        'amount_untaxed' : fields.float('Subtotal', readonly=True),
        'amount_tax' : fields.float('Tax Base'),
        'vat' : fields.float('VAT'),
        'amount_total' : fields.float('Total'),
        'residual' : fields.float('Balance'),
        'luxury_sale_ids' : fields.one2many('tax.luxury.sale.line','luxury_id','Tax Luxury Sales'),
        'lst_amount': fields.function(_calculate_lst_amount,
                                         store=True,
                                         type='float',
                                         string='LST Total',
                                         digits_compute=dp.get_precision('Account')),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('cancel', 'Cancelled'),
            ('done', 'Done'),
            ], 'Status', readonly=True, track_visibility='onchange')        
        
            }
    
    _order = "id desc"
    
#     def write(self, cr, uid, ids, vals, context=None):
#         if vals and vals.has_key('amount_tax'):
#             vals['vat'] = (vals['amount_tax'] * 10)/100.0
#             li = [data.amount_untaxed for data in self.browse(cr, uid, ids)]
#             vals['amount_total'] = vals['amount_tax'] + li[0]
#             vals['residual'] = vals['amount_total']
#         return super(tax_invoice, self).write(cr, uid, ids, vals, context=context)
    
    def action_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'done'}, context=context)
        return True
    
    def unlink(self, cr, uid, ids, context=None):
        for data in self.browse(cr,uid,ids,context=context):
            if data.state == 'done':
                raise osv.except_osv(('Error'),('You cannot delete this record...'))
        return super(tax_invoice, self).unlink(cr,uid,ids,context=context)
    
    def button_calculate_taxes(self, cr, uid, ids, context=None):
        for data in self.browse(cr,uid,ids,context=context):
            dt = data.amount_tax
            vat = (data.amount_tax * 10)/100.0
            amt = data.amount_untaxed
        self.write(cr, uid, ids, {'vat':vat, 'amount_total':dt + amt, 'residual':dt + amt}, context=context)
        return True
        
tax_invoice()

class tax_invoice_line(osv.osv):
    _name = "tax.invoice.line"
    _description = "tax.invoice.line table"
    
    _columns = {
        'invoice_id' : fields.many2one('tax.invoice', 'Invoice'),
        'uos_id': fields.many2one('product.uom', 'Unit of Measure', ondelete='set null', select=True),
        'product_id': fields.many2one('product.product', 'Product', ondelete='set null', select=True),
        'account_id': fields.many2one('account.account', 'Account', help="The income or expense account related to the selected product."),
        'price_unit': fields.float('Unit Price', digits_compute= dp.get_precision('Product Price')),
        'price_subtotal' : fields.float('Amount'),
        'quantity': fields.float('Quantity', digits_compute= dp.get_precision('Product Unit of Measure')),
                }

class tax_luxury_sale_line(osv.osv):
    _name = "tax.luxury.sale.line"
    _description = "tax.luxury.sale.line table"
    
    _columns = {
      'luxury_id' : fields.many2one("tax.invoice", 'Luxury'),
      'tax_rate' : fields.float('Tax Rate'),
      'tax_reg' : fields.char('Director of Tax Regulation', size=64),
      'lst' : fields.float('LST'),  
                }
    
tax_luxury_sale_line()

class res_partner(osv.osv):
    _inherit = "res.partner"
    
    _columns = {
        'tax_reg_number' : fields.char("Tax Registration Number"),
                }

res_partner()