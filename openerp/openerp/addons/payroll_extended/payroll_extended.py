#-*- coding:utf-8 -*-
from osv import osv, fields
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from dateutil import parser, rrule
from datetime import timedelta
import copy
import math
import tools.safe_eval
import calendar
from dateutil.relativedelta import relativedelta

tools.safe_eval._ALLOWED_MODULES.append('math')

def _offset_format_timestamp(src_tstamp_str, src_format, dst_format, ignore_unparsable_time=True, context=None):
    """
    Convert a source timestamp string into a destination timestamp string, attempting to apply the
    correct offset if both the server and local timezone are recognized, or no
    offset at all if they aren't or if tz_offset is false (i.e. assuming they are both in the same TZ).

    @param src_tstamp_str: the str value containing the timestamp.
    @param src_format: the format to use when parsing the local timestamp.
    @param dst_format: the format to use when formatting the resulting timestamp.
    @param server_to_client: specify timezone offset direction (server=src and client=dest if True, or client=src and server=dest if False)
    @param ignore_unparsable_time: if True, return False if src_tstamp_str cannot be parsed
                                   using src_format or formatted using dst_format.

    @return: destination formatted timestamp, expressed in the destination timezone if possible
            and if tz_offset is true, or src_tstamp_str if timezone offset could not be determined.
    """
    if not src_tstamp_str:
        return False

    res = src_tstamp_str
    
    if src_format and dst_format:
        try:
            dt_value = datetime.strptime(src_tstamp_str, src_format)
            if context.get('tz', False):
                try:
                    import pytz
                    src_tz = pytz.timezone(context['tz'])
                    dst_tz = pytz.timezone('UTC')
                    src_dt = src_tz.localize(dt_value, is_dst=True)
                    dt_value = src_dt.astimezone(dst_tz)
                except Exception, e:
                    pass
            res = dt_value.strftime(dst_format)
        except Exception, e:
            if not ignore_unparsable_time:
                return False
            pass
    return res

class ir_cron(osv.osv):
    """ Model describing cron jobs (also called actions or tasks).
    """
    _inherit = "ir.cron"
    
    def change_contract_default_name_year(self, cr, uid, reminder_to_change_year_number=None, context=None):
        if context is None:
            context = {}
        user_data = self.pool.get('res.users').browse(cr, uid, uid, context)
        context.update({'tz': user_data.tz})
        if reminder_to_change_year_number:
            cron_data = self.browse(cr, uid, reminder_to_change_year_number, context)
            str_dt_current = _offset_format_timestamp(cron_data.nextcall, '%Y-%m-%d %H:%M:%S', DEFAULT_SERVER_DATETIME_FORMAT, context=context)
            cr.execute("UPDATE ir_cron SET nextcall=%s WHERE id=%s", (str_dt_current, reminder_to_change_year_number))
        return True

ir_cron()

class res_partner_bank(osv.osv):
    _inherit = 'res.partner.bank'
    
    _columns = {
            'branch_id':fields.char("Branch ID", size=48),
    }
res_partner_bank()

class payroll_extended(osv.osv):
    _inherit = 'hr.payslip.input'
    
    _columns = {
        'code': fields.char('Code', size=52, required=False, readonly=False, help="The code that can be used in the salary rules"),
        'contract_id': fields.many2one('hr.contract', 'Contract', required=False, help="The contract for which applied this input"),
    }
payroll_extended()
class hr_payslip_worked_days(osv.osv):

    _inherit = 'hr.payslip.worked_days'

    _columns = {
        'code': fields.char('Code', size=52, required=False, readonly=False, help="The code that can be used in the salary rules"),
        'contract_id': fields.many2one('hr.contract', 'Contract', required=False, help="The contract for which applied this input"),
    }
hr_payslip_worked_days() 

class hr_payslip_line(osv.osv):

    _inherit = 'hr.payslip.line'
    
    _columns = {
        'contract_id':fields.many2one('hr.contract', 'Contract', required=False, select=True),
        'employee_id':fields.many2one('hr.employee', 'Employee', required=False),
    }
hr_payslip_line()

class hr_salary_rule(osv.osv):
    _inherit = 'hr.salary.rule'
    _columns = {
        'code':fields.char('Code', size=64, required=False, help="The code of salary rules can be used as reference in computation of other rules. In that case, it is case sensitive."),
        'id': fields.integer('ID', readonly=True),
        'hr_salary_rule_glcode_ids': fields.one2many('hr.salary.rule.glcode', 'salaryrule_id', 'Salary Rule GL Code'),
    }
hr_salary_rule()

class hr_contribution_register(osv.osv):
    _inherit = 'hr.contribution.register'
    _columns = {
            'register_glcode_ids': fields.one2many('hr.salary.rule.glcode', 'register_id', 'Contribution GL Code')
    }
hr_contribution_register()

class hr_salary_rule_glcode(osv.osv):

    _name = 'hr.salary.rule.glcode'

    _rec_name = 'salaryrule_id'#glcode_id

    _columns = {
        'register_id': fields.many2one('hr.contribution.register', 'GL Code'),
        'salaryrule_id': fields.many2one('hr.salary.rule', 'GL Code'),
        'gl_code_id': fields.many2one('salary.report.for.exchequer.glcode', 'GL Code', required=True),
        'emp_categ_id': fields.many2one('hr.employee.category', 'Employee Category', required=True),
        'saved_back_cpf': fields.boolean('Saved Back CPF'),
        'saved_back_salary': fields.boolean('Saved Back Salary'),
        'nagative': fields.boolean('Negative'),
        'apply_bank_cheque': fields.selection([('apply_for_bank', 'Apply for Bank'), ('apply_for_cheque', 'Apply For Cheque')], string='Apply for Bank/Cheque'),
    }

hr_salary_rule_glcode()

class hr_payslip(osv.osv):
    
    _inherit = 'hr.payslip'
    _order = 'employee_name'

    _columns = {
        'cheque_number':fields.char("Cheque Number", size=64),
        'active': fields.boolean('Pay'),
        'pay_by_cheque': fields.boolean('Pay By Cheque'),
        'employee_name': fields.related('employee_id', 'name', type="char", size=256, string="Employee Name", store=True),
        'active_employee': fields.related('employee_id', 'active', type="boolean", string="Active Employee")
    }

    _defaults = {
        'active': True,
    }

    def get_worked_day_lines(self, cr, uid, contract_ids, date_from, date_to, context=None):
        """
        @param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        if date_from and date_to:
            date_from_cur = datetime.strptime(date_from, DEFAULT_SERVER_DATE_FORMAT)
            previous_month_obj = parser.parse(date_from_cur.strftime(DEFAULT_SERVER_DATE_FORMAT)) - relativedelta(months=1)
            total_days = calendar.monthrange(previous_month_obj.year, previous_month_obj.month)[1]
            first_day_of_previous_month = datetime.strptime("1-" + str(previous_month_obj.month) + "-" + str(previous_month_obj.year) , '%d-%m-%Y')
            last_day_of_previous_month = datetime.strptime(str(total_days) + "-" + str(previous_month_obj.month) + "-" + str(previous_month_obj.year) , '%d-%m-%Y')
            date_from = datetime.strftime(first_day_of_previous_month, DEFAULT_SERVER_DATE_FORMAT)
            date_to = datetime.strftime(last_day_of_previous_month, DEFAULT_SERVER_DATE_FORMAT)

        results = super(hr_payslip, self).get_worked_day_lines(cr, uid, contract_ids, date_from, date_to, context=context)
        def was_on_leave(employee_id, datetime_day, context=None):
            res = False
            day = datetime_day.strftime("%Y-%m-%d")
            holiday_ids = self.pool.get('hr.holidays').search(cr, uid, [('state', '=', 'validate'), ('employee_id', '=', employee_id), ('type', '=', 'remove'), ('date_from', '<=', day), ('date_to', '>=', day)])
            if holiday_ids:
                res = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[0]
            return res
        holiday_obj = self.pool.get('hr.holidays')
        calendar_obj = self.pool.get('resource.calendar')
        final_results = []
        for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
            if not contract.working_hours:
                continue
            leaves = {}
            day_from = datetime.strptime(date_from, "%Y-%m-%d")
            day_to = datetime.strptime(date_to, "%Y-%m-%d")
            nb_of_days = (day_to - day_from).days + 1
            for day in range(0, nb_of_days):
                new_day_format = (day_from + timedelta(days=day)).strftime("%Y-%m-%d")
                holiday_ids = holiday_obj.search(cr, uid, [('state', '=', 'validate'), ('employee_id', '=', contract.employee_id.id),
                                                    ('type', '=', 'remove'), ('date_from', '<=', new_day_format), ('date_to', '>=', new_day_format),
                                                    ('holiday_status_id.weekend_calculation', '=', True)])
                if holiday_ids:
                    leave_type = holiday_obj.browse(cr, uid, holiday_ids[0], context=context)
                else:
                    leave_type = False
                    working_hours_on_day = calendar_obj.working_hours_on_day(cr, uid, contract.working_hours, day_from + timedelta(days=day), context)
                    if working_hours_on_day:
                        leave_type = was_on_leave(contract.employee_id.id, day_from + timedelta(days=day), context=context)
                if leave_type:
                    if leave_type.leave_type not in ['pm', 'am']:
                        no_of_day = 1.0
                    else:
                        no_of_day = 0.5 
                    if leave_type.holiday_status_id.name in leaves:
                        leaves[leave_type.holiday_status_id.name]['number_of_days'] += no_of_day
                        leaves[leave_type.holiday_status_id.name]['number_of_hours'] += working_hours_on_day * no_of_day
                    else:
                        leaves[leave_type.holiday_status_id.name] = {
                            'name': leave_type.holiday_status_id.name2,
                            'sequence': 5,
                            'code': leave_type.holiday_status_id.name,
                            'number_of_days': no_of_day,
                            'number_of_hours': working_hours_on_day * no_of_day,
                            'contract_id': contract.id,
                        }
            final_results += copy.deepcopy(results)
            for rec in results:
                if rec.get('code') in leaves and leaves.get(rec.get('code', {})):
                    final_results.remove(rec)
                    final_results.append(leaves.get(rec.get('code')))
            for key, val in leaves.items():
                flag = True
                for rec in results:
                    if key == rec.get('code'):
                        flag = False
                if flag:
                    final_results.append(leaves.get(key))
        return final_results

    def onchange_employee_id(self, cr, uid, ids, date_from, date_to, employee_id, contract_id, context=None):
        result = super(hr_payslip, self).onchange_employee_id(cr, uid, ids, date_from, date_to, employee_id, contract_id, context=context)
        if employee_id:
            active_employee = self.pool.get('hr.employee').browse(cr, uid, employee_id).active
            result['value'].update({'active_employee': active_employee})
        if date_from and date_to:
            current_date_from = date_from
            current_date_to = date_to
            date_from_cur = datetime.strptime(date_from, DEFAULT_SERVER_DATE_FORMAT)
            previous_month_obj = parser.parse(date_from_cur.strftime(DEFAULT_SERVER_DATE_FORMAT)) - relativedelta(months=1)
            total_days = calendar.monthrange(previous_month_obj.year, previous_month_obj.month)[1]
            first_day_of_previous_month = datetime.strptime("1-" + str(previous_month_obj.month) + "-" + str(previous_month_obj.year) , '%d-%m-%Y')
            last_day_of_previous_month = datetime.strptime(str(total_days) + "-" + str(previous_month_obj.month) + "-" + str(previous_month_obj.year) , '%d-%m-%Y')
            date_from = datetime.strftime(first_day_of_previous_month, DEFAULT_SERVER_DATE_FORMAT)
            date_to = datetime.strftime(last_day_of_previous_month, DEFAULT_SERVER_DATE_FORMAT)
            dates = list(rrule.rrule(rrule.DAILY, dtstart=parser.parse(date_from), until=parser.parse(date_to)))
            sunday = saturday = weekdays = 0
            for day in dates:
                if day.weekday() == 5:
                    saturday += 1
                elif day.weekday() == 6:
                    sunday += 1
                else:
                    weekdays += 1
            res = {'code':'TTLPREVDAYINMTH','name':'Total number of days for previous month','number_of_days':len(dates), 'sequence': 2}
            result.get('value').get('worked_days_line_ids').append(res)
            res = {'code':'TTLPREVSUNINMONTH','name':'Total sundays in previous month','number_of_days':sunday, 'sequence': 3}
            result.get('value').get('worked_days_line_ids').append(res)
            res = {'code':'TTLPREVSATINMONTH','name':'Total saturdays in previous month','number_of_days':saturday, 'sequence': 4}
            result.get('value').get('worked_days_line_ids').append(res)
            res = {'code':'TTLPREVWKDAYINMTH','name':'Total weekdays in previous month','number_of_days':weekdays, 'sequence': 5}
            result.get('value').get('worked_days_line_ids').append(res)

            dates = list(rrule.rrule(rrule.DAILY, dtstart=parser.parse(current_date_from), until=parser.parse(current_date_to)))
            sunday = saturday = weekdays = 0
            for day in dates:
                if day.weekday() == 5:
                    saturday += 1
                elif day.weekday() == 6:
                    sunday += 1
                else:
                    weekdays += 1
            res = {'code':'TTLCURRDAYINMTH','name':'Total number of days for current month','number_of_days':len(dates), 'sequence': 2}
            result.get('value').get('worked_days_line_ids').append(res)
            res = {'code':'TTLCURRSUNINMONTH','name':'Total sundays in current month','number_of_days':sunday, 'sequence': 3}
            result.get('value').get('worked_days_line_ids').append(res)
            res = {'code':'TTLCURRSATINMONTH','name':'Total saturdays in current month','number_of_days':saturday, 'sequence': 4}
            result.get('value').get('worked_days_line_ids').append(res)
            res = {'code':'TTLCURRWKDAYINMTH','name':'Total weekdays in current month','number_of_days':weekdays, 'sequence': 5}
            result.get('value').get('worked_days_line_ids').append(res)
            cur_month_weekdays = 0
            if contract_id:
                contract_data = self.pool.get('hr.contract').browse(cr, uid, contract_id)
                contract_start_date = contract_data.date_start
                contract_end_date = contract_data.date_end
                print "::::::", contract_start_date, contract_end_date, current_date_from, current_date_to
                if contract_start_date:
                    if contract_start_date >= current_date_from and contract_start_date <= current_date_to:
                        current_month_days = list(rrule.rrule(rrule.DAILY, dtstart=parser.parse(contract_start_date), until=parser.parse(current_date_to)))
                        for day in current_month_days:
                            if day.weekday() not in [5,6]:
                                cur_month_weekdays += 1
                elif contract_end_date:
                    if contract_end_date >= current_date_from and contract_end_date <= current_date_to:
                        current_month_days = list(rrule.rrule(rrule.DAILY, dtstart=parser.parse(current_date_from), until=parser.parse(contract_end_date)))
                        for day in current_month_days:
                            if day.weekday() not in [5,6]:
                                cur_month_weekdays += 1
            if cur_month_weekdays:
                res = {'code':'TTLCURCONTDAY','name':'Total current contract days in current month','number_of_days':cur_month_weekdays, 'sequence': 6}
                result.get('value').get('worked_days_line_ids').append(res)
            else:
                res = {'code':'TTLCURCONTDAY','name':'Total current contract days in current month','number_of_days':weekdays, 'sequence': 6}
                result.get('value').get('worked_days_line_ids').append(res)

        if employee_id:
            holiday_status_obj = self.pool.get("hr.holidays.status")
            holiday_status_ids = holiday_status_obj.search(cr, uid, [])
            for holiday_status in holiday_status_obj.browse(cr, uid, holiday_status_ids, context=context):
                flag = False
                for payslip_data in result["value"].get("worked_days_line_ids"):
                    if payslip_data.get("code") == holiday_status.name:
                        flag = True
                if not flag:
                    res = {'code':holiday_status.name, 'name':holiday_status.name2, 'number_of_days':0.0, 'sequence': 0}
                    result.get('value').get('worked_days_line_ids').append(res)
        return result

    def compute_sheet(self, cr, uid, ids, context=None):
        result = super(hr_payslip, self).compute_sheet(cr, uid, ids, context=context)
        slip_line_pool = self.pool.get('hr.payslip.line')
        lines = []
        for payslip in self.browse(cr, uid, ids, context=context):
            for line in payslip.line_ids:
                if line.amount == 0:
                    lines.append(line.id)
        if lines:
            slip_line_pool.unlink(cr, uid, lines, context=context)
        return result

hr_payslip()

class hr_contract(osv.osv):
    
    _inherit = 'hr.contract'

    _columns = {
        'hr_contract_income_tax_ids': fields.one2many('hr.contract.income.tax', 'contract_id', 'Income Tax'),
        'wage_to_pay': fields.float('Wage To Pay'),
        'rate_per_hour': fields.float('Rate per hour for part timer'),
        'active_employee': fields.related('employee_id', 'active', type="boolean", string="Active Employee")
    }

    _defaults = {
        'name': '/'
    }

    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        result = {'value': {}}
        if employee_id:
            active_employee = self.pool.get('hr.employee').browse(cr, uid, employee_id).active
            result['value'].update({'active_employee': active_employee})
        return result

    def create(self, cr, uid, vals, context=None):
        vals.update({'name': self.pool.get('ir.sequence').get(cr, uid, 'hr.contract')})
        return super(hr_contract, self).create(cr, uid, vals, context=context)

    def reminder_to_change_year_number(self, cr, uid, context=None):
        sequence_obj = self.pool.get('ir.sequence')
        sequence_id = sequence_obj.search(cr, uid, [('code', '=', 'hr.contract')])
        sequence_obj.write(cr, uid, sequence_id, {'number_next': 1})
        return True

hr_contract()

class hr_contract_income_tax(osv.osv):

    _name = 'hr.contract.income.tax'
    _rec_name = 'contract_id'

    def _get_payroll_computational_data(self, cr, uid, ids, name, args, context=None):
        res={}
        payslip_obj = self.pool.get('hr.payslip')
        for data in self.browse(cr, uid, ids, context):
            res[data.id] = {
                    'mbf': 0.0,
                    'donation': 0.0,
                    'CPF_designated_pension_provident_fund':0.0,
                    'payslip_net_amount': 0.0,
                    'bonus_amount': 0.0
            }
            mbf = donation = CPF_designated_pension_provident_fund = payslip_net_amount = bonus_amount = 0.00
            start_date = data.year_id.date_start
            end_date = data.year_id.date_stop
            payslip_ids = payslip_obj.search(cr, uid, [('date_from', '>=', start_date), ('date_from', '<=', end_date), ('employee_id', '=', data.contract_id.employee_id.id)])
            for payslip in payslip_obj.browse(cr, uid, payslip_ids):
                for line in payslip.line_ids:
                    if line.code == 'CPFMBMF':
                        mbf += line.amount
                    if line.code in ['CPFSINDA', 'CPFCDAC', 'CPFECF']:
                        donation += line.amount
                    if line.category_id.code == 'CAT_CPF_EMPLOYEE':
                        CPF_designated_pension_provident_fund += line.amount
                    if line.code == 'GROSS':
                        payslip_net_amount += line.amount
                    if line.amount == 'SC121':
                        bonus_amount += line.amount
            res[data.id]['mbf'] = mbf or 0.0
            res[data.id]['donation'] = donation or 0.0
            res[data.id]['CPF_designated_pension_provident_fund'] = CPF_designated_pension_provident_fund or 0.0
            res[data.id]['payslip_net_amount'] = payslip_net_amount or 0.0
            res[data.id]['bonus_amount'] = bonus_amount or 0.0
        return res

    _columns = {
#            'address_type': fields.selection([('L', 'Local residential address'),
#                                              ('F', 'Foreign address'),
#                                              ('C', 'Local C/O address'),
#                                              ('N', 'Not Available')], string='Address Type'),
            'contract_id': fields.many2one('hr.contract', 'Contract'),
            'year_id': fields.many2one('account.fiscalyear', 'Year Of Assessment'),
#            'identification_no': fields.selection([('1', 'NRIC'), ('2', 'FIN'), ('3', 'Immigration File Ref No.'),
#                                                   ('4', 'Work Permit No'), ('5', 'Malaysian I/C (for non-resident director and seaman only)'),
#                                                   ('6', 'Passport No. (for non-resident director and seaman only)')], string='2. ID Type of Employee'),
#            'empcountry_id': fields.many2one('employee.country', '6(k). Country Code of address'),
#            'empnationality_id': fields.many2one('employee.nationality', '7. Nationality Code'),
            'cessation_date': fields.date('Cessation Date'),
            'director_fee': fields.float('18. Directors fee'),
            'gain_profit': fields.float('19(a). Gains & Profit from Share Options For S10 (1) (g)'),
            'exempt_income': fields.float('20. Exempt Income/ Income subject to Tax Remission'),
            'employment_income': fields.float('21. Amount of employment income for which tax is borne by employer'),
            'benefits_kind': fields.selection([('Y', "Benefits-in-kind rec'd"), ('N', "Benefits-in-kind not rec'd")], string='23. Benefits-in-kind'),
            'section_applicable': fields.selection([('Y', 'S45 applicable'), ('N', 'S45 not applicable')], string='24. Section 45 applicable'),
            'employee_income_tax': fields.selection([('F', 'Tax fully borne by employer on employment income only'), ('P', 'Tax partially borne by employer on certain employment income items'),
                                                     ('H', 'A fixed amount of income tax liability borne by employee. Not applicable if income tax is fully paid by employee'),
                                                     ('N', 'Not Applicable')], string='25. Employees Income Tax borne by employer'),
            'gratuity_payment': fields.selection([('Y', 'Gratuity/ payment in lieu of notice/ex-gratia paid'),
                                                  ('N', 'No Gratuity/ payment in lieu of notice/ex-gratia paid')], string='26. Gratuity/ Notice Pay/ Ex-gratia payment/ Others'),
            'compensation': fields.selection([('Y', ' Compensation / Retrenchment benefits paid'),
                                              ('N', 'No Compensation / Retrenchment benefits paid')], string='27. Compensation for loss of office'),
            'approve_obtain_iras': fields.selection([('Y', 'Approval obtained from IRAS'),
                                                     ('N', 'No approval obtained from IRAS ')], string='27(a). Approval obtained from IRAS'),
            'approval_date': fields.date('27(b). Date of approval'),
#            'cessation_provisions': fields.selection([('Y', 'Cessation Provisions applicable'),
#                                                      ('N', 'Cessation Provisions not applicable')], string='28. Cessation Provisions'),
            'from_ir8s': fields.selection([('Y', 'IR8S is applicable'), ('N', 'IR8S is not applicable')], string='29. Form IR8S'),
            'exempt_remission': fields.selection([('1', 'Tax Remission on Overseas Cost of Living Allowance (OCLA)'),
                                                  ('2', ' Tax remission on Operation Headquarters (OHQ)'),
                                                  ('3', 'Seaman'), ('4', 'Exemption'),
                                                  ('N', 'Not Applicable')], string='30. Exempt/ Remission income Indicator'),
            'gross_commission': fields.float('31. Gross Commission'),
            'fromdate': fields.date('32(a). From Date'),
            'todate': fields.date('32(b). To Date'),
            'gross_commission_indicator': fields.selection([('M', ' Monthly'), ('O', 'Other than monthly'),
                                                            ('B', 'Both')], string='33. Gross Commission Indicator'),
            'pension': fields.float('34. Pension'),
            'transport_allowance': fields.float('35. Transport Allowance'),
            'entertainment_allowance': fields.float('36. Entertainment Allowance'),
            'other_allowance': fields.float('37. Other Allowance'),
            'gratuity_payment_amt': fields.float('38. Gratuity/ Notice Pay/ Ex-gratia payment/ Others'),
            'compensation_loss_office': fields.float('38(a). Compensation for loss of office'),
            'retirement_benifit_up': fields.float('39. Retirement benefits accrued up to 31.12.92'),
            'retirement_benifit_from': fields.float('40. Retirement benefits accrued from 1993'),
            'contribution_employer': fields.float('41. Contributions made by employer to any pension / provident fund constituted outside Singapore'),
            'excess_voluntary_contribution_cpf_employer': fields.float('42. Excess / voluntary contribution to CPF by employer'),
            'gains_profit_share_option': fields.float('43. Gains and profits from share options for S10 (1) (b)'),
            'benifits_in_kinds': fields.float('44. Value of benefits-in- kinds'),
            'emp_voluntary_contribution_cpf': fields.float("45. E'yees voluntary contribution to CPF obligatory by contract of employment (overseas posting)"),
            'bonus_declaration_date': fields.date('49. Date of declaration of bonus'),
            'director_fee_approval_date': fields.date('50. Date of approval of directors fees'),
            'fund_name': fields.char('51. Name of fund for Retirement benefits', size=32),
            'deginated_pension': fields.char("52. Name of Designated Pension or Provident Fund for which e'yee made compulsory contribution", size=32),
            'mbf': fields.function(_get_payroll_computational_data, string='12. MBF', type='float', multi="payroll_data_all"),
            'donation': fields.function(_get_payroll_computational_data, string='13. Donation', type='float', multi="payroll_data_all"),
            'CPF_designated_pension_provident_fund': fields.function(_get_payroll_computational_data, string='14. CPF/Designated Pension or Provident Fund', type='float', multi="payroll_data_all"),
            
            'indicator_for_CPF_contributions': fields.selection([('Y','Obligatory'), ('N','Not obligatory')], string='84. Indicator for CPF contributions in respect of overseas posting which is obligatory by contract of employment'),
            'CPF_capping_indicator': fields.selection([('Y','Capping has been applied'), ('N','Capping has been not applied')], string='85. CPF capping indicator'),
            'singapore_permanent_resident_status': fields.selection([('Y','Singapore Permanent Resident Status is approved'), 
                                                                     ('N','Singapore Permanent Resident Status is not approved')], string='86. Singapore Permanent Resident Status is approved'),
            'approval_has_been_obtained_CPF_board': fields.selection([('Y',' Approval has been obtained from CPF Board to make full contribution'),
                                                                      ('N',' Approval has NOT been obtained from CPF Board to make full contribution')], string='87. Approval has been obtained from CPF Board to make full contribution'),
            'eyer_contibution': fields.float('88. Eyers Contribution'),
            'eyee_contibution': fields.float('89. Eyees Contribution'),
            'additional_wage': fields.float('99. Additional wages'),
            'add_wage_pay_date': fields.date('101. Date of payment for additional wages'),
            'refund_eyers_contribution': fields.float('102. Amount of refund applicable to Eyers contribution'),
            'refund_eyees_contribution': fields.float('105. Amount of refund applicable to Eyees contribution'),
            'refund_eyers_date': fields.date('104. Date of refund given to employer'),
            'refund_eyees_date': fields.date('107. Date of refund given to employee'),
            'refund_eyers_interest_contribution': fields.float('103. Amount of refund applicable to Eyers Interest on contribution'),
            'refund_eyees_interest_contribution': fields.float('106. Amount of refund applicable to Eyees Interest on contribution'),
            'insurance': fields.float('Insurance'),
            'payslip_net_amount': fields.function(_get_payroll_computational_data, string='Gross Salary, Fees, Leave Pay, Wages and Overtime Pay', type='float', multi="payroll_data_all"),
            'bonus_amount': fields.function(_get_payroll_computational_data, string='Bonus', type='float', multi="payroll_data_all"),
    }
hr_contract_income_tax()

class hr_employee(osv.osv):
    
    _inherit = 'hr.employee'

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        """
            Override Search method for put filter on current working status. 
        """
        if context and context.get('batch_start_date') and context.get('batch_end_date'):
            contract_obj = self.pool.get('hr.contract')
            active_contract_employee_list = []
            contract_ids = contract_obj.search(cr, uid, ['|', ('date_end', '>=', context.get('batch_start_date')), ('date_end', '=', False), ('date_start', '<=', context.get('batch_end_date'))])
            for contract in contract_obj.browse(cr, uid, contract_ids):
                active_contract_employee_list.append(contract.employee_id.id)
            args.append(('id', 'in', active_contract_employee_list))
        return super(hr_employee, self).search(cr, uid, args, offset, limit, order, context=context, count=count)

    _columns = {
            'cessation_date': fields.date('Cessation Date'),
            'identification_no': fields.selection([('1', 'NRIC'), ('2', 'FIN'), ('3', 'Immigration File Ref No.'),
                                                   ('4', 'Work Permit No'), ('5', 'Malaysian I/C (for non-resident director and seaman only)'),
                                                   ('6', 'Passport No. (for non-resident director and seaman only)')], string='2. ID Type of Employee'),
            'address_type': fields.selection([('L', 'Local residential address'),
                                              ('F', 'Foreign address'),
                                              ('C', 'Local C/O address'),
                                              ('N', 'Not Available')], string='Address Type'),
            'empcountry_id': fields.many2one('employee.country', '6(k). Country Code of address'),
            'empnationality_id': fields.many2one('employee.nationality', '7. Nationality Code'),
            'cessation_provisions': fields.selection([('Y', 'Cessation Provisions applicable'),
                                                      ('N', 'Cessation Provisions not applicable')], string='28. Cessation Provisions'),
    }

hr_employee()

class employee_country(osv.osv):
    _name = 'employee.country'
    _columns = {
            'name': fields.char('Country', size=32, required=True),
            'code': fields.integer('Code', size=3, required=True)
    }
employee_country()

class employee_nationality(osv.osv):
    _name = 'employee.nationality'
    _columns = {
            'name': fields.char('Nationality', size=32, required=True),
            'code': fields.integer('Code', size=3, required=True)
    }
employee_nationality()

class salary_report_for_exchequer_glcode(osv.osv):

    _name = 'salary.report.for.exchequer.glcode'

    _columns = {
            'name': fields.char('GL Code', size=32, required=True),
    }

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'The GL Code Name must be unique !'),
    ]

salary_report_for_exchequer_glcode()

class hr_payslip_run(osv.osv):

    _inherit = 'hr.payslip.run'
    _description = 'Payslip Batches'
    def open_payslip_employee(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return True
        payslip_batch_data = self.browse(cr, uid, ids[0], context)
        context.update({'default_date_start': payslip_batch_data.date_start, 'default_date_end': payslip_batch_data.date_end})
        return {'name': ('Payslips by Employees'),
                'context': context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.payslip.employees',
                'type': 'ir.actions.act_window',
                'target': 'new',
        }

hr_payslip_run()

class hr_payslip_employees(osv.osv_memory):
    
    _inherit = 'hr.payslip.employees'

    _columns = {
        'date_start': fields.date('Date From'),
        'date_end': fields.date('Date To'),
    }

hr_payslip_employees()

#class many2many_mod2(fields.many2many):
#    def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
#        if context is None:
#            context = {}
##        context.update({'active_test': False})
#        return super(many2many_mod2, self).get(cr, obj, ids, name, user, offset, context=context)

class res_users(osv.osv):
    
    _inherit = 'res.users'
    
    _columns = {
        'user_ids': fields.many2many('res.users', 'ppd_res_user_payroll_rel','usr_id','user_id','User Name'),
    }
res_users()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


