from openerp.report import report_sxw

from openerp.addons.account.report.account_financial_report import report_account_common

from netsvc import Service

del Service._services['report.account.financial.report']
report_sxw.report_sxw('report.account.financial.report', 'account.financial.report',
    'addons/project_costing_sinar/report/account_financial_report.rml', parser=report_account_common, header='internal')