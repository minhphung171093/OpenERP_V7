
# -*- coding: utf-8 -*-
__author__ = 'Son Pham'
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp import netsvc

class dk_invoice(osv.osv):
    _inherit='account.invoice'

    _columns = {
        'contract_id':fields.many2one('dk.contract','Contract'),
        'contract_type':fields.related('contract_id','type',relation='dk.contract.type',type='many2one',string='Type', readonly=True),
        'contract_type2':fields.related('contract_id','type',relation='dk.contract.type',type='many2one',string='Type',readonly=True),
        'contract_amount':fields.related('contract_id','amount',string='AMT',type='float',digits_compute=dp.get_precision('Account'), readonly=True),
        'dk_remark':fields.text('Remarks'),
        'contract_start_date':fields.related('contract_id','start_date',type='char', size=4,string='Start Date',readonly=True),
        'contract_end_date':fields.related('contract_id','exp_date',type='char',size=4,string='End Date',readonly=True),
        'contract_ref_no':fields.related('contract_id','ref_no',type='char',string='CONTRACT REF',readonly=True),
        'contract_date_order':fields.related('contract_id','date_order',type='date',string='DATE',readonly=True),
        'dk_bank_cheque_no':fields.char('BANK/CHECKQUE No',size=128),
        'dk_bank_cheque_amount':fields.float('bank check amount',digits_compute=dp.get_precision('Account'),),
        'dk_bank_date':fields.date('DATE'),
        'contact_person_id':fields.many2one('res.partner','Contact Person'),
        'contact_person_phone':fields.related('contact_person_id','phone',string='Contact No.', readonly=True, type='char'),
        'location_of_service':fields.related('contact_person_id','use_parent_address',type='char',readonly=True,string='Location of Service'),
        'dk_subject':fields.char('Subject',size=255),
        'appoint_holder':fields.many2one('res.partner','Appointment Holder',),
        'appoint_holder_phone':fields.related('appoint_holder','phone',type='char',string='HP',readonly=True),
        'dk_company_id':fields.many2one('res.company','Company'),
        'dk_company_logo':fields.related('dk_company_id','logo_web',type='binary',string='logo'),
        'dk_company_name':fields.related('dk_company_id','name',type='char',string='name',readonly=True),
        'dk_company_street':fields.related('dk_company_id','street',type='char',string='street',readonly=True),
        'dk_company_phone':fields.related('dk_company_id','phone',type='char',string='phone',readonly=True),
        'dk_company_fax':fields.related('dk_company_id','fax',type='char',string='fax',readonly=True),
        'dk_company_email':fields.related('dk_company_id','email',type='char',string='Email',readonly=True),
        'dk_company_rml_report_footer':fields.related('dk_company_id','rml_footer_readonly',type='text',readonly=True),
        }
    
    _defaults={
        'dk_subject':'Breakdown of Air-conditioning equipment:',

    }

dk_invoice()
