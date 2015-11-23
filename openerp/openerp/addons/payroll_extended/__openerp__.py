# -*- coding: utf-8 -*-
{
    "name": "payroll_extended",
    "version": "1.433",
    "depends": [
        "base", "hr_payroll", "account"
    ],
    "author" :"Son Pham & Di Ho",
    "website" : "",
    "category": "HRMS Report",
    "description": """
        This module provide :
        For Generating Report For HRMS
    """,
    'data': [
       'security/group.xml',
#       'security/ir.model.access.csv',
       'security/hr.employee.category.csv',
       'security/hr.salary.rule.category.csv',
       'security/hr.contribution.register.csv',
       'security/salary.report.for.exchequer.glcode.csv',
       'salary_rule.xml',
#       'security/hr.salary.rule.csv',
       'security/hr.rule.input.csv',
       'security/hr.salary.rule.glcode.csv',
       'payroll_extended_view.xml',
#       'wizard/upload_xls_wizard_view.xml',
#        'wizard/payroll_summary_wizard_view.xml',
#       'wizard/cpf_payment_wizard_view.xml',
       'payment_report_view.xml',
#       'wizard/bank_summary_wirard_view.xml',
#       'wizard/payslip_sample_wiz_view.xml',
#       'wizard/ocbc_bank_specification_view.xml',
       'payroll_sequence.xml',
#        'payroll_schedule_data.xml',
#       'wizard/pr_wh_payroll_summary_view.xml',
#       'wizard/payroll_exchequer_report_view.xml',
       'wizard/emp_ir8a_text_file_view.xml',
       'wizard/emp_ir8s_text_file_view.xml',
#       "wizard/export_employee_summary_wiz_view.xml",
#       'wizard/comput_confirm_payslip_wiz_view.xml',
#       'wizard/cimb_bank_text_file_view.xml'
    ],
    'installable': True,
    'auto_install':False,
    'application':True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: