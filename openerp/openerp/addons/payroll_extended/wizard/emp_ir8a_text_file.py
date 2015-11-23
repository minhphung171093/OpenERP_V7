# -*- coding: utf-8 -*-

from osv import osv, fields
import base64
import tempfile
from tools.translate import _
import datetime
from tools import DEFAULT_SERVER_DATE_FORMAT
from time import gmtime, strftime
import tools
import time

class emp_ir8a_text_file(osv.osv):

    _name = 'emp.ir8a.text.file'

    def _get_payroll_user_name(self, cr, uid, context=None):
        if context is None:
            context = {}
        supervisors_list = [(False,'')]
        data_obj = self.pool.get('ir.model.data')
        result_data = data_obj._get_id(cr, uid, 'payroll_extended', 'group_hr_payroll_admin')
        model_data = data_obj.browse(cr, uid, result_data, context=context)
        group_data = self.pool.get('res.groups').browse(cr, uid, model_data.res_id, context)
        for user in group_data.users:
            supervisors_list.append((tools.ustr(user.id), tools.ustr(user.name)))
        return supervisors_list

    _columns = {
            'employee_ids': fields.many2many('hr.employee', 'hr_employe_ir8a_text_rel', 'emp_id', 'employee_id', 'Employee', required=False),
            'year_id': fields.many2one('account.fiscalyear', 'Year Of Assessment', required=True),
            'source': fields.selection([('1', 'Mindef'), ('4', 'Government Department'), ('5', 'Statutory Board'),
                                        ('6', 'Private Sector'), ('9', 'Others')], string='Source', required=True),
            'organization_id_type': fields.selection([('7', 'UEN – Business Registration number issued by ACRA'),
                                                      ('8', 'UEN – Local Company Registration number issued by ACRA'),
                                                      ('A', 'ASGD – Tax Reference number assigned by IRAS'),
                                                      ('I', 'ITR – Income Tax Reference number assigned by IRAS'),
                                                      ('U', 'UENO – Unique Entity Number Others')], string='Organization ID Type', required=True),
            'organization_id_no': fields.char('Organization ID No', size=16, required=True),
            'batch_indicatior': fields.selection([('O', 'Original'), ('A', 'Amendment')], string='Batch Indicator', required=True),
            'batch_date': fields.date('Batch Date', required=True),
            'payroll_user': fields.selection(_get_payroll_user_name, 'Name of authorised person', size=128, required=True),
            'print_type' : fields.selection([('text','Text'), ('pdf', 'PDF')], 'Print as', required=True)
    }

    _defaults = {
        'source': '6',
        'print_type' : 'text',
#        'year_id': 3,
#        'organization_id_type': '8',
#        'batch_indicatior': 'A',
#        'payroll_user': '1',
#        'source': '1',
#        'employee_ids': [22],
#        'organization_id_no': '201102376W',
#        'batch_date': time.strftime(DEFAULT_SERVER_DATE_FORMAT)
    }

    def download_ir8a_txt_file(self, cr, uid, ids, context):
        context.update({'active_test': False})
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        context.update({'employe_id': data['employee_ids'], 'datas': data})
        if data.get('print_type', '') == 'text':
            return {
              'name': _('Binary'),
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'binary.ir8a.text.file.wizard',
              'type': 'ir.actions.act_window',
              'target': 'new',
              'context': context,
            }
        elif data.get('print_type', '') == 'pdf':
            data = {
                'ids' : [],
                'model' : 'hr.payslip',
                'form' : data
            }
            ret =  {
                'type' : 'ir.actions.report.xml',
                'report_name' : 'ppd_ir8a_form_report',
                'datas' : data
            }
            return ret

emp_ir8a_text_file()

class binary_ir8a_text_file_wizard(osv.osv_memory):

    _name = 'binary.ir8a.text.file.wizard'

    _columns = {
        'name': fields.char('Name', size=64),
        'ir8a_txt_file': fields.binary('Click On Save As Button To Download File', readonly=True),
    }

    def _generate_file(self, cr, uid, context=None):
        if context is None:
            context = {}
        employee_obj = self.pool.get('hr.employee')
        payslip_obj = self.pool.get('hr.payslip')
        contract_obj = self.pool.get('hr.contract')
        hr_contract_income_tax_obj = self.pool.get('hr.contract.income.tax')
        tgz_tmp_filename = tempfile.mktemp('.' + "txt")
        tmp_file = False
        start_date = end_date = prev_yr_start_date = prev_yr_end_date = False
        if context.get('datas')['year_id'][1]:
            basis_year = tools.ustr(int(context.get('datas')['year_id'][1]) - 1)
            fiscal_start_date = '%s0101' % tools.ustr(int(context.get('datas')['year_id'][1]) - 1)
            fiscal_end_date = '%s1231' % tools.ustr(int(context.get('datas')['year_id'][1]) - 1)
            start_date = '%s-01-01' % tools.ustr(int(context.get('datas')['year_id'][1]) - 1)
            end_date = '%s-12-31' % tools.ustr(int(context.get('datas')['year_id'][1]) - 1)
            prev_yr_start_date = '%s-01-01' % tools.ustr(int(context.get('datas')['year_id'][1]) - 2)
            prev_yr_end_date = '%s-12-31' % tools.ustr(int(context.get('datas')['year_id'][1]) - 2)
            start_date = datetime.datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)
            end_date = datetime.datetime.strptime(end_date, DEFAULT_SERVER_DATE_FORMAT)
            prev_yr_start_date = datetime.datetime.strptime(prev_yr_start_date, DEFAULT_SERVER_DATE_FORMAT)
            prev_yr_end_date = datetime.datetime.strptime(prev_yr_end_date, DEFAULT_SERVER_DATE_FORMAT)

        try:
            tmp_file = open(tgz_tmp_filename, "wr")
            batchdate = datetime.datetime.strptime(context.get('datas')['batch_date'], DEFAULT_SERVER_DATE_FORMAT)
            batchdate = batchdate.strftime('%Y%m%d')
            server_date = basis_year + strftime("%m%d", gmtime())
            emp_id = employee_obj.search(cr, uid, [('user_id', '=', int(context.get('datas')['payroll_user']))])
            emp_designation = ''
            user_obj = self.pool.get('res.users')
            payroll_admin_user_name = user_obj.browse(cr, uid, int(context.get('datas')['payroll_user'])).name
            company_name = user_obj.browse(cr, uid, int(context.get('datas')['payroll_user'])).company_id.name
            for emp in employee_obj.browse(cr, uid, emp_id):
                emp_designation = emp.job_id.name
            header_record = '0'.ljust(1) + \
                            tools.ustr(context.get('datas')['source'] or '').ljust(1) + \
                            tools.ustr(basis_year).ljust(4) + \
                            '08'.ljust(2) + \
                            tools.ustr(context.get('datas')['organization_id_type'] or '').ljust(1) + \
                            tools.ustr(context.get('datas')['organization_id_no'] or '').ljust(12) + \
                            tools.ustr(payroll_admin_user_name or '')[:30].ljust(30) + \
                            tools.ustr(emp_designation)[:30].ljust(30) + \
                            tools.ustr(company_name)[:60].ljust(60) + \
                            ' '.ljust(20) + \
                            ' '.ljust(60) + \
                            tools.ustr(context.get('datas')['batch_indicatior'] or '').ljust(1) + \
                            tools.ustr(server_date or '').ljust(8) + \
                            ''.ljust(30) + \
                            ''.ljust(10) + \
                            ''.ljust(930) + \
                            "\r\n"
            tmp_file.write(header_record)
            
            total_detail_record = 0
            tot_prv_yr_gross_amt = tot_payment_amount = tot_insurance = tot_employment_income = tot_exempt_income = tot_other_data = tot_director_fee = tot_mbf_amt = tot_donation_amt = tot_catemp_amt = tot_net_amt = tot_salary_amt = tot_bonus_amt = 0
            contract_ids = contract_obj.search(cr, uid, [('employee_id','in',context.get('employe_id'))]) #, ('date_start','<=', end_date), '|', ('date_end', '>=', end_date),('date_end','=',False)
            for contract in contract_obj.browse(cr, uid, contract_ids):
                contract_income_tax_ids = hr_contract_income_tax_obj.search(cr, uid, [('contract_id','=',contract.id),('year_id','=',context.get('datas')['year_id'][0])])
                if contract_income_tax_ids:
                    for emp in hr_contract_income_tax_obj.browse(cr, uid, [contract_income_tax_ids[0]]):
                        total_detail_record += 1
                        sex = birthday = join_date = cessation_date = bonus_declare_date = approve_director_fee_date = fromdate = todate = approval_date = ''
                        if contract.employee_id.gender == 'male':
                            sex = 'M'
                        if contract.employee_id.gender == 'female':
                            sex = 'F'
                        if contract.employee_id.birthday:
                            birthday = datetime.datetime.strptime(contract.employee_id.birthday, DEFAULT_SERVER_DATE_FORMAT)
                            birthday = birthday.strftime('%Y%m%d')
                        if contract.employee_id.join_date:
                            join_date = datetime.datetime.strptime(contract.employee_id.join_date, DEFAULT_SERVER_DATE_FORMAT)
                            join_date = join_date.strftime('%Y%m%d')
                        if contract.employee_id.cessation_date:
                            cessation_date = datetime.datetime.strptime(contract.employee_id.cessation_date, DEFAULT_SERVER_DATE_FORMAT)
                            cessation_date = cessation_date.strftime('%Y%m%d')
                        if emp.bonus_declaration_date:
                            bonus_declare_date = datetime.datetime.strptime(emp.bonus_declaration_date, DEFAULT_SERVER_DATE_FORMAT)
                            bonus_declare_date = bonus_declare_date.strftime('%Y%m%d')
                        if emp.director_fee_approval_date:
                            approve_director_fee_date = datetime.datetime.strptime(emp.director_fee_approval_date, DEFAULT_SERVER_DATE_FORMAT)
                            approve_director_fee_date = approve_director_fee_date.strftime('%Y%m%d')
                        if emp.approval_date:
                            approval_date = datetime.datetime.strptime(emp.approval_date, DEFAULT_SERVER_DATE_FORMAT)
                            approval_date = approval_date.strftime('%Y%m%d')
                        salary_amt = other_allowance = other_data = amount_data = mbf_amt = donation_amt = catemp_amt = net_amt = bonus_amt = prv_yr_gross_amt = gross_comm = 0
                        prev_yr_payslip_ids = payslip_obj.search(cr, uid, [('date_from', '>=', prev_yr_start_date), ('date_from', '<=', prev_yr_end_date), ('employee_id', '=', contract.employee_id.id)])
                        for payslip in payslip_obj.browse(cr, uid, prev_yr_payslip_ids):
                            for line in payslip.line_ids:
                                if line.code == 'GROSS':
                                    prv_yr_gross_amt += line.amount
                        payslip_ids = payslip_obj.search(cr, uid, [('date_from', '>=', start_date), ('date_from', '<=', end_date), ('employee_id', '=', contract.employee_id.id)], order="date_from")
                        for payslip in payslip_obj.browse(cr, uid, payslip_ids):
                            basic_flag = False
                            for line in payslip.line_ids:
                                if line.code == 'BASIC':
                                    basic_flag = True
                            if basic_flag and emp.contract_id.wage:
                                salary_amt += contract.wage
                            for line in payslip.line_ids:
                                if not contract.wage and contract.rate_per_hour and line.code == 'SC100':
                                    salary_amt += line.amount
                                if line.code == 'CPFMBMF':
                                    mbf_amt += line.amount
                                if line.code in ['CPFMBMF', 'CPFSINDA', 'CPFCDAC', 'CPFECF']:
                                    donation_amt += line.amount
                                if line.category_id.code == 'CAT_CPF_EMPLOYEE':
                                    catemp_amt += line.amount
                                if line.code == 'GROSS':
#                                    salary_amt += line.amount
                                    net_amt += line.amount
                                if line.code == 'SC121':
                                    salary_amt -= line.amount
                                    bonus_amt += line.amount
                                    net_amt -= line.amount
                                if line.code in ['SC106','SC108','SC123']:
                                    other_allowance += line.amount
                                    net_amt -= line.amount
                                if line.category_id.code == 'ADD':
                                    salary_amt += line.amount
                                if line.code in ['SC200', 'SC206']:
                                    salary_amt -= line.amount
                                if line.code in ['SC104', 'SC105']:
                                    salary_amt -= line.amount
                                    if not fromdate:
                                        fromdate = datetime.datetime.strptime(payslip.date_from, DEFAULT_SERVER_DATE_FORMAT)
                                        fromdate = fromdate.strftime('%Y%m%d')
                                    todate = datetime.datetime.strptime(payslip.date_to, DEFAULT_SERVER_DATE_FORMAT)
                                    todate = todate.strftime('%Y%m%d')
                                    gross_comm += line.amount
                                    net_amt -= line.amount
#                        if gross_comm and (not emp.fromdate or not emp.todate):
#                            raise osv.except_osv(_('Error'), _('You must be define Gross Commission from date and to date because employee have commission or incentive. for %s employee.' % (contract.employee_id.name) ))
#                        if gross_comm and not emp.gross_commission_indicator:
#                            raise osv.except_osv(_('Error'), _('You must be define Gross Commission indicator because employee have commission or incentive. for %s employee.' % (contract.employee_id.name) ))
#                        if emp.bonus_declaration_date and not bonus_amt:
#                            raise osv.except_osv(_('Error'), _('Bonus Amount not found for %s employee.' % (contract.employee_id.name) ))
#                        if not net_amt:
#                            raise osv.except_osv(_('Error'), _('Net Amount not found for %s employee.' % (contract.employee_id.name) ))
#                        
#                        if not other_data:
#                            raise osv.except_osv(_('Error'), _('Other Data Amount not found for %s employee.' % (contract.employee_id.name) ))
#                        
                        mbf_amt = '%0*d' % (5, int(abs(round(mbf_amt, 0))))
                        donation_amt = '%0*d' % (5, int(abs(round(donation_amt, 0))))
                        catemp_amt = '%0*d' % (7, int(abs(round(catemp_amt, 0))))
                        net_amt = '%0*d' % (9, int(abs(net_amt)))
                        salary_amt = '%0*d' % (9, int(abs(salary_amt)))
                        bonus_amt = '%0*d' % (9, int(abs(bonus_amt)))
                        insurance = director_fee = gain_profit = exempt_income = gross_commission = emp_voluntary_contribution_cpf = benifits_in_kinds = gains_profit_share_option = excess_voluntary_contribution_cpf_employer = contribution_employer = retirement_benifit_from = retirement_benifit_up = compensation_loss_office = gratuity_payment_amt = entertainment_allowance = transport_allowance = pension = 0
                        insurance = '%0*d' % (5, int(abs(emp.insurance)))
                        tot_insurance +=  int(insurance[:5])
                        director_fee = '%0*d' % (9, int(abs(emp.director_fee)))
                        gain_profit = '%0*d' % (9, int(abs(emp.gain_profit)))
                        exempt_income = '%0*d' % (9, int(abs(emp.exempt_income)))
                        employment_income = '%0*d' % (9, int(abs(emp.employment_income)))
                        tot_employment_income += emp.employee_income_tax == 'H' and emp.employment_income or 0
                        gross_commission = '%0*d' % (11, int(abs(gross_comm * 100)))
                        pension = '%0*d' % (11, int(abs(emp.pension * 100)))
                        transport_allowance = '%0*d' % (11, int(abs(transport_allowance * 100)))
                        entertainment_allowance = '%0*d' % (11, int(abs(entertainment_allowance * 100)))
                        gratuity_payment_amt = '%0*d' % (11, int(abs(emp.gratuity_payment_amt * 100)))
                        compensation_loss_office = '%0*d' % (11, int(abs(emp.compensation_loss_office)))
                        retirement_benifit_up = '%0*d' % (11, int(abs(emp.retirement_benifit_up)))
                        retirement_benifit_from = '%0*d' % (11, int(abs(emp.retirement_benifit_from * 100)))
                        contribution_employer = '%0*d' % (11, int(abs(emp.contribution_employer * 100)))
                        excess_voluntary_contribution_cpf_employer = '%0*d' % (11, int(abs(emp.excess_voluntary_contribution_cpf_employer * 100)))
                        gains_profit_share_option = '%0*d' % (11, int(abs(emp.gains_profit_share_option * 100)))
                        benifits_in_kinds = '%0*d' % (11, int(abs(emp.benifits_in_kinds * 100)))
                        emp_voluntary_contribution_cpf = '%0*d' % (7, int(abs(emp.emp_voluntary_contribution_cpf)))
                        prv_yr_gross_amt = '%0*d' % (9, int(abs(prv_yr_gross_amt)))
                        other_data = (int(gross_comm) or 0) + (int(emp.pension) or 0) + (int(transport_allowance) or 0) + \
                                (int(entertainment_allowance) or 0) + (int(other_allowance) or 0) + (int(emp.gratuity_payment_amt) or 0) + \
                                (int(emp.retirement_benifit_from) or 0) + (int(emp.contribution_employer) or 0) + \
                                (int(emp.excess_voluntary_contribution_cpf_employer) or 0) + (int(emp.gains_profit_share_option) or 0) + \
                                (int(emp.benifits_in_kinds) or 0)
                        print "OTHERDATA", other_data
#                        other_data = (int(emp.gross_commission) or 0) + (int(emp.pension) or 0) + (int(emp.transport_allowance) or 0) + \
#                                        (int(emp.entertainment_allowance) or 0) + (int(emp.other_allowance) or 0) + (int(emp.gratuity_payment_amt) or 0) + \
#                                        (int(emp.retirement_benifit_from) or 0) + (int(emp.contribution_employer) or 0) + \
#                                        (int(emp.excess_voluntary_contribution_cpf_employer) or 0) + (int(emp.gains_profit_share_option) or 0) + \
#                                        (int(emp.benifits_in_kinds) or 0)
                        #(emp.compensation_loss_office or 0)
                        
                        amount_data = other_data + int(salary_amt) + int(emp.director_fee) + int(bonus_amt)
                        tot_other_data += other_data
                        other_data = '%0*d' % (9, int(abs(other_data)))
                        other_allowance = '%0*d' % (11, int(abs(other_allowance * 100)))
                        amount_data = '%0*d' % (9, int(abs(amount_data)))
                        tot_prv_yr_gross_amt += int(prv_yr_gross_amt[:9])
                        tot_mbf_amt += int(mbf_amt[:5])
                        tot_donation_amt += int(donation_amt[:5])
                        tot_catemp_amt += int(catemp_amt[:7])
                        tot_net_amt += int(net_amt[:9])
                        tot_salary_amt += int(salary_amt[:9])
                        tot_bonus_amt += int(bonus_amt[:9])
                        tot_director_fee += int(director_fee[:9])
                        tot_exempt_income += int(exempt_income[:9])

                        if not contract.employee_id.gender:
                            raise osv.except_osv(_('Error'), _('There is no gender define for %s employee.' % (contract.employee_id.name) ))
                        if not contract.employee_id.birthday:
                            raise osv.except_osv(_('Error'), _('There is no birth date define for %s employee.' % (contract.employee_id.name) ))
                        if not contract.employee_id.identification_id:
                            raise osv.except_osv(_('Error'), _('There is no identification no define for %s employee.' % (contract.employee_id.name) ))
#                        if not emp.mbf:
#                            raise osv.except_osv(_('Error'), _('MBF Amount not found for %s employee.' % (contract.employee_id.name) ))
#                        if not emp.donation:
#                            raise osv.except_osv(_('Error'), _('Donation Amount not found for %s employee.' % (contract.employee_id.name) ))
#                        if not emp.CPF_designated_pension_provident_fund:
#                            raise osv.except_osv(_('Error'), _('CPF/Designated Pension or Provident Fund Amount not found for %s employee.' % (contract.employee_id.name) ))
#                        if emp.director_fee_approval_date and not emp.director_fee:
#                            raise osv.except_osv(_('Error'), _('Directors Fee not found for %s employee.' % (contract.employee_id.name) ))
#                        if not emp.gain_profit:
#                            raise osv.except_osv(_('Error'), _('Gain Profit not found for %s employee.' % (contract.employee_id.name) ))
#                        if not emp.exempt_income:
#                            raise osv.except_osv(_('Error'), _('Exempt Income not found for %s employee.' % (contract.employee_id.name) ))
#                        if emp.employee_income_tax == 'H' and not emp.employment_income:
#                            raise osv.except_osv(_('Error'), _('Employment Income not found for %s employee.' % (contract.employee_id.name) ))
#                        if not emp.pension:
#                            raise osv.except_osv(_('Error'), _('Pension not found for %s employee.' % (contract.employee_id.name) ))
#                        if not emp.transport_allowance:
#                            raise osv.except_osv(_('Error'), _('Transport Allowance not found for %s employee.' % (contract.employee_id.name) ))
#                        if not emp.entertainment_allowance:
#                            raise osv.except_osv(_('Error'), _('Entertainment Allowance not found for %s employee.' % (contract.employee_id.name) ))
#                        if not emp.other_allowance:
#                            raise osv.except_osv(_('Error'), _('Other Allowance not found for %s employee.' % (contract.employee_id.name) ))
#                        if not emp.gratuity_payment_amt:
#                            raise osv.except_osv(_('Error'), _('Gratuity Payment Amount not found for %s employee.' % (contract.employee_id.name) ))
#                        if not emp.compensation_loss_office:
#                            raise osv.except_osv(_('Error'), _('Compensation Loss Office not found for %s employee.' % (contract.employee_id.name) ))
#                        if not emp.retirement_benifit_up:
#                            raise osv.except_osv(_('Error'), _('Retirement Benifit Up not found for %s employee.' % (contract.employee_id.name) ))
#                        if not emp.retirement_benifit_from:
#                            raise osv.except_osv(_('Error'), _('Retirement Benifit From not found for %s employee.' % (contract.employee_id.name) ))
#                        if not emp.contribution_employer:
#                            raise osv.except_osv(_('Error'), _('Contribution Employer not found for %s employee.' % (contract.employee_id.name) ))
#                        if not emp.excess_voluntary_contribution_cpf_employer:
#                            raise osv.except_osv(_('Error'), _('Excess voluntary contribution cpf employer not found for %s employee.' % (contract.employee_id.name) ))
#                        if not emp.gains_profit_share_option:
#                            raise osv.except_osv(_('Error'), _('Gains profit share option not found for %s employee.' % (contract.employee_id.name) ))
#                        if not emp.emp_voluntary_contribution_cpf:
#                            raise osv.except_osv(_('Error'), _('Employee voluntary contribution cpf not found for %s employee.' % (contract.employee_id.name) ))
#                        if not join_date:
#                            raise osv.except_osv(_('Error'), _('Join Date not found for %s employee.' % (contract.employee_id.name) ))
#                        if not cessation_date and not contract.employee_id.active:
#                            raise osv.except_osv(_('Error'), _('Cessation Date not found for %s employee.' % (contract.employee_id.name) ))
#                        if not emp.address_type:
#                            raise osv.except_osv(_('Error'), _('There is no address type define for %s employee.' % (contract.employee_id.name) ))
#                        if emp.address_type == 'F' and not emp.empcountry_id.code:
#                            raise osv.except_osv(_('Error'), _('There is no country code define for %s employee.' % (contract.employee_id.name) ))
#                        if not emp.empnationality_id:
#                            raise osv.except_osv(_('Error'), _('There is no nationality code define for %s employee.' % (contract.employee_id.name) ))
                        country_code = ''
                        payment_period_form_date = fiscal_start_date
                        payment_period_to_date = fiscal_end_date
                        if cessation_date:
                            payment_period_to_date = cessation_date
                        detail_record = '1'.ljust(1) + \
                                        tools.ustr(contract.employee_id.identification_no or '').ljust(1) + \
                                        tools.ustr(contract.employee_id.identification_id or '')[:12].ljust(12) + \
                                        tools.ustr(contract.employee_id.name or '')[:80].ljust(80) + \
                                        'N'.ljust(1) + \
                                        ''.ljust(10) + \
                                        ''.ljust(32) + \
                                        ''.ljust(3) + \
                                        ''.ljust(5) + \
                                        ''.ljust(6) + \
                                        ''.ljust(30) + \
                                        ''.ljust(30) + \
                                        ''.ljust(30) + \
                                        ''.ljust(6) + \
                                        tools.ustr(country_code).ljust(3) + \
                                        tools.ustr(contract.employee_id.empnationality_id.code or '').ljust(3) + \
                                        tools.ustr(sex).ljust(1) + \
                                        tools.ustr(birthday).ljust(8) + \
                                        tools.ustr(amount_data)[:9].ljust(9) + \
                                        tools.ustr(payment_period_form_date).ljust(8) + \
                                        tools.ustr(payment_period_to_date).ljust(8) + \
                                        tools.ustr(mbf_amt)[:5].ljust(5) + \
                                        tools.ustr(donation_amt)[:5].ljust(5) + \
                                        tools.ustr(catemp_amt)[:7].ljust(7) + \
                                        tools.ustr(insurance)[:5].ljust(5) + \
                                        tools.ustr(salary_amt)[:9].ljust(9) + \
                                        tools.ustr(bonus_amt)[:9].ljust(9) + \
                                        tools.ustr(director_fee)[:9].ljust(9) + \
                                        tools.ustr(other_data)[:9].ljust(9) + \
                                        tools.ustr(gain_profit)[:9].ljust(9) + \
                                        tools.ustr(exempt_income)[:9].ljust(9) + \
                                        tools.ustr(emp.employee_income_tax == 'H' and employment_income or '')[:9].ljust(9) + \
                                        tools.ustr(prv_yr_gross_amt)[:9].ljust(9) + \
                                        tools.ustr(emp.benefits_kind or '').ljust(1) + \
                                        tools.ustr(emp.section_applicable or '').ljust(1) + \
                                        tools.ustr(emp.employee_income_tax or '').ljust(1) + \
                                        tools.ustr(emp.gratuity_payment or '').ljust(1) + \
                                        tools.ustr(emp.compensation or '').ljust(1) + \
                                        tools.ustr(emp.approve_obtain_iras or '').ljust(1) + \
                                        tools.ustr(approval_date).ljust(8) + \
                                        tools.ustr(contract.employee_id.cessation_provisions or '').ljust(1) + \
                                        tools.ustr(emp.from_ir8s or '').ljust(1) + \
                                        tools.ustr(emp.exempt_remission or '').ljust(1) + \
                                        ''.ljust(1) + \
                                        tools.ustr(gross_commission)[:11].ljust(11) + \
                                        tools.ustr(fromdate).ljust(8) + \
                                        tools.ustr(todate).ljust(8) + \
                                        tools.ustr(gross_comm and 'M' or '').ljust(1) + \
                                        tools.ustr(pension)[:11].ljust(11) + \
                                        tools.ustr(transport_allowance)[:11].ljust(11) + \
                                        tools.ustr(entertainment_allowance)[:11].ljust(11) + \
                                        tools.ustr(other_allowance)[:11].ljust(11) + \
                                        tools.ustr(gratuity_payment_amt)[:11].ljust(11) + \
                                        tools.ustr(compensation_loss_office)[:11].ljust(11) + \
                                        tools.ustr(retirement_benifit_up)[:11].ljust(11) + \
                                        tools.ustr(retirement_benifit_from)[:11].ljust(11) + \
                                        tools.ustr(contribution_employer)[:11].ljust(11) + \
                                        tools.ustr(excess_voluntary_contribution_cpf_employer)[:11].ljust(11) + \
                                        tools.ustr(gains_profit_share_option)[:11].ljust(11) + \
                                        tools.ustr(benifits_in_kinds)[:11].ljust(11) + \
                                        tools.ustr(emp_voluntary_contribution_cpf)[:7].ljust(7) + \
                                        tools.ustr(contract.employee_id.job_id.name or '')[:30].ljust(30) + \
                                        tools.ustr(join_date).ljust(8) + \
                                        tools.ustr(cessation_date).ljust(8) + \
                                        tools.ustr(bonus_declare_date).ljust(8) + \
                                        tools.ustr(approve_director_fee_date).ljust(8) + \
                                        tools.ustr(emp.fund_name or '').ljust(60) + \
                                        tools.ustr(emp.deginated_pension or '').ljust(60) + \
                                        ''.ljust(1) + \
                                        ''.ljust(8) + \
                                        ''.ljust(393) + \
                                        ''.ljust(50) + \
                                         "\r\n"
                        tmp_file.write(detail_record)
            tot_payment_amount = tot_salary_amt + tot_bonus_amt + tot_director_fee + tot_other_data
            
            total_detail_record = '%0*d' % (6, int(abs(total_detail_record)))
            tot_payment_amount = '%0*d' % (12, int(abs(tot_payment_amount)))
            tot_mbf_amt = '%0*d' % (12, int(abs(tot_mbf_amt)))
            tot_donation_amt = '%0*d' % (12, int(abs(tot_donation_amt)))
            tot_catemp_amt = '%0*d' % (12, int(abs(tot_catemp_amt)))
            tot_net_amt = '%0*d' % (12, int(abs(tot_net_amt)))
            tot_salary_amt = '%0*d' % (12, int(abs(tot_salary_amt)))
            tot_bonus_amt = '%0*d' % (12, int(abs(tot_bonus_amt)))
            tot_director_fee = '%0*d' % (12, int(abs(tot_director_fee)))
            tot_other_data = '%0*d' % (12, int(abs(tot_other_data)))
            tot_exempt_income = '%0*d' % (12, int(abs(tot_exempt_income)))
            tot_employment_income= '%0*d' % (12, int(abs(tot_employment_income)))
            tot_insurance = '%0*d' % (12, int(abs(tot_insurance)))
            tot_prv_yr_gross_amt = '%0*d' % (12, int(abs(tot_prv_yr_gross_amt)))
            footer_record = '2'.ljust(1) + \
                            tools.ustr(total_detail_record)[:6].ljust(6) + \
                            tools.ustr(tot_payment_amount)[:12].ljust(12) + \
                            tools.ustr(tot_salary_amt)[:12].ljust(12) + \
                            tools.ustr(tot_bonus_amt)[:12].ljust(12) + \
                            tools.ustr(tot_director_fee)[:12].ljust(12) + \
                            tools.ustr(tot_other_data)[:12].ljust(12) + \
                            tools.ustr(tot_exempt_income)[:12].ljust(12) + \
                            tools.ustr(tot_employment_income)[:12].ljust(12) + \
                            tools.ustr(tot_prv_yr_gross_amt)[:12].ljust(12) + \
                            tools.ustr(tot_donation_amt)[:12].ljust(12) + \
                            tools.ustr(tot_catemp_amt)[:12].ljust(12) + \
                            tools.ustr(tot_insurance)[:12].ljust(12) + \
                            tools.ustr(tot_mbf_amt)[:12].ljust(12) + \
                            ' '.ljust(1049) + "\r\n"
            tmp_file.write(footer_record)
        
        finally:
            if tmp_file:
                tmp_file.close()
        file = open(tgz_tmp_filename, "rb")
        out = file.read()
        file.close()
        
        return base64.b64encode(out)
    

    _defaults = {
         'name': 'IR8A.txt',
         'ir8a_txt_file': _generate_file,
    }
    
binary_ir8a_text_file_wizard()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
