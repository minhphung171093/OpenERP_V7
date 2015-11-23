
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_billing(osv.osv):
    _inherit ='account.invoice'
    _name='account.invoice'
    _track = {
        'type': {
        },
        'state': {
            'account.mt_invoice_paid': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'paid' and obj['type'] in ('out_invoice', 'out_refund'),
            'account.mt_invoice_validated': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'open' and obj['type'] in ('out_invoice', 'out_refund'),
        },
    }

    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()

    def _amount_remain(self, cr, uid, ids, name, args, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = {
                'remain_budget': 0.0,
            }
            if invoice.sale_order_id:
                res[invoice.id]['remain_budget'] = invoice.sale_order_id.total_budget-invoice.amount_total
        return res

    _columns = {
        'project_id':fields.many2one('project.project',string='Project No.',),
        'revision_no':fields.integer('Revision No',),
        'sale_order_id':fields.many2one('sale.order',string='Quotation No',),
        'customer_id':fields.many2one('res.partner',string='Customer',),
        'bill_type':fields.selection([('bill_by_project','Bill by Project'),('bill_by_phase','Bill by Phase'),('bill_by_claim','Bill by Claim'),('bill_by_draft_bill','Bill by Draft Bill'),],'Bill Type',),
        'no_more_stock_issue':fields.selection([('yes','Yes'),('no','No'),],'No More Stock Issue',),
        'estimate_date':fields.date('Estimate Date',),
        'customer_contact':fields.char('Customer Contact',size=100,),
        'start_date':fields.date('Start Date',),
        'end_date':fields.date('End Date',),
        'project_class_id':fields.related('project_id','project_class_id',string='Project Class',type='many2one',relation='project.class',readonly=True),
        'project_category_id':fields.related('project_id','project_category_id',string='Project Category',type='many2one',relation='project.category',readonly=True),
        'currency_id':fields.many2one('res.currency',string='Currency',),
        'sale_tax_ids':fields.many2one('account.tax',string='Sale Tax',),
        'retention_required':fields.boolean('Retention Required',),
        'retention_amount':fields.float('Retention Amount',digits_compute=dp.get_precision('Account'),),
        'max_retention_amount':fields.float('Max Retention Amt',digits_compute=dp.get_precision('Account'),),
        'retention_days':fields.integer('Retention Days',),
        'retention_due_date':fields.date('Retention Due Date',),
        'tolerable_variance':fields.float('Tolerable Variance %',digits_compute=dp.get_precision('Account'),),
        'sale_person':fields.many2one('res.users',string='Sales Person',),
        'sale_manager':fields.many2one('res.users',string='Sales Manager',),
        'site_supervisor':fields.many2one('res.users',string='Site Supervisor',),
        'customer_po_no':fields.char('Customer PO No',size=20,),
        'default_location_id':fields.many2one('stock.location',string='Default Loading Location',),
        'subject':fields.char('Subject',size=100,),
        'project_billing_product_ids':fields.one2many('project.billing.product','project_billing_id',string='Project Products',),
        'exchange_rate':fields.float('Exchange Rate',digits_compute=dp.get_precision('Account'),),
        'profit_margin':fields.float('Profit Margin',digits_compute=dp.get_precision('Account'),),
        'total_original_contract_home_amt':fields.float('Total Original Contract Home Amt',digits_compute=dp.get_precision('Account'),),
        'total_original_contract_amt':fields.float('Total Original Contract Amt',digits_compute=dp.get_precision('Account'),),
        'total_vo_addition_home_amt':fields.float('Total VO Addition Home Amt',digits_compute=dp.get_precision('Account'),),
        'total_vo_addition_amt':fields.float('Total VO Addition Amt',digits_compute=dp.get_precision('Account'),),
        'omission_home_amt':fields.float('Omission Home Amt',digits_compute=dp.get_precision('Account'),),
        'omission_amt':fields.float('Omission Amt',digits_compute=dp.get_precision('Account'),),
        'total_home_amt':fields.float('Total Home Amt',digits_compute=dp.get_precision('Account'),),
        'total_amt':fields.float('Total Amount',digits_compute=dp.get_precision('Account'),),
        'total_budgeted_home_cost':fields.float('Total Budgeted Home Cost',digits_compute=dp.get_precision('Account'),),
        'total_budgeted_cost':fields.float('Total Budgeted Cost',digits_compute=dp.get_precision('Account'),),
        'budgeted_profit_home':fields.float('Budgeted Profit Home',digits_compute=dp.get_precision('Account'),),
        'budgeted_profit':fields.float('Budgeted Profit',digits_compute=dp.get_precision('Account'),),
        'total_sale_tax_home_amt':fields.float('Total Sales Tax Home Amt',digits_compute=dp.get_precision('Account'),),
        'total_sale_tax_amt':fields.float('Total Sales Tax Amt',digits_compute=dp.get_precision('Account'),),
        'total_after_tax_home_amt':fields.float('Total After Tax Home Amt',digits_compute=dp.get_precision('Account'),),
        'total_after_tax_amt':fields.float('Total After Tax Amt',digits_compute=dp.get_precision('Account'),),
        'operation_manager':fields.related('sale_order_id','operation_manager', relation='res.users',type='many2one',string='Operation Manager',readonly=True),
        'project_manager':fields.related('sale_order_id','project_manager', relation='res.users',type='many2one',string='Project Manager',readonly=True),
        'claim_officer':fields.related('sale_order_id','claim_officer', relation='res.users',type='many2one',string='Claim Officer',readonly=True),
        'project_coordinator':fields.related('sale_order_id','project_coordinator', relation='res.users',type='many2one',string='Project Coordinator',readonly=True),
        'resident_technical_officer':fields.related('sale_order_id','resident_technical_officer', relation='res.users',type='many2one',string='Resident Technical Officer',readonly=True),
        'head_of_department':fields.related('sale_order_id','head_of_department', relation='res.users',type='many2one',string='Head of Department',readonly=True),
        'project_billing_member_ids':fields.related('sale_order_id','user_ids', relation='project.user.sale',type='one2many',string='Other Member',readonly=True),
        'total_budget':fields.related('sale_order_id','total_budget',type='float',readonly=True,string="Total Budget"),
        'remain_budget':fields.function(_amount_remain, digits_compute=dp.get_precision('Account'), string='Budget Remain', track_visibility='always',
                                        store=False,multi='remain'),
        'payment_option':fields.many2one('project.billing.payment.option',string='Payment Option',),
        'payment_tenor':fields.float('Payment Term Tenor',digits_compute=dp.get_precision('Account'),),
        'payment_method':fields.many2one('account.journal',string='Payment Method',),
        'billing_party':fields.many2one('project.billing.party',string='Billing Party',),
        'billing_address':fields.char('Billing Address',size=100,),
        'billing_contact':fields.many2one('res.partner',string='Billing Contact',),
        'project_billing_src':fields.one2many('project.billing.src','project_billing_id',string='SRC',),
        'project_billing_customer_po_ids':fields.one2many('project.billing.customer.po','project_billing_id',string='Customer Po',),
        'internal_remarks':fields.text('Internal Remarks',),
        'external_remarks':fields.text('External Remarks',),
        'project_status':fields.selection([('status1','status1'),('status2','status2'),('status3','status3'),],'Project Status',),
        'attachment_ids':fields.one2many('project.attachment','project_billing_id',string='Attachments',),
        'move_id': fields.many2one('account.move', 'Journal Entry', readonly=True, select=1, ondelete='restrict', help="Link to the automatically generated Journal Items."),
        'state': fields.selection([
            ('draft','Draft'),
            ('proforma','Pro-forma'),
            ('proforma2','Pro-forma'),
            ('open','Open'),
            ('paid','Paid'),
            ('cancel','Cancelled'),
            ],'Status', select=True, readonly=True, track_visibility='onchange',
            help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed Invoice. \
            \n* The \'Pro-forma\' when invoice is in Pro-forma status,invoice does not have an invoice number. \
            \n* The \'Open\' status is used when user create invoice,a invoice number is generated.Its in open status till user does not pay invoice. \
            \n* The \'Paid\' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled. \
            \n* The \'Cancelled\' status is used when user cancel invoice.'),
        'type': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('out_refund','Customer Refund'),
            ('in_refund','Supplier Refund'),
            ],'Type', readonly=True, select=True, change_default=True, track_visibility='always'),
        }

    
    _defaults={
        'state':'draft',
    }

project_billing()
