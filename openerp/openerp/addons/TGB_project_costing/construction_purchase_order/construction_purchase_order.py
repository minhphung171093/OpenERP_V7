
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class construction_purchase_order(osv.osv):
    _name='construction.purchase.order'
    def apply_discount(self,cr,uid,ids,context={}):
        for order in self.browse(cr,uid,ids):
            for line in order.construction_purchase_order_line_ids:
                line_discount = line.qty * line.unit_cost * order.discount_percent / 100
                self.pool.get('construction.purchase.order.line').write(cr,uid,line.id,{'discount_amount':line_discount})
        return True

    def _get_amount(self,cr,uid,ids,fields,args,context={}):
        res = {}
        for order in self.browse(cr,uid,ids):
            res[order.id] = {'discount_percent':0,
                        'discount_amount':0,
                        'total_volume':0,
                        'total_weight':0,
                        'total_discount_amt':0,
                        'total_sales_tax_amt':0,
                        'sub_total_after_discount':0,
                        'total_after_tax_amt':0,
                        'total_after_tax_home_amt':0,
            }
            amount = total =  discount = tax  = 0
            for line in order.construction_purchase_order_line_ids:
                amount += line.qty * line.unit_cost
                total += line.total
                discount += line.discount_amount
                tax += line.tax
            res[order.id]['discount_amount'] = amount/100 * order.discount_percent
            res[order.id]['total_discount_amt'] = discount
            res[order.id]['total_sales_tax_amt'] = tax
            res[order.id]['sub_total_after_discount'] = total
            res[order.id]['total_after_tax_amt'] = total + tax
            res[order.id]['total_after_tax_home_amt'] = (total + tax)*order.exchange_rate
        return res
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('construction.purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.construction_purchase_order_id.id] = True
        return result.keys()
    _columns = {
        'purchase_order_no':fields.char('Purchase Order No',size=20,),
        'supplier_id':fields.many2one('res.partner',string='Supplier',required=True),
        'source_voucher_no':fields.selection([('draft','Draft'),('active','Active')],'Source Voucher No',),
        'copy_from':fields.char('Copy From',size=100,),
        'copy':fields.many2one('construction.purchase.order',string='Copy',),
        'supplier_contact':fields.many2one('res.partner',string='Supplier Contact',required=True),
        'purchase_order_date':fields.date('Purchase Order Date',required=True),
        'order_currency':fields.many2one('res.currency',string='Order Currency',required=True),
        'sales_tax':fields.many2one('account.tax',string='Sales Tax',required=True),
        'purchaser_id':fields.many2one('res.partner',string='Purchaser',required=True),
        'reference_no':fields.char('Reference No',size=20,),
        'subject':fields.char('Subject',size=100,),
        'shipment_mode':fields.many2one('project.shipment.mode',string='Shipment Mode',required=True),
        'shipment_term':fields.many2one('project.shipment.term',string='Shipment Term',required=True),
        'default_to_location':fields.many2one('stock.location',string='Default ship to Location',required=True),
        'estimated_shipment_date':fields.date('Estimated Shipment Date',),
        'estimated_arrival_date':fields.date('Estimated Arrival Date',required=True),
        'discount_percent':fields.float('Discount Percent',digits_compute=dp.get_precision('Account'),),
        'discount_amount':fields.function(_get_amount,type='float',multi='amount_total',string='Discount Amount',digits_compute=dp.get_precision('Account'),
                                          stored={
                                              'construction.purchase.order':(lambda self, cr, uid, ids, c={}: ids, ['construction_purchase_order_line_ids','discount_percent'], 10),
                                              'construction.purchase.order.line': (_get_order, ['total', 'tax', 'discount_amount', 'qty','unit_cost'], 10),
                                          }
                                          ),
        'exchange_rate':fields.float('Exchange Rate',digits_compute=dp.get_precision('Account'),),
        'total_volume':fields.function(_get_amount,type='float',multi='amount_total',string='Total Volume',digits_compute=dp.get_precision('Account'),
                                        stored={
                                              'construction.purchase.order':(lambda self, cr, uid, ids, c={}: ids, ['construction_purchase_order_line_ids','discount_percent'], 10),
                                              'construction.purchase.order.line': (_get_order, ['total', 'tax', 'discount_amount', 'qty','unit_cost'], 10),
                                          }),
        'total_weight':fields.function(_get_amount,type='float',multi='amount_total',string='Total Weight',digits_compute=dp.get_precision('Account'),
                                        stored={
                                              'construction.purchase.order':(lambda self, cr, uid, ids, c={}: ids, ['construction_purchase_order_line_ids','discount_percent'], 10),
                                              'construction.purchase.order.line': (_get_order, ['total', 'tax', 'discount_amount', 'qty','unit_cost'], 10),
                                          }),
        'total_discount_amt':fields.function(_get_amount,type='float',multi='amount_total',string='Total Discount Amt',digits_compute=dp.get_precision('Account'),
                                              stored={
                                              'construction.purchase.order':(lambda self, cr, uid, ids, c={}: ids, ['construction_purchase_order_line_ids','discount_percent'], 10),
                                              'construction.purchase.order.line': (_get_order, ['total', 'tax', 'discount_amount', 'qty','unit_cost'], 10),
                                          }),
        'total_sales_tax_amt':fields.function(_get_amount,type='float',multi='amount_total',string='Total Sales Tax Amt',digits_compute=dp.get_precision('Account'),
                                               stored={
                                              'construction.purchase.order':(lambda self, cr, uid, ids, c={}: ids, ['construction_purchase_order_line_ids','discount_percent'], 10),
                                              'construction.purchase.order.line': (_get_order, ['total', 'tax', 'discount_amount', 'qty','unit_cost'], 10),
                                          }),
        'sub_total_after_discount':fields.function(_get_amount,type='float',multi='amount_total',string='Sub Total After Discount',digits_compute=dp.get_precision('Account'),
                                                    stored={
                                              'construction.purchase.order':(lambda self, cr, uid, ids, c={}: ids, ['construction_purchase_order_line_ids','discount_percent'], 10),
                                              'construction.purchase.order.line': (_get_order, ['total', 'tax', 'discount_amount', 'qty','unit_cost'], 10),
                                          }),
        'total_after_tax_amt':fields.function(_get_amount,type='float',multi='amount_total',string='Total After Tax Amt',digits_compute=dp.get_precision('Account'),
                                               stored={
                                              'construction.purchase.order':(lambda self, cr, uid, ids, c={}: ids, ['construction_purchase_order_line_ids','discount_percent'], 10),
                                              'construction.purchase.order.line': (_get_order, ['total', 'tax', 'discount_amount', 'qty','unit_cost'], 10),
                                          }),
        'total_after_tax_home_amt':fields.function(_get_amount,type='float',multi='amount_total',string='Total After Tax Home Amt',digits_compute=dp.get_precision('Account'),
                                                    stored={
                                              'construction.purchase.order':(lambda self, cr, uid, ids, c={}: ids, ['construction_purchase_order_line_ids','discount_percent'], 10),
                                              'construction.purchase.order.line': (_get_order, ['total', 'tax', 'discount_amount', 'qty','unit_cost'], 10),
                                          }),
        'project_id':fields.many2one('project.project',string='Project No',),
        'phase_sequence_id':fields.many2one('phase.sequence',string='Phase Sequence No',),
        'line_item_id':fields.many2one('construction.purchase.order.line',string='Line Item No',),
        'payment_option':fields.many2one('project.billing.payment.option',string='Payment Option',required=True),
        'payment_term':fields.many2one('account.payment.term',string='Payment Term',required=True),
        'payment_term_tenor':fields.many2one('construction.payment.term.tenor',string='Payment Term Tenor',required=True),
        'payment_method':fields.many2one('account.journal',string='Payment Method',),
        'payment_amount':fields.float('Payment Amount',digits_compute=dp.get_precision('Account'),),
        'payment_party':fields.many2one('project.billing.party',string='Payment Party',required=True),
        'payment_address':fields.char('Payment Address',size=100,),
        'payment_contact':fields.many2one('res.partner',string='Payment Contact',),
        'internal_remarks_code':fields.many2one('project.remark',string='Internal Remarks Code',),
        'external_remarks_code':fields.many2one('project.remark',string='External Remarks Code',),
        'internal_remarks':fields.text('Internal Remarks',),
        'external_remarks':fields.text('External Remarks',),
        'construction_purchase_order_line_ids':fields.one2many('construction.purchase.order.line','construction_purchase_order_id',string='Detail',),
        }
    
    _defaults={
        'exchange_rate':1,
    }

construction_purchase_order()
