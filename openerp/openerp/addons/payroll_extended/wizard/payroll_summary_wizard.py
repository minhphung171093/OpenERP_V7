from osv import osv, fields
from tools.translate import _
import tools

class payroll_summary_wizard(osv.osv):

    _name = 'payroll.summary.wizard'

    _columns = {
                'date_from': fields.date('Date From'),
                'date_to': fields.date('Date To'),
                'employee_ids': fields.many2many('hr.employee', 'ihrms_hr_employee_payroll_rel','emp_id3','employee_id','Employee Name'),
                'export_report' : fields.selection([('pdf','PDF')] , "Export"),
    }
    _defaults = {
        'export_report': "pdf"
    }

    def print_order(self, cr, uid, ids, context):
        data = self.read(cr, uid, ids)[0]
        if data.get("export_report") == "pdf":
            res_user = self.pool.get("res.users").browse(cr, uid,uid,context=context)
            data.update({'currency': " " + tools.ustr(res_user.company_id.currency_id.symbol), 'company': res_user.company_id.name})
            
            datas = {
                'ids': [],
                'form': data,
                'model':'hr.payslip',
            }
            return {'type': 'ir.actions.report.xml', 'report_name': 'payrollsummary_receipt', 'datas': datas}

payroll_summary_wizard()