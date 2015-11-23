
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class project_claim(osv.osv):
    _name='project.claim'

    def _get_total_ar(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for claim in self.browse(cr,uid,ids):
            res[claim.id] = {}
            amount = 0
            for ar in claim.ar_credit_note_ids:
                amount += ar.amount
            res[claim.id]['total_ar_credit_note_amt'] = amount
            res[claim.id]['total_ar_credit_note_amt_home'] = amount*claim.exchange_rate
        return res

    def _get_ar_credit_note_ids(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('ar.credit.note').browse(cr, uid, ids, context=context):
            result[line.project_claim_id.id] = True
        return result.keys()

    _columns = {
        'claim_voucher_no':fields.char('Claim Voucher No.',size=20,),
        'claim_sequence_no':fields.integer('Claim Sequence No',),
        'project_no':fields.many2one('project.project','Project No',required=True,),
        'revision_no':fields.integer('Revision No.',),
        'claim_date':fields.date('Claim Date',required=True),
        'customer_name':fields.many2one('res.partner',string='Customer Name',),
        'customer_job_no':fields.char('Customer Job No.',size=20,),
        'subject':fields.char('Subject',size=100,),
        'max_retention_amt':fields.float('Max Retention Amt',digits_compute=dp.get_precision('Account'),),
        'retention_percent':fields.float('Retention Percent',digits_compute=dp.get_precision('Account'),),
        'currency_id':fields.many2one('res.currency',string='Currency',),
        'sales_tax':fields.many2one('account.tax',string='Sales Tax',),
        'claim_type':fields.selection([('by_phase','By Phase'),('by_project','By Project'),],'Claim Type',),
        'final_claim':fields.boolean('Final Claim',),
        'original_project_amount':fields.float('Original Project Amount',digits_compute=dp.get_precision('Account'),),
        'vo_amount':fields.float('VO Amount',digits_compute=dp.get_precision('Account'),),
        'omission_amount':fields.float('Omission Amount',digits_compute=dp.get_precision('Account'),),
        'total_project_amount':fields.float('Total Project Amount',digits_compute=dp.get_precision('Account'),),
        'original_cumulative_claim':fields.float('Original Cumulative Claim',digits_compute=dp.get_precision('Account'),),
        'vo_cumulative_claim':fields.float('VO Cumulative Claim',digits_compute=dp.get_precision('Account'),),
        'total_cumulative_claim':fields.float('Total Cumulative Claim',digits_compute=dp.get_precision('Account'),),
        'less_cumulative_claim':fields.float('Less Total Current Cumulative Claim',digits_compute=dp.get_precision('Account'),),
        'exchange_rate':fields.float('Exchange Rate',digits_compute=dp.get_precision('Account'),),
        'total_this_claim_amt_home':fields.float('Total This Claim Amt Home ',digits_compute=dp.get_precision('Account'),),
        'total_this_claim_amt':fields.float('Total This Claim Amt ',digits_compute=dp.get_precision('Account'),),
        'total_ar_credit_note_amt_home':fields.function(_get_total_ar, digits_compute=dp.get_precision('Account'),
                                           string='Total AR Credit Note Amt Home',
                                           store={
                                               'project.claim': (lambda self, cr, uid, ids, c={}: ids, ['ar_credit_note_ids','exchange_rate'], 10),
                                               'ar.credit.note': (_get_ar_credit_note_ids, ['amount'], 10),
                                           },
                                           multi='ar',  track_visibility='always'),

        'total_ar_credit_note_amt': fields.function(_get_total_ar, digits_compute=dp.get_precision('Account'),
                                           string='Total AR Credit Note Amt',
                                           store={
                                               'project.claim': (lambda self, cr, uid, ids, c={}: ids, ['ar_credit_note_ids','exchange_rate'], 10),
                                               'ar.credit.note': (_get_ar_credit_note_ids, ['amount'], 10),
                                           },
                                           multi='ar', track_visibility='always'),
        'project_claim_detail_ids':fields.one2many('project.claim.detail','project_claim_id',string='Project Claim Details',),
        'project_claimable_item_transaction_ids':fields.one2many('project.claimable.item.transaction.detail','project_claim_id',string='Project Claimable Item Transaction',),
        'project_claimable_item_detail_ids':fields.one2many('project.claimable.item.detail','project_claim_id',string='Project Claimable Item detail',),
        'ar_credit_note_ids':fields.one2many('ar.credit.note','project_claim_id',string='AR Credit Note',),
        'internal_remarks_code':fields.many2one('project.remark',string='Internal Remarks Code',domain=[('type','=','internal')]),
        'internal_remarks':fields.text('Internal Remarks',),
        'external_remarks_code':fields.many2one('project.remark',string='External Remarks Code',domain=[('type','=','external')]),
        'external_remarks':fields.text('External Remarks',),
        'attachment_ids':fields.one2many('project.attachment','project_claim_id',string='Attachments',),
        'account_invoice_ids':fields.one2many('account.invoice','project_claim_id',string='Invoices',),
        }
    
    _defaults={
        'claim_date': fields.date.context_today,
        'retention_percent':100,
        'exchange_rate':1,
    }

project_claim()
