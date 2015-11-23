#-*- coding:utf-8 -*-
from osv import osv, fields
import base64
import tempfile
from xlrd import open_workbook
from tools.translate import _
import tools
from datetime import datetime


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
            # dt_value needs to be a datetime.datetime object (so no time.struct_time or mx.DateTime.DateTime here!)
            dt_value = datetime.strptime(src_tstamp_str,src_format)
            if context.get('tz',False):
                try:
                    import pytz
                    src_tz = pytz.timezone('UTC')
                    dst_tz = pytz.timezone(context['tz'])
                    src_dt = src_tz.localize(dt_value, is_dst=True)
                    dt_value = src_dt.astimezone(dst_tz)
                except Exception,e:
                    pass
            res = dt_value.strftime(dst_format)
        except Exception,e:
            # Normal ways to end up here are if strptime or strftime failed
            if not ignore_unparsable_time:
                return False
            pass
    return res

class upload_xls_wiz(osv.osv_memory):

    _name  = "upload.xls.wiz"

    _description = 'Upload xls file for allowances or deductions input fields.'

    _columns = {
        'in_file':fields.binary('Input File', required=True, filters='*.xls'),
        'period_id': fields.many2one('account.period','Period', required=True),
        'clear_all_prev_value': fields.boolean('OVERRITE ALL VALUES'),
    }

    _defaults = {
        'clear_all_prev_value': True,
    }

    def upload_file(self, cr, uid, ids, context=None):
        """
            This method will upload the xsl file   
                @param cr: the current row, from the database cursor,
                @param uid: the current user’s ID for security checks,
                @param ids: ID or list of IDs
                @param context:global dictionary
        """
        temp_path = tempfile.gettempdir()
        user_object = self.pool.get('res.users')
        payslip_object = self.pool.get('hr.payslip')
        employee_object = self.pool.get('hr.employee')
        payslip_input_object = self.pool.get('hr.payslip.input')
        hr_rule_input_obj = self.pool.get('hr.rule.input')
        contract_obj = self.pool.get('hr.contract')
        wiz_rec = self.browse(cr, uid, ids[0], context=context)
        csv_data = base64.decodestring(wiz_rec.in_file)
        fp=open(temp_path+'/xsl_file.xls', 'wb+')
        fp.write(csv_data)
        fp.close()
        wb = open_workbook(temp_path+'/xsl_file.xls')
        
        hr_rule_input_id = hr_rule_input_obj.search(cr, uid, [])
        hr_rule_input_list = []
        for input in hr_rule_input_obj.browse(cr, uid, hr_rule_input_id):
            hr_rule_input_list.append(input.code)
        
        xls_dict = {}
        xls_new_dict = {}
        for sheet in wb.sheets():
            for rownum in range(sheet.nrows):
                if rownum == 0:
                    i=1
                    first_headers = []
                    header_list = sheet.row_values(rownum)
                    new_header_list = sheet.row_values(rownum)
                    for header in new_header_list:
                        if header not in hr_rule_input_list and header not in ['name', 'NAME', 'REMARKS', 'EMPLOYEELOGIN']:
                            raise osv.except_osv(_('Error'), _('Check Salary input code. %s Salary Input code not exists.' % header))
                    for header in header_list:
                        xls_dict.update({i: tools.ustr(header)})
                        i=i+1
                        if header in first_headers:
                            raise osv.except_osv(_('Error'), _('Duplicate salary input code %s found.' % header))
                        elif header not in ['name', 'NAME']:
                            first_headers.append(header)
                    remark_index = header_list.index('REMARKS')
                
                else:
                    i=1
                    headers = sheet.row_values(rownum)
                    for record in headers:
                        xls_new_dict.update({i: tools.ustr(record)})
                        i = i+1
                    emp_login = ''
                    if type(sheet.row_values(rownum)[header_list.index('EMPLOYEELOGIN')]) == type(0.0):
                        emp_login = tools.ustr(int(sheet.row_values(rownum)[header_list.index('EMPLOYEELOGIN')]))
                    else:
                        emp_login = tools.ustr(sheet.row_values(rownum)[header_list.index('EMPLOYEELOGIN')])
                    user_ids = user_object.search(cr, uid,[('login', '=', emp_login)])
                    if not user_ids:
                        user_ids = user_object.search(cr, uid,[('login', '=', emp_login), ('active', '=', False)])
                        if user_ids:
                            raise osv.except_osv(_('Error'), _('Employee login %s is inactive for row number %s. ' % (emp_login, rownum+1) ))
                        raise osv.except_osv(_('Error'), _('Employee login %s not found for row number %s. ' % (emp_login, rownum+1) ))
                    emp_ids = employee_object.search(cr, uid, [('user_id', 'in', user_ids)])
                    if not emp_ids:
                        emp_ids = employee_object.search(cr, uid, [('user_id', 'in', user_ids), ('active', '=', False)])
                        if emp_ids:
                            raise osv.except_osv(_('Error'), _('Employee is inactive for login %s for row number %s.' % (emp_login, rownum+1) ))
                        raise osv.except_osv(_('Error'), _('No employee found for %s login name for row number %s.' % (emp_login, rownum+1) ))
                    if emp_ids:
                        contract_ids = contract_obj.search(cr, uid, [('employee_id', '=', emp_ids[0]), ('date_start','<=', wiz_rec.period_id.date_stop), '|', ('date_end', '>=', wiz_rec.period_id.date_stop),('date_end','=',False)])
                        if not contract_ids:
                            raise osv.except_osv(_('Error'), _('Contract not found for Employee login %s in row number %s.' % (emp_login, rownum+1) ))
                        pay_slip_ids = payslip_object.search(cr, uid,[('state','=','draft'),('employee_id', '=', emp_ids[0]), ('date_from', '>=', wiz_rec.period_id.date_start), ('date_to', '<=', wiz_rec.period_id.date_stop)])
                        if not pay_slip_ids:
                            raise osv.except_osv(_('Error'), _('Payslip not found for Employee login %s in row number %s.' % (emp_login, rownum+1) ))
                        for pay_slip in payslip_object.browse(cr, uid, pay_slip_ids):
                            if not pay_slip.contract_id:
                                raise osv.except_osv(_('Error'), _('Employee contract not found or not assign in payslip for %s for row number %s.' % (pay_slip.employee_id.name, rownum+1) ))
                            note = pay_slip.note or ''
                            user_data = self.pool.get('res.users').browse(cr, uid, uid, context)
                            context.update({'tz': user_data.context_tz})
                            user_current_date =  _offset_format_timestamp(datetime.today(), '%Y-%m-%d %H:%M:%S', '%d-%B-%Y %H:%M:%S', context=context)
                            note += '\nUploaded by ' + tools.ustr(user_data.name or '') + ' on ' + tools.ustr(user_current_date.strftime('%d-%b-%Y %H:%M:%S')) + ' \n ------------------------------------------------------ \n'
                            for xls in xls_dict:
                                for input_data in pay_slip.input_line_ids:
                                    xls_dict[xls]
                                    if input_data.code == xls_dict[xls]:
                                        salary_amt = 0.00
                                        salary_amt = xls_new_dict.get(xls).strip()
                                        if salary_amt:
                                            salary_amt = float(salary_amt)
                                        else :
                                            salary_amt = 0.00
                                        if wiz_rec.clear_all_prev_value:
                                            input_line_amount = salary_amt or 0.00
                                        else:
                                            input_line_amount = salary_amt + input_data.amount or 0.0
                                        payslip_input_object.write(cr, uid, input_data.id,{'amount': input_line_amount})
                                        note += tools.ustr(xls_dict[xls]) + " "*5 + tools.ustr(salary_amt) + " "*5 + sheet.row_values(rownum)[remark_index] + '\n'
                            if note:
                                payslip_object.write(cr, uid, pay_slip.id, {'note':note})
                                payslip_object.compute_sheet(cr, uid, [pay_slip.id], context=context)

        return {'type' : 'ir.actions.act_window_close'}

upload_xls_wiz()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: