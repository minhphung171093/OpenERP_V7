# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import osv, fields

from openerp.tools.translate import _
from datetime import date, datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF

class res_company(osv.Model):
    _inherit = 'res.company'

    payday_value = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), 
                    (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20),
                    (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31)]
    
    _columns = {
        'registration_number': fields.char('Business Registration Number', size=64, required=True, help='Business registration number for ACRA.'),
        'cpf_number': fields.char('CPF Submission Number (CSN)', size=64, required=True, help='This is required for electronic submission of return to CPF Board.'),
        'iras_tax_number': fields.char('IRAS Tax Reference Number', size=64, required=True, help='This is required for electronic tax reporting to IRAS'),
        'payday': fields.selection(payday_value, 'When is the payday every month?', help=''),
        'next_payday': fields.selection([('next_day', 'Next Day'), ('previous_day', 'Previous Day')], 'If the payday falls on a non-working day, when is the salary payout?', help=''),
        'company_sector': fields.selection([('public', 'Public'), ('private', 'Private')], 'Company Sector', help='This specifies whether company belongs to Public sector or Private.'),
        'business_nature': fields.char('Business Nature', size=64, translate=True),
        'establishment': fields.date('Business Established In Year'),
        'enable_esubmission': fields.selection([('yes', 'Yes'), ('no', 'No')], 'Do you have an account registered with CPF Board for e-Submission?'),
        'giro_pay': fields.boolean('Interbank GIRO'),
        'cheque_pay': fields.boolean('Cheque'),
        'cash_pay': fields.boolean('Cash'),
        'passport_id':fields.char('NRIC / FIN / Passport Number', required=True, size=64, help='Enter the NRIC for Singaporean or Singaporean PR employees,' 
                                  'Foreigh Identification Number(FIN) for employees work/employment pass, otherwise enter passport number.'),
    }

class company_sector_type(osv.Model):
    _name = 'company.sector.type'

    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
        'company_sector': fields.selection([('public', 'Public'), ('private', 'Private')], 'Company Sector'),
        'description': fields.text('Description', translate=True),
    }
    
    
class citizen_applicable(osv.Model):
    _name = 'citizen.applicable'

    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
        'citizenship': fields.selection([('singaporean', 'Singaporean'), ('singapore_pr', 'Singapore PR'), ('singapore_pr1', 'Singapore PR 1st Year'), ('singapore_pr2', 'Singapore PR 2nd Year'), ('singapore_pr3_and_on', 'Singapore PR 3rd Year and onwards'), ('singapore_pr1st_2nd_joint', 'Singapore PR 1st Year/2nd Year Joint'), ('foreigner', 'Foreigner')], 'Citizenship'),
        'description': fields.text('Description', translate=True),
    }

class hr_employee(osv.Model):
    _inherit = 'hr.employee'
    
    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()

    def _employee_employer_cpf_rate_for_employee(self, cr, uid, ids, fields, arg, context=None):
        if context is None: context = {}
        rule_line_obj = self.pool.get('age.rule.line')
        contract_obj = self.pool.get('hr.contract')
        result = {}
        for employee in self.browse(cr, uid, ids, context=context):
            result[employee.id] = {'employee_cpf_rate': 0.0, 'employer_cpf_rate': 0.0}
            wage = 0
            age = self.calc_age(datetime.strptime(employee.birthday, "%Y-%m-%d").date())
            cpf_rule_id = self.get_cpf_register(cr, uid, [employee.id], employee.citizenship, employee.company_id.company_sector, context=context)
#             if not cpf_rule_id:
#                 raise osv.except_osv(_('Warning!'),
#                             _('Employee %s does not fall into any CPF register!!!' % employee.name))
            contract_ids = contract_obj.search(cr, uid, [('employee_id', '=', employee.id)], context=context)
            if contract_ids:
                contract = contract_obj.browse(cr, uid, contract_ids[0], context=context)
                wage = contract.wage
            line_ids = rule_line_obj.search(cr, uid, [('cpf_rule_id', '=', cpf_rule_id),
                                           ('age_start', '<=', age),
                                           ('age_end', '>=', age),
                                           ('wage_start', '<=', wage),
                                           ('wage_end', '>=', wage)])
            if line_ids:
                line = rule_line_obj.browse(cr, uid, line_ids[0], context=context)
                result[employee.id] = {
                    'employee_cpf_rate': line.employee_percentage,
                    'employer_cpf_rate': line.employer_percentage
                }
        return result

    _columns = {
        'name_related': fields.related('resource_id', 'name', type='char', string='Name', readonly=True, store=True, help='Exact Name per NRIC / Passport'),
        'passport_id':fields.char('NRIC / FIN / Passport Number', required=True, size=64, help='Enter the NRIC for Singaporean or Singaporean PR employees,' 
                                  'Foreigh Identification Number(FIN) for employees work/employment pass, otherwise enter passport number.'),
        'gender': fields.selection([('male', 'Male'),('female', 'Female')], 'Gender', required=True,),
        'birthday': fields.date("Date of Birth", required=True),
        'citizenship': fields.selection([('singaporean', 'Singaporean'), ('singapore_pr', 'Singapore PR'), ('foreigner', 'Foreigner')], 'Citizenship', required=True,),
        'country_id': fields.many2one('res.country', 'Country of Origin'),
        'pr_startdate': fields.date('Singapore PR Start Date (dd/MMM/yyyy)'), 
        'work_pass_information': fields.selection([('s_pass', 'S Pass'),('e_pass', 'E Pass'),('work_permit', 'Work Permit')], 'Worker’s Qualifications & Permit / Pass Information', ),
        'permit_startdate': fields.date('Permit/Pass Start Date'),
        'permit_enddate': fields.date('Permit/Pass Expiry Date'),
        'religion_id': fields.many2one('res.religion', 'Religion'),
        #Mobile field already there in hr.employee
        'employee_code': fields.char('Employee Code', size=64, required=True),
        'mobile': fields.char('Mobile', size=32,),
        'ethnic_race': fields.many2one('ethnic.race', 'Ethnic Race'),
        'mbmf': fields.boolean('Contribution for MBMF', help='Please Un-tick if not contributing'),
        'sinda': fields.boolean('Contribution for SINDA', help='Please Un-tick if not contributing'),
        'sdl': fields.boolean('Contribution for SDL', help='Please Un-tick if not contributing'),
        'other_address_id': fields.many2one('res.partner', 'Other Address', help='Overseas or Alternative address of the employee'),
        'status': fields.selection([('confirmed','Confirmed'), ('probation', 'Probation'), ('resigned', 'Resigned')], 'Status', help='Present employee status'),
        'ir8a_submission': fields.boolean('Exclude employee from IR8A eSubmission'),
        'employer_cpf_rate': fields.function(_employee_employer_cpf_rate_for_employee, type='float', string='Employer CPF Rate', multi="rate"),
        'employee_cpf_rate': fields.function(_employee_employer_cpf_rate_for_employee, type='float', string='Employee CPF Rate', multi="rate"),
        'cpf_detail_ids': fields.one2many('employee.cpf.detail', 'employee_id', 'CPF Contribution Details'),
        'spr_1and2_joint': fields.boolean('Ready to contribute at full employer and employee rates ?', help='SPR in the 1st and 2nd year of obtaining SPR status but who has jointly applied with employer to contribute at full employer and employee rates. It will be applied only if employee is having the Singapore PR citizenship.'),
    }

    def calc_age(self, joining_date):
        '''
        joining_date: datetime.date() value
        '''
        today = date.today()
        try: 
            age = joining_date.replace(year=today.year)
        except ValueError: # raised when birth date is February 29 and the current year is not a leap year
            age = joining_date.replace(year=today.year, day=joining_date.day-1)
        if age > today:
            return today.year - joining_date.year - 1
        else:
            return today.year - joining_date.year

    def get_cpf_register(self, cr, uid, ids, citizenship, sector, context=None):
        cpf_register_rule_obj = self.pool.get('cpf.rule')
        citizen_applicable_obj = self.pool.get('citizen.applicable')
        citizen_domain = [('citizenship', 'in', ('singaporean', 'singapore_pr', 'singapore_pr1',
                          'singapore_pr2', 'singapore_pr3_and_on', 'singapore_pr1st_2nd_joint'))]
        ca_ids = citizen_applicable_obj.search(cr, uid, citizen_domain, context=context)
        s=[];spr=[];spr1=[];spr2=[];spr3=[];sprj=[];
        for citizen in citizen_applicable_obj.read(cr, uid, ca_ids, ['citizenship'], context=context):
            if citizen['citizenship'] == 'singaporean':
                s.append(citizen['id'])
            elif citizen['citizenship'] == 'singapore_pr':
                spr.append(citizen['id'])
            elif citizen['citizenship'] == 'singapore_pr1':
                spr1.append(citizen['id'])
            elif citizen['citizenship'] == 'singapore_pr2':
                spr2.append(citizen['id'])
            elif citizen['citizenship'] == 'singapore_pr3_and_on':
                spr3.append(citizen['id'])
            elif citizen['citizenship'] == 'singapore_pr1st_2nd_joint':
                sprj.append(citizen['id'])
        all_rules = cpf_register_rule_obj.search(cr, uid, [], context=context)
        def identify_cpf_rule_for_private_sector(citizenship_ids):
            for rule in cpf_register_rule_obj.browse(cr, uid, all_rules, context=context):
                flag = False
                for sector in rule.sector_ids:
                    if sector.company_sector != 'private':
                        # Atleast one sector is set to public, hence can not consider this register
                        flag = True
                if flag:
                    continue
                for applicable_type in rule.applicable_ids:
                    for id in citizenship_ids:
                        if id == applicable_type.id:
                            return rule.id
            return False
        def identify_cpf_rule_for_public_sector(citizenship_ids):
            for rule in cpf_register_rule_obj.browse(cr, uid, all_rules, context=context):
                flag = False
                for sector in rule.sector_ids:
                    if sector.company_sector != 'public':
                        # Atleast one sector is set to private, hence can not consider this register
                        flag = True
                if flag:
                    continue
                for applicable_type in rule.applicable_ids:
                    for id in citizenship_ids:
                        if id == applicable_type.id:
                            return rule.id
            return False
        cpf_rule = False
        if citizenship == 'singapore_pr':
            joining_date = self.browse(cr, uid, ids[0], context=context).pr_startdate
            joining_date = datetime.strptime(joining_date, "%Y-%m-%d").date()
            age = self.calc_age(joining_date)
            if age >= 0 and age < 3 and self.browse(cr, uid, ids[0], context=context).spr_1and2_joint:
                cpf_rule = identify_cpf_rule_for_private_sector(sprj) if not sector == 'private' else \
                            identify_cpf_rule_for_public_sector(sprj)
            if age >= 3:
                cpf_rule = identify_cpf_rule_for_private_sector(spr3) if not sector == 'private' else \
                            identify_cpf_rule_for_public_sector(spr3)
        elif citizenship == 'singaporean':
            cpf_rule = identify_cpf_rule_for_private_sector(s) if not sector == 'private' else \
                            identify_cpf_rule_for_public_sector(s)
        return cpf_rule

    def _default_company_sector(self, cr, uid, context=None):
        if context is None: context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company_sector = user.company_id.company_sector
        return company_sector

    _defaults = {
        'citizenship': 'singaporean',
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.employee', context=c),
        'birthday': fields.date.context_today,
    }
    def _check_unique_code(self, cr, uid, ids, context=None):
        return True

    _constraints = [
            (_check_unique_code, 'Error! You cannot create duplicate code for Employee(s).', ['employee_code'])
    ]

class res_religion(osv.Model):
    _name = 'res.religion'

    _columns = {
        'name': fields.char('Religion Name', size=64, translate=True),
    }

class ethnic_race(osv.Model):
    _name = 'ethnic.race'

    _columns = {
        'name': fields.char('Name', size=64, translate=True),
    }
class hr_contract(osv.Model):
    _inherit = 'hr.contract'

    _columns = {
        #'wage': fields.float('Basic Salary', digits=(16,2), required=True, help="Basic Salary of the employee"),
        'overtime_applicable': fields.boolean('Overtime Pay Applicable'),
        'payment_mode': fields.selection([('cash', 'Cash')], 'Payment Mode', help=''),
    }

class cpf_wage_type(osv.Model):
    _name = 'cpf.wage.type'
    _columns = {
        'name': fields.char('Name', required=True, translate=True),
        'code': fields.char('Code', size=8, required=True),
        'description': fields.text('Description', translate=True),
    }

class hr_salary_rule(osv.Model):
    _inherit = 'hr.salary.rule'

    irab_code = [("a_gross_salary", "A-Gross Salary"), ("b_bonus", "B-Bonus"), ("c_director_fees", "C-Director's Fees"), ("d11", "D11 - Transport"), ("d12", "D12 - Entertainment"), 
                 ("d13", "D13 - Other Allowances"), ("d2", "D2 - Gross Commission"), ("d3", "D3 - Pension, D41 - Gratuity"), ("d42", "D42 - Notice Pay"), 
                 ("d43", "D43 - Ex-Gratia"), ("d44", "D44 - Other Lump Sum"), 
                 ("d45", "D45 - Compensation"), ("d51", "D51 - Retirement Benefits accrued up to 31 December 1992"), 
                 ("d52", "D52 - Retirement Benefits accrued from 1993"), ("d6", "D6 - Employer Overseas Pension / Provident Fund"), 
                 ("d7", "D7 - Employer Excess / Voluntary CPF"), ("d8", "D8 - Gains / Profits from Employee ESOP / ESOW Plans"), 
                 ("d9", "D9 - Value of Benefits-In-Kind"), ("e2", "E2 - Employee CPF / Pension / Fund"), ("e3", "E3 - Donations"), 
                 ("e4", "E4- Insurance Premium"), ("e5", "E5 - MBF Donation"), ("na", "NA - Not Applicable"),
                 ("iestr", "Income Exempt/Subject to Tax Remission")]
    _columns = {
        'cpf_applicability': fields.selection([('ordinary_wages','Ordinary Wages'), ('additional_wages', 'Additional Wages'), ('no_cpf', 'No CPF')], 'CPF Applicability & Type'),
        'irab_code': fields.selection(irab_code, 'IR8A Code', required=True),
        'wage_type_id': fields.many2one('cpf.wage.type', 'Wage Type', required=True)
    }

class hr_payslip(osv.Model):
    _inherit = "hr.payslip"
    
    _columns = {
        'employee_cpf': fields.float('Employee CPF Contribution'),
        'employee_cpf_rate': fields.float('Employee Contribution Rate(%)'),
        'employer_cpf': fields.float('Employer CPF Contribution'),
        'employer_cpf_rate': fields.float('Employer Contribution Rate(%)'),
    }

    def check_done(self, cr, uid, ids, context=None):
        if context is None: context = {}
        rule_line_obj = self.pool.get('age.rule.line')
        payslip_line_obj = self.pool.get('hr.payslip.line')
        contract_obj = self.pool.get('hr.contract')
        emp_obj = self.pool.get('hr.employee')
        for payslip in self.browse(cr, uid, ids, context=context):
            employee_total = 0.0
            employee_cpf_amount = 0.0
            employer_total = 0.0
            employer_cpf_amount = 0.0
            cpf_rule_id = emp_obj.get_cpf_register(cr, uid, [payslip.employee_id.id], payslip.employee_id.citizenship, payslip.employee_id.company_id.company_sector, context=context)
#             if not cpf_rule_id:
#                 raise osv.except_osv(_('Warning!'),
#                             _('Employee %s does not fall into any CPF register!!!' % payslip.employee_id.name))
            contract = contract_obj.browse(cr, uid, payslip.contract_id.id, context=context)
            wage = contract.wage
            age = emp_obj.calc_age(datetime.strptime(payslip.employee_id.birthday, "%Y-%m-%d").date())
            line_ids = rule_line_obj.search(cr, uid, [('cpf_rule_id', '=', cpf_rule_id),
                                           ('age_start', '<=', age),
                                           ('age_end', '>=', age),
                                           ('wage_start', '<=', wage),
                                           ('wage_end', '>=', wage)])
            if line_ids:
                line = rule_line_obj.browse(cr, uid, line_ids[0], context=context)
                
                # Employee Rate Calculation
                employee_rate = line.employee_percentage
                employee_applied_on = line.employee_applied_on
                
                if employee_applied_on == 'aw':
                    pay_line_ids = payslip_line_obj.search(cr, uid, [('slip_id', '=', payslip.id),
                                    ('salary_rule_id.wage_type_id.code', '=', 'AW')])
                    for pay_line in payslip_line_obj.browse(cr, uid, pay_line_ids, context=context):
                        employee_total += pay_line.total
                if employee_applied_on == 'ow':
                    pay_line_ids = payslip_line_obj.search(cr, uid, [('slip_id', '=', payslip.id),
                                    ('salary_rule_id.wage_type_id.code', '=', 'OW')])
                    for pay_line in payslip_line_obj.browse(cr, uid, pay_line_ids, context=context):
                        employee_total += pay_line.total
                if employee_applied_on == 'tw':
                    pay_line_ids = payslip_line_obj.search(cr, uid, [('slip_id', '=', payslip.id),
                                    ('salary_rule_id.wage_type_id.code', 'in', ['OW', 'AW'])])
                    for pay_line in payslip_line_obj.browse(cr, uid, pay_line_ids, context=context):
                        employee_total += pay_line.total
                
                # Employer Rate Calculation
                employer_rate = line.employer_percentage
                employer_applied_on = line.employer_applied_on
                
                if employer_applied_on == 'aw':
                    pay_line_ids = payslip_line_obj.search(cr, uid, [('slip_id', '=', payslip.id),
                                    ('salary_rule_id.wage_type_id.code', '=', 'AW')])
                    for pay_line in payslip_line_obj.browse(cr, uid, pay_line_ids, context=context):
                        employer_total += pay_line.total
                if employer_applied_on == 'ow':
                    pay_line_ids = payslip_line_obj.search(cr, uid, [('slip_id', '=', payslip.id),
                                    ('salary_rule_id.wage_type_id.code', '=', 'OW')])
                    for pay_line in payslip_line_obj.browse(cr, uid, pay_line_ids, context=context):
                        employer_total += pay_line.total
                if employer_applied_on == 'tw':
                    pay_line_ids = payslip_line_obj.search(cr, uid, [('slip_id', '=', payslip.id),
                                    ('salary_rule_id.wage_type_id.code', 'in', ['OW', 'AW'])])
                    for pay_line in payslip_line_obj.browse(cr, uid, pay_line_ids, context=context):
                        employer_total += pay_line.total
                
                employee_cpf_amount = employee_total * (employee_rate/100)
                employer_cpf_amount = employer_total * (employer_rate/100)
                self.write(cr, uid, payslip.id,
                           {'employee_cpf': employee_cpf_amount, 'employee_cpf_rate':employee_rate,
                            'employer_cpf': employer_cpf_amount, 'employer_cpf_rate':employer_rate}, context=context)
                
                payslip_date = datetime.strptime(payslip.date_from, DF)
                month = payslip_date.strftime('%B')
                
                self.pool.get('employee.cpf.detail').create(cr, uid, {'employee_id':payslip.employee_id.id,
                                                'name': 'Contribution for %s' %month, 'date':payslip.date_from, 'employee_cpf':employee_cpf_amount, 'employer_cpf':employer_cpf_amount}, context=context)
        return True
    
    def get_payslip_lines(self, cr, uid, contract_ids, payslip_id, context):
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = category.code in localdict['categories'].dict and localdict['categories'].dict[category.code] + amount or amount
            return localdict
        
        def _sum_salary_rule_wage_type(localdict, wage_type, amount):
            localdict['wage_types'].dict[wage_type.code] = wage_type.code in localdict['wage_types'].dict and localdict['wage_types'].dict[wage_type.code] + amount or amount
            return localdict

        class BrowsableObject(object):
            def __init__(self, pool, cr, uid, employee_id, dict):
                self.pool = pool
                self.cr = cr
                self.uid = uid
                self.employee_id = employee_id
                self.dict = dict

            def __getattr__(self, attr):
                return attr in self.dict and self.dict.__getitem__(attr) or 0.0

        class InputLine(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""
            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = datetime.now().strftime('%Y-%m-%d')
                result = 0.0
                self.cr.execute("SELECT sum(amount) as sum\
                            FROM hr_payslip as hp, hr_payslip_input as pi \
                            WHERE hp.employee_id = %s AND hp.state = 'done' \
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s",
                           (self.employee_id, from_date, to_date, code))
                res = self.cr.fetchone()[0]
                return res or 0.0

        class WorkedDays(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""
            def _sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = datetime.now().strftime('%Y-%m-%d')
                result = 0.0
                self.cr.execute("SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours\
                            FROM hr_payslip as hp, hr_payslip_worked_days as pi \
                            WHERE hp.employee_id = %s AND hp.state = 'done'\
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s",
                           (self.employee_id, from_date, to_date, code))
                return self.cr.fetchone()

            def sum(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[0] or 0.0

            def sum_hours(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[1] or 0.0

        class Payslips(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = datetime.now().strftime('%Y-%m-%d')
                self.cr.execute("SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)\
                            FROM hr_payslip as hp, hr_payslip_line as pl \
                            WHERE hp.employee_id = %s AND hp.state = 'done' \
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s",
                            (self.employee_id, from_date, to_date, code))
                res = self.cr.fetchone()
                return res and res[0] or 0.0

        #we keep a dict with the result because a value can be overwritten by another rule with the same code
        result_dict = {}
        rules = {}
        #added
        wage_types_dict = {}
        categories_dict = {}
        blacklist = []
        payslip_obj = self.pool.get('hr.payslip')
        inputs_obj = self.pool.get('hr.payslip.worked_days')
        obj_rule = self.pool.get('hr.salary.rule')
        payslip = payslip_obj.browse(cr, uid, payslip_id, context=context)
        worked_days = {}
        for worked_days_line in payslip.worked_days_line_ids:
            worked_days[worked_days_line.code] = worked_days_line
        inputs = {}
        for input_line in payslip.input_line_ids:
            inputs[input_line.code] = input_line

        #added
        wage_types_obj = BrowsableObject(self.pool, cr, uid, payslip.employee_id.id, wage_types_dict)
        categories_obj = BrowsableObject(self.pool, cr, uid, payslip.employee_id.id, categories_dict)
        input_obj = InputLine(self.pool, cr, uid, payslip.employee_id.id, inputs)
        worked_days_obj = WorkedDays(self.pool, cr, uid, payslip.employee_id.id, worked_days)
        payslip_obj = Payslips(self.pool, cr, uid, payslip.employee_id.id, payslip)
        rules_obj = BrowsableObject(self.pool, cr, uid, payslip.employee_id.id, rules)

        localdict = {'wage_types':wage_types_obj, 'categories': categories_obj, 'rules': rules_obj, 'payslip': payslip_obj, 'worked_days': worked_days_obj, 'inputs': input_obj}
        #get the ids of the structures on the contracts and their parent id as well
        structure_ids = self.pool.get('hr.contract').get_all_structures(cr, uid, contract_ids, context=context)
        #get the rules of the structure and thier children
        rule_ids = self.pool.get('hr.payroll.structure').get_all_rules(cr, uid, structure_ids, context=context)
        #run the rules by sequence
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]

        for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
            employee = contract.employee_id
            localdict.update({'employee': employee, 'contract': contract})
            for rule in obj_rule.browse(cr, uid, sorted_rule_ids, context=context):
                key = rule.code + '-' + str(contract.id)
                localdict['result'] = None
                localdict['result_qty'] = 1.0
                #check if the rule can be applied
                if obj_rule.satisfy_condition(cr, uid, rule.id, localdict, context=context) and rule.id not in blacklist:
                    #compute the amount of the rule
                    amount, qty, rate = obj_rule.compute_rule(cr, uid, rule.id, localdict, context=context)
                    #check if there is already a rule computed with that code
                    previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                    #set/overwrite the amount computed for this rule in the localdict
                    tot_rule = amount * qty * rate / 100.0
                    localdict[rule.code] = tot_rule
                    rules[rule.code] = rule
                    #sum the amount for its salary category
                    localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                    localdict = _sum_salary_rule_wage_type(localdict, rule.wage_type_id, tot_rule - previous_amount)
                    #create/overwrite the rule in the temporary results
                    result_dict[key] = {
                        'salary_rule_id': rule.id,
                        'contract_id': contract.id,
                        'name': rule.name,
                        'code': rule.code,
                        'category_id': rule.category_id.id,
                        'sequence': rule.sequence,
                        'appears_on_payslip': rule.appears_on_payslip,
                        'condition_select': rule.condition_select,
                        'condition_python': rule.condition_python,
                        'condition_range': rule.condition_range,
                        'condition_range_min': rule.condition_range_min,
                        'condition_range_max': rule.condition_range_max,
                        'amount_select': rule.amount_select,
                        'amount_fix': rule.amount_fix,
                        'amount_python_compute': rule.amount_python_compute,
                        'amount_percentage': rule.amount_percentage,
                        'amount_percentage_base': rule.amount_percentage_base,
                        'register_id': rule.register_id.id,
                        'amount': amount,
                        'employee_id': contract.employee_id.id,
                        'quantity': qty,
                        'rate': rate,
                    }
                else:
                    #blacklist this rule and its children
                    blacklist += [id for id, seq in self.pool.get('hr.salary.rule')._recursive_search_of_rules(cr, uid, [rule], context=context)]

        result = [value for code, value in result_dict.items()]
        return result

class employee_cpf_detail(osv.Model):
    _name = 'employee.cpf.detail'
    _columns = {
        'name': fields.char('Name', translate=True),
        'date': fields.date('Date/Month'),
        'employee_cpf': fields.float('Employee Contribution'),
        'employer_cpf': fields.float('Employer Contribution'),
        'employee_id': fields.many2one('hr.employee', 'Employee')
    }

class cpf_rule(osv.Model):
    _name = 'cpf.rule'

    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
        'sector_ids':fields.many2many('company.sector.type', 'cpf_rule_sector_rel', 'rule_id', 'sector_id', 'Company Sectors'),
        'applicable_ids':fields.many2many('citizen.applicable', 'cpf_rule_citz_app_rel', 'rule_id', 'citizen_app_id', 'Applicable for'),
        'age_rule_ids': fields.one2many('age.rule.line', 'cpf_rule_id', 'Age Rules'),
    }
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = self.search(cr, user, [('name', operator, name)]+ args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        res = super(cpf_rule, self).search(cr, uid, args, offset, limit, order, context, count)
        if context.get('employee_company_id') and context.get('emp_citizen'):
            company = self.pool.get('res.company').browse(cr, uid, context['employee_company_id'])
            company_sector = company.company_sector
            cpf_rule_ids = self.search(cr, uid, [('sector_ids.company_sector', '=', company_sector), ('applicable_ids.citizenship', '=', context['emp_citizen'])])
            if cpf_rule_ids:
                return cpf_rule_ids
        elif context.get('employee_company_id') and not context.get('emp_citizen'):
            company = self.pool.get('res.company').browse(cr, uid, context['employee_company_id'])
            company_sector = company.company_sector
            cpf_rule_ids = self.search(cr, uid, [('sector_ids.company_sector', '=', company_sector)])
            if cpf_rule_ids:
                return cpf_rule_ids
        elif not context.get('employee_company_id') and context.get('emp_citizen'):
            cpf_rule_ids = self.search(cr, uid, [('applicable_ids.citizenship', '=', context['emp_citizen'])])
            if cpf_rule_ids:
                return cpf_rule_ids
        return res


class age_rule_line(osv.Model):
    _name = 'age.rule.line'

    _columns = {
        'name': fields.char('Name', size=64, translate=True),
        'cpf_rule_id': fields.many2one('cpf.rule', 'CPF Rule Register'),
        'age_start': fields.integer('Age Start'),
        'age_end': fields.integer('Age End'),
        'wage_start': fields.float('Wage From'),
        'wage_end': fields.float('Wage End'),
        'employer_percentage': fields.float('Employer Percentages'),
        'employer_applied_on': fields.selection([('ow', 'Ordinary Wage'), ('aw', 'Additional Wage'), ('tw', 'Total Wage')], 'Employer Percentage Applied On'),
        'employee_percentage': fields.float('Employee Percentages'),
        'employee_applied_on': fields.selection([('ow', 'Ordinary Wage'), ('aw', 'Additional Wage'), ('tw', 'Total Wage')], 'Employee Percentage Applied On'),
    }
    
class cpf_submission_file(osv.Model):
    _name = "cpf.submission.file"
    
    state = [('draft', 'Draft'), ('wait', 'Waiting Approval'), ('approve', 'Approved')]
    
    _columns = {
        'name': fields.char("Name", size=64, translate=True,required=True),
        'cpf_file_id': fields.many2one('ir.attachment',"CPF File"),
        'employee_ids': fields.many2many('hr.employee','cpf_submission_file_rel', 'emp_id', 'cpf_file_id', 'Employee'),
        'state': fields.selection(state, 'State'),
        'validate_id': fields.many2one('res.users', 'Validated By'),
        'user_id': fields.many2one('res.users', 'Created By'),
        'date': fields.datetime('Create Date'),
    }