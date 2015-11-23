# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
import datetime

class binary_ir8a_text_file_wizard(osv.osv):
    _name = 'binary.ir8a.text.file.wizard'
    _columns = {
        'ir8a_txt_file': fields.binary("Click On Save As Button To Download File"),
        'name': fields.char("Name", size=255),
    }


binary_ir8a_text_file_wizard()

class binary_ir8s_text_file_wizard(osv.osv):
    _name = 'binary.ir8s.text.file.wizard'
    _columns = {
        'ir8s_txt_file': fields.binary("Click On Save As Button To Download File"),
        'name': fields.char("Name", size=255),
    }


binary_ir8s_text_file_wizard()


class emp_ir8a_text_file(osv.osv):
    _name = 'emp.ir8a.text.file'

    def _get_payroll_user(self, cr, uid, context={}):
        user_id = self.pool.get('res.users').search(cr, uid, [])
        res = []
        for user in self.pool.get('res.users').browse(cr, uid, user_id):
            res.append((user.id, user.name))
        return res

    _columns = {
        'batch_date': fields.date("Batch Date"),
        'batch_indicatior': fields.selection([("O", "Original"), ("A", "Amendment")], "Batch Indicator"),
        'employee_ids': fields.many2many('hr.employee', 'hr_employe_ir8a_text_rel', 'text_file_id', 'employee_id',
                                         'Employees', required=True),
        'organization_id_no': fields.char("Organization ID No", size=255),
        'organization_id_type': fields.selection([("7", "UEN - Business Registration number issued by ACRA"),
                                                  ("8", "UEN - Local Company Registration number issued by ACRA"),
                                                  ("A", "ASGD - Tax Reference number assigned by IRAS"),
                                                  ("I", "ITR - Income Tax Reference number assigned by IRAS"),
                                                  ("U", "UENO - Unique Entity Number Others")], "Organization ID Type"),
        'payroll_user': fields.selection(_get_payroll_user, "Name of authorised person"),
        'print_type': fields.selection([("text", "Text"), ("pdf", "PDF")], "Print as"),
        'source': fields.selection(
            [("1", "Mindef"), ("2", "Government Department"), ("5", "Statutory Board"), ("6", "Private Sector"),
             ("9", "Others")], "Source"),
        'year_id': fields.many2one("account.fiscalyear", "Year Of Assessment"),
    }


emp_ir8a_text_file()


class emp_ir8s_text_file(osv.osv):
    _name = 'emp.ir8s.text.file'

    def _get_payroll_user(self, cr, uid, context={}):
        user_id = self.pool.get('res.users').search(cr, uid, [])
        res = []
        for user in self.pool.get('res.users').browse(cr, uid, user_id):
            res.append((user.id, user.name))
        return res

    _columns = {
        'batch_date': fields.date("Batch Date"),
        'batch_indicatior': fields.selection([("O", "Original"), ("A", "Amendment")], "Batch Indicator"),
        'employee_ids': fields.many2many('hr.employee', 'hr_employe_ir8s_text_rel', 'text_file_id', 'employee_id',
                                         'Employees', required=True),
        'organization_id_no': fields.char("Organization ID No", size=255),
        'organization_id_type': fields.selection([("7", "UEN - Business Registration number issued by ACRA"),
                                                  ("8", "UEN - Local Company Registration number issued by ACRA"),
                                                  ("A", "ASGD - Tax Reference number assigned by IRAS"),
                                                  ("I", "ITR - Income Tax Reference number assigned by IRAS"),
                                                  ("U", "UENO - Unique Entity Number Others")], "Organization ID Type"),
        'payroll_user': fields.selection(_get_payroll_user, "Name of authorised person"),
        'print_type': fields.selection([("text", "Text"), ("pdf", "PDF")], "Print as"),
        'source': fields.selection(
            [("1", "Mindef"), ("2", "Government Department"), ("5", "Statutory Board"), ("6", "Private Sector"),
             ("9", "Others")], "Source"),
        'year_id': fields.many2one("account.fiscalyear", "Accounting Year"),
    }


emp_ir8s_text_file()


class employee_city(osv.osv):
    _name = 'employee.city'
    _columns = {
        'code': fields.char("City Code", size=255),
        'name': fields.char("City Name", size=255),
        'state_id': fields.many2one("res.country.state", "State"),
    }


employee_city()


class employee_country(osv.osv):
    _name = 'employee.country'
    _columns = {
        'code': fields.integer("Code"),
        'name': fields.char("Country", size=255),
    }


employee_country()


class employee_document(osv.osv):
    _name = 'employee.document'
    _columns = {
        'document': fields.char("Documents", size=255),
        'document_attachment': fields.binary("Attachment Data"),
        'employee_doc_id': fields.many2one("hr.holidays", "Holiday"),
    }


employee_document()


class employee_history(osv.osv):
    _name = 'employee.history'
    _columns = {
        'cessation_date': fields.date("Cessation Date"),
        'confirm_date': fields.date("Date of Confirmation"),
        'date_changed': fields.datetime("Date Changed"),
        'emp_status': fields.selection(
            [("probation", "Probation"), ("active", "Active"), ("in_notice", "In notice Period"),
             ("terminated", "Terminated"), ("inactive", "Inactive")], "Employment Status"),
        'history_id': fields.many2one("hr.employee", "History"),
        'job_id': fields.many2one("hr.job", "Job title"),
        'join_date': fields.date("Joined Date"),
        'user_id': fields.many2one("res.users", "Changed By"),
    }


employee_history()


class employee_id_type(osv.osv):
    _name = 'employee.id.type'
    _columns = {
        'name': fields.char("EP", size=255),
        's_pass': fields.selection([("skilled", "Skilled"), ("unskilled", "Un Skilled")], "S Pass"),
        'wp': fields.selection([("skilled", "Skilled"), ("unskilled", "Un Skilled")], "Wp"),
    }


employee_id_type()


class employee_immigration(osv.osv):
    _name = 'employee.immigration'
    _columns = {
        'comments': fields.text("Comments"),
        'documents': fields.char("Documents", size=255),
        'eligible_review_date': fields.date("Eligible Review Date"),
        'eligible_status': fields.char("Eligible Status", size=255),
        'employee_id': fields.many2one("hr.employee", "Employee Name"),
        'exp_date': fields.date("Expiry Date"),
        'issue_by': fields.many2one("res.country", "Issue By"),
        'issue_date': fields.date("Issue Date"),
        'number': fields.char("Number", size=255),
    }


employee_immigration()


class employee_nationality(osv.osv):
    _name = 'employee.nationality'
    _columns = {
        'code': fields.integer("Code"),
        'name': fields.char("Nationality", size=255),
    }


employee_nationality()


class employee_news(osv.osv):
    _name = 'employee.news'
    _columns = {
        'date': fields.datetime("Date"),
        'department_ids': fields.many2many('hr.department', 'hr_employe_news_department_rel', 'employee_news_id',
                                           'department_id',
                                           'Departments'),
        'description': fields.text("Description"),
        'subject': fields.char("Subject", size=255),
        'user_ids': fields.many2many('res.users', 'hr_employee_news_rel', 'employee_news_id', 'user_id',
                                     'Users'),
    }


employee_news()


class employee_training(osv.osv):
    _name = 'employee.training'
    _columns = {
        'comments': fields.text("Comments"),
        'training_attachment': fields.binary("Attachment Data"),
        'tr_date': fields.date("Date"),
        'tr_id': fields.many2one("hr.employee", "Employee"),
        'tr_institution': fields.char("Institution", size=255),
        'tr_title': fields.char("Title of TRAINING/WORKSHOP", size=255),
    }


employee_training()


class hr_bank_details(osv.osv):
    _name = 'hr.bank.details'
    _columns = {
        'bank_ac_no': fields.char("Bank Account Number", size=255),
        'bank_code': fields.char("Bank Code", size=255),
        'bank_emp_id': fields.many2one("hr.employee", "Bank Detail"),
        'bank_name': fields.char("Name Of Bank", size=255),
        'beneficiary_name': fields.char("Beneficiary Name", size=255),
        'branch_code': fields.char("Branch Code", size=255),
    }


hr_bank_details()


class hr_contract(osv.osv):
    _inherit = 'hr.contract'
    _columns = {
        'active_employee': fields.boolean("Active Employee"),
        'hr_contract_income_tax_ids': fields.one2many("hr.contract.income.tax", "contract_id", string="Income Tax"),
        'rate_per_hour': fields.float("Rate per hour for part timer"),
        'wage_to_pay': fields.float("Wage To Pay"),
    }


hr_contract()


class hr_contract_income_tax(osv.osv):
    _name = 'hr.contract.income.tax'
    _columns = {
        'additional_wage': fields.float("99. Additional wages"),
        'add_wage_pay_date': fields.date("101. Date of payment for additional wages"),
        'approval_date': fields.date("27(b). Date of approval"),
        'approval_has_been_obtained_CPF_board': fields.selection(
            [("Y", " Approval has been obtained from CPF Board to make full contribution"),
             ("N", " Approval has NOT been obtained from CPF Board to make full contribution")],
            "87. Approval has been obtained from CPF Board to make full contribution"),
        'approve_obtain_iras': fields.selection(
            [("Y", "Approval obtained from IRAS"), ("N", "No approval obtained from IRAS ")],
            "27(a). Approval obtained from IRAS"),
        'benefits_kind': fields.selection([("Y", "Benefits-in-kind rec'd"), ("N", "Benefits-in-kind not rec'd")],
                                          "23. Benefits-in-kind"),
        'benifits_in_kinds': fields.float("44. Value of benefits-in- kinds"),
        'bonus_amount': fields.float("Bonus"),
        'bonus_declaration_date': fields.date("49. Date of declaration of bonus"),
        'cessation_date': fields.date("Cessation Date"),
        'compensation': fields.selection([("Y", " Compensation / Retrenchment benefits paid"),
                                          ("N", "No Compensation / Retrenchment benefits paid")],
                                         "27. Compensation for loss of office"),
        'compensation_loss_office': fields.float("38(a). Compensation for loss of office"),
        'contract_id': fields.many2one("hr.contract", "Contract"),
        'contribution_employer': fields.float(
            "41. Contributions made by employer to any pension / provident fund constituted outside Singapore"),
        'CPF_capping_indicator': fields.selection(
            [("Y", "Capping has been applied"), ("N", "Capping has been not applied")], "85. CPF capping indicator"),
        'CPF_designated_pension_provident_fund': fields.float("14. CPF/Designated Pension or Provident Fund"),
        'deginated_pension': fields.char(
            "52. Name of Designated Pension or Provident Fund for which e'yee made compulsory contribution", size=255),
        'director_fee': fields.float("18. Directors fee"),
        'director_fee_approval_date': fields.date("50. Date of approval of directors fees"),
        'donation': fields.float("13. Donation"),
        'employee_income_tax': fields.selection([("F", "Tax fully borne by employer on employment income only"), (
        "P", "Tax partially borne by employer on certain employment income items"), ("H",
                                                                                     "A fixed amount of income tax liability borne by employee. Not applicable if income tax is fully paid by employee"),
                                                 ("N", "Not Applicable")],
                                                "25. Employees Income Tax borne by employer"),
        'employment_income': fields.float("21. Amount of employment income for which tax is borne by employer"),
        'emp_voluntary_contribution_cpf': fields.float(
            "45. E'yees voluntary contribution to CPF obligatory by contract of employment (overseas posting)"),
        'entertainment_allowance': fields.float("36. Entertainment Allowance"),
        'excess_voluntary_contribution_cpf_employer': fields.float(
            "42. Excess / voluntary contribution to CPF by employer"),
        'exempt_income': fields.float("20. Exempt Income/ Income subject to Tax Remission"),
        'exempt_remission': fields.selection([("1", "Tax Remission on Overseas Cost of Living Allowance (OCLA)"),
                                              ("2", " Tax remission on Operation Headquarters (OHQ)"), ("3", "Seaman"),
                                              ("4", "Exemption"), ("N", "Not Applicable")],
                                             "30. Exempt/ Remission income Indicator"),
        'eyee_contibution': fields.float("89. Eyees Contribution"),
        'eyer_contibution': fields.float("88. Eyers Contribution"),
        'fromdate': fields.date("32(a). From Date"),
        'from_ir8s': fields.selection([("Y", "IR8S is applicable"), ("N", "IR8S is not applicable")], "29. Form IR8S"),
        'fund_name': fields.char("51. Name of fund for Retirement benefits", size=255),
        'gain_profit': fields.float("19(a). Gains & Profit from Share Options For S10 (1) (g)"),
        'gains_profit_share_option': fields.float("43. Gains and profits from share options for S10 (1) (b)"),
        'gratuity_payment': fields.selection([("", ""), ("", ""), ("", ""), ("", "")],
                                             "26. Gratuity/ Notice Pay/ Ex-gratia payment/ Others"),
        'gratuity_payment_amt': fields.float("38. Gratuity/ Notice Pay/ Ex-gratia payment/ Others"),
        'gross_commission': fields.float("31. Gross Commission"),
        'gross_commission_indicator': fields.selection([("M", " Monthly"), ("O", "Other than monthly"), ("B", "Both")],
                                                       "33. Gross Commission Indicator"),
        'indicator_for_CPF_contributions': fields.selection([("Y", "Obligatory"), ("N", "Not obligatory")],
                                                            "84. Indicator for CPF contributions in respect of overseas posting which is obligatory by contract of employment"),
        'insurance': fields.float("Insurance"),
        'mbf': fields.float("12. MBF"),
        'other_allowance': fields.float("37. Other Allowance"),
        'payslip_net_amount': fields.float("Gross Salary, Fees, Leave Pay, Wages and Overtime Pay"),
        'pension': fields.float("34. Pension"),
        'refund_eyees_contribution': fields.float("105. Amount of refund applicable to Eyees contribution"),
        'refund_eyees_date': fields.date("107. Date of refund given to employee"),
        'refund_eyees_interest_contribution': fields.float(
            "106. Amount of refund applicable to Eyees Interest on contribution"),
        'refund_eyers_contribution': fields.float("102. Amount of refund applicable to Eyers contribution"),
        'refund_eyers_date': fields.date("104. Date of refund given to employer"),
        'refund_eyers_interest_contribution': fields.float(
            "103. Amount of refund applicable to Eyers Interest on contribution"),
        'retirement_benifit_from': fields.float("40. Retirement benefits accrued from 1993"),
        'retirement_benifit_up': fields.float("39. Retirement benefits accrued up to 31.12.92"),
        'section_applicable': fields.selection([("Y", "S45 applicable"), ("N", "S45 not applicable")],
                                               "24. Section 45 applicable"),
        'singapore_permanent_resident_status': fields.selection(
            [("Y", "Singapore Permanent Resident Status is approved"),
             ("N", "Singapore Permanent Resident Status is not approved")],
            "86. Singapore Permanent Resident Status is approved"),
        'todate': fields.date("32(b). To Date"),
        'transport_allowance': fields.float("35. Transport Allowance"),
        'year_id': fields.many2one("account.fiscalyear", "Year Of Assessment"),
    }


hr_contract_income_tax()


class hr_contribution_register(osv.osv):
    _inherit = 'hr.contribution.register'
    _columns = {
        'register_glcode_ids': fields.one2many("hr.salary.rule.glcode", "register_id", string="Contribution GL Code"),
    }


hr_contribution_register()


class hr_employee(osv.osv):
    _inherit = 'hr.employee'

    def onchange_health_yes(self,cr,uid,ids,active,context=None):
        res = {}
        if active:
            res['physical_stability_no'] = False
        return {'value':res}
    def onchange_health_no(self,cr,uid,ids,active,context=None):
        res = {}
        if active:
            res['physical_stability'] = False
        return {'value':res}
    def onchange_court_yes(self,cr,uid,ids,active,context=None):
        res = {}
        if active:
            res['court_no'] = False
        return {'value':res}
    def onchange_court_no(self,cr,uid,ids,active,context=None):
        res = {}
        if active:
            res['court_b'] = False
        return {'value':res}
    def onchange_dismissed_yes(self,cr,uid,ids,active,context=None):
        res = {}
        if active:
            res['dismissed_no'] = False
        return {'value':res}
    def onchange_dismissed_no(self,cr,uid,ids,active,context=None):
        res = {}
        if active:
            res['dismissed_b'] = False
        return {'value':res}
    def onchange_bankrupt_yes(self,cr,uid,ids,active,context=None):
        res = {}
        if active:
            res['bankrupt_no'] = False
        return {'value':res}
    def onchange_bankrupt_no(self,cr,uid,ids,active,context=None):
        res = {}
        if active:
            res['bankrupt_b'] = False
        return {'value':res}
    def onchange_emp_active(self,cr,uid,ids,active,context=None):
        res = {}
        print 'active',active
        res['emp_status'] = 'inactive'
        if active:
            res['emp_status'] = 'active'
        return {'value':res}
    def onchange_employee_status(self,cr,uid,ids,active,context=None):
        res = {}
        res['active'] = True
        print 'status',active
        if active == 'inactive':
            res['active'] = False
        return {'value':res}
    _columns = {
        'address_type': fields.selection(
            [("L", "Local residential address"), ("F", "Foreign address"), ("C", "Local C/O address"),
             ("N", "Not Available")], "Address Type"),
        'cessation_date': fields.date("Cessation Date"),
        'cessation_provisions': fields.selection(
            [("normal", "Normal"), ("credit", "Credit Centralisation"), ("debit", "Debit Centralisation"),
             ("currency", "Currency Adjustment")], "28. Cessation Provisions"),
        'empcountry_id': fields.many2one("employee.country", "6(k). Country Code of address"),
        'empnationality_id': fields.many2one("employee.nationality", "7. Nationality Code"),
        'identification_no': fields.selection(
            [("1", "NRIC"), ("2", "FIN"), ("3", "Immigration File Ref No."), ("4", "Work Permit No"),
             ("5", "Malaysian I/C (for non-resident director and seaman only)"),
             ("6", "Passport No. (for non-resident director and seaman only)")], "2. ID Type of Employee"),
        'about': fields.text("About Yourself"),
        'age': fields.integer("Age"),
        'bank_detail_ids': fields.one2many("hr.bank.details", "bank_emp_id", string="Bank Details"),
        'bankrupt': fields.char("Bankrupt Information", size=255),
        'bankrupt_b': fields.boolean("Bankrupt (Yes)"),
        'bankrupt_no': fields.boolean("Bankrupt (No)"),
        'birthday_day': fields.char("unknown", size=255),
        'birthday_month': fields.char("unknown", size=255),
        'car': fields.boolean("Do you own a car?"),
        'comp_prog_knw': fields.char("Computer Programs Knowledge", size=255),
        'confirm_date': fields.date("Date Confirmation"),
        'contact_num2': fields.char("Contact:Mobile", size=255),
        'course': fields.char("Courses Taken", size=255),
        'court': fields.char("Court Information", size=255),
        'court_b': fields.boolean("Court (Yes)"),
        'court_no': fields.boolean("Court (No)"),
        'dialect': fields.char("Dialect", size=255),
        'dismiss': fields.char("Dismissed Information", size=255),
        'dismissed_b': fields.boolean("Dismissed (Yes)"),
        'dismissed_no': fields.boolean("Dismissed (No)"),
        'driving_licence': fields.char("Driving Licence:Class", size=255),
        'edu_ids': fields.one2many("applicant.edu", "employee_id", string="Education"),
        'emp_city_id': fields.many2one("employee.city", "City"),
        'emp_country_id': fields.many2one("res.country", "Country"),
        'employee_leave_ids': fields.one2many("hr.holidays", "employee_id", string="Leaves"),
        'employee_type_id': fields.many2one("employee.id.type", "Type Of ID"),
        'employment_history_ids': fields.one2many("applicant.history", "employee_id", string="Employement History"),
        'emp_state_id': fields.many2one("res.country.state", "State"),
        'emp_status': fields.selection(
            [("probation", "Probation"), ("active", "Active"), ("in_notice", "In notice Period"),
             ("terminated", "Terminated"), ("inactive", "Inactive")], "Employment Status"),
        'history_ids': fields.one2many("employee.history", "history_id", string="Job History"),
        'hr_manager': fields.boolean("Hr Manager"),
        'immigration_ids': fields.one2many("employee.immigration", "employee_id", string="Immigration"),
        'inact_date': fields.datetime("Inactive Date"),
        'is_all_final_leave': fields.boolean(
            "Receiving email notifications of 2nd Reminder to Direct / Indirect Managers?"),
        'is_daily_notificaiton_email_send': fields.boolean(
            "Receiving email notifications of employees who are on leave?"),
        'is_pending_leave_notificaiton': fields.boolean(
            "Receiving email notifications of Pending Leaves Notification Email?"),
        'issue_date': fields.date("Passport Issue Date"),
        'join_date': fields.date("Date Joined"),
        'language_ids': fields.one2many("applicant.language", "employee_id", string="Language Proficiency"),
        'last_date': fields.date("Last Date"),
        'national_service_ids': fields.one2many("national.service", "employee_id", string="National Service"),
        'other_know': fields.char("Other Knowledge & Skills", size=255),
        'parent_id2': fields.many2one("hr.employee", "Indirect Manager"),
        'parent_user_id': fields.many2one("res.users", "Direct Manager User"),
        'parent_user_id2': fields.many2one("res.users", "Indirect Manger User"),
        'passport_exp_date': fields.date("Passport Expiry Date"),
        'physical': fields.text("Physical Stability Information"),
        'physical_stability': fields.boolean("Physical Stability (Yes)"),
        'physical_stability_no': fields.boolean("Physical Disability (No)"),
        'reason': fields.text("Reason"),
        'reference_ids': fields.one2many("applicant.ref", "employee_id", string="References"),
        'relative_ids': fields.one2many("applicant.relative", "employee_id",
                                        string="Parents,Brothers & Sisters (Dependent)"),
        'rem_days': fields.integer("Remaining Days"),
        'resume': fields.binary("Resume"),
        'shorthand': fields.integer("Shorthand"),
        'training_ids': fields.one2many("employee.training", "tr_id", string="Training"),
        'typing': fields.integer("Typing"),
    }


hr_employee()


class hr_holiday_lines(osv.osv):
    _name = 'hr.holiday.lines'
    _columns = {
        'day': fields.char("Day", size=255),
        'holiday_date': fields.date("Date"),
        'holiday_id': fields.many2one("hr.holiday.public", "Holiday List"),
        'name': fields.char("Reason", size=255),
    }
    def onchange_holiday_date(self,cr,uid,ids,date,context=None):
        weekday = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        res = {}
        if date:
            date = datetime.datetime.strptime(date,'%Y-%m-%d')
            res['day'] = weekday[date.weekday()]
        return {'value':res}
hr_holiday_lines()


class hr_holiday_public(osv.osv):
    _name = 'hr.holiday.public'
    _columns = {
        'email_body': fields.text("Email Body"),
        'holiday_line_ids': fields.one2many("hr.holiday.lines", "holiday_id", string="Holidays"),
        'name': fields.char("Holiday", size=255),
        'state': fields.selection(
            [("draft", "Draft"), ("confirmed", "Confirmed"), ("validated", "Validated"), ("refused", "Refused"),
             ("cancelled", "Cancelled")], "State"),
    }


hr_holiday_public()


class hr_holidays(osv.osv):
    _inherit = 'hr.holidays'
    _columns = {
        'carry_forward': fields.boolean("Carry Forward Leave"),
        'create_date': fields.datetime("Create Date"),
        'day': fields.char("Day", size=255),
        'employee_document_ids': fields.one2many("employee.document", "employee_doc_id", string="Documents"),
        'fiscal_year_id': fields.many2one("account.fiscalyear", "Fiscal Year"),
        'leave_type': fields.selection([("am", "AM"), ("pm", "PM"), ("full", "FULL")], "Duration"),
        'rejection': fields.text("Reason"),
        'unallocated': fields.boolean("Unallocation"),
        'write_date': fields.datetime("Write Date"),
    }


hr_holidays()


class hr_holidays_status(osv.osv):
    _inherit = 'hr.holidays.status'
    _columns = {
        'cry_frd_leave': fields.float("Carry Forward Leave"),
        'default_leave_allocation': fields.integer("Default Annual Leave Allocation"),
        'name2': fields.char("Leave Type", size=255),
        'weekend_calculation': fields.boolean("Weekend Calculation"),
    }


hr_holidays_status()


class hr_payslip(osv.osv):
    _inherit = 'hr.payslip'
    _columns = {
        'active': fields.boolean("Pay"),
        'active_employee': fields.boolean("Active Employee"),
        'cheque_number': fields.char("Cheque Number", size=255),
        'employee_name': fields.char("Employee Name", size=255),
        'pay_by_cheque': fields.boolean("Pay By Cheque"),
    }


hr_payslip()


class hr_payslip_employees(osv.osv):
    _inherit = 'hr.payslip.employees'
    _columns = {
        'date_end': fields.date("Date To"),
        'date_start': fields.date("Date From"),
    }


hr_payslip_employees()


class hr_salary_rule(osv.osv):
    _inherit = 'hr.salary.rule'
    _columns = {
        'hr_salary_rule_glcode_ids': fields.one2many("hr.salary.rule.glcode", "salaryrule_id",
                                                     string="Salary Rule GL Code"),
        'id': fields.integer("ID"),
    }


hr_salary_rule()


class hr_salary_rule_glcode(osv.osv):
    _name = 'hr.salary.rule.glcode'
    _columns = {
        'apply_bank_cheque': fields.selection(
            [("apply_for_bank", "Apply for Bank"), ("apply_for_cheque", "Apply For Cheque")], "Apply for Bank/Cheque"),
        'emp_categ_id': fields.many2one("hr.employee.category", "Employee Category"),
        'gl_code_id': fields.many2one("salary.report.for.exchequer.glcode", "GL Code"),
        'nagative': fields.boolean("Negative"),
        'register_id': fields.many2one("hr.contribution.register", "GL Code"),
        'salaryrule_id': fields.many2one("hr.salary.rule", "GL Code"),
        'saved_back_cpf': fields.boolean("Saved Back CPF"),
        'saved_back_salary': fields.boolean("Saved Back Salary"),
    }


hr_salary_rule_glcode()


class inactive_status(osv.osv):
    _name = 'inactive.status'
    _columns = {
        'inact_date': fields.datetime("Inactive Date"),
        'reason': fields.text("Reason"),
    }


inactive_status()


class refuse_leave(osv.osv):
    _name = 'refuse.leave'
    _columns = {
        'reason': fields.text("Reason"),
    }


refuse_leave()


class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
        'department_id': fields.many2one("hr.department", "Department"),
    }


res_company()


class res_partner_bank(osv.osv):
    _inherit = 'res.partner.bank'
    _columns = {
        'branch_id': fields.char("Branch ID", size=255),
    }


res_partner_bank()


class res_users(osv.osv):
    _inherit = 'res.users'
    _columns = {
        'user_ids': fields.many2many('res.users', 'hr_user_user_rel', 'hr_user_id', 'user_id',
                                     'Users'),
    }


res_users()


class roster_timesheet(osv.osv):
    _name = 'roster.timesheet'
    _columns = {
        'counter_id': fields.many2one("sale.shop", "Counter"),
        'current_date': fields.date("Date"),
        'employee_id': fields.many2one("hr.employee", "Employee"),
        'state': fields.selection([("open", "Waiting For Approval"), ("draft", "Draft"), ("done", "Done")], "State"),
        'time_from': fields.datetime("Time From"),
        'time_to': fields.datetime("Time To"),
    }


roster_timesheet()


class salary_report_for_exchequer_glcode(osv.osv):
    _name = 'salary.report.for.exchequer.glcode'
    _columns = {
        'name': fields.char("GL Code", size=255), }


salary_report_for_exchequer_glcode()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

