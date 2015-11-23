from osv import fields, osv
import time
import netsvc
import datetime
from tools.translate import _
import tools
from datetime import date, timedelta
from dateutil import parser, rrule
import addons
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import logging
import base64
import netsvc
WEB_LINK_URL = "db=%s&uid=%s&pwd=%s&id=%s&state=%s&action_id=%s"


def _offset_format_timestamp1(src_tstamp_str, src_format, dst_format, ignore_unparsable_time=True, context=None):
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
            dt_value = datetime.datetime.strptime(src_tstamp_str,src_format)
            if context.get('tz',False):
                try:
                    import pytz
                    src_tz = pytz.timezone(context['tz'])
                    dst_tz = pytz.timezone('UTC')
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

class res_partner(osv.osv):
    _inherit ='res.partner'

    def default_get(self, cr, uid, fields, context=None):
        result = super(res_partner, self).default_get(cr, uid, fields, context=context)
        result['lang'] = False
        return result

res_partner()

class ir_cron(osv.osv):
    """ Model describing cron jobs (also called actions or tasks).
    """
    _inherit = "ir.cron"
#
    def change_scheduler_time(self, cr, uid, send_mail_notification_today=None, carry_forward_leave=None,
                              lapsed_leave=None, employee_reminder=None, emp_check_documents=None, emp_leave_direct_indirect=None, pending_leave=None, assign_def_cry_leave=None, assign_default_leave=None, hr_manager_reminder=None, context=None):
        if context is None:
            context = {}
        user_data = self.pool.get('res.users').browse(cr, uid, uid, context)
        context.update({'tz': user_data.context_tz})
        if send_mail_notification_today:
            cron_data = self.browse(cr, uid, send_mail_notification_today, context)
            str_dt_current =  _offset_format_timestamp1(cron_data.nextcall, '%Y-%m-%d %H:%M:%S', DEFAULT_SERVER_DATETIME_FORMAT, context=context)
            cr.execute("UPDATE ir_cron SET nextcall=%s WHERE id=%s", (str_dt_current, send_mail_notification_today))
        if carry_forward_leave:
            cron_data = self.browse(cr, uid, carry_forward_leave, context)
            str_dt_current =  _offset_format_timestamp1(cron_data.nextcall, '%Y-%m-%d %H:%M:%S', DEFAULT_SERVER_DATETIME_FORMAT, context=context)
            cr.execute("UPDATE ir_cron SET nextcall=%s WHERE id=%s", (str_dt_current, carry_forward_leave))
        if lapsed_leave:
            cron_data = self.browse(cr, uid, lapsed_leave, context)
            str_dt_current =  _offset_format_timestamp1(cron_data.nextcall, '%Y-%m-%d %H:%M:%S', DEFAULT_SERVER_DATETIME_FORMAT, context=context)
            cr.execute("UPDATE ir_cron SET nextcall=%s WHERE id=%s", (str_dt_current, lapsed_leave))
        if employee_reminder:
            cron_data = self.browse(cr, uid, employee_reminder, context)
            str_dt_current =  _offset_format_timestamp1(cron_data.nextcall, '%Y-%m-%d %H:%M:%S', DEFAULT_SERVER_DATETIME_FORMAT, context=context)
            cr.execute("UPDATE ir_cron SET nextcall=%s WHERE id=%s", (str_dt_current, employee_reminder))
        if emp_check_documents:
            cron_data = self.browse(cr, uid, emp_check_documents, context)
            str_dt_current =  _offset_format_timestamp1(cron_data.nextcall, '%Y-%m-%d %H:%M:%S', DEFAULT_SERVER_DATETIME_FORMAT, context=context)
            cr.execute("UPDATE ir_cron SET nextcall=%s WHERE id=%s", (str_dt_current, emp_check_documents))
        if emp_leave_direct_indirect:
            cron_data = self.browse(cr, uid, emp_leave_direct_indirect, context)
            str_dt_current =  _offset_format_timestamp1(cron_data.nextcall, '%Y-%m-%d %H:%M:%S', DEFAULT_SERVER_DATETIME_FORMAT, context=context)
            cr.execute("UPDATE ir_cron SET nextcall=%s WHERE id=%s", (str_dt_current, emp_leave_direct_indirect))
        if pending_leave:
            cron_data = self.browse(cr, uid, pending_leave, context)
            str_dt_current =  _offset_format_timestamp1(cron_data.nextcall, '%Y-%m-%d %H:%M:%S', DEFAULT_SERVER_DATETIME_FORMAT, context=context)
            cr.execute("UPDATE ir_cron SET nextcall=%s WHERE id=%s", (str_dt_current, pending_leave))
        if assign_def_cry_leave:
            cron_data = self.browse(cr, uid, assign_def_cry_leave, context)
            str_dt_current =  _offset_format_timestamp1(cron_data.nextcall, '%Y-%m-%d %H:%M:%S', DEFAULT_SERVER_DATETIME_FORMAT, context=context)
            cr.execute("UPDATE ir_cron SET nextcall=%s WHERE id=%s", (str_dt_current, assign_def_cry_leave))
        if assign_default_leave:
            cron_data = self.browse(cr, uid, assign_default_leave, context)
            str_dt_current =  _offset_format_timestamp1(cron_data.nextcall, '%Y-%m-%d %H:%M:%S', DEFAULT_SERVER_DATETIME_FORMAT, context=context)
            cr.execute("UPDATE ir_cron SET nextcall=%s WHERE id=%s", (str_dt_current, assign_default_leave))
        if hr_manager_reminder:
            cron_data = self.browse(cr, uid, hr_manager_reminder, context)
            str_dt_current =  _offset_format_timestamp1(cron_data.nextcall, '%Y-%m-%d %H:%M:%S', DEFAULT_SERVER_DATETIME_FORMAT, context=context)
            cr.execute("UPDATE ir_cron SET nextcall=%s WHERE id=%s", (str_dt_current, hr_manager_reminder))
        return True

ir_cron()

class ir_rule(osv.osv):
    _inherit = 'ir.rule'

    def domain_get(self, cr, uid, model_name, mode='read', context=None):
        if context is None:
            context = {}
        if context and type(context) == dict and context.get('holiday_donot_compute_domain'):
            return [], [], ['"'+self.pool.get(model_name)._table+'"']
        return super(ir_rule, self).domain_get(cr, uid, model_name, mode, context=context)

ir_rule()

class hr_holidays(osv.osv):

    _inherit = "hr.holidays"

    def _get_fiscalyear(self, cr, uid, context=None):
        """Return default Fiscalyear value"""
        today = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        return  self.fetch_fiscalyear(cr, uid, today, context=context)

    def _day_compute(self, cr, uid, ids, fieldnames, args, context=None):
        res = dict.fromkeys(ids, 'Allocation')
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.date_from:
                date_from = obj.date_from.split(' ')[0]
                res[obj.id] = time.strftime('%Y-%m-%d', time.strptime(date_from, '%Y-%m-%d'))
        return res

    def fetch_fiscalyear(self, cr, uid, date=False, context=None):
        if not date:
            date = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        fiscal_obj = self.pool.get('account.fiscalyear')
        args = [('date_start', '<=' ,date), ('date_stop', '>=', date)]
        fiscal_ids = fiscal_obj.search(cr, uid, args, context=context)
        if fiscal_ids:
            fiscal_ids = fiscal_ids[0]
        else:
            company_obj = self.pool.get('res.company')
            company_id = company_obj._company_default_get(cr, uid, 'account.fiscalyear',context=context)
            year = datetime.datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT).year
            end_date = str(year) + '-12-31'
            start_date = str(year) + '-01-01'
            fiscal_ids = fiscal_obj.create(cr, uid, {'date_start': start_date, 'date_stop' : end_date, 'code': str(year), 'name': str(year), 'company_id': company_id})
        return fiscal_ids

    _columns = {
        
        'leave_type' : fields.selection([('am', 'AM'), ('pm', 'PM'), ('full', 'FULL')], 'Duration'), 
        'notes': fields.text('Reasons', readonly=False, states={'validate':[('readonly', True)]}), 
        'state': fields.selection([('draft', 'New'), ('confirm', 'Waiting Pre-Approval'), ('refuse', 'Refused'), 
            ('validate1', 'Waiting Final Approval'), ('validate', 'Approved'), ('cancel', 'Cancelled')], 
            'State', readonly=True, help='The state is set to \'Draft\', when a holiday request is created.\
            \nThe state is \'Waiting Approval\', when holiday request is confirmed by user.\
            \nThe state is \'Refused\', when holiday request is refused by manager.\
            \nThe state is \'Approved\', when holiday request is approved by manager.'), 
        'employee_document_ids':fields.one2many('employee.document', 'employee_doc_id', 'Documents'), 
        'rejection' : fields.text('Reason'),
        'create_date': fields.datetime('Create Date', readonly=True),
        'write_date': fields.datetime('Write Date', readonly=True),
        'unallocated' : fields.boolean('Unallocation'),
        'day': fields.function(_day_compute, type='char', string='Day', store=True, size=32),
        'fiscal_year_id' : fields.many2one('account.fiscalyear', 'Fiscal Year', required=True),
        'carry_forward' : fields.boolean('Carry Forward Leave'),
    }

    _defaults = {
        'fiscal_year_id' : _get_fiscalyear
    }

    def browse(self, cr, uid, select, context=None, list_class=None, fields_process=None):
        if context is None:
            context = {}
        context.update({'holiday_donot_compute_domain': True})
        return super(hr_holidays, self).browse(cr, uid, select, context=context, list_class=list_class, fields_process=fields_process)

#    def schedule_lapsed_leave(self, cr, uid, context = None):
#        """ scheduler that remove a leave that not approved and time lapsed"""
#        if context is None:
#            context= {}
#        today = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
#        holiday_ids = self.search(cr, uid, [('date_to', '<', today), ('type','=','remove'), ('state','in',['confirm', 'validate1'])])
##        obj_mail_server = self.pool.get('ir.mail_server')
#        if holiday_ids:
#            self.write(cr, uid, holiday_ids, {'state': 'cancel'}, context=context)
##            to_dt = (datetime.datetime.strptime(leave_data.date_to,DEFAULT_SERVER_DATETIME_FORMAT))
##            if today > to_dt:
##                notes = ''
##                if leave_data.notes:
##                    notes = leave_data.notes
##                notes += '\n\n Leave lapsed detail \n\
##                  ----------------------------------\n\
##               Leave has been cancelled as %s has lapsed in leave.'%today
##                #Get mail server id
##                mail_server_id = self.get_mail_server_id(cr, uid, context=context)
##                #Check for mail server 
##                if not mail_server_id:
##                    raise osv.except_osv(_('Mail Error'), _('No mail server found!'))
##                #Check for hr manager's email
##                if not self.get_employee_data(cr, uid, [leave_data.id], context=context)[2]:
##                    raise osv.except_osv(_('Error'), _('Email of HR manager is not found!')) 
##                
##                #message body for HR department
##                result_data = self.get_leave_data(cr, uid, [leave_data.id], context=context)
##                result_emp_data = self.get_employee_data(cr, uid, [leave_data.id], context=context)
##
##                #message body for employee
##                employee_body = self.get_employee_body(cr, uid, 
##                                           result_emp_data[0], 
##                                           result_data[1], 
##                                           result_data[2], 
##                                           result_data[5], 
##                                           'Cancelled', 
##                                           result_data[3],
##                                           'LEAVE HAS LAPSED',
##                                           context=context)
##                #message for hr manager of employee    
##                message_employee  = obj_mail_server.build_email(
##                    email_from=self.get_email_from(cr, uid, [leave_data.id], context=context), 
##                    email_to=[result_emp_data[1]], 
##                    subject='Cancellation of leave', 
##                    body=employee_body, 
##                    body_alternative=employee_body, 
##                    email_cc=None, 
##                    email_bcc=None, 
##                    reply_to=self.get_email_from(cr, uid, [leave_data.id], context=context), 
##                    attachments=None, 
##                    references = None, 
##                    object_id=None, 
##                    subtype='html', 
##                    subtype_alternative=None, 
##                    headers=None)
##                #Employee Mail content adding in notes
##
##                notes += '\n\nLeave Cancelled Employee Mail Content. \n----------------------------------------------------------------------------\n\n' + employee_body.replace('<br/>','\n')
#                #self.write(cr, uid, [leave_data.id], {'state': 'cancel'}, context=context)
#                #Send mail to employee
#                #self.send_email(cr, uid, message_employee, self.get_mail_server_id(cr, uid, context=context), context=context)
#        return True
#
#    def _get_number_of_days(self, date_from, date_to):
#        """Returns a float equals to the timedelta between two dates given as string."""
#
#        DATETIME_FORMAT = "%Y-%m-%d"
#        from_dt = datetime.datetime.strptime(date_from.split(' ')[0], DATETIME_FORMAT)
#        to_dt = datetime.datetime.strptime(date_to.split(' ')[0], DATETIME_FORMAT)
#        timedelta = to_dt - from_dt
#        diff_day = timedelta.days + float(timedelta.seconds) / 86400
#        return diff_day
#
#    def chk_group(self, cr, uid, record):
#        group_obj = self.pool.get('res.groups')
#        user_obj = self.pool.get('res.users')
#        mgr_ids = group_obj.search(cr, uid, [('name', '=', 'HR Manager')])
#        for group in user_obj.browse(cr, uid, uid).groups_id:
#            if group.id in mgr_ids:
#                return True
#        return False
#    
#    def unlink(self, cr, uid, ids, context=None):
#        unlink_ids = []
#        for rec in self.browse(cr, uid, ids, context=context):
#            if rec.state == 'draft' or rec.state == 'cancel':
#                unlink_ids.append(rec.id)
#            else:
#                return super(hr_holidays, self).unlink(cr, uid, ids, context)
#        if unlink_ids:
#            osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
#        return True
#
#    def get_mail_server_id(self, cr, uid, context=None):
#        '''
#            This method fetches the id of first mail server.
#            If no smtp server is found then False will be returned
#        '''
#        obj_mail_server = self.pool.get('ir.mail_server')
#        mail_server_ids = obj_mail_server.search(cr, uid, [], context=context)
#        if not mail_server_ids:
#            return False
#        else:
#            return mail_server_ids[0]
#
#    def get_email_from(self, cr, uid, ids, context=None):
#        '''
#            This method the username field of first configured smtp server
#        '''
#        obj_mail_server = self.pool.get('ir.mail_server')
#        mail_server_ids = obj_mail_server.search(cr, uid, [], context=context)
#        mail_server_record = obj_mail_server.browse(cr, uid, mail_server_ids)[0]        
#        return mail_server_record.smtp_user or False    
#
#    def get_remaining_leave(self, cr, uid, holiday_id, leave_type, emp_id, context=None):
#        '''
#            This method returns remaining leave of leave_type for emp_id
#        '''
#        holiday_data = self.browse(cr, uid, holiday_id, context=context)
#        add = 0.0
#        remove = 0.0
#        cr.execute("SELECT employee_id,number_of_days_temp FROM hr_holidays where fiscal_year_id=%d and employee_id=%d and holiday_status_id = %d and type='add' and state='validate'"%(holiday_data.fiscal_year_id.id, emp_id, leave_type.id))
#        all_datas = cr.fetchall()
#        if all_datas:
#            for data in all_datas:
#                add += data[1]
#        cr.execute("SELECT employee_id,number_of_days_temp FROM hr_holidays where fiscal_year_id=%d and employee_id=%d and holiday_status_id = %d and type='remove' and state='validate'"%(holiday_data.fiscal_year_id.id, emp_id, leave_type.id))
#        leave_datas = cr.fetchall()
#        if leave_datas:
#            for data in leave_datas:
#                remove += data[1]
#        final = add - remove
#        return final
#
#    def send_email(self, cr, uid, message, mail_server_id, context):
#        '''
#           This method sends mail using information given in message 
#        '''
#        obj_mail_server = self.pool.get('ir.mail_server')
#        obj_mail_server.send_email(cr, uid, message=message, mail_server_id=mail_server_id, context=context)
#    
#    def get_manager_body(self, cr, uid, leave, manager_name, emp_name, fromdate, todate, leave_type, duration, double_validation, leave_date, reason, remaining_leaves, context=None):
#        '''
#            This method returns email body text for manager
#        '''
#        data_obj = self.pool.get('ir.model.data')
#        result_data = data_obj._get_id(cr, uid, 'hr_holidays', 'open_ask_holidays')
#        model_data = data_obj.browse(cr, uid, result_data, context=context)
#        half_day=''
#        rec_id = leave.id
#        user_id = leave.employee_id and leave.employee_id.parent_id.user_id.login
#        cr.execute("select password from res_users where id=%s" % leave.employee_id.parent_id.user_id.id)
#        res = cr.fetchone()
#        pwd = res and res[0] or ''
#        db_name = cr.dbname
#        approve_action = "validate1"
#        reject_action = "refuse"
#        msg_string = ' pre-approve'
#        if not double_validation:
#            msg_string = ' final approve'
#
#        if duration:
#            if duration == 'am': 
#                half_day = 'Half Day Morning'
#            elif duration == 'pm':
#                half_day = 'Half Day Evening'    
#            else:     
#                half_day = 'Full Day'
#            
#        if fromdate:
#            fromdate = fields.datetime.context_timestamp(cr, uid, datetime.datetime.strptime( fromdate, DEFAULT_SERVER_DATETIME_FORMAT), context)
#            fromdate = fromdate.strftime("%d-%m-%Y")
#        else:
#            fromdate = ''
#
#        if todate:
#            todate = fields.datetime.context_timestamp(cr, uid, datetime.datetime.strptime( todate, DEFAULT_SERVER_DATETIME_FORMAT), context)
#            todate = todate.strftime("%d-%m-%Y")
#        else:
#            todate = ''
#        link_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
#        send_link = WEB_LINK_URL % (db_name,user_id,pwd,rec_id,approve_action,model_data.res_id)
#        send_link_encoded = base64.b64encode(send_link)
#        link_url += '/web/webclient/home#'
#        approve_link_url =link_url + send_link_encoded
#        reject_send_link = WEB_LINK_URL % (db_name,user_id,pwd,rec_id,reject_action,model_data.res_id)
#        reject_send_link_encoded = base64.b64encode(reject_send_link)
#        reject_link_url = link_url + reject_send_link_encoded
#        body =  'Hello %s,<br/><br/> \
#                %s has applied for %s on %s. <br/><br/> \
#                Leave Period : %s to %s %s. <br/><br/>\
#                Reason : %s. <br/><br/>\
#                No of Day balance before deduction : %s. <br/><br/>\
#                Please login to iServer %s to %s/reject the leave.<br/><br/> \
#                Thank you.' % (manager_name, emp_name, leave_type, leave_date, fromdate, todate, half_day,reason, remaining_leaves, cr.dbname, msg_string)
#        mail_body =  'Hello %s,<br/><br/> \
#                 %s has applied for %s on %s. <br/><br/> \
#                 Leave Period : %s to %s %s. <br/><br/>\
#                 Reason : %s. <br/><br/>\
#                 No of Day balance before deduction : %s. <br/><br/>\
#                 Approve Leave :- <a href=%s>Click Here</a><br/><br/>\
#                 Reject Leave  :- <a href=%s>Click Here</a><br/><br/>\
#                 Thank you.' % (manager_name, emp_name, leave_type, leave_date, fromdate, todate, half_day,reason, remaining_leaves, approve_link_url, reject_link_url)
#        return {'note': body or '','mail': mail_body or ''}
#    
#    def get_indirect_manager_body(self, cr, uid, leave, indirect_manager_name, hr_manager_name, emp_name, fromdate, todate, leave_type, duration, singnature, leave_date, reason, remaining_leaves, context=None):
#        '''
#            This method return email body text for indirect_manager
#        '''
#        data_obj = self.pool.get('ir.model.data')
#        result_data = data_obj._get_id(cr, uid, 'hr_holidays', 'open_ask_holidays')
#        model_data = data_obj.browse(cr, uid, result_data, context=context)
#        half_day = ''
#        rec_id = leave.id
#        user_id = leave.employee_id and leave.employee_id.parent_id2.user_id.login
#        cr.execute("select password from res_users where id=%s" % leave.employee_id.parent_id2.user_id.id)
#        res = cr.fetchone()
#        pwd = res and res[0] or ''
#        db_name = cr.dbname
#        approve_action = "validate"
#        reject_action = "refuse"
#
#        if duration:
#            if duration == 'am': 
#                half_day = 'Half Day Morning'
#            elif duration == 'pm':
#                half_day = 'Half Day Evening' 
#            else:     
#                half_day = 'Full Day'
#                
#        if fromdate:
#            fromdate = fields.datetime.context_timestamp(cr, uid, datetime.datetime.strptime( fromdate, DEFAULT_SERVER_DATETIME_FORMAT), context)
#            fromdate = fromdate.strftime("%d-%m-%Y")
#        else:
#            fromdate = ''
#
#        if todate:
#            todate = fields.datetime.context_timestamp(cr, uid, datetime.datetime.strptime( todate, DEFAULT_SERVER_DATETIME_FORMAT), context)
#            todate = todate.strftime("%d-%m-%Y")
#        else:
#            todate = ''
#        today = datetime.datetime.now().strftime('%d-%m-%Y')
#        link_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
#        send_link = WEB_LINK_URL % (db_name,user_id,pwd,rec_id,approve_action,model_data.res_id)
#        send_link_encoded = base64.b64encode(send_link)
#        link_url += '/web/webclient/home#'
#        approve_link_url =link_url + send_link_encoded
#        reject_send_link = WEB_LINK_URL % (db_name,user_id,pwd,rec_id,reject_action,model_data.res_id)
#        reject_send_link_encoded = base64.b64encode(reject_send_link)
#        reject_link_url = link_url + reject_send_link_encoded
#        body =  'Hello %s,<br/><br/> \
#                %s has applied for %s on %s which has been pre-approved by %s on %s.<br/><br/> \
#                Leave Period : %s to %s %s. <br/><br/>\
#                Reason : %s. <br/><br/>\
#                No of Day balance before deduction : %s. <br/><br/>\
#                Please login to iServer %s to approve/reject the leave.<br/><br/>\
#                Thank you, <br/>\
#                %s' % (indirect_manager_name, emp_name, leave_type, leave_date, hr_manager_name, today, fromdate, todate, half_day,reason, remaining_leaves, cr.dbname, singnature)
#        mail_body =  'Hello %s,<br/><br/> \
#                 %s has applied for %s on %s which has been pre-approved by %s on %s.<br/><br/> \
#                 Leave Period : %s to %s %s. <br/><br/>\
#                 Reason : %s. <br/><br/>\
#                 No of Day balance before deduction : %s. <br/><br/>\
#                 Approve Leave :- <a href=%s>Click Here</a><br/><br/>\
#                 Reject Leave  :- <a href=%s>Click Here</a><br/><br/>\
#                 Thank you, <br/>\
#                 %s' % (indirect_manager_name, emp_name, leave_type, leave_date, hr_manager_name, today, fromdate, todate, half_day,reason, remaining_leaves, approve_link_url, reject_link_url, singnature)
#        return {'note': body or '','mail': mail_body or ''}
#
#    def get_indirect_manager_body2(self, cr, uid, leave, indirect_manager_name, manager_name, emp_name, fromdate, todate, leave_type, duration, leave_date, reason, remaining_leaves, context=None):
#        '''
#            This method return email body text for indirect_manager
#        '''
#        data_obj = self.pool.get('ir.model.data')
#        result_data = data_obj._get_id(cr, uid, 'hr_holidays', 'open_ask_holidays')
#        model_data = data_obj.browse(cr, uid, result_data, context=context)
#        half_day = ''
#        rec_id = leave.id
#        user_id = leave.employee_id and leave.employee_id.parent_id2.user_id.login
#        cr.execute("select password from res_users where id=%s" % leave.employee_id.parent_id2.user_id.id)
#        res = cr.fetchone()
#        pwd = res and res[0] or ''
#        db_name = cr.dbname
#        approve_action = "validate"
#        reject_action = "refuse"
#        today = datetime.datetime.now().strftime('%d-%m-%Y')
#        if duration:
#            if duration == 'am': 
#                half_day = 'Half Day Morning'
#            elif duration == 'pm':
#                half_day = 'Half Day Evening' 
#            else:     
#                half_day = 'Full Day'
#        if fromdate:
#            fromdate = datetime.datetime.strptime(fromdate.split(' ')[0], "%Y-%m-%d")
#            fromdate = fromdate.strftime("%d/%m/%Y")
#        else:
#            fromdate = ''
#
#        if todate:
#            todate = datetime.datetime.strptime(todate.split(' ')[0], "%Y-%m-%d")
#            todate = todate.strftime("%d/%m/%Y")
#        else:
#            todate = ''
#        
#        link_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
#        send_link = WEB_LINK_URL % (db_name,user_id,pwd,rec_id,approve_action,model_data.res_id)
#        send_link_encoded = base64.b64encode(send_link)
#        link_url += '/web/webclient/home#'
#        approve_link_url= link_url + send_link_encoded
#        reject_send_link = WEB_LINK_URL % (db_name,user_id,pwd,rec_id,reject_action,model_data.res_id)
#        reject_send_link_encoded = base64.b64encode(reject_send_link)
#        reject_link_url = link_url + reject_send_link_encoded
#        
#        body =  'Hello %s,<br/><br/> \
#                %s has applied for %s on %s which has been pre-approved by %s on %s.<br/><br/> \
#                Leave Period : %s to %s %s. <br/><br/>\
#                Reason : %s. <br/><br/>\
#                No of Day balance before deduction : %s. <br/><br/>\
#                Please login to iServer %s to approve/reject the leave.<br/><br/>\
#                Thank you.' % (indirect_manager_name, emp_name, leave_type, leave_date, manager_name, today, fromdate, todate, half_day, reason,remaining_leaves, cr.dbname)
#        
#        mail_body =  'Hello %s,<br/><br/> \
#                 %s has applied for %s on %s which has been pre-approved by %s on %s.<br/><br/> \
#                 Leave Period : %s to %s %s. <br/><br/>\
#                 Reason : %s. <br/><br/>\
#                 No of Day balance before deduction : %s. <br/><br/>\
#                 Approve Leave :- <a href=%s>Click Here</a><br/><br/>\
#                 Reject Leave  :- <a href=%s>Click Here</a><br/><br/>\
#                 Thank you.' % (indirect_manager_name, emp_name, leave_type, leave_date, manager_name, today, fromdate, todate, half_day, reason,remaining_leaves, approve_link_url, reject_link_url)
#        return {'note': body or '','mail': mail_body or ''}
#   
#    def get_hr_body(self, cr, uid, ids, hr_manager_name, emp_name, leave_type, fromdate, todate, duration, reason, current_status, leave_date,leave_reason, context=None):
#        '''
#            This method return email body text for hr department
#        '''
#        if context is None:
#            context = {}
#        if fromdate:
#            fromdate = fields.datetime.context_timestamp(cr, uid, datetime.datetime.strptime( fromdate, DEFAULT_SERVER_DATETIME_FORMAT), context)
#            fromdate = fromdate.strftime("%d-%m-%Y")
#        else:
#            fromdate = ''
#
#        if todate:
#            todate = fields.datetime.context_timestamp(cr, uid, datetime.datetime.strptime( todate, DEFAULT_SERVER_DATETIME_FORMAT), context)
#            todate = todate.strftime("%d-%m-%Y")
#        else:
#            todate = ''
#        half_day = ''
#
#        if duration:
#            if duration == 'am': 
#                half_day = 'Half Day Morning'
#            elif duration == 'pm':    
#                half_day = 'Half Day Evening'        
#            else:     
#                half_day = 'Full Day'
#                
#        cancelled_by = ''
#        if context.get('cancel',False):
#            cancelled_by = 'This Leave has been cancelled by %s.' %(self.pool.get('res.users').browse(cr, uid, uid).name)
#            
#        today = datetime.datetime.now().strftime('%d-%m-%Y')
#
#        if current_status == 'Waiting for Final Approval':
#            body = 'Hello,<br/><br/> \
#                    %s has applied for %s on %s.<br/><br/> \
#                    Leave Period : %s to %s %s.<br/><br/> \
#                    Reason : %s. <br/><br/>\
#                    It has been Pre-Approved by %s on %s.<br/><br/> \
#                    Current Status now is Final Approval.<br/><br/> \
#                    Thank You.' % (emp_name, leave_type, leave_date, fromdate, todate, half_day, leave_reason, hr_manager_name, today)
#        elif current_status == 'Approved':
#            body = 'Hello,<br/><br/> \
#                    %s has applied for %s on %s.<br/><br/> \
#                    Leave Period : %s to %s %s.<br/><br/> \
#                    Reason : %s. <br/><br/>\
#                    It has been %s by %s on %s.<br/><br/> \
#                    Current Status now is %s.<br/><br/> \
#                    Thank You.' % (emp_name, leave_type, leave_date, fromdate, todate, half_day, leave_reason, current_status, hr_manager_name, today, current_status)
#        elif current_status == 'Refused':
#            body = 'Hello,<br/><br/> \
#                    %s has applied for %s on %s.<br/><br/> \
#                    Leave Period : %s to %s %s.<br/><br/> \
#                    It has been %s by %s on %s.<br/><br/> \
#                    Current Status now is %s.<br/><br/> \
#                    Rejection Reason : %s <br/><br/>\
#                    Thank You.' % (emp_name, leave_type, leave_date, fromdate, todate, half_day, current_status, hr_manager_name, today, current_status, reason)
#        elif current_status == 'Cancelled':
#            body =  'Hello,<br/><br/> \
#                     %s has applied for %s on %s.<br/><br/> \
#                     Leave Period : %s to %s %s. <br/><br/> \
#                     %s<br/><br/> \
#                     Cancellation Reason: %s <br/><br/> \
#                     Thank You.' % (emp_name, leave_type, leave_date, fromdate, todate, half_day, cancelled_by, reason)
#        else:
#            body =  'Hello,<br/><br/> \
#                     %s has applied for %s on %s.<br/><br/> \
#                     Leave Period : %s to %s %s. <br/><br/> \
#                     Current Status now is %s. %s<br/><br/> \
#                     Thank You.' % (emp_name, leave_type, leave_date, fromdate, todate, half_day, current_status, cancelled_by)
#        return body or ''
#
#    def get_employee_body(self, cr, uid, emp_name, fromdate, todate, duration, current_status, leave_type, reject_reason='', context=None):
#        '''
#            This method return email body text for employee
#        '''
#        half_day = ''
#        today = datetime.datetime.now().strftime('%d-%m-%Y')
#        if duration:
#            if duration == 'am': 
#                half_day = 'Half Day Morning'
#            elif duration == 'pm':
#                half_day = 'Half Day Evening'     
#            else:     
#                half_day = 'Full Day'
#
#        if fromdate:
#            fromdate = fields.datetime.context_timestamp(cr, uid, datetime.datetime.strptime( fromdate, DEFAULT_SERVER_DATETIME_FORMAT), context)
#            fromdate = fromdate.strftime("%d-%m-%Y")
#        else:
#            fromdate = ''
#
#        if todate:
#            todate = fields.datetime.context_timestamp(cr, uid, datetime.datetime.strptime( todate, DEFAULT_SERVER_DATETIME_FORMAT), context)
#            todate = todate.strftime("%d-%m-%Y")
#        else:
#            todate = ''
#        approved_by = self.pool.get('res.users').browse(cr, uid, uid, context = context).name
#
#        if current_status == 'Refused':
#            body =  'Hello %s,<br/><br/> \
#                     Your %s has been %s by %s on %s.<br/><br/> \
#                     Leave Applied : From %s to %s %s.<br/><br/>\
#                     Rejection Reason : %s <br/><br/>\
#                     Thank You.' % (emp_name, leave_type, current_status, approved_by, today, fromdate, todate, half_day, reject_reason)
#        elif current_status == 'Cancelled':
#            body =  'Hello %s,<br/><br/> \
#                     Your %s has been %s by %s on %s.<br/><br/> \
#                     Leave Applied : From %s to %s %s.<br/><br/>\
#                     Cancellation Reason: %s <br/><br/>\
#                     Thank You.' % (emp_name, leave_type, current_status, approved_by, today, fromdate, todate, half_day, reject_reason)
#        else:
#            body =  'Hello %s,<br/><br/> \
#                     Your %s has been %s by %s on %s.<br/><br/> \
#                     Leave Applied : From %s to %s %s.<br/><br/>\
#                     Thank You.' % (emp_name, leave_type, current_status, approved_by, today, fromdate, todate, half_day)
#        return body or ''
#
#
#    def get_leave_data(self, cr, uid, ids, context=None):
#        '''
#            This method returns required data from current leave
#        '''
#        user_data = self.pool.get('res.users').browse(cr, uid, uid, context=context)
#        #Getting Leave Request Date
#        leave_recs = self.browse(cr, uid, ids, context=context)
#        cr.execute("SELECT create_date FROM hr_holidays where id=%d" %(ids[0]))
#        all_datas = cr.fetchall()
#        all_datas = all_datas[0][0].split(' ')
#        leave_dt = datetime.datetime.strptime(all_datas[0],'%Y-%m-%d')
#        leave_dt = datetime.datetime.strftime(leave_dt,'%d-%m-%Y')
#        return (leave_recs[0].holiday_status_id or False, 
#                leave_recs[0].date_from or '', 
#                leave_recs[0].date_to or '', 
#                leave_recs[0].holiday_status_id.name2 or '', 
#                leave_recs[0].number_of_days_temp or '', 
#                leave_recs[0].leave_type or '', 
#                leave_recs[0].holiday_status_id.double_validation or '',
#                leave_recs[0].rejection,
#                user_data.signature or '',
#                user_data.name or '',
#                '',
#                leave_dt,
#                leave_recs[0].name)
#
#    def get_employee_data(self, cr, uid, ids, context=None):
#        '''
#            This method returns employee's name,work email and 
#            name of manager of dept of company associated with that employee
#        '''
#        emp_obj = self.pool.get('hr.employee')
#        data_obj = self.pool.get('ir.model.data')
#        group_object = self.pool.get('res.groups')
#        
#        result_data = data_obj._get_id(cr, uid, 'base', 'group_hr_manager')
#        model_data = data_obj.browse(cr, uid, result_data, context=context)
#        group_data = group_object.browse(cr, uid, model_data.res_id, context)
#
#        work_email = []
#        manager_name = ''
#        user_ids = [user.id for user in group_data.users]
#        emp_ids = emp_obj.search(cr, uid, [('user_id', 'in', user_ids)])
#        for emp in emp_obj.browse(cr, uid, emp_ids, context=context):
##            manager_name += str(emp.name)
#            if not emp.work_email:
#                if emp.user_id.user_email and emp.user_id.user_email not in work_email:
#                    work_email.append(str(user.user_email))
#                else:
#                    raise osv.except_osv(_('Warning'), _('Email must be configured in %s HR manager !') % (emp.name))
#            elif emp.work_email not in work_email:
#                work_email.append(str(emp.work_email))
#
##        company_data = self.pool.get('res.users').browse(cr, uid, uid, context).company_id
##        if not company_data.department_id:
##            raise osv.except_osv(_('Warning'), _('Department must be configured in user company !'))
##        if not company_data.department_id.manager_id:
##            raise osv.except_osv(_('Warning'), _('Manager must be configured in company department !'))
##
##        work_email = company_data.department_id.manager_id.work_email
##        if not work_email:
##            work_email = company_data.department_id.manager_id.user_id.user_email
##        if not work_email:
##            raise osv.except_osv(_('Warning'), _('Email must be configured in department manager !'))
#        leave_recs = self.browse(cr, uid, ids, context=context)
#        if not leave_recs[0].employee_id.work_email:
#            raise osv.except_osv(_('Warning'), _('Email must be configured in employee !'))
#        return (leave_recs[0].employee_id.name or False, 
#                leave_recs[0].employee_id.work_email or False, 
#                work_email, 
#                leave_recs[0].employee_id or False, 
#                manager_name or False)
#     
#    def get_manager_data(self, cr, uid, ids, context=None):
#        '''
#            This method returns name and email of first manager of employee
#        '''
#        leave_recs = self.browse(cr, uid, ids, context=context)
#        if leave_recs[0].employee_id and not leave_recs[0].employee_id.parent_id.work_email:
#            raise osv.except_osv(_('Warning'), _('Manager email must be configured !'))
#        return (leave_recs[0].employee_id and leave_recs[0].employee_id.parent_id or False, 
#                leave_recs[0].employee_id and leave_recs[0].employee_id.parent_id.name or False, 
#                leave_recs[0].employee_id and leave_recs[0].employee_id.parent_id.work_email or False,
#                leave_recs[0].employee_id and leave_recs[0].employee_id.parent_id.user_id.signature or False)
#   
#    def get_indirect_manager_data(self, cr, uid, ids, context=None):
#        '''
#            This method returns name and email of first indirect manager of employee
#        '''
#        leave_recs = self.browse(cr, uid, ids, context=context)
#        return (leave_recs[0].employee_id.parent_id2 or False, 
#                leave_recs[0].employee_id.parent_id2.name or False, 
#                leave_recs[0].employee_id.parent_id2.work_email or False,
#                leave_recs[0].employee_id.parent_id2.user_id.signature or False)
#
#    def holiday_cancel_button(self, cr, uid, ids, context=None):
#        if context is None:
#            context = {}
#        vals = {}
#        wf_service = netsvc.LocalService('workflow')
#        for holiday in self.browse(cr, uid, ids, context):
#            if holiday.type == 'remove' and holiday.holiday_type == 'employee':
#                context.update({'active_id': holiday.id, 'cancel': True})
#                vals = {
#                  'name': _('Cancel Leave'),
#                  'view_type': 'form',
#                  "view_mode": 'form',
#                  'res_model': 'refuse.leave',
#                  'type': 'ir.actions.act_window',
#                  'target': 'new',
#                  'context': context,
#                  }
#            else:
#                wf_service.trg_validate(uid, 'hr.holidays', holiday.id, 'cancel', cr)
#        return vals
#
#    def holiday_refuse_button(self, cr, uid, ids, context=None):
#        if context is None:
#            context = {}
#        vals = {}
#        wf_service = netsvc.LocalService('workflow')
#        for holiday in self.browse(cr, uid, ids, context):
#            if holiday.type == 'remove' and holiday.holiday_type == 'employee':
#                context.update({'active_id': holiday.id, 'refuse': True})
#                vals = {
#                  'name': _('Refuse Leave'),
#                  'view_type': 'form',
#                  "view_mode": 'form',
#                  'res_model': 'refuse.leave',
#                  'type': 'ir.actions.act_window',
#                  'target': 'new',
#                  'context': context,
#                  }
#            else:
#                wf_service.trg_validate(uid, 'hr.holidays', holiday.id, 'refuse', cr)
#        return vals
#
#    def holidays_cancelled(self, cr, uid, ids, context=None):
#        if context is None:
#            context= {}
#        obj_mail_server = self.pool.get('ir.mail_server')
#        for holiday in self.browse(cr, uid, ids, context):
#            if holiday.holiday_type != 'employee':
#                continue
#            if holiday.type == 'remove':
#                #Get mail server id
#                mail_server_id = self.get_mail_server_id(cr, uid, context=context)
#                employee_user_id = holiday.employee_id.user_id and holiday.employee_id.user_id.id or False
#                #Check for mail server 
#                if not mail_server_id:
#                    raise osv.except_osv(_('Mail Error'), _('No mail server found!'))
#                
#                #message body for HR department
#                result_data = self.get_leave_data(cr, uid, ids, context=context)
#                result_emp_data = self.get_employee_data(cr, uid, ids, context=context)
#                ctx = context.copy()
#                ctx.update({'cancel':True})
#                notes = ''
#                if holiday.notes:
#                    notes = holiday.notes
#                #message body for employee
#                employee_body = self.get_employee_body(cr, uid, 
#                                           result_emp_data[0], 
#                                           result_data[1], 
#                                           result_data[2], 
#                                           result_data[5], 
#                                           'Cancelled', 
#                                           result_data[3],
#                                           result_data[7],
#                                           context=context)
#                hr_body = self.get_hr_body(cr, uid, ids, 
#                                           result_emp_data[4], 
#                                           result_emp_data[0], 
#                                           result_data[3], 
#                                           result_data[1], 
#                                           result_data[2], 
#                                           result_data[5],
#                                           result_data[7], 
#                                           'Cancelled', 
#                                           result_data[11],
#                                           result_data[12],
#                                           context=ctx)
#                #message for manager of employee    
#                message_manager  = obj_mail_server.build_email(
#                    email_from=self.get_email_from(cr, uid, ids, context=context), 
#                    email_to=[self.get_manager_data(cr, uid, ids, context=context)[2]], 
#                    subject='Notification for leave', 
#                    body=hr_body, 
#                    body_alternative=hr_body, 
#                    email_cc=None, 
#                    email_bcc=None, 
#                    reply_to=self.get_email_from(cr, uid, ids, context=context), 
#                    attachments=None, 
#                    references = None, 
#                    object_id=None, 
#                    subtype='html', 
#                    subtype_alternative=None, 
#                    headers=None)
#
#                notes += '\n\nLeave Cancelled Direct Manager Mail Content. \n-------------------------------------------------------------------------\n\n' + hr_body.replace('<br/>','\n')
#                #Send mail to manager
#                self.send_email(cr, uid, message_manager, self.get_mail_server_id(cr, uid, context=context), context=context)
#                indirect_detail = self.get_indirect_manager_data(cr, uid, ids, context=context)
#                indirect_message_manager  = obj_mail_server.build_email(
#                    email_from=self.get_email_from(cr, uid, ids, context=context), 
#                    email_to=[indirect_detail[2]], 
#                    subject='Notification for leave', 
#                    body=hr_body, 
#                    body_alternative=hr_body, 
#                    email_cc=None, 
#                    email_bcc=None, 
#                    reply_to=self.get_email_from(cr, uid, ids, context=context), 
#                    attachments=None, 
#                    references = None, 
#                    object_id=None, 
#                    subtype='html', 
#                    subtype_alternative=None, 
#                    headers=None)  
#                #Manager Mail content adding in notes
#                notes += '\n\nLeave Cancelled Indirect Manager Mail Content. \n---------------------------------------------------------------------------------------\n\n' + hr_body.replace('<br/>','\n')
#                self.send_email(cr, uid, indirect_message_manager, self.get_mail_server_id(cr, uid, context=context), context=context)
#                #message for hr manager of employee    
#                message_employee  = obj_mail_server.build_email(
#                    email_from=self.get_email_from(cr, uid, ids, context=context), 
#                    email_to=[result_emp_data[1]], 
#                    subject='Cancellation of leave', 
#                    body=employee_body, 
#                    body_alternative=employee_body, 
#                    email_cc=None, 
#                    email_bcc=None, 
#                    reply_to=self.get_email_from(cr, uid, ids, context=context), 
#                    attachments=None, 
#                    references = None, 
#                    object_id=None, 
#                    subtype='html', 
#                    subtype_alternative=None, 
#                    headers=None)
#                #Employee Mail content adding in notes
#
#                notes += '\n\nLeave Cancelled Employee Mail Content. \n----------------------------------------------------------------------------\n\n' + employee_body.replace('<br/>','\n')
#                
#                #Send mail to hr manager
#                if employee_user_id == uid:
#                    #Check for hr manager's email
#                    if not result_emp_data[2]:
#                        raise osv.except_osv(_('Error'), _('Email of HR manager is not found!')) 
#
#                    #message for hr manager of employee    
#                    message_hr  = obj_mail_server.build_email(
#                        email_from=self.get_email_from(cr, uid, ids, context=context), 
#                        email_to=result_emp_data[2], 
#                        subject='Notification for cancellation of leave', 
#                        body=hr_body, 
#                        body_alternative=hr_body, 
#                        email_cc=None, 
#                        email_bcc=None, 
#                        reply_to=self.get_email_from(cr, uid, ids, context=context), 
#                        attachments=None, 
#                        references = None, 
#                        object_id=None, 
#                        subtype='html', 
#                        subtype_alternative=None, 
#                        headers=None)
#    
#                    notes += '\n\nLeave Cancelled HR Manager Mail Content. \n-------------------------------------------------------------------------\n\n' + hr_body.replace('<br/>','\n')
#
#                    self.send_email(cr, uid, message_hr, self.get_mail_server_id(cr, uid, context=context), context=context)
#                self.write(cr, uid, ids, {'notes' : notes}, context=context)
#                #Send mail to employee
#                self.send_email(cr, uid, message_employee, self.get_mail_server_id(cr, uid, context=context), context=context)
#        ##############################################################################################################################################################    
#        self.write(cr, uid, ids, {'state': 'cancel'}, context)
#        return True
#        
#    
#    def holidays_confirm(self, cr, uid, ids, context=None):
#        obj_mail_server = self.pool.get('ir.mail_server') 
#        schedule_mail_object = self.pool.get('mail.message')
#        mail_server_ids = obj_mail_server.search(cr, uid, [], context=context)
#        mail_server_record = obj_mail_server.browse(cr, uid, mail_server_ids)[0]
#        email_from = mail_server_record.smtp_user
#        for holiday in self.browse(cr, uid, ids, context):
#            if holiday.holiday_type != 'employee':
#                continue
#            if holiday.employee_id and not holiday.employee_id.parent_id.user_id:
#                raise osv.except_osv(_('Warning!'), _('Direct manager is not defined in employee !'))
#
#            if holiday.type == 'remove':
#                if holiday.employee_id and not holiday.employee_id.work_email:
#                    raise osv.except_osv(_('Warning!'), _('E-mail is not defined in user !'))
#                if holiday.employee_id and not holiday.employee_id.parent_id.work_email:
#                    raise osv.except_osv(_('Warning!'), _('E-mail is not defined in direct manager !'))
##                print "holiday.number_of_days_temp", holiday.number_of_days_temp
##                if holiday.number_of_days_temp <= 0:
##                    raise osv.except_osv(_('Notification!'), _('The leaves you are applying for are already public holidays!'))
#                obj_mail_server = self.pool.get('ir.mail_server')
#                
#                #Get mail server id
#                mail_server_id = self.get_mail_server_id(cr, uid, context=context)
#                
#                #Check for mail server 
#                if not mail_server_id:
#                    raise osv.except_osv(_('Mail Error'), _('No mail server found!'))
#                
#                #Check for manager 
#                if not self.get_manager_data(cr, uid, ids, context=context)[0]:
#                    raise osv.except_osv(_('Error'), _('Parent manager is not assigned!'))
#                
#                #Check for hr manager
##                if not self.get_employee_data(cr, uid, ids, context=context)[4]:
##                     raise osv.except_osv(_('Error'), _('Manager is not assigned to HR department!'))
#                
#                #Check for hr manager's email
##                if not self.get_employee_data(cr, uid, ids, context=context)[2]:
##                    raise osv.except_osv(_('Error'), _('Email of HR manager is not found!')) 
#                 
#                #Getting remaining leaves for employee 
#                result_emp_data = self.get_employee_data(cr, uid, ids, context=context)
#                result_data = self.get_leave_data(cr, uid, ids, context=context)
#                remaining_leaves = self.get_remaining_leave(cr, uid, holiday.id, 
#                                         result_data[0], 
#                                         result_emp_data[3], 
#                                         context=context)
#                
#                #message body for manager
#                manager_body = self.get_manager_body(cr, uid, holiday, 
#                                                     self.get_manager_data(cr, uid, ids, context=context)[1], #manager name
#                                                     result_emp_data[0], #employee name 
#                                                     result_data[1], 
#                                                     result_data[2], 
#                                                     result_data[3], 
#                                                     result_data[5], 
#                                                     result_data[6], 
#                                                     result_data[11],
#                                                     result_data[12],
#                                                     remaining_leaves = remaining_leaves, 
#                                                     context=context)
##                if holiday.holiday_status_id.double_validation:
##                    hr_status = 'Waiting for Pre-Approval'
##                else: 
##                    hr_status = 'Waiting for Final-Approval'
#                #message body for HR department
##                hr_body = self.get_hr_body(cr, uid, ids, 
##                                           result_data[8], 
##                                           result_emp_data[0], 
##                                           result_data[3], 
##                                           result_data[1], 
##                                           result_data[2], 
##                                           result_data[5],
##                                           result_data[7], 
##                                           hr_status, 
##                                           result_data[11], 
##                                           context=context)
#                #message for manager of employee    
##                message_manager  = obj_mail_server.build_email(
##                    email_from=self.get_email_from(cr, uid, ids, context=context), 
##                    email_to=[self.get_manager_data(cr, uid, ids, context=context)[2]], 
##                    subject='Notification for leave', 
##                    body=manager_body, 
##                    body_alternative=manager_body, 
##                    email_cc=None, 
##                    email_bcc=None, 
##                    reply_to=self.get_email_from(cr, uid, ids, context=context), 
##                    attachments=None, 
##                    references = None, 
##                    object_id=None, 
##                    subtype='html', 
##                    subtype_alternative=None, 
##                    headers=None)
#
#                #message for hr manager of employee    
##                message_hr  = obj_mail_server.build_email(
##                    email_from=self.get_email_from(cr, uid, ids, context=context), 
##                    email_to=result_emp_data[2], 
##                    subject='Notification for leave', 
##                    body=hr_body, 
##                    body_alternative=hr_body, 
##                    email_cc=None, 
##                    email_bcc=None, 
##                    reply_to=self.get_email_from(cr, uid, ids, context=context), 
##                    attachments=None, 
##                    references = None, 
##                    object_id=None, 
##                    subtype='html', 
##                    subtype_alternative=None, 
##                    headers=None)
#                #Mail content of Manager
#                notes = ''
#                if holiday.notes:
#                    notes = holiday.notes
#                notes += '\n\nLeave Applied Direct Manager Mail Content. \n-------------------------------------------------------------------------\n\n' + manager_body.get('note').replace('<br/>','\n')
#                self.write(cr, uid, ids, {'notes' : notes}, context=context)
#                #Send mail to manager
#                email_to=[self.get_manager_data(cr, uid, ids, context=context)[2]]
##                schedule_mail_object.schedule_with_attach(cr, uid, email_from, email_to, 'Notification for leave', manager_body.get('mail'), subtype="html", context=context)
#                if email_to:
#                    vals = {'state': 'outgoing',
#                            'subject': 'Notification for leave',
#                            'body_html': '<pre>%s</pre>' % notes,
#                            'email_to': email_to,
#                            'email_from': email_from}
#                    self.pool.get('mail.mail').create(cr, uid, vals, context=context)
##                self.send_email(cr, uid, message_manager, self.get_mail_server_id(cr, uid, context=context), context=context)
#                #Send mail to hr manager
##                email_to=result_emp_data[2]
##                self.send_email(cr, uid, message_hr, self.get_mail_server_id(cr, uid, context=context), context=context)
##                schedule_mail_object.schedule_with_attach(cr, uid, email_from, email_to, 'Notification for leave', hr_body, context=context)
#        return super(hr_holidays, self).holidays_confirm(cr, uid, ids, context=context)
#
#    
#    def holidays_refuse(self, cr, uid, ids, approval, context=None):
#        for holiday in self.browse(cr, uid, ids, context):
#            if holiday.holiday_type != 'employee':
#                continue
#            if holiday.type == 'remove':
#                if not holiday.employee_id.work_email:
#                    raise osv.except_osv(_('Warning!'), _('E-mail not defined in user !') % (holiday.employee_id.name))
#    
#                obj_mail_server = self.pool.get('ir.mail_server')
#                #Get mail server id
#                mail_server_id = self.get_mail_server_id(cr, uid, context=context)
#                if not mail_server_id:
#                    raise osv.except_osv(_('Mail Error'), _('No mail server found!'))
#                
#                #Check for hr manager's email 
##                if not self.get_employee_data(cr, uid, ids, context=context)[2]:
##                    raise osv.except_osv(_('Error'), _('Email of HR manager is not found!')) 
#                
#                if not (holiday.employee_id.parent_id and holiday.employee_id.parent_id.user_id):
#                    raise osv.except_osv(_('Warning!'), _('Direct user is not defined in employee !'))
#                
#                #message body for HR department
#                result_data =self.get_leave_data(cr, uid, ids, context=context)
#                result_emp_data = self.get_employee_data(cr, uid, ids, context=context) 
##                hr_body = self.get_hr_body(cr, uid, ids, 
##                                           result_data[9], 
##                                           result_emp_data[0], 
##                                           result_data[3], 
##                                           result_data[1], 
##                                           result_data[2], 
##                                           result_data[5],
##                                           result_data[7], 
##                                           'Refused', 
##                                           result_data[11],
##                                           result_data[12],
##                                           context=context)
#                
#                #message body for employee
#                employee_body = self.get_employee_body(cr, uid, 
#                                           result_emp_data[0], 
#                                           result_data[1], 
#                                           result_data[2], 
#                                           result_data[5], 
#                                           'Refused', 
#                                           result_data[3],
#                                           result_data[7],
#                                           context=context)
#                #message for hr manager of employee    
##                message_hr  = obj_mail_server.build_email(
##                    email_from=self.get_email_from(cr, uid, ids, context=context), 
##                    email_to=self.get_employee_data(cr, uid, ids, context=context)[2], 
##                    subject='Notification for rejection of leave', 
##                    body=hr_body, 
##                    body_alternative=hr_body, 
##                    email_cc=None, 
##                    email_bcc=None, 
##                    reply_to=self.get_email_from(cr, uid, ids, context=context), 
##                    attachments=None, 
##                    references = None, 
##                    object_id=None, 
##                    subtype='html', 
##                    subtype_alternative=None, 
##                    headers=None)
#                
#                #message for hr manager of employee    
#                message_employee  = obj_mail_server.build_email(
#                    email_from=self.get_email_from(cr, uid, ids, context=context), 
#                    email_to=[self.get_employee_data(cr, uid, ids, context=context)[1]], 
#                    subject='Rejection of leave', 
#                    body=employee_body, 
#                    body_alternative=employee_body, 
#                    email_cc=None, 
#                    email_bcc=None, 
#                    reply_to=self.get_email_from(cr, uid, ids, context=context), 
#                    attachments=None, 
#                    references = None, 
#                    object_id=None, 
#                    subtype='html', 
#                    subtype_alternative=None, 
#                    headers=None)
#                #Employee Mail content adding in notes
#                notes = ''
#                if holiday.notes:
#                    notes = holiday.notes
#                notes += '\n\nLeave Refused Employee Mail Content. \n----------------------------------------------------------------------------\n\n' + employee_body.replace('<br/>','\n')
#                self.write(cr, uid, ids, {'notes' : notes}, context=context)
#                #Send mail to hr manager
##                self.send_email(cr, uid, message_hr, self.get_mail_server_id(cr, uid, context=context), context=context)
#                #Send mail to employee
#                self.send_email(cr, uid, message_employee, self.get_mail_server_id(cr, uid, context=context), context=context)
#        return super(hr_holidays, self).holidays_refuse(cr, uid, ids, approval, context=context)
#
#    def holidays_validate(self, cr, uid, ids, context=None): 
#        obj_mail_server = self.pool.get('ir.mail_server') 
#        schedule_mail_object = self.pool.get('mail.message')
#        self.check_holidays(cr, uid, ids, context=context)
#        super_call = False
#        res= True
#        mail_server_ids = obj_mail_server.search(cr, uid, [], context=context)
#        mail_server_record = obj_mail_server.browse(cr, uid, mail_server_ids)[0]
#        email_from = mail_server_record.smtp_user
#        for record in self.browse(cr, uid, ids):
#            if record.holiday_type == 'employee':
#                if not (record.employee_id.parent_id and record.employee_id.parent_id.user_id):
#                    raise osv.except_osv(_('Warning!'), _('Direct user is not defined in employee !'))
#                if not (record.employee_id.user_id and record.employee_id.work_email):
#                    raise osv.except_osv(_('Warning!'), _('E-mail is not defined in user !'))
#                if record.holiday_status_id.double_validation and record.employee_id.parent_id2 and not record.employee_id.parent_id2.work_email:
#                    raise osv.except_osv(_('Warning!'), _('E-mail is not defined in indirect manager !'))
#            if record.holiday_type == 'employee' and record.type == 'remove':
#                if record.employee_id.parent_id.user_id.id != uid:
#                    if self.chk_group(cr, uid, record):
#                        super_call = True
#                    else:
#                        raise osv.except_osv(_('Warning!'), _('You cannot validate leaves for employee %s: Only direct manager or HR manager can approve.') % (record.employee_id.name))
#                else:
#                    super_call = True
#            elif record.holiday_type == 'employee' and record.type == 'add':
#                if record.employee_id.parent_id.user_id.id != uid:
#                    if self.chk_group(cr, uid, record):
#                        super_call = True
#                    else:
#                        raise osv.except_osv(_('Warning!'), _('You cannot allocate leaves for employee %s: Only direct manager or HR manager can allocate.') % (record.employee_id.name))
#                else:
#                    super_call = True
#            else:
#                if self.chk_group(cr, uid, record):
#                    super_call = True
#                else:
#                    raise osv.except_osv(_('Warning!'), _('You cannot Approve leaves only HR manager can Approve.'))
#            if record.holiday_type != 'employee':
#                super_call = True
#                continue
#            if record.type == 'remove':
#                obj_mail_server = self.pool.get('ir.mail_server')
#                
#                #Get mail server id
#                mail_server_id = self.get_mail_server_id(cr, uid, context=context)
#                
#                #Check for mail server 
#                if not mail_server_id:
#                    raise osv.except_osv(_('Mail Error'), _('No mail server found!'))
#                
#                #Check for indirect manager 
#                if record.holiday_status_id.double_validation and not self.get_indirect_manager_data(cr, uid, ids, context=context)[0]:
#                    raise osv.except_osv(_('Error'), _('Indirect manager is not assigned!'))
#                
#                #Check for hr manager
##                if not self.get_employee_data(cr, uid, ids, context=context)[4]:
##                     raise osv.except_osv(_('Error'), _('Manager is not assigned to HR Department!'))
#                
#                if not (record.employee_id.parent_id and record.employee_id.parent_id.user_id):
#                    raise osv.except_osv(_('Warning!'), _('Direct user is not defined in employee !'))
#                 
#                #Getting remaining leaves for employee 
#                remaining_leaves = self.get_remaining_leave(cr, uid, record.id, 
#                                         self.get_leave_data(cr, uid, ids, context)[0], 
#                                         self.get_employee_data(cr, uid, ids, context=context)[3], 
#                                         context=context)
#                #message body for manager
#                result_emp_data = self.get_employee_data(cr, uid, ids, context=context)
#                result_data = self.get_leave_data(cr, uid, ids, context=context)
#                employee_body = self.get_employee_body(cr, uid, 
#                                           result_emp_data[0], 
#                                           result_data[1], 
#                                           result_data[2], 
#                                           result_data[5], 
#                                           'Approved', 
#                                           result_data[3],
#                                           '',
#                                           context=context)
#                if record.holiday_status_id.double_validation:
#                    #Direct manager does pre-approval
#                    indirect_detail = self.get_indirect_manager_data(cr, uid, ids, context=context)
#                    if record.employee_id.parent_id.user_id.id == uid:
#                        indirect_manager_body2 = self.get_indirect_manager_body2(cr, uid, record, 
#                                                 indirect_detail[1], #Indirect manager name
#                                                 self.get_manager_data(cr, uid, ids, context=context)[1], #manager name
#                                                 self.get_employee_data(cr, uid, ids, context=context)[0], #employee name 
#                                                 result_data[1], 
#                                                 result_data[2], 
#                                                 result_data[3], 
#                                                 result_data[5], 
#                                                 result_data[11], #Leave Request Date
#                                                 result_data[12],
#                                                 remaining_leaves = remaining_leaves, 
#                                                 context=context)
##                        indirect_message_manager  = obj_mail_server.build_email(
##                        email_from=self.get_email_from(cr, uid, ids, context=context), 
##                        email_to=[indirect_detail[2]], 
##                        subject='Notification for leave', 
##                        body=indirect_manager_body2, 
##                        body_alternative=indirect_manager_body2, 
##                        email_cc=None, 
##                        email_bcc=None, 
##                        reply_to=self.get_email_from(cr, uid, ids, context=context), 
##                        attachments=None, 
##                        references = None, 
##                        object_id=None, 
##                        subtype='html', 
##                        subtype_alternative=None, 
##                        headers=None)
#                        
#                        #Manager Mail content adding in notes
#                        notes = ''
#                        if record.notes:
#                            notes = record.notes
#                        notes += '\n\nLeave Pre-Approved Indirect Manager Mail Content. \n---------------------------------------------------------------------------------------\n\n' + indirect_manager_body2.get("note").replace('<br/>','\n')
#                        self.write(cr, uid, ids, {'notes' : notes}, context=context)
#                        email_to=[indirect_detail[2]]
##                        self.send_email(cr, uid, indirect_message_manager, self.get_mail_server_id(cr, uid, context=context), context=context)
#                        schedule_mail_object.schedule_with_attach(cr, uid, email_from, email_to, 'Notification for leave', indirect_manager_body2.get("mail"), subtype='html', context=context)
##                    elif self.chk_group(cr, uid, record):
##                        #HR manager pre-approves
##                        indirect_manager_body = self.get_indirect_manager_body(cr, uid, ids, 
##                                                                     indirect_detail[1], #Indirect manager name
##                                                                     result_data[8],#HR manager name
##                                                                     result_emp_data[0], #employee name 
##                                                                     result_data[1], 
##                                                                     result_data[2], 
##                                                                     result_data[3], 
##                                                                     result_data[5],
##                                                                     result_data[9], #HR manager signature
##                                                                     result_data[11], #Leave Request Date 
##                                                                     remaining_leaves = remaining_leaves,
##                                                                     context=context)
##                        indirect_message_manager  = obj_mail_server.build_email(
##                                    email_from=self.get_email_from(cr, uid, ids, context=context), 
##                                    email_to=[indirect_detail[2]], 
##                                    subject='Approval of leave', 
##                                    body=indirect_manager_body, 
##                                    body_alternative=indirect_manager_body, 
##                                    email_cc=None, 
##                                    email_bcc=None, 
##                                    reply_to=self.get_email_from(cr, uid, ids, context=context), 
##                                    attachments=None, 
##                                    references = None, 
##                                    object_id=None, 
##                                    subtype='html', 
##                                    subtype_alternative=None, 
##                                    headers=None)  
##                        #Manager Mail content adding in notes
##                        notes = ''
##                        if record.notes:
##                            notes = record.notes
##                        notes += '\n\nLeave Pre-Approved Indirect Manager Mail Content. \n----------------------------------------------------------------------------\n\n' + indirect_manager_body.replace('<br/>','\n')
##                        self.write(cr, uid, ids, {'notes' : notes}, context=context)
##                        email_to=[indirect_detail[2]]
##                        body=indirect_manager_body
##                        attachments=None
##                        self.send_email(cr, uid, indirect_message_manager, self.get_mail_server_id(cr, uid, context=context), context=context)
##                        schedule_mail_object.schedule_with_attach(cr, uid, email_from, email_to, body, attachments, context)
#
#                #Email to Employee
#                if not record.holiday_status_id.double_validation:
##                    message_employee  = obj_mail_server.build_email(
##                        email_from=self.get_email_from(cr, uid, ids, context=context), 
##                        email_to=[result_emp_data[1]], 
##                        subject='Approval of leave', 
##                        body=employee_body, 
##                        body_alternative=employee_body, 
##                        email_cc=None, 
##                        email_bcc=None, 
##                        reply_to=self.get_email_from(cr, uid, ids, context=context), 
##                        attachments=None, 
##                        references = None, 
##                        object_id=None, 
##                        subtype='html', 
##                        subtype_alternative=None, 
##                        headers=None)
#                    #Email content in comments for approval of leave
#                    notes = ''
#                    if record.notes:
#                        notes = record.notes
#                    #Check for hr manager's email
#                    if not self.get_employee_data(cr, uid, ids, context=context)[2]:
#                        raise osv.except_osv(_('Error'), _('Email of HR manager is not found!')) 
#                    #message body for HR department
#                    hr_status = 'Approved'
#                    hr_body = self.get_hr_body(cr, uid, ids, 
#                                               result_data[9], 
#                                               result_emp_data[0], 
#                                               result_data[3],
#                                               result_data[1], 
#                                               result_data[2], 
#                                               result_data[5],
#                                               False, 
#                                               hr_status, 
#                                               result_data[11],
#                                               result_data[12],
#                                               context=context)
#                    email_to=result_emp_data[2]
##                    schedule_mail_object.schedule_with_attach(cr, uid, email_from, email_to, 'Notification for leave', hr_body, subtype='html', context=context)
#                    if email_to:
#                        vals = {'state': 'outgoing',
#                                'subject': 'Notification for leave',
#                                'body_html': '<pre>%s</pre>' % hr_body,
#                                'email_to': email_to,
#                                'email_from': email_from}
#                        self.pool.get('mail.mail').create(cr, uid, vals, context=context)
#
#                    notes += '\n\nLeave Approval Employee Mail Content. \n------------------------------------------------------------------\n\n' + employee_body.replace('<br/>','\n')
#                    self.write(cr, uid, ids, {'notes' : notes}, context=context)
#                    email_to=[result_emp_data[1]]
##                    self.send_email(cr, uid, message_employee, self.get_mail_server_id(cr, uid, context=context), context=context)
##                    schedule_mail_object.schedule_with_attach(cr, uid, email_from, email_to, 'Approval of leave', employee_body, subtype='html',  context= context)
#                    if email_to:
#                        vals = {'state': 'outgoing',
#                                'subject': 'Approval of leave',
#                                'body_html': '<pre>%s</pre>' % employee_body,
#                                'email_to': email_to,
#                                'email_from': email_from}
#                        self.pool.get('mail.mail').create(cr, uid, vals, context=context)
#
#
#                #message for hr manager of employee    
##                message_hr  = obj_mail_server.build_email(
##                    email_from=self.get_email_from(cr, uid, ids, context=context), 
##                    email_to=result_emp_data[2], 
##                    subject='Notification for leave', 
##                    body=hr_body, 
##                    body_alternative=hr_body, 
##                    email_cc=None, 
##                    email_bcc=None, 
##                    reply_to=self.get_email_from(cr, uid, ids, context=context), 
##                    attachments=None, 
##                    references = None, 
##                    object_id=None, 
##                    subtype='html', 
##                    subtype_alternative=None, 
##                    headers=None)
#
#                #Send mail to hr manager
##                self.send_email(cr, uid, message_hr, self.get_mail_server_id(cr, uid, context=context), context=context)
#        if super_call:
#            res =  super(hr_holidays, self).holidays_validate(cr, uid, ids, context=context)
#        return res
#
#    def holidays_validate2(self, cr, uid, ids, context=None):
#        schedule_mail_object = self.pool.get('mail.message')
#        self.check_holidays(cr, uid, ids, context=context)
#        super_call = False
#        for record in self.browse(cr, uid, ids):
#            if record.holiday_type == 'employee':
#                if not record.holiday_status_id.double_validation:
#                    return super(hr_holidays, self).holidays_validate2(cr, uid, ids, context=context)
#    
#                if not (record.employee_id.parent_id2 and record.employee_id.parent_id2.user_id):
#                    raise osv.except_osv(_('Warning!'), _('Indirect manager is not defined in employee !'))
#                if not record.employee_id.work_email:
#                    raise osv.except_osv(_('Warning!'), _('E-mail is not defined in user !') % (record.employee_id.name))
#
#            if record.holiday_type == 'employee' and record.type == 'remove':
#                if record.employee_id.parent_id2.user_id.id != uid:
#                    if self.chk_group(cr, uid, record):
#                        super_call = True
#                    else:
#                        raise osv.except_osv(_('Warning!'), _('You cannot validate leaves for employee %s: Only indirect manager or HR manager can approve.') % (record.employee_id.name))
#                else:
#                    super_call = True
#            elif record.holiday_type == 'employee' and record.type == 'add':
#                if record.employee_id.parent_id2.user_id.id != uid:
#                    if self.chk_group(cr, uid, record):
#                        super_call = True
#                    else:
#                        raise osv.except_osv(_('Warning!'), _('You cannot allocate leaves for employee %s: Only in direct manager or HR manager can allocate.') % (record.employee_id.name))
#                else:
#                    super_call = True
#            else:
#                if self.chk_group(cr, uid, record):
#                    super_call = True
#                else:
#                    raise osv.except_osv(_('Warning!'), _('You cannot approve leaves only HR manager can approve.'))                        
#            if record.holiday_type != 'employee':
#                super_call = True
#                continue
#            if record.type == 'remove':
##                obj_mail_server = self.pool.get('ir.mail_server')
#                
#                #Get mail server id
#                mail_server_id = self.get_mail_server_id(cr, uid, context=context)
#                
#                #Check for mail server 
#                if not mail_server_id:
#                    raise osv.except_osv(_('Mail Error'), _('No mail server found!'))
#
#                #Check for hr manager's email
#                if not self.get_employee_data(cr, uid, ids, context=context)[2]:
#                    raise osv.except_osv(_('Error'), _('Email of HR manager is not found!')) 
#
#                #message body for HR department
#                result_data =self.get_leave_data(cr, uid, ids, context=context)
#                result_emp_data = self.get_employee_data(cr, uid, ids, context=context) 
#                hr_body = self.get_hr_body(cr, uid, ids, 
#                                           result_data[9], 
#                                           result_emp_data[0], 
#                                           result_data[3], 
#                                           result_data[1], 
#                                           result_data[2], 
#                                           result_data[5],
#                                           False, 
#                                           'Approved', 
#                                           result_data[11],
#                                           result_data[12],
#                                           context=context)
#                
#                #message body for employee
#                employee_body = self.get_employee_body(cr, uid, 
#                                           result_emp_data[0], 
#                                           result_data[1], 
#                                           result_data[2], 
#                                           result_data[5], 
#                                           'Approved',
#                                           result_data[3],
#                                           '',
#                                           context=context)
#                
#                #message for hr manager of employee    
##                message_hr  = obj_mail_server.build_email(
##                    email_from=self.get_email_from(cr, uid, ids, context=context), 
##                    email_to=result_emp_data[2], 
##                    subject='Notification for leave', 
##                    body=hr_body, 
##                    body_alternative=hr_body, 
##                    email_cc=None, 
##                    email_bcc=None, 
##                    reply_to=self.get_email_from(cr, uid, ids, context=context), 
##                    attachments=None, 
##                    references = None, 
##                    object_id=None, 
##                    subtype='html', 
##                    subtype_alternative=None, 
##                    headers=None)        
#                
#                #message for hr manager of employee    
##                message_employee  = obj_mail_server.build_email(
##                    email_from=self.get_email_from(cr, uid, ids, context=context), 
##                    email_to=[result_emp_data[1]], 
##                    subject='Approval of leave', 
##                    body=employee_body, 
##                    body_alternative=employee_body, 
##                    email_cc=None, 
##                    email_bcc=None, 
##                    reply_to=self.get_email_from(cr, uid, ids, context=context), 
##                    attachments=None, 
##                    references = None, 
##                    object_id=None, 
##                    subtype='html', 
##                    subtype_alternative=None, 
##                    headers=None)        
#                #Email content in comments for approval of leave
#                notes = ''
#                if record.notes:
#                    notes = record.notes
#                notes += '\n\nLeave Approval Employee Mail Content. \n----------------------------------------------------------------------------\n\n' + employee_body.replace('<br/>','\n')
#                self.write(cr, uid, ids, {'notes' : notes}, context=context)
#                #Send mail to hr manager
#                email_from = self.get_email_from(cr, uid, ids, context=context), 
#                email_to = result_emp_data[2]
#                res_user_email = self.pool.get('res.users').browse(cr, uid, uid, context=context).user_email
#                current_user_id = self.pool.get('hr.employee').search(cr, uid, [("user_id" , '=' , uid)], context = context)
#                current_user_email = ''
#                if current_user_id:
#                    current_user_email = self.pool.get('hr.employee').browse(cr, uid, current_user_id, context = context)[0].work_email
#                index = 0
#                for email in email_to:
#                    if (res_user_email or current_user_email) and email_to[index] == current_user_email or email_to[index] == res_user_email:
#                        email_to.pop(index)
#                    index += 1
##                schedule_mail_object.schedule_with_attach(cr, uid, email_from, email_to, 'Notification for leave', hr_body, subtype='html', context=context)
#                if email_to:
#                    vals = {'state': 'outgoing',
#                            'subject': 'Notification of leave',
#                            'body_html': '<pre>%s</pre>' % hr_body,
#                            'email_to': email_to,
#                            'email_from': email_from}
#                    self.pool.get('mail.mail').create(cr, uid, vals, context=context)
##            self.send_email(cr, uid, message_hr, self.get_mail_server_id(cr, uid, context=context), context=context)       
#                
#                #Send mail to employee
#                email_to=[result_emp_data[1]]
##                schedule_mail_object.schedule_with_attach(cr, uid, email_from, email_to, 'Approval of leave', employee_body, subtype='html', context=context)
#                if email_to:
#                    vals = {'state': 'outgoing',
#                            'subject': 'Approval of leave',
#                            'body_html': '<pre>%s</pre>' % employee_body,
#                            'email_to': email_to,
#                            'email_from': email_from}
#                    self.pool.get('mail.mail').create(cr, uid, vals, context=context)
##                self.send_email(cr, uid, message_employee, self.get_mail_server_id(cr, uid, context=context), context=context)
#        res = True
#        if super_call:
#            res = super(hr_holidays, self).holidays_validate2(cr, uid, ids, context=context)
#        return res
#
#    def onchange_leave_type(self, cr, uid, ids, leave_type, context=None):
#        result = {}
#        if leave_type == 'am' or leave_type == 'pm':
#            result['value']={
#                'number_of_days_temp': 0.5
#                }
#            return result
#        result['value'] = {
#            'number_of_days_temp': 1, 
#        }
#        return result
#
#    def onchange_date_from(self, cr, uid, ids, date_to, date_from, holiday_status_id, leave_type, context = None):
#        print 'YYYjjjjjjjjjjj'
#        result = {}
#        if not context:
#            context = {}
#        if not date_to or not date_from or not holiday_status_id:
#            return {}
#        if date_from and date_to and leave_type and (date_to.split(' ')[0] == date_from.split(' ')[0]) and leave_type in ['am', 'pm']: 
#            result['value'] = {
#                'number_of_days_temp': 0.5
#            }
#        elif date_to and date_from and holiday_status_id:
#            days = self._check_holiday_dates(cr, uid, date_from, date_to, holiday_status_id, leave_type, context)
#            result['value'] = {
#                'number_of_days_temp': round(days)
#            }
#        else:
#            result['value'] = {
#                'number_of_days_temp': 0, 
#            }
#        print "OHHHHHHHHhhhhhhhhhhhhhhhhh"
#        return result
#
#
#    def cal_fwd_period(self, cr, uid, ids=None, context=None):
#        wf_service = netsvc.LocalService("workflow")
#        today = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
#        year = datetime.datetime.strptime(today, DEFAULT_SERVER_DATE_FORMAT).year
#        fiscalyear_id = self.fetch_fiscalyear(cr, uid, today, context=context)
#        fiscalyear_obj = self.pool.get('account.fiscalyear')
#        fiscalyear_rec = fiscalyear_obj.browse(cr, uid, fiscalyear_id, context=context)
#        end_date = str(year) + "-03-31"
#        holiday_ids = self.search(cr , uid, [('type', '=', 'add'), ('state', '=', 'validate'), ('holiday_type', '!=', 'category'),('fiscal_year_id','=', fiscalyear_id),('carry_forward','=',True)])
#        leave_allocations = self.browse(cr, uid, holiday_ids)
#        for leave in leave_allocations:
#            domain = [('type', '=', 'remove'), ('holiday_status_id', '=', leave.holiday_status_id.id), ('state', '=', 'validate'), ('employee_id', '=', leave.employee_id.id),('date_from','>=', fiscalyear_rec.date_start),('date_to','<=', end_date)]
#            leave_req_ids = self.search(cr, uid, domain, context=context)
#            leave_requests = self.browse(cr, uid, leave_req_ids, context=context)
#            total_taken_leaves = 0.0
#            for leave_request in leave_requests:
#                total_taken_leaves += leave_request.number_of_days_temp
#            domain = [('type', '=', 'remove'), ('holiday_status_id', '=', leave.holiday_status_id.id), ('state', '=', 'validate'), ('employee_id', '=', leave.employee_id.id),('date_from','<=', end_date),('date_to','>', end_date)]
#            leave_req_ids = self.search(cr, uid, domain, context=context)
#            for leave_request in self.browse(cr, uid, leave_req_ids, context):
#                total_taken_leaves += self._check_holiday_carryforward(cr, uid, leave_request.id, fiscalyear_rec.date_start, end_date)
#            if leave.number_of_days_temp > total_taken_leaves:
#                alloc_leaves = leave.number_of_days_temp - total_taken_leaves
#                cleave_dict = {
#                    'name' : 'Carry Forward Clear Leave Allocation', 
#                    'employee_id': leave.employee_id.id, 
#                    'holiday_type' : 'employee',
#                    'holiday_status_id' : leave.holiday_status_id.id, 
#                    'number_of_days_temp' : alloc_leaves * -1, 
#                    'type' : 'add',
#                    'fiscal_year_id' : fiscalyear_id,
#                    'unallocated' : True
#                    }
#                holiday_id = self.create(cr, uid, cleave_dict)
#                wf_service.trg_validate(uid, 'hr.holidays', holiday_id, 'confirm', cr)
#                wf_service.trg_validate(uid, 'hr.holidays', holiday_id, 'validate', cr)
#                wf_service.trg_validate(uid, 'hr.holidays', holiday_id, 'second_validate', cr)
#        return {'type' : 'ir.actions.act_window_close'}
#    
#    def chk_approval(self, cr, uid, ids=None, context=None):
#        holiday_ids = self.search(cr, uid, [('type','=','remove'), ('state','=','confirm'), ('employee_id.parent_id.is_all_final_leave', '=', True)])
#        holiday_recs = self.browse(cr, uid, holiday_ids, context=context)
#        today = datetime.datetime.strftime(datetime.date.today(),"%Y-%m-%d")
#        obj_mail_server = self.pool.get('ir.mail_server')
#        for holiday in holiday_recs:
#            result_data = self.get_leave_data(cr, uid, [holiday.id], context=context)
#            result_emp_data = self.get_employee_data(cr, uid, [holiday.id], context=context)
#            remaining_leaves = self.get_remaining_leave(cr, uid, holiday.id, 
#                                 result_data[0], 
#                                 result_emp_data[3], 
#                                 context=context)
#            day = self._get_number_of_days(today, holiday.date_from)
#            if day == 3.0:
#                #message body for manager
#                manager_body = self.get_manager_body(cr, uid, holiday, 
#                                                     self.get_manager_data(cr, uid, [holiday.id], context=context)[1], #manager name
#                                                     result_emp_data[0], #employee name 
#                                                     result_data[1], 
#                                                     result_data[2], 
#                                                     result_data[3], 
#                                                     result_data[5], 
#                                                     result_data[6], 
#                                                     result_data[11],
#                                                     result_data[12],
#                                                     remaining_leaves = remaining_leaves, 
#                                                     context=context)
#                #message for manager of employee    
#                message_manager  = obj_mail_server.build_email(
#                    email_from=self.get_email_from(cr, uid, [holiday.id], context=context), 
#                    email_to=[self.get_manager_data(cr, uid, [holiday.id], context=context)[2]], 
#                    subject='Notification for leave', 
#                    body=manager_body.get('note'), 
#                    body_alternative=manager_body.get('note'), 
#                    email_cc=None, 
#                    email_bcc=None, 
#                    reply_to=self.get_email_from(cr, uid, [holiday.id], context=context), 
#                    attachments=None, 
#                    references = None, 
#                    object_id=None, 
#                    subtype='html', 
#                    subtype_alternative=None, 
#                    headers=None)
#                #Send mail to manager
#                self.send_email(cr, uid, message_manager, self.get_mail_server_id(cr, uid, context=context), context=context)
#        holiday_ids = self.search(cr, uid, [('type','=','remove'), ('state','=','validate1'), ('employee_id.parent_id2.is_all_final_leave', '=', True)])
#        holiday_recs = self.browse(cr, uid, holiday_ids, context=context)
#        for holiday in holiday_recs:
#            result_data = self.get_leave_data(cr, uid, [holiday.id], context=context)
#            result_emp_data = self.get_employee_data(cr, uid, [holiday.id], context=context)
#            remaining_leaves = self.get_remaining_leave(cr, uid, holiday.id, 
#                                 result_data[0], 
#                                 result_emp_data[3], 
#                                 context=context)
#            day = self._get_number_of_days(today, holiday.date_from)
#            if day == 3.0:
#                indirect_detail = self.get_indirect_manager_data(cr, uid, [holiday.id], context=context)
#                if holiday.employee_id.parent_id.user_id.id == uid:
#                    indirect_manager_body2 = self.get_indirect_manager_body2(cr, uid, holiday, 
#                                             indirect_detail[1], #Indirect manager name
#                                             self.get_manager_data(cr, uid, [holiday.id], context=context)[1], #manager name
#                                             result_emp_data[0], #employee name 
#                                             result_data[1], 
#                                             result_data[2], 
#                                             result_data[3], 
#                                             result_data[5], 
#                                             result_data[11], #Leave Request Date
#                                             result_data[12],
#                                             remaining_leaves = remaining_leaves, 
#                                             context=context)
#                    indirect_message_manager  = obj_mail_server.build_email(
#                        email_from=self.get_email_from(cr, uid, [holiday.id], context=context), 
#                        email_to=[indirect_detail[2]], 
#                        subject='Notification for leave', 
#                        body=indirect_manager_body2.get('note'), 
#                        body_alternative=indirect_manager_body2.get('note'), 
#                        email_cc=None, 
#                        email_bcc=None, 
#                        reply_to=self.get_email_from(cr, uid, [holiday.id], context=context), 
#                        attachments=None, 
#                        references = None, 
#                        object_id=None, 
#                        subtype='html', 
#                        subtype_alternative=None, 
#                        headers=None)  
#                    self.send_email(cr, uid, indirect_message_manager, self.get_mail_server_id(cr, uid, context=context), context=context)
#                
#                elif self.chk_group(cr, uid, holiday):
#                    #HR manager pre-approves
#                    indirect_manager_body = self.get_indirect_manager_body(cr, uid, holiday, 
#                                                                 indirect_detail[1], #Indirect manager name
#                                                                 result_data[9],#HR manager name
#                                                                 result_emp_data[0], #employee name 
#                                                                 result_data[1], 
#                                                                 result_data[2], 
#                                                                 result_data[3], 
#                                                                 result_data[5],
#                                                                 result_data[8], #HR manager signature
#                                                                 result_data[11], #Leave Request Date 
#                                                                 result_data[12],
#                                                                 remaining_leaves = remaining_leaves,
#                                                                 context=context)
#                    indirect_message_manager  = obj_mail_server.build_email(
#                                email_from=self.get_email_from(cr, uid, [holiday.id], context=context), 
#                                email_to=[indirect_detail[2]], 
#                                subject='Approval of leave', 
#                                body=indirect_manager_body.get('note'), 
#                                body_alternative=indirect_manager_body.get('note'), 
#                                email_cc=None, 
#                                email_bcc=None, 
#                                reply_to=self.get_email_from(cr, uid, [holiday.id], context=context), 
#                                attachments=None, 
#                                references = None, 
#                                object_id=None, 
#                                subtype='html', 
#                                subtype_alternative=None, 
#                                headers=None)  
#                    #Send mail to manager
#                    self.send_email(cr, uid, indirect_message_manager, self.get_mail_server_id(cr, uid, context=context), context=context)
#        return True
#
#    def get_check_leave_overlap(self, cr, uid, ids, context=None):
#        ''' 
#            This Function checks overlapping of date applied for leave
#            @return: Returns True if date overlaps otherwise returns false
#        '''
#        if context is None:
#            context = {}
#        
#        holiday_rec = self.browse(cr, uid, ids[0])
#        # Retrieve ids of hr.holidays records for employee_id of employee who has applied for leave. Record state must be <validate>
#        leave_ids = self.search(cr, uid, [('type','=','remove'), ('employee_id', '=',holiday_rec.employee_id.id),('id','<>',holiday_rec.id),('state','in',['draft', 'confirm', 'validate', 'validate1'])])
#        
#        # List to store already leave dates for which employee already applied  
#        approved_leave_date_list = [] 
#        # Get list of dates applied for leave 
#        applied_dates_list = self.get_date_from_range(cr, uid, ids, 
#                                         holiday_rec.date_from, 
#                                         holiday_rec.date_to, 
#                                         context=context)
#        applied_dates_list = [x.strftime('%Y-%m-%d') for x in applied_dates_list]
#        # Retrieve list of browse records
#        leave_recs = self.browse(cr, uid, leave_ids)
#        
#        # Create list of dates already applied for leave
#        for rec in leave_recs:
#            # Get list of dates from date_from and date_to of from <rec
#            leave_dates = self.get_date_from_range(cr, uid, ids, rec.date_from, rec.date_to, context=context)
#            # Fetch only date (By splitting date) from each date in <leave_dates> list and store it in <approved_leave_date_list> list if it does not exist
#            leave_dates = [x.strftime('%Y-%m-%d') for x in leave_dates]
#            
#            for dt in leave_dates:
#                if dt not in approved_leave_date_list:
#                    approved_leave_date_list += [dt]
#        if holiday_rec.leave_type in ['am', 'pm']:
#            leave_ids = self.search(cr, uid, [('type','=','remove'), ('date_from' ,'=', holiday_rec.date_from) , ('state','in',['draft', 'confirm', 'validate', 'validate1']), ('id','<>',holiday_rec.id), ('employee_id', '=',holiday_rec.employee_id.id), ('date_to' ,'=', holiday_rec.date_to)])
#            for leave in self.browse(cr, uid, leave_ids, context=context):
#                if leave.leave_type == holiday_rec.leave_type:
#                    return False
#        else:
#            # Check for each date of <applied_dates_list> that it exists in <approved_leave_date_list> list or not
#            for dt in applied_dates_list:
#                if dt in approved_leave_date_list:
#                    return False
#        return True
#
#    def get_check_leave_days(self, cr, uid, ids, context=None):
#        holiday_status_obj = self.pool.get('hr.holidays.status')
#        holiday_ids = holiday_status_obj.search(cr, uid, [('name','=','AL')], context=context)
#        today = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
#        year = datetime.datetime.strptime(today, DEFAULT_SERVER_DATE_FORMAT).year
#        start_date = str(year+1) + '-01-01'
#        end_date = str(year+1) + '-03-31'
#        for holiday in self.browse(cr, uid, ids, context=context):
#            if holiday.type == 'add' or holiday.state != 'draft':
#                continue
#            if holiday.date_from and holiday.date_to and holiday.holiday_status_id.name == 'AL':
#                if holiday.date_from.split(' ')[0] < start_date and holiday.date_to.split(' ')[0] < start_date:
#                    return True
#                if holiday.date_from.split(' ')[0] > end_date or holiday.date_to.split(' ')[0] > end_date:
#                    return False
#                leave_id1 = self.search(cr, uid, [('type','=','remove'),
#                                                 ('state', '!=', 'cancel'),
#                                                 ('employee_id', '=',holiday.employee_id.id),
#                                                 ('holiday_status_id','in',holiday_ids),
#                                                 ('date_from','>=',start_date),('date_to','<=',end_date)])
#                leave_id2 = self.search(cr, uid, [('type','=','remove'),
#                                                 ('state', '!=', 'cancel'),
#                                                 ('employee_id', '=',holiday.employee_id.id),
#                                                 ('holiday_status_id','in',holiday_ids),
#                                                 ('date_from','<=',end_date), ('date_to','>',end_date)])
#                leave_id3 = self.search(cr, uid, [('type','=','remove'),
#                                                 ('state', '!=', 'cancel'),
#                                                 ('employee_id', '=',holiday.employee_id.id),
#                                                 ('holiday_status_id','in',holiday_ids),
#                                                 ('date_from','<',start_date), ('date_to','>=',start_date)])
#                total_leave_day = 0
#                for leave in self.browse(cr, uid, leave_id1, context=context):
#                    total_leave_day += leave.number_of_days_temp
#                for leave in self.browse(cr, uid, leave_id2, context=context):
#                    total_leave_day += self._check_holiday_carryforward(cr, uid, leave.id, start_date, end_date)
#                for leave in self.browse(cr, uid, leave_id3, context=context):
#                    total_leave_day += self._check_holiday_carryforward(cr, uid, leave.id, start_date, end_date)
#                if total_leave_day > 5:
#                    return False
#        return True
#
#    def get_check_year_leave(self, cr, uid, ids, context=None):
#        for holiday in self.browse(cr, uid, ids, context=context):
#            if holiday.type == 'add'  or holiday.state != 'draft':
#                continue
#            from_fiscal_year_id = self.fetch_fiscalyear(cr, uid, holiday.date_from.split(' ')[0], context=context)
#            to_fiscal_year_id = self.fetch_fiscalyear(cr, uid, holiday.date_to.split(' ')[0], context=context)
#            if from_fiscal_year_id != to_fiscal_year_id:
#                return False
#        return True
#
#
#    _constraints = [
#        (get_check_leave_overlap, _('Please check the dates. You already have applied on one of the dates specified !'), ['date_from,date_to']),
#        (get_check_leave_days, _('You can only apply maximum of 5 days for the first 3months of the following year.'), ['date_from,date_to']),
#        (get_check_year_leave, _('Please split your leave applications.'), ['date_from,date_to']),
#    ]
#
#    def drop_const_if_exists(self, cr, constname):
#        cr.execute('SELECT conname FROM pg_constraint where conname = \'hr_holidays_date_check\'')
#        if cr.fetchall():
#            cr.execute('ALTER TABLE hr_holidays DROP CONSTRAINT hr_holidays_date_check')
#            cr.commit()
#        return True
#    def init(self, cr):
#        self.drop_const_if_exists(cr,'hr_holidays_date_check')
#        return True   
#    def get_date_from_range(self, cr, uid, ids, from_date, to_date, context=None):
#        '''
#            Returns list of dates from from_date tp to_date
#            @param from_date: Starting date for range
#            @param to_date: Ending date for range
#            @return : Returns list of dates from from_date to to_date  
#        '''
#        dates = []
#        if from_date and to_date:
#            dates = list(rrule.rrule(rrule.DAILY, 
#                             dtstart=parser.parse(from_date), 
#                             until=parser.parse(to_date)))
#        return dates 
#        
#    def _check_holiday_dates(self, cr, uid, date_from, date_to, holiday_status_id, leave_duration, context=None):
#        '''
#            Checks that there is a public holiday on date of leave
#        '''
#        if  not context:
#            context = {}
#        holiday_status_data = self.pool.get('hr.holidays.status').browse(cr, uid, holiday_status_id)
#        obj_public_holiday =  self.pool.get('hr.holiday.public')
#        holiday_date_list = [] 
#        week_end_days = 0
#        dates = self.get_date_from_range(cr, uid, [], 
#                             date_from, 
#                             date_to, 
#                             context=context)
#        public_holiday_ids = obj_public_holiday.search(cr, uid, [('state', '=', 'validated')], context=context)
#        # Checking date of leaves for public holidays
#        for public_holiday_record in obj_public_holiday.browse(cr, uid, public_holiday_ids, context=context):
#            for holidays in public_holiday_record.holiday_line_ids:
#                if parser.parse(holidays.holiday_date).isoweekday() in [6,7] and not holiday_status_data.weekend_calculation:
#                    continue
#                if parser.parse(holidays.holiday_date) in dates:
#                    holiday_date_list += [holidays.holiday_date]
#        if not holiday_status_data.weekend_calculation:
#            for item in dates:
#                if item.isoweekday() in [6,7]:
#                    week_end_days +=1
#        return len(dates) - (len(holiday_date_list) + week_end_days) 
#    
#    def notification_leave_information(self, cr, uid, ids=None, context = None):
#        obj_mail_server = self.pool.get('ir.mail_server')
#        emp_obj = self.pool.get('hr.employee')
#        mail_server_ids = obj_mail_server.search(cr, uid, [], context=context)
#        if not mail_server_ids:
#            raise osv.except_osv(_('Mail Error'), _('No mail outgoing mail server specified!'))
#        mail_server_record = obj_mail_server.browse(cr, uid, mail_server_ids[0])
#
#        work_email = []
#        emp_ids = emp_obj.search(cr, uid, [('is_daily_notificaiton_email_send', '=', True)])
#        for emp in emp_obj.browse(cr, uid, emp_ids, context=context):
#            if not emp.work_email:
#                if emp.user_id and emp.user_id.user_email and emp.user_id.user_email not in work_email:
#                    work_email.append(str(emp.user_id.user_email))
#            elif emp.work_email not in work_email:
#                work_email.append(str(emp.work_email))
#        if not work_email:
#            raise osv.except_osv(_('Warning'), _('Email must be configured in employess. which have notification is enable for Receiving email notifications of employees who are on leave !'))
#        hr_manager = ''
#        today = datetime.datetime.now()
#        #day_from = datetime.datetime.strptime(datetime.datetime.now(), DEFAULT_SERVER_DATE_FORMAT)
#        new_list_holidays = []
#        for day in range(0, 6):
#            date_calc = today+timedelta(days=day)
#            date_calc = date_calc.strftime(DEFAULT_SERVER_DATE_FORMAT)
#            holiday_ids = self.search(cr, uid, [('type','=','remove'),('state', 'in', ['validate']),('date_from' , '<=', date_calc + " 00:00:00"),('date_to','>=',date_calc  + " 00:00:00")], context=context)
#            for holiday in holiday_ids:
#                if holiday in new_list_holidays:
#                    continue
#                new_list_holidays.append(holiday)
#        for holiday in self.browse(cr, uid, new_list_holidays, context=context):
#            leave_type = tools.ustr(holiday.holiday_status_id.name2)
#            start_date = datetime.datetime.strptime(holiday.date_from,DEFAULT_SERVER_DATETIME_FORMAT)
#            end_date = datetime.datetime.strptime(holiday.date_to, DEFAULT_SERVER_DATETIME_FORMAT)
#            if holiday.leave_type == 'am':
#                leave_type += '(Half Day AM)'
#            elif holiday.leave_type == 'pm':
#                leave_type += '(Half Day PM)'
#            hr_manager += '<tr><td width="25%%">' + holiday.employee_id.name + '</td><td width="20%%">' + start_date.strftime('%d-%m-%Y') + '</td><td width="20%%">' + end_date.strftime('%d-%m-%Y') + '</td><td width="20%%">' + leave_type +'</td></tr>'
#        if not hr_manager:
#            return True
#        start_mail = """Hi,<br/><br/>These are the list of employees who are on leave this week.<br/><br/>
#        <table>
#         <tr><td width="25%%"> Employee Name </td><td width="20%%">Date From</td><td width="20%%">Date To</td><td width="20%%">Leave Type</td></tr>"""
#        final_hrmanager_body = start_mail + hr_manager + "</table><br/><br/>Thank You.<br/><br/>Prestige iServer <b>"+ cr.dbname +"</b>"
#        message_hrmanager  = obj_mail_server.build_email(
#            email_from=mail_server_record.smtp_user, 
#            email_to=work_email, 
#            subject='Notification : Employees who are on Leave this week.', 
#            body=final_hrmanager_body, 
#            body_alternative=final_hrmanager_body, 
#            email_cc=None, 
#            email_bcc=None, 
#            attachments=None, 
#            references = None, 
#            object_id=None, 
#            subtype='html', 
#            subtype_alternative=None, 
#            headers=None)
#        self.send_email(cr, uid, message_hrmanager, mail_server_id=mail_server_ids[0], context=context)
#        return True
#    
#    def notofication_leave_approval(self, cr, uid, context=None):
#        if datetime.datetime.now().weekday() not in [0]:
#            return False
#        holiday_ids = self.search(cr, uid, [('type','=','remove'), ('state', 'in', ['confirm', 'validate1'])], context=context)
#        if not holiday_ids:
#            return False
#        obj_mail_server = self.pool.get('ir.mail_server')
#        emp_obj = self.pool.get('hr.employee')
#        data_obj = self.pool.get('ir.model.data')
#        group_object = self.pool.get('res.groups')
#        mail_server_ids = obj_mail_server.search(cr, uid, [], context=context)
#        if not mail_server_ids:
#            raise osv.except_osv(_('Mail Error'), _('No mail outgoing mail server specified!'))
#        mail_server_record = obj_mail_server.browse(cr, uid, mail_server_ids[0])
#        result_data = data_obj._get_id(cr, uid, 'base', 'group_hr_manager')
#        model_data = data_obj.browse(cr, uid, result_data, context=context)
#        group_data = group_object.browse(cr, uid, model_data.res_id, context)
#        work_email = []
#        user_ids = [user.id for user in group_data.users]
#        emp_ids = emp_obj.search(cr, uid, [('user_id', 'in', user_ids)])
#        for emp in emp_obj.browse(cr, uid, emp_ids, context=context):
#            if not emp.is_pending_leave_notificaiton:
#                continue
#            if not emp.work_email:
#                if emp.user_id.user_email and emp.user_id.user_email not in work_email:
#                    work_email.append(str(user.user_email))
#                else:
#                    raise osv.except_osv(_('Warning'), _('Email must be configured in %s HR manager !') % (emp.name))
#            elif emp.work_email not in work_email:
#                work_email.append(str(emp.work_email))
#        hrmanager = ''
#        directmanager = {}
#        indirectmanager = {}
#        for holiday in self.browse(cr, uid, holiday_ids, context=context):
#            start_date = datetime.datetime.strptime(holiday.date_from, "%Y-%m-%d %H:%M:%S")
#            end_date = datetime.datetime.strptime(holiday.date_to, "%Y-%m-%d %H:%M:%S")
#            create_date = datetime.datetime.strptime(holiday.create_date, "%Y-%m-%d %H:%M:%S")
#            state_dict = {
#                          'draft': 'New',
#                          'confirm': 'Waiting Pre-Approval',
#                          'refuse': 'Refused',
#                          'validate1': 'Waiting Final Approval',
#                          'validate': 'Approved',
#                          'cancel': 'Cancelled',
#                    }
#            mail_content = '<tr><td width="25%%">' + holiday.employee_id.name + '</td><td width="20%%">' + state_dict.get(holiday.state) + '</td><td width="20%%">' + create_date.strftime('%d-%m-%Y') + '</td><td width="20%%">' + start_date.strftime('%d-%m-%Y') + '</td><td width="20%%">' + end_date.strftime('%d-%m-%Y') + '</td></tr>'
#            hrmanager += mail_content
#            if holiday.state == 'confirm' and holiday.employee_id and holiday.employee_id.parent_id and holiday.employee_id.parent_id.is_pending_leave_notificaiton:
#                direct_manager_mail = holiday.employee_id.parent_id and holiday.employee_id.parent_id.work_email or holiday.employee_id.parent_id.user_id.user_email or False
#                if direct_manager_mail not in work_email:
#                    if direct_manager_mail and direct_manager_mail in directmanager:
#                        directmanager[direct_manager_mail] = directmanager[direct_manager_mail] + mail_content
#                    elif direct_manager_mail:
#                        directmanager[direct_manager_mail] = mail_content
#            elif holiday.state == 'validate1' and holiday.employee_id and holiday.employee_id.parent_id2 and holiday.employee_id.parent_id2.is_pending_leave_notificaiton:
#                indirect_manager_mail = holiday.employee_id.parent_id2 and holiday.employee_id.parent_id2.work_email or holiday.employee_id.parent_id2.user_id.user_email or False
#                if indirect_manager_mail not in work_email:
#                    if indirect_manager_mail and indirect_manager_mail in indirectmanager:
#                        indirectmanager[indirect_manager_mail] = indirectmanager[indirect_manager_mail] + mail_content
#                    elif indirect_manager_mail:
#                        indirectmanager[indirect_manager_mail] = mail_content
#        start_mail = """Hi,<br/><br/>Below are the list of employees who have pending leave approval.<br/><br/>
#        <table>
#         <tr><td width="25%%"> Name Of Employee </td><td width="20%%">Status</td><td width="20%%">Date Applied</td><td width="20%%">Leave Start Date</td><td width="20%%">Leave End Date</td></tr>"""
#        final_hrmanager_body = start_mail + hrmanager + "</table><br/><br/>Thanks."
#        #Send mail to HR Manager
#        if work_email:
#            message_hrmanager  = obj_mail_server.build_email(
#                email_from=mail_server_record.smtp_user, 
#                email_to=work_email, 
#                subject='Notification For Leave Approval.', 
#                body=final_hrmanager_body, 
#                body_alternative=final_hrmanager_body, 
#                email_cc=None, 
#                email_bcc=None, 
#                attachments=None, 
#                references = None, 
#                object_id=None, 
#                subtype='html', 
#                subtype_alternative=None, 
#                headers=None)
#            self.send_email(cr, uid, message_hrmanager, mail_server_id=mail_server_ids[0], context=context)
#
#        #Send mail to Direct Manager
#        for key, val in directmanager.items():
#            final_direcmanager_body = start_mail + val + "</table><br/><br/>Thanks."
#            message_directmanager  = obj_mail_server.build_email(
#                email_from=mail_server_record.smtp_user, 
#                email_to=[key], 
#                subject='Notification For Leave Approval.', 
#                body=final_direcmanager_body, 
#                body_alternative=final_direcmanager_body, 
#                email_cc=None, 
#                email_bcc=None, 
#                attachments=None, 
#                references = None, 
#                object_id=None, 
#                subtype='html', 
#                subtype_alternative=None, 
#                headers=None)
#            self.send_email(cr, uid, message_directmanager, mail_server_id=mail_server_ids[0], context=context)
#
#        #Send mail to Indirect Manager
#        for key, val in indirectmanager.items():
#            final_indirecmanager_body = start_mail + val + "</table><br/><br/>Thanks."
#            message_indirectmanager  = obj_mail_server.build_email(
#                email_from=mail_server_record.smtp_user, 
#                email_to=[key], 
#                subject='Notification For Leave Approval.', 
#                body=final_indirecmanager_body, 
#                body_alternative=final_indirecmanager_body, 
#                email_cc=None, 
#                email_bcc=None, 
#                attachments=None, 
#                references = None, 
#                object_id=None, 
#                subtype='html', 
#                subtype_alternative=None, 
#                headers=None)
#            self.send_email(cr, uid, message_indirectmanager, mail_server_id=mail_server_ids[0], context=context)
#        return True
#
#    def create(self, cr, uid, vals, context=None):
#        if context is None:
#            context = {}
#        if vals.get('date_from'):
#            from_fiscal_year_id = self.fetch_fiscalyear(cr, uid, vals.get('date_from').split(' ')[0], context=context)
#            vals.update({'fiscal_year_id': from_fiscal_year_id})
#        holiday_id = super(hr_holidays, self).create(cr, uid, vals, context=context)
#        holiday_data = self.browse(cr, uid, holiday_id, context=context)
#        vals = self.onchange_date_from(cr, uid, [holiday_id], holiday_data.date_to, holiday_data.date_from, holiday_data.holiday_status_id.id, holiday_data.leave_type, context=context)
#        if vals and vals.get('value') and vals.get('value').get('number_of_days_temp'):
#            super(hr_holidays, self).write(cr, uid, [holiday_data.id], {'number_of_days_temp': vals.get('value').get('number_of_days_temp')}, context=context) 
#        if holiday_data.type == 'add':
#            mod_obj = self. pool.get('ir.model.data')
#            group_obj = self.pool.get('res.groups')
#            grp_result = mod_obj._get_id(cr, uid, 'base', 'group_hr_manager')
##            group_id = mod_obj.browse(cr, uid, grp_result, ['res_id']).res_id
#            group_id = mod_obj.read(cr, uid, grp_result, ['res_id'], context=context)['res_id']
#            group = group_obj.browse(cr, uid, group_id, context=context)
#            user_add = [user.id for user in group.users]
#            if uid not in user_add:
#                raise osv.except_osv(_('Validation Error'), _('You cannot create allocation request because you are not HR Manager!'))
#        return holiday_id
#
#    def write(self, cr, uid, ids, vals, context=None):
#        if not context:
#            context = {}
#        if not isinstance(ids, list):
#            ids = [ids]
#        mod_obj = self. pool.get('ir.model.data')
#        group_obj = self.pool.get('res.groups')
#        result = super(hr_holidays, self).write(cr, uid, ids, vals, context=context)
#
#        for holiday in self.browse(cr, uid, ids, context):
#            vals = self.onchange_date_from(cr, uid, [holiday.id], holiday.date_to, holiday.date_from, holiday.holiday_status_id.id, holiday.leave_type, context=context)
#            if vals and vals.get('value') and vals.get('value').get('number_of_days_temp'):
#                super(hr_holidays, self).write(cr, uid, [holiday.id], {'number_of_days_temp': vals.get('value').get('number_of_days_temp')}, context=context) 
#            if holiday.type == 'remove' and holiday.date_from:
#                from_fiscal_year_id = self.fetch_fiscalyear(cr, uid, holiday.date_from.split(' ')[0], context=context)
#                if from_fiscal_year_id != holiday.fiscal_year_id.id:
#                    self.write(cr, uid, [holiday.id], {'fiscal_year_id': from_fiscal_year_id})
#            if holiday.type == 'add':
#                grp_result = mod_obj._get_id(cr, uid, 'base', 'group_hr_manager')
##                group_id = mod_obj.browse(cr, uid, grp_result, ['res_id']).res_id
#                group_id = mod_obj.read(cr, uid, grp_result, ['res_id'], context=context)['res_id']
#                group = group_obj.browse(cr, uid, group_id, context=context)
#                user_add = [user.id for user in group.users]
#                if uid not in user_add:
#                    raise osv.except_osv(_('Validation Error'), _('You cannot create allocation request because you are not HR Manager!'))
#        return result
#
#    def _check_holiday_carryforward(self, cr, uid, holiday_id, start_date, end_date, context=None):
#        '''
#            Checks that there is a public holiday,Saturday and Sunday on date of leave
#        '''
#        obj_public_holiday =  self.pool.get('hr.holiday.public')
#        holiday_rec = self.browse(cr, uid, holiday_id)
#        dates = self.get_date_from_range(cr, uid, holiday_id, 
#                                         holiday_rec.date_from, 
#                                         holiday_rec.date_to, 
#                                         context=context)
#        dates = [x.strftime('%Y-%m-%d') for x in dates]
#
#        remove_date = []
#        for day in dates:
#            date = datetime.datetime.strptime(day,DEFAULT_SERVER_DATE_FORMAT).date()
#            if date.isoweekday() in [6,7]:
#                remove_date.append(day)
#        
#        for remov in remove_date:
#            if remov in dates:
#                dates.remove(remov)
#        
#        public_holiday_ids = obj_public_holiday.search(cr, uid, [('state', '=', 'validated')], context=context)
#        if public_holiday_ids:
#            for public_holiday_record in obj_public_holiday.browse(cr, uid, public_holiday_ids, context=context):
#                for holidays in public_holiday_record.holiday_line_ids:
#                    if holidays.holiday_date in dates:
#                        dates.remove(holidays.holiday_date)
#        no_of_day = 0.0
#        for day in dates:
#            if day >= start_date and day <= end_date:
#                no_of_day += 1
#        return no_of_day 
#
#    def assign_carry_forward_leave(self, cr, uid, ids=None, context=None):
#        '''
#        This method will be called by scheduler which will assign 
#        carry forward leave on end of the year i.e YYYY/12/31 23:59:59
#        '''
#        emp_obj = self.pool.get('hr.employee')
#        holiday_status_obj = self.pool.get('hr.holidays.status')
#        obj_mail_server = self.pool.get('ir.mail_server')
#        data_obj = self.pool.get('ir.model.data')
#        fiscal_obj = self.pool.get('account.fiscalyear')
#
#        today = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
#        year = datetime.datetime.strptime(today, DEFAULT_SERVER_DATE_FORMAT).year
#        next_year_date = str(year + 1) + '-01-01'
#        empl_ids = emp_obj.search(cr, uid, [('active','=', True)], context=context)
#        holiday_status_ids = holiday_status_obj.search(cr, uid, [('cry_frd_leave', '>', 0)], context=context)
#        fiscalyear_id = self.fetch_fiscalyear(cr, uid, next_year_date, context=context)
#
#        current_fiscalyear_id = self.fetch_fiscalyear(cr, uid, today, context=context)
#
#        fiscalyear_rec = fiscal_obj.browse(cr, uid, current_fiscalyear_id, context=context)
#        start_date = fiscalyear_rec.date_start
#        end_date = fiscalyear_rec.date_stop
#        for holiday in  holiday_status_obj.browse(cr, uid, holiday_status_ids, context=context):
#            for employee in emp_obj.browse(cr, uid, empl_ids, context):
#                if employee.user_id and employee.user_id.id == 1:
#                    continue 
#                add = 0.0
#                remove = 0.0
#                cr.execute("SELECT sum(number_of_days_temp) FROM hr_holidays where employee_id=%d and state='validate' and holiday_status_id = %d and type='add' and fiscal_year_id=%d" % (employee.id, holiday.id, current_fiscalyear_id))
#                all_datas = cr.fetchone()
#                if all_datas and all_datas[0]:
#                    add += all_datas[0]
#                cr.execute("SELECT sum(number_of_days_temp) FROM hr_holidays where employee_id=%d and state='validate' and holiday_status_id = %d and type='remove' and date_from >= '%s' and date_to <= '%s'" % (employee.id, holiday.id, start_date, end_date))
#                leave_datas = cr.fetchone()
#                if leave_datas and leave_datas[0]:
#                    remove += leave_datas[0]
#                cr.execute("SELECT id FROM hr_holidays where employee_id=%d and state='validate' and holiday_status_id = %d and type='remove' and date_from <= '%s' and date_to >= '%s'" % (employee.id, holiday.id, end_date, end_date))
#                leave_datas = cr.fetchall()
#                if leave_datas:
#                    for data in leave_datas:
#                        if data[0]:
#                            remove += self._check_holiday_carryforward(cr, uid, data[0], start_date, end_date)
#                final = add - remove
#                final = final > holiday.cry_frd_leave and holiday.cry_frd_leave or final
#                if final > 0.0:
#                    cleave_dict = {
#                        'name' : 'Default Carry Forward Leave Allocation',
#                        'employee_id': employee.id,
#                        'holiday_type' : 'employee',
#                        'holiday_status_id' : holiday.id,
#                        'number_of_days_temp' : final,
#                        'type' : 'add',
#                        'fiscal_year_id' : fiscalyear_id,
#                        'carry_forward' : True
#                        }
#                    self.create(cr, uid, cleave_dict)
#        mail_server_ids = obj_mail_server.search(cr, uid, [], context=context)
#        if not mail_server_ids:
#            raise osv.except_osv(_('Mail Error'), _('No mail outgoing mail server specified!'))
#        mail_server_record = obj_mail_server.browse(cr, uid, mail_server_ids[0])
#
#        result_data = data_obj._get_id(cr, uid, 'base', 'group_hr_manager')
#        model_data = data_obj.browse(cr, uid, result_data, context=context)
#        group_data = self.pool.get('res.groups').browse(cr, uid, model_data.res_id, context)
#        user_ids = [user.id for user in group_data.users]
#        work_email = []
#        emp_ids = emp_obj.search(cr, uid, [('user_id', 'in', user_ids)])
#        for emp in emp_obj.browse(cr, uid, emp_ids, context=context):
#            if not emp.work_email:
#                if emp.user_id.user_email and emp.user_id.user_email not in work_email:
#                    work_email.append(str(user.user_email))
#                else:
#                    raise osv.except_osv(_('Warning'), _('Email must be configured in %s HR manager !') % (emp.name))
#            elif emp.work_email not in work_email:
#                work_email.append(str(emp.work_email))
#        body = "Hi,<br/><br/>Prestige iServer <b> " + cr.dbname + "</b> has finished performing the Auto Allocation For <b>\
#" + str(year + 1) + "</b>.<br/><br/>Kindly login to Prestige iServer <b> " + cr.dbname + "</b> to confirm the leave allocations. \
#<br/><br/>Thank You,<br/><br/>Prestige iServer <b>" + cr.dbname + "</b>"
#        message_hrmanager = obj_mail_server.build_email(
#            email_from=mail_server_record.smtp_user,
#            email_to=work_email,
#            subject='Notification : Auto Allocation Complete for ' + str(year + 1),
#            body=body,
#            body_alternative=body,
#            email_cc=None,
#            email_bcc=None,
#            attachments=None,
#            references=None,
#            object_id=None,
#            subtype='html',
#            subtype_alternative=None,
#            headers=None)
#        self.send_email(cr, uid, message_hrmanager, mail_server_id=mail_server_ids[0], context=context)
#        return True
#
#    def assign_default_leave(self, cr, uid, ids=None, context=None):
#        '''
#        This method will be called by scheduler which will assign 
#        Annual leave at end of the year i.e YYYY/12/01 00:01:01
#        '''
#        emp_obj = self.pool.get('hr.employee')
#        holiday_status_obj = self.pool.get('hr.holidays.status')
#        
#        today = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
#        year = datetime.datetime.strptime(today, DEFAULT_SERVER_DATE_FORMAT).year
#        next_year_date = str(year + 1) + '-01-01'
#        fiscalyear_id = self.fetch_fiscalyear(cr, uid, next_year_date, context=context)
#        
#        holiday_status_ids = holiday_status_obj.search(cr, uid, [('default_leave_allocation', '>', 0)], context=context)
#        empl_ids = emp_obj.search(cr, uid, [('active','=', True)], context=context)
#        
#        for holiday in  holiday_status_obj.browse(cr, uid, holiday_status_ids, context=context):
#            for employee in emp_obj.browse(cr, uid, empl_ids, context):
#                if employee.user_id and employee.user_id.id == 1:
#                    continue 
#                leave_dict = {
#                    'name' : 'Assign Default Allocation.',
#                    'employee_id': employee.id,
#                    'holiday_type' : 'employee',
#                    'holiday_status_id' : holiday.id,
#                    'number_of_days_temp' : holiday.default_leave_allocation,
#                    'type' : 'add',
#                    'fiscal_year_id' : fiscalyear_id
#                }
#                self.create(cr, uid, leave_dict)
#        return True
#    
#    def reminder_to_hr_manager(self, cr, uid, id=None, context=None):
#        '''
#        This method will be called by scheduler on YYYY/01/07 00:01:01 
#        which will send reminder to HR manager for New Leaves which is not approved
#        '''
#        obj_mail_server = self.pool.get('ir.mail_server')
#        emp_obj = self.pool.get('hr.employee')
#        data_obj = self.pool.get('ir.model.data')
#        holiday_status_obj = self.pool.get('hr.holidays.status')
#        mail_server_ids = obj_mail_server.search(cr, uid, [], context=context)
#        if not mail_server_ids:
#            raise osv.except_osv(_('Mail Error'), _('No mail outgoing mail server specified!'))
#        mail_server_record = obj_mail_server.browse(cr, uid, mail_server_ids[0])
#
#        result_data = data_obj._get_id(cr, uid, 'base', 'group_hr_manager')
#        model_data = data_obj.browse(cr, uid, result_data, context=context)
#        group_data = self.pool.get('res.groups').browse(cr, uid, model_data.res_id, context)
#        user_ids = [user.id for user in group_data.users]
#        work_email = []
#        emp_ids = emp_obj.search(cr, uid, [('user_id', 'in', user_ids)])
#        for emp in emp_obj.browse(cr, uid, emp_ids, context=context):
#            if not emp.work_email:
#                if emp.user_id.user_email and emp.user_id.user_email not in work_email:
#                    work_email.append(str(user.user_email))
#                else:
#                    raise osv.except_osv(_('Warning'), _('Email must be configured in %s HR manager !') % (emp.name))
#            elif emp.work_email not in work_email:
#                work_email.append(str(emp.work_email))
#        hr_manager = ''
#        today = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
#        year = datetime.datetime.strptime(today, DEFAULT_SERVER_DATE_FORMAT).year
#        next_year_date = str(year + 1) + '-01-01'
#        current_fiscalyear_id = self.fetch_fiscalyear(cr, uid, next_year_date, context=context)
#        holiday_status_ids = holiday_status_obj.search(cr, uid, [('default_leave_allocation', '>', 0)], context=context)
#        holiday_ids = self.search(cr, uid, [('carry_forward','=',True),('type','=','add'),('state', 'in', ['draft']),('fiscal_year_id', '=',current_fiscalyear_id)], context=context)
#        holiday_ids += self.search(cr, uid, [('holiday_status_id','in',holiday_status_ids),('type','=','add'),('state', 'in', ['draft']),('fiscal_year_id', '=',current_fiscalyear_id)], context=context)
#        hr_data = {}
#        for holiday in self.browse(cr, uid, holiday_ids, context=context):
#            hr_name = holiday.employee_id.name + str(holiday.id)
#            hr_data.update({hr_name:{"name":holiday.employee_id.name, "status":holiday.holiday_status_id.name2,"day":holiday.number_of_days_temp}}) 
#        hr_data_sorted_keys = sorted(hr_data.keys())
#        for hr_value in hr_data_sorted_keys:
#            hr_manager += '<tr><td width="25%%">' + hr_data[hr_value].get("name") + '</td><td width="20%%">' + str(hr_data[hr_value].get("status")) +'</td><td width="20%%">' + str(hr_data[hr_value].get("day")) + '</td></tr>'
#        if not hr_manager:
#            return True
#        start_mail = """Hi,<br/><br/>This is a gentle reminder that Allocation Statuses have yet to be confirmed by you.<br/><br/>
#        <table>
#         <tr><td width="25%%"> Employee Name </td><td width="20%%">Allocation Type</td><td width="20%%">Number of Days</td></tr>"""
#        final_hrmanager_body = start_mail + hr_manager + "</table><br/><br/>Thank You.<br/><br/>Prestige iServer <b>"+ cr.dbname +"</b>"
#        message_hrmanager  = obj_mail_server.build_email(
#            email_from=mail_server_record.smtp_user, 
#            email_to=work_email, 
#            subject='Reminder : Allocation Statuses Have yet to be Confirmed', 
#            body=final_hrmanager_body, 
#            body_alternative=final_hrmanager_body, 
#            email_cc=None, 
#            email_bcc=None, 
#            attachments=None, 
#            references = None, 
#            object_id=None, 
#            subtype='html', 
#            subtype_alternative=None, 
#            headers=None)
#        self.send_email(cr, uid, message_hrmanager, mail_server_id=mail_server_ids[0], context=context)
#        return True
#
#    def check_holidays(self, cr, uid, ids, context=None):
#        fiscal_obj = self.pool.get('account.fiscalyear')
#        for holiday in self.browse(cr, uid, ids):
#            if holiday.holiday_type == 'employee' and holiday.type == 'remove':
#                if holiday.employee_id and not holiday.holiday_status_id.limit:
#                    from_fiscal_year_id = self.fetch_fiscalyear(cr, uid, holiday.date_from, context=context)
#                    fiscalyear_rec = fiscal_obj.browse(cr, uid, from_fiscal_year_id, context=context)
#                    start_date = str(fiscalyear_rec.date_start) + " 00:00:00"
#                    end_date = str(fiscalyear_rec.date_stop) + " 23:59:59"
#                    add = remove = 0.0
#                    cr.execute("SELECT sum(number_of_days_temp) FROM hr_holidays where employee_id=%d and state='validate' and holiday_status_id = %d and type='add' and fiscal_year_id=%d" % (holiday.employee_id.id, holiday.holiday_status_id.id, from_fiscal_year_id))
#                    all_datas = cr.fetchone()
#                    if all_datas and all_datas[0]:
#                        add += all_datas[0]
#                    cr.execute("SELECT sum(number_of_days_temp) FROM hr_holidays where employee_id=%d and state='validate' and holiday_status_id = %d and type='remove' and date_from >= '%s' and date_to <= '%s'" % (holiday.employee_id.id, holiday.holiday_status_id.id, start_date, end_date))
#                    leave_datas = cr.fetchone()
#                    if leave_datas and leave_datas[0]:
#                        remove += leave_datas[0]
#                    leaves_rest = add - remove
#                    if leaves_rest < holiday.number_of_days_temp:
#                        raise osv.except_osv(_('Warning!'),_('You cannot validate leaves for employee %s: too few remaining days (%s).') % (holiday.employee_id.name, leaves_rest))
#        return True

hr_holidays()

class employee_document(osv.osv):
    _name = 'employee.document'
    _rec_name = 'document'
    _description = 'Attachment'
    _columns = {
        'employee_doc_id': fields.many2one('hr.holidays', 'Holiday', invisible=True), 
        'document_attachment': fields.binary('Attachment Data'), 
        'document': fields.char("Documents", size=256)
    }
employee_document()

class employee_imegration(osv.osv):
   
    _name = 'employee.immigration'
    _description = 'Employee Immigration'
    _rec_name = 'documents'
    _columns = {
             'documents' : fields.char("Documents" , size=256), 
             'number': fields.char('Number', size=256), 
             'employee_id': fields.many2one('hr.employee', 'Employee Name'), 
             'exp_date' : fields.date('Expiry Date'), 
             'issue_date' : fields.date('Issue Date'), 
             'eligible_status': fields.char('Eligible Status' , size=256), 
             'issue_by':fields.many2one('res.country', 'Issue By'), 
             'eligible_review_date' : fields.date('Eligible Review Date'), 
             'comments':fields.text("Comments"), 
    }
    
employee_imegration()
        
class hr_employee(osv.osv):
    _inherit="hr.employee"

    def calculate_age(self, cr, uid, born):
        today = datetime.datetime.today()
        try: # raised when birth date is February 29 and the current year is not a leap year
            birthday = born.replace(year=today.year)
        except ValueError:
            birthday = born.replace(year=today.year, day=born.day-1)
        if birthday > today:
            return today.year - born.year - 1
        else:
            return today.year - born.year

    def compute_age(self, cr, uid, ids, field_name, field_value, arg, context=None):
        result = {}
        for records in self.browse(cr, uid, ids, context=context):
            years = 0
            if records.birthday:
                born = datetime.datetime.strptime(records.birthday,"%Y-%m-%d")
                born = born.replace(day=1)
                years = self.calculate_age(cr, uid, born)
            result[records.id] = years
        return result

    def _get_rem_days(self, cr, uid, ids, name, args, context=None):
        days_dict = {}
        for employee in self.browse(cr, uid, ids):
            if employee.last_date and employee.emp_status == 'in_notice':
                from_dt = datetime.datetime.strptime(employee.last_date, "%Y-%m-%d")
                today = datetime.datetime.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d")
                timedelta = from_dt - today
                diff_day = timedelta.days + float(timedelta.seconds) / 86400
                days_dict[employee.id] = diff_day > 0 and round(diff_day) or 0
        return days_dict
    
    def _compute_manager(self, cr, uid, ids, name, args, context=None):
        print "_compute_manager"
        result = {}
        mod_obj = self. pool.get('ir.model.data')
        grp_result = mod_obj._get_id(cr, uid, 'base', 'group_hr_manager')
#        group_id = mod_obj.browse(cr, uid, grp_result, context=context).res_id
        group_id = mod_obj.read(cr, uid, grp_result, ['res_id'], context=context)['res_id']
        group_obj = self.pool.get('res.groups')
        group = group_obj.browse(cr, uid, group_id, context=context)
        user_add = [user.id for user in group.users]
        
        allow_to_see_all_tabs = False
        #Procedure for HR dept manager matching HR dept of company config
        emp_obj = self.pool.get('hr.employee')
        emp_id = emp_obj.search(cr, uid, [('user_id', '=', uid)])
        if emp_id:
            emp_rec = emp_obj.browse(cr, uid, emp_id[0])
            cur_user = self.pool.get('res.users').browse(cr, uid, uid)
            if emp_rec.department_id and cur_user.company_id.department_id and emp_rec.department_id.id == cur_user.company_id.department_id.id:
                allow_to_see_all_tabs = True
            
        #Procedure for HR manager
        for employee in self.browse(cr, uid, ids, context):
#            result[employee.id] = False
#            if employee.user_id and employee.user_id.id in user_add:
#                result[employee.id] = True
            if not allow_to_see_all_tabs:
                result[employee.id] = False
                if uid in user_add:
                    result[employee.id] = True
            else:
                result[employee.id] = True
                
        return result

    def _get_month(self, cr, uid, ids, name, args, context=None):
        res = {}
        for emp in self.browse(cr, uid, ids, context=context):
            y, m, d = emp.birthday and emp.birthday.split('-') or [0, 0, 0]
            res[emp.id] = m
        return res
    
    def _get_date(self, cr, uid, ids, name, args, context=None):
        res = {}
        for emp in self.browse(cr, uid, ids, context=context):
            y, m, d = emp.birthday and emp.birthday.split('-') or [0, 0, 0]
            res[emp.id] = d
        return res

    def default_get(self, cr, uid, fields_list, context=None):
        res = super(hr_employee, self).default_get(cr, uid, fields_list, context)
        mod_obj = self. pool.get('ir.model.data')
        grp_result = mod_obj._get_id(cr, uid, 'base', 'group_hr_manager')
#        group_id = mod_obj.browse(cr, uid, grp_result, ['res_id']).res_id
#        group_obj = self.pool.get('res.groups')
#        group = group_obj.browse(cr, uid, group_id, context=context)
#        user_add = [user.id for user in group.users]
        #Procedure for HR manager
        
#        group_result = mod_obj.get_object(cr, uid, 'base', ['group_system', 'group_erp_manager'])
#        new_user_add = [user.id for user in group_result.users]
        
#        if uid in user_add:
#            res['hr_manager'] = True
#        else:
#            res['hr_manager'] = False
        
#        if uid not in new_user_add:
#            raise osv.except_osv(_('Warning'), _('Access Denied.'))
        
        return res

#    def _compute_age(self, cr, uid, ids, name, args, context=None):
#        res = {}
#        for emp in self.browse(cr, uid, ids, context=context):
#            age = 0.0
#            if emp.birthday:
#                age = (datetime.datetime.now() - datetime.datetime.strptime(emp.birthday, DEFAULT_SERVER_DATE_FORMAT)).days
#            res[emp.id] = age
#        return res

    def onchange_emp_active(self, cr, uid, ids, active):
        vals = {}
        if active:
            vals.update({'emp_status': 'active'})
        if not active:
            vals.update({'emp_status': 'inactive'})
        return {'value' : vals}

    def onchange_employee_status(self, cr, uid, ids, emp_status):
        if emp_status == 'inactive':
            return {'value' : {'active': False}}
        return {'value' : {'active': True}}

    _columns = {
        'job_id': fields.many2one('hr.job', 'Job', domain="[('state','=','open')]"),
        'country_id': fields.char('Nationality',size=256),
#        'children_ids':fields.one2many('applicant.children', 'employee_id', "Children's Information"), 
        'relative_ids':fields.one2many('applicant.relative', 'employee_id', "Parents,Brothers & Sisters (Dependent)"), 
#        'emr_name' : fields.char('Emergency Contact Name', size=64), 
#        'emr_relationship_id':fields.many2one('applicant.relationship','Emergency Relationship'), 
#        'emr_address':fields.char('Emergency Address', size=64), 
#        'emr_telephone':fields.char('Emergency Phone', size=16),
        'parent_id': fields.many2one('hr.employee', 'Direct Manager'),
        'parent_id2': fields.many2one('hr.employee', 'Indirect Manager'),
        'address_home_id' : fields.char('Home Address', size=255), 
        'employee_leave_ids' : fields.one2many('hr.holidays', 'employee_id', 'Leaves'), 
        'emp_status' : fields.selection([('probation', 'Probation'), ('active', 'Active'), ('in_notice', 'In notice Period'), ('terminated', 'Terminated'), ('inactive', 'Inactive'),('promoted','Promoted')], 'Employment Status'), 
        'join_date' : fields.date('Date Joined'), 
        'confirm_date' : fields.date('Date Confirmation'), 
        'history_ids':fields.one2many('employee.history', 'history_id', 'Job History'),
        'employment_history_ids' : fields.one2many('applicant.history', 'employee_id', 'Employement History'),
        'reason' : fields.text('Reason'), 
        'inact_date' : fields.datetime('Inactive Date'), 
        'passport_exp_date' : fields.date('Passport Expiry Date'), 
        'immigration_ids' : fields.one2many('employee.immigration', 'employee_id', 'Immigration'), 
        'parent_user_id':fields.related('parent_id', 'user_id', type="many2one", relation="res.users", string="Direct Manager User"), 
        'parent_user_id2':fields.related('parent_id2', 'user_id', type="many2one", relation="res.users", string="Indirect Manger User"), 
        'last_date' : fields.date('Last Date'), 
        'rem_days' : fields.function(_get_rem_days, type='integer', method=True, store=True, string = 'Remaining Days'), 
        'hr_manager': fields.function(_compute_manager, type="boolean", string='Hr Manager'), 
        'training_ids' : fields.one2many('employee.training', 'tr_id', 'Training'), 
        'birthday_month' : fields.function(_get_month, type='char', size=2, store=True), 
        'birthday_day' : fields.function(_get_date, type='char', size=2,store=True),
        'edu_ids' : fields.one2many('applicant.edu', 'employee_id', 'Education'),
        'age': fields.function(compute_age, type="integer", store=True, string='Age'), 
        'contact_num2' : fields.char('Contact:Mobile', size=16),
        'place_of_birth':fields.char('Place Of Birth', size=32),
        'issue_date':fields.date('Passport Issue Date'),
#        'race_id' : fields.many2one('applicant.race', "Race"), 
        'dialect' : fields.char('Dialect', size=32), 
#        'religion_id': fields.many2one('applicant.religion','Religion'), 
        'driving_licence':fields.char('Driving Licence:Class', size=16), 
        'car':fields.boolean('Do you own a car?'),
        'resume':fields.binary('Resume'),
        'national_service_ids' : fields.one2many('national.service', 'employee_id', 'National Service'),
        'comp_prog_knw':fields.char('Computer Programs Knowledge', size=64), 
        'typing' : fields.integer('Typing'), 
        'shorthand':fields.integer('Shorthand'), 
        'other_know':fields.char('Other Knowledge & Skills', size=64), 
        'course':fields.char('Courses Taken', size=64), 
        'language_ids' : fields.one2many('applicant.language', 'employee_id', 'Language Proficiency'),
        'physical_stability' : fields.boolean('Physical Stability (Yes)'),
        'physical' : fields.text('Physical Stability Information'),
        'court_b' :fields.boolean('Court (Yes)'),
        'court':fields.char('Court Information', size=256), 
        'dismissed_b':fields.boolean('Dismissed (Yes)'), 
        'dismiss':fields.char('Dismissed Information', size=256), 
        'bankrupt_b' : fields.boolean('Bankrupt (Yes)'),
        'bankrupt':fields.char('Bankrupt Information', size=256), 
        'about' : fields.text('About Yourself'),
        'reference_ids' : fields.one2many('applicant.ref', 'employee_id', 'References'), 
        'bankrupt_no': fields.boolean('Bankrupt (No)'),
        'dismissed_no': fields.boolean('Dismissed (No)'), 
        'court_no': fields.boolean('Court (No)'),
        'physical_stability_no': fields.boolean('Physical Disability (No)'),
        'bank_detail_ids' : fields.one2many('hr.bank.details', 'bank_emp_id','Bank Details'),
        'employee_type_id': fields.many2one('employee.id.type', 'Type Of ID'),
        'emp_country_id' : fields.many2one('res.country', 'Country'),
        'emp_state_id' : fields.many2one('res.country.state', 'State'),
        'emp_city_id' : fields.many2one('employee.city', 'City'),
        'is_daily_notificaiton_email_send': fields.boolean('Receiving email notifications of employees who are on leave?'),
        'is_pending_leave_notificaiton': fields.boolean('Receiving email notifications of Pending Leaves Notification Email?'),
        'is_all_final_leave': fields.boolean('Receiving email notifications of 2nd Reminder to Direct / Indirect Managers?')
    }
    
    _defaults = {
        'emp_status': 'active',
        'is_daily_notificaiton_email_send': True,
    }
    
    def onchange_health_yes(self, cr, uid, ids, physical_stability):
        
        if physical_stability == True:
            return {'value': {'physical_stability_no': False}}
        else:
            return {'value': {'physical_stability_no': True}}
   
    def onchange_health_no(self, cr, uid, ids, physical_stability_no):

        if physical_stability_no == True:
            return {'value': {'physical_stability': False}}
        else:
            return {'value': {'physical_stability': True}}
        
    def onchange_court_yes(self, cr, uid, ids, court_b):
        
        if court_b == True:
            return {'value': {'court_no': False}}
        else:
            return {'value': {'court_no': True}}
    
    def onchange_court_no(self, cr, uid, ids, court_no):
        
        if court_no == True:
            return {'value': {'court_b': False}}
        else:
            return {'value': {'court_b': True}}
        
    def onchange_dismissed_yes(self, cr, uid, ids, dismissed_b):
        
        if dismissed_b == True:
            return {'value': {'dismissed_no': False}}
        else:
            return {'value': {'dismissed_no': True}}
    
    def onchange_dismissed_no(self, cr, uid, ids, dismissed_no):
        
        if dismissed_no == True:
            return {'value': {'dismissed_b': False}}
        else:
            return {'value': {'dismissed_b': True}}
        
    def onchange_bankrupt_yes(self, cr, uid, ids, bankrupt_b):
        
        if bankrupt_b == True:
            return {'value': {'bankrupt_no': False}}
        else:
            return {'value': {'bankrupt_no': True}}
    
    def onchange_bankrupt_no(self, cr, uid, ids, bankrupt_no):
        
        if bankrupt_no == True:
            return {'value': {'bankrupt_b': False}}
        else:
            return {'value': {'bankrupt_b': True}}

    def copy(self, cr, uid, id, default={}, context=None):
        if context is None:
            context = {}
        default = default or {}
        default['employment_history_ids'] = []
        default['employee_leave_ids'] = []
        default['child_ids'] = []
        default['contract_ids'] = []
        return super(hr_employee, self).copy(cr, uid, id, default, context)

    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context = {}
        user_pool = self.pool.get('res.users')
        if vals.get('job_id','') or vals.get('emp_status','') or vals.get('join_date','') or vals.get('confirm_date',''):
            job_history_obj = self.pool.get('employee.history')
            for emp_rec in self.browse(cr, uid, ids, context=context):
                job_history_obj.create(cr, uid, {'job_id':  vals.get('job_id','') or emp_rec.job_id.id, 'history_id': emp_rec.id, 'user_id': uid, 'emp_status' : vals.get('emp_status',emp_rec.emp_status), 'join_date': vals.get('join_date',emp_rec.join_date), 'confirm_date': vals.get('confirm_date',emp_rec.confirm_date), 'cessation_date': vals.get('cessation_date', emp_rec.cessation_date)})
        
        if 'active' in vals:
            user_ids = []
            for employee in self.browse(cr, uid, ids, context):
                if employee.user_id:
                    user_ids.append(employee.user_id.id)
            if user_ids:
                user_pool.write(cr, uid, user_ids, {'active': vals.get('active')})
        return super(hr_employee, self).write(cr, uid, ids, vals, context=context)
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        employee_id = super(hr_employee, self).create(cr, uid, vals, context=context)
        job_history_obj = self.pool.get('employee.history')
        if vals.get('job_id','') or vals.get('emp_status','') or vals.get('join_date','') or vals.get('confirm_date',''):
            job_history_obj.create(cr, uid, {'job_id':  vals.get('job_id'), 'history_id': employee_id, 'user_id': uid, 'emp_status' : vals.get('emp_status','active'), 'join_date': vals.get('join_date',False), 'confirm_date': vals.get('confirm_date',False), 'cessation_date': vals.get('cessation_date',False)})
        
        active = vals.get('active', False)
        user_obj = self.pool.get('res.users')
        if vals.get('user_id') and not active:
            user_obj.write(cr, uid, [vals.get('user_id')], {'active' : active})
        return employee_id    
        
    def _check_employee_status(self, cr, uid, context=None):
        """
        This Function is call by scheduler.
        """
        emp_resign_str = 'Employee Name\t\tLast Date\n'
        obj_mail_server = self.pool.get('ir.mail_server')
        obj_mail_msg = self.pool.get('mail.message')

        data_obj = self.pool.get('ir.model.data')
        group_object = self.pool.get('res.groups')
        
        result_data = data_obj._get_id(cr, uid, 'base', 'group_hr_manager')
        model_data = data_obj.browse(cr, uid, result_data, context=context)
        group_data = group_object.browse(cr, uid, model_data.res_id, context)

        work_email = []
        user_ids = [user.id for user in group_data.users]
        emp_ids = self.search(cr, uid, [('user_id', 'in', user_ids)])
        for emp in self.browse(cr, uid, emp_ids, context=context):
#            manager_name += str(emp.name) + ", "
            if not emp.work_email:
                if emp.user_id.user_email:
                    work_email.append(str(user.user_email))
                else:
                    raise osv.except_osv(_('Warning'), _('Email must be configured in %s HR manager !') % (emp.name))
            else:
                work_email.append(str(emp.work_email))


        mail_server_ids = obj_mail_server.search(cr, uid, [], context=context)
        
        if not mail_server_ids:
            raise osv.except_osv(_('Mail Error'), _('No mail outgoing mail server specified!'))
        
#        company_data = self.pool.get('res.users').browse(cr, uid, uid, context).company_id
#        if not company_data.department_id:
#            raise osv.except_osv(_('Warning'), _('Department must be configured in user company !'))
#        if not company_data.department_id.manager_id:
#            raise osv.except_osv(_('Warning'), _('Manager must be configured in company department !'))
#        work_email = company_data.department_id.manager_id.work_email
#        if not work_email:
#            work_email = company_data.department_id.manager_id.user_id.user_email
#        if not work_email:
#            raise osv.except_osv(_('Warning'), _('Email must configured in department manager !'))

        mail_server_record = obj_mail_server.browse(cr, uid, mail_server_ids)[0]
        email_from = mail_server_record.smtp_user
    
        if not email_from:
            raise osv.except_osv(_('Mail Error'), _('No email specified in smtp server!'))    
        if not work_email:
            raise osv.except_osv(_('Mail Error'), _('No Hr Manger email found!'))
        

        employee_ids = self.search(cr, uid, [], context=context)
        emp_change_ids = []
        emp_resign_list = []
        self.write(cr, uid, employee_ids, {})
        current_date = datetime.datetime.now()
        for employee in self.browse(cr, uid, employee_ids, context=context):
            if employee.evaluation_date: 
#                evaluation_date = datetime.datetime.strptime(employee.evaluation_date, "%Y-%m-%d")
                evaluation_date = fields.datetime.context_timestamp(cr, uid, datetime.datetime.strptime( employee.evaluation_date, DEFAULT_SERVER_DATE_FORMAT), context)
                diff_days = (evaluation_date - current_date).days
                if diff_days == 30:
                    body =  'Hello,\n\n \
                            %s has an upcoming performance review on %s : \n\n \
                            Please conduct it by %s \n\n \
                            Thanks,' % (employee.name, evaluation_date.strftime("%d/%m/%Y"), evaluation_date.strftime("%d/%m/%Y"))
#                    obj_mail_msg.schedule_with_attach(cr, uid, 
#                        email_from, 
#                        email_to = work_email, 
#                        subject='Upcoming performance review date on %s.' % evaluation_date.strftime("%d/%m/%Y"), 
#                        body=tools.ustr(body) or '', 
#                        mail_server_id = mail_server_ids[0])
                    if work_email:
                        vals = {'state': 'outgoing',
                                'subject': 'Upcoming performance review date on %s.' % evaluation_date.strftime("%d/%m/%Y"), 
                                'body_html': '<pre>%s</pre>' % tools.ustr(body) or '', 
                                'email_to': work_email,
                                'email_from': email_from}
                        self.pool.get('mail.mail').create(cr, uid, vals, context=context)
            if employee.rem_days == 0 and employee.emp_status == "in_notice":
                emp_change_ids.append(employee.id)
            if employee.rem_days == 3 and employee.emp_status == "in_notice":
                emp_resign_list.append(employee.id)
                emp_resign_str += '%s\t\t%s\n'%(employee.name,employee.last_date)

        if emp_resign_list:
            body =  'Hello,\n\n Below is the list of employees who are resigning this month \n\n %s\n\n Thanks,' % (emp_resign_str)
    
#            obj_mail_msg.schedule_with_attach(cr, uid, 
#                email_from, 
#                email_to = work_email, 
#                subject='Notification for Terminate with in 3 days', 
#                body=tools.ustr(body) or '', 
#                mail_server_id = mail_server_ids[0])
            if work_email:
                vals = {'state': 'outgoing',
                        'subject': 'Notification for Terminate with in 3 days', 
                        'body_html': '<pre>%s</pre>' % tools.ustr(body) or '', 
                        'email_to': work_email,
                        'email_from': email_from}
                self.pool.get('mail.mail').create(cr, uid, vals, context=context)
        if emp_change_ids:
            self.write(cr, uid, emp_change_ids, {'emp_status':'terminated'})
        return True

    def _check_employee_doc_expiry(self, cr, uid, context=None):
        """
        This Function is call by scheduler.
        """
        doc_emp_list= 'Employee Name\t\tDocument\t\tExpiry Date\n'
        doc_exp_list = []
        obj_mail_server = self.pool.get('ir.mail_server')
        obj_mail_msg = self.pool.get('mail.message')
        
        mail_server_ids = obj_mail_server.search(cr, uid, [], context=context)
        
        if not mail_server_ids:
            raise osv.except_osv(_('Mail Error'), _('No mail outgoing mail server specified!'))

        data_obj = self.pool.get('ir.model.data')
        group_object = self.pool.get('res.groups')
        
        result_data = data_obj._get_id(cr, uid, 'base', 'group_hr_manager')
        model_data = data_obj.browse(cr, uid, result_data, context=context)
        group_data = group_object.browse(cr, uid, model_data.res_id, context)

        work_email = []
        user_ids = [user.id for user in group_data.users]
        emp_ids = self.search(cr, uid, [('user_id', 'in', user_ids)])
        for emp in self.browse(cr, uid, emp_ids, context=context):
#            manager_name += str(emp.name) + ", "
            if not emp.work_email:
                if emp.user_id.user_email:
                    work_email.append(str(user.user_email))
                else:
                    raise osv.except_osv(_('Warning'), _('Email must be configured in %s HR manager !') % (emp.name))
            else:
                work_email.append(str(emp.work_email))

#        company_data = self.pool.get('res.users').browse(cr, uid, uid, context).company_id
#        if not company_data.department_id:
#            raise osv.except_osv(_('Warning'), _('Department must be configured in user company !'))
#        if not company_data.department_id.manager_id:
#            raise osv.except_osv(_('Warning'), _('Manager must be configured in company department !'))
#        work_email = company_data.department_id.manager_id.work_email
#        if not work_email:
#            work_email = company_data.department_id.manager_id.user_id.user_email
#        if not work_email:
#            raise osv.except_osv(_('Warning'), _('Email must configured in department manager !'))

        mail_server_record = obj_mail_server.browse(cr, uid, mail_server_ids)[0]
        email_from = mail_server_record.smtp_user

        if not email_from:
            raise osv.except_osv(_('Mail Error'), _('No email specified in smtp server!'))    
        if not work_email:
            raise osv.except_osv(_('Mail Error'), _('No Hr Manager found!'))

        employee_ids = self.search(cr, uid, [], context=context)
        current_date = datetime.datetime.now()
        for employee in self.browse(cr, uid, employee_ids, context=context):
                        
            for document in employee.immigration_ids:
                doc_expiry_date = datetime.datetime.strptime(document.exp_date, '%Y-%m-%d')
                doc_name = document.documents
                rem_day =  (doc_expiry_date - current_date).days
                if rem_day > 113 or rem_day <= 123:
                    doc_exp_list.append(employee.id)
                    doc_emp_list += '%s\t\t%s\t\t%s\n'%(employee.name,doc_name,doc_expiry_date)

        if doc_exp_list:
            exp_doc_mail_body = 'Hello,\n\n Below is the list of names which documents are going to expire within this month\
                                \n\n\n%s\n\nThanks,'%(doc_emp_list)
#            obj_mail_msg.schedule_with_attach(cr, uid, 
#                        email_from, 
#                        email_to = work_email, 
#                        subject='Notification for Document Expiry Date',
#                        body=tools.ustr(exp_doc_mail_body) or '', 
#                        mail_server_id = mail_server_ids[0])
            if work_email:
                vals = {'state': 'outgoing',
                        'subject': 'Notification for Document Expiry Date', 
                        'body_html': '<pre>%s</pre>' % tools.ustr(exp_doc_mail_body) or '', 
                        'email_to': work_email,
                        'email_from': email_from}
                self.pool.get('mail.mail').create(cr, uid, vals, context=context)
        return True

    def search(self,cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        res = super(hr_employee,self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)

        if context.get('no_past_date_bday',False):
            new_args = [('birthday_month','=',time.strftime('%m')),('birthday_day','>=',time.strftime('%d'))]
            new_res = super(hr_employee,self).search(cr, uid, new_args, offset=offset, limit=limit, order=order, context=context, count=count)
            res += new_res

        return res
            
hr_employee()

class employee_city(osv.osv):
    _name = "employee.city"
    _columns = {
        'name' : fields.char('City Name', size = 64, required=True),
        'code' : fields.char('City Code', size = 64, required=True),
        'state_id' : fields.many2one('res.country.state', 'State', required=True)
    }
    
employee_city()


class hr_bank_details(osv.osv):
    _name = 'hr.bank.details'
    _rec_name = 'bank_name'
    _columns = {
        'bank_name': fields.char('Name Of Bank', size=256),
        'bank_code': fields.char('Bank Code', size=256),
        'bank_ac_no': fields.char('Bank Account Number', size=256),
        'bank_emp_id' : fields.many2one('hr.employee', 'Bank Detail'),
        'branch_code': fields.char('Branch Code', size=256),
        'beneficiary_name': fields.char('Beneficiary Name', size=256)
    }
hr_bank_details()


class employee_id_type(osv.osv):
    _name = 'employee.id.type'
    _columns = {
        'name': fields.char("EP", size=256, required=True),
        's_pass': fields.selection([('skilled', 'Skilled'), ('unskilled', 'Un Skilled')], 'S Pass'), 
        'wp': fields.selection([('skilled', 'Skilled'), ('unskilled', 'Un Skilled')], 'Wp'),
    }
employee_id_type()

class employee_training(osv.osv):
    _name = 'employee.training'
    _description = 'Employee Training'
    _rec_name = 'tr_title'
    _columns={
        'tr_id' : fields.many2one('hr.employee', 'Employee'), 
        'tr_title' : fields.char('Title of TRAINING/WORKSHOP', size=64, required= True), 
        'tr_institution' : fields.char('Institution', size=64), 
        'tr_date' : fields.date('Date'), 
        'comments' : fields.text('Comments'), 
        'training_attachment': fields.binary('Attachment Data'), 
    }

employee_training()

class employee_history(osv.osv):
    _name = 'employee.history'
    _description = 'Employee History'
    _rec_name = 'history_id'
    _columns = {
        'history_id' : fields.many2one('hr.employee', 'History'), 
        'job_id' : fields.many2one('hr.job', 'Job title', readonly=True, store=True), 
        'date_changed' :fields.datetime('Date Changed', readonly=True), 
        'user_id': fields.many2one('res.users', "Changed By", readonly=True), 
        'emp_status' : fields.selection([('probation', 'Probation'), ('active', 'Active'), ('in_notice', 'In notice Period'), ('terminated', 'Terminated'), ('inactive', 'Inactive')], 'Employment Status'), 
        'join_date' : fields.date('Joined Date'), 
        'confirm_date' : fields.date('Date of Confirmation'),
        'cessation_date': fields.date('Cessation Date')
        }
    
    _defaults = {
        'date_changed' : lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'), 
    }
employee_history()

class employee_news(osv.osv):
    _name='employee.news'
    _description = 'Employee News'
    _rec_name = 'subject'
    _columns={
        'subject' : fields.char('Subject', size=255, required=True), 
        'description' : fields.text('Description'), 
        'date' :fields.datetime('Date'),
        'department_ids' : fields.many2many('hr.department','department_news_rel','parent_id','news_id','Manager News'),
        'user_ids' : fields.many2many('res.users','user_news_rel','id','user_ids','User News'),
        }
    
    def news_update(self, cr, uid, ids, context = None):
        emp_obj = self.pool.get("hr.employee")
        obj_mail_server = self.pool.get('ir.mail_server')
        mail_server_ids = obj_mail_server.search(cr, uid, [], context=context)
        if not mail_server_ids:
            raise osv.except_osv(_('Mail Error'), _('No mail outgoing mail server specified!'))
        mail_server_record = obj_mail_server.browse(cr, uid, mail_server_ids[0])
        email_list = []

        for news in self.browse(cr, uid, ids, context):
            if news.department_ids:
                dep_name_ids = [department.id for department in news.department_ids]
                emp_ids = emp_obj.search(cr, uid,[('department_id','in',dep_name_ids)], context=context )
                for emp_rec in emp_obj.browse(cr, uid, emp_ids, context=context):
                    if emp_rec.work_email:
                        email_list.append(emp_rec.work_email)
                    elif emp_rec.user_id and emp_rec.user_id.user_email:
                        email_list.append(emp_rec.user_id.user_email)
                if not email_list:
                    raise osv.except_osv(_('Department ' ), _("Email not found in employee !"))
            elif news.user_ids:
                for user in news.user_ids:
                    if user.user_email:
                        email_list.append(user.user_email)
                if not email_list:
                    raise osv.except_osv(_('User Email Configuration ' ), _("Email not found in users !"))
            else:
                emp_ids = emp_obj.search(cr, uid, [], context = context)
                for employee in emp_obj.browse(cr, uid,emp_ids, context=context ):
                    if employee.work_email:
                        email_list.append(employee.work_email)
                    elif employee.user_id and employee.user_id.user_email:
                        email_list.append(employee.user_id.user_email)
                if not email_list:
                    raise osv.except_osv(_('Mail Error' ), _("Email not defined!")) 
            rec_date = fields.datetime.context_timestamp(cr, uid, datetime.datetime.strptime(news.date, DEFAULT_SERVER_DATETIME_FORMAT), context)
            body =  'Hi,<br/><br/> \
                This is a news update from <b>%s</b> posted at %s<br/><br/>\
                %s <br/><br/>\
                Thank you.' % (cr.dbname, rec_date.strftime('%d-%m-%Y %H:%M:%S'), news.description )
            message  = obj_mail_server.build_email(
                            email_from=mail_server_record.smtp_user, 
                            email_to=email_list, 
                            subject='Notification for news update.', 
                            body=body, 
                            body_alternative=body, 
                            email_cc=None, 
                            email_bcc=None, 
                            reply_to=mail_server_record.smtp_user, 
                            attachments=None, 
                            references = None, 
                            object_id=None, 
                            subtype='html', #It can be plain or html
                            subtype_alternative=None, 
                            headers=None)
            
            obj_mail_server.send_email(cr, uid, message=message, mail_server_id=mail_server_ids[0], context=context)
            
        return True
        
employee_news()

class hr_applicant_extended(osv.osv):
    
    _inherit = 'hr_evaluation.evaluation'
    
    def button_done(self, cr, uid, ids, context=None):
        '''
            This methods overrides button_plan_in_progress() method of hr_evaluation.evaluation
            class and sends email to employee when appraisal is done  
        '''      
        #Getting object of ir.mail_server
        obj_mail_server = self.pool.get('ir.mail_server')

        for apprisal in self.browse(cr, uid, ids, context):
            
            #Getting ids of all the servers
            mail_server_ids = obj_mail_server.search(cr, uid, [], context=context)
    
            if not mail_server_ids:
                raise osv.except_osv(_('Mail Error'), _('No outgoing mail server specified!'))
            
            #Getting browse records for mail_server_ids  
            mail_server_record = obj_mail_server.browse(cr, uid, mail_server_ids[0])
            email_to = apprisal.employee_id.work_email or apprisal.employee_id.user_id.user_email or False

            if not email_to:
                raise osv.except_osv(_('Mail Error'), _('No email address specified!'))
            
            #Formation of email body
            body =  'Resp %s,<br/><br/> \
                     Your appraisal has been done.<br/><br/> \
                                ' % (apprisal.employee_id.user_id.name or 'Sir/Madam')
    
            #Check if at least one outgoing smtp mail server is specified            
            message  = obj_mail_server.build_email(
                email_from=mail_server_record.smtp_user, 
                email_to=[email_to], 
                subject='Notification for appraisal', 
                body=body, 
                body_alternative=body, 
                email_cc=None, 
                email_bcc=None, 
                reply_to=mail_server_record.smtp_user, 
                attachments=None, 
                references = None, 
                object_id=None, 
                subtype='html', #It can be plain or html
                subtype_alternative=None, 
                headers=None)
            obj_mail_server.send_email(cr, uid, message=message, mail_server_id=mail_server_ids[0], context=context)

        return super(hr_applicant_extended, self).button_done(cr, uid, ids, context=context)    

    def button_plan_in_progress(self, cr, uid, ids, context=None):
        '''
            This methods overrides button_plan_in_progress() method of hr_evaluation.evaluation
            class and sends email when appraisal is started  
        '''   
        #Getting object of ir.mail_server
        obj_mail_server = self.pool.get('ir.mail_server')

        for apprisal in self.browse(cr, uid, ids, context):
            
            #Getting ids of all the servers
            mail_server_ids = obj_mail_server.search(cr, uid, [], context=context)
    
            if not mail_server_ids:
                raise osv.except_osv(_('Mail Error'), _('No mail outgoing mail server specified!'))
            
            #Getting browse records for mail_server_ids  
            mail_server_record = obj_mail_server.browse(cr, uid, mail_server_ids[0])
            email_to = apprisal.employee_id.work_email or apprisal.employee_id.user_id.user_email or False

            if not email_to:
                raise osv.except_osv(_('Mail Error'), _('No email address specified!'))
            
            #Formation of email body
            body =  'Resp %s,<br/><br/> \
                     Your appraisal has been submitted.<br/><br/> \
                                ' % (apprisal.employee_id.user_id.name or 'Sir/Madam')
    
            #Check if at least one outgoing smtp mail server is specified            
            message  = obj_mail_server.build_email(
                email_from=mail_server_record.smtp_user, 
                email_to=[email_to], 
                subject='Notification for submission of appraisal', 
                body=body, 
                body_alternative=body, 
                email_cc=None, 
                email_bcc=None, 
                reply_to=mail_server_record.smtp_user, 
                attachments=None, 
                references = None, 
                object_id=None, 
                subtype='html', #It can be plain or html
                subtype_alternative=None, 
                headers=None)
            obj_mail_server.send_email(cr, uid, message=message, mail_server_id=mail_server_ids[0], context=context)

        return super(hr_applicant_extended, self).button_plan_in_progress(cr, uid, ids, context=context)

hr_applicant_extended()


class act_window(osv.osv):
    _inherit = 'ir.actions.act_window'

    _columns = {
        'domain': fields.text('Domain Value', help="Optional domain filtering of the destination data, as a Python expression"), 
    }

act_window()

class res_company(osv.osv):
    _inherit = 'res.company'
    
    _columns = {
            'department_id' : fields.many2one('hr.department', 'Department'),
    }
    
res_company()

class hr_holidays_status(osv.osv):
    _inherit = "hr.holidays.status"
     
    _columns = {
        'cry_frd_leave' : fields.float('Carry Forward Leave', help='Maximum number of Leaves to be carry forwarded!'), 
        'name2' : fields.char('Leave Type',size=64),
        'default_leave_allocation' : fields.integer('Default Annual Leave Allocation'),
        'weekend_calculation': fields.boolean('Weekend Calculation')
    }
    
    _defaults = {
        'default_leave_allocation' : 0.0
        }
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        ids = []
##   ids = self.search(cr, user, [('name2', '=', name)]+ args, limit=limit, context=context)
        ids += self.search(cr, user, [('name2', operator, name)]+ args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = [(r['id'],(r['name2'] or '')) for r in self.read(cr, uid, ids, ['name2'], context)]
        return res
hr_holidays_status()

class hr_holiday_public(osv.osv):
    
    '''
        This class stores a list of public holidays
    '''
    _name = 'hr.holiday.public'
    
    _description = 'Public holidays'
    
    _columns = {
        'name':fields.char('Holiday', size=128, required=True, help='Name of holiday list'), 
        'holiday_line_ids':fields.one2many('hr.holiday.lines', 'holiday_id', 'Holidays'), 
        'email_body' : fields.text('Email Body'), 
        'state':fields.selection([('draft', 'Draft'), 
                                  ('confirmed', 'Confirmed'), 
                                  ('validated', 'Validated'), 
                                  ('refused', 'Refused'), 
                                  ('cancelled', 'Cancelled'), 
                                  ], 'State', select=True, readonly=True)    
    }
    
    _defaults = {
        'state':'draft', 
        'email_body':'Dear Manager,\n\nKindly find attached pdf document containing Public Holiday List.\n\nThanks,'
    }
    
    def setstate_draft(self, cr, uid, ids, context=None):
        '''
            Sets state to draft
        '''
        self.write(cr, uid, ids , {'state':'draft'})
        return True
    
    def setstate_cancel(self, cr, uid, ids, context=None):
        '''
            Sets state to cancelled
        '''
        self.write(cr, uid, ids, {'state': 'cancelled'})
        return True
    
#    def send_email(self, cr, uid, message, mail_server_id, context):
#        '''
#           This method sends mail using information given in message 
#        '''
#        obj_mail_server = self.pool.get('ir.mail_server')
#        obj_mail_server.send_email(cr, uid, message=message, mail_server_id=mail_server_id, context=context)

#    def get_mail_server_id(self, cr, uid, context=None):
#        '''
#            Fetches the id of first mail server.
#            If no smtp server is found then False will be returned
#            @return: Returns id of first configured outgoing server or False 
#        '''
#        obj_mail_server = self.pool.get('ir.mail_server')
#        mail_server_ids = obj_mail_server.search(cr, uid, [], context=context)
#        if not mail_server_ids:
#            return False
#        else:
#            return mail_server_ids[0]
#   
#    def get_from(self, cr, uid, ids, context=None):
#        '''
#            Returns the value of smtp_user (Username ) field 
#            of first smtp server
#            @return: smtp_user field of first smtp server configured on success or False 
#        '''
#        mail_server_id = self.get_mail_server_id(cr, uid, context=context)
#        email_record = self.pool.get('ir.mail_server').browse(cr, uid, mail_server_id)
#        return email_record.smtp_user or False    

#    def send_email(self, cr, uid, message, mail_server_id, context):
#        '''
#           Sends mail using information given in message 
#        '''
#        obj_mail_server = self.pool.get('ir.mail_server')
#        obj_mail_server.send_email(cr, uid, message=message, mail_server_id=mail_server_id, context=context)

    def setstate_validate(self, cr, uid, ids, context=None):
        '''
            Sets state to validated
        '''
#        file_name = 'HolidayList' # Name of report file
#        attachments = [] # To store attachments
#        email_body = '' # To store email body text specified for each employee
#        
#        self_rec = self.browse(cr, uid, ids)[0]
#        
#        # Getting id of first outgoing mail server
#        mail_server_id = self.get_mail_server_id(cr, uid, context=context)
#        mail_obj = self.pool.get("ir.mail_server")
#        #Check for mail server 
#        if not mail_server_id:
#            raise osv.except_osv(_('Mail Error'), _('No mail server found!'))
#
#        #Check for mail body 
#        if not self_rec.email_body:
#            raise osv.except_osv(_('Mail Error'), _('Please specify email body!'))
#
#        data_obj = self.pool.get('ir.model.data')
#        group_object = self.pool.get('res.groups')
#        emp_obj = self.pool.get('hr.employee')
#        result_data = data_obj._get_id(cr, uid, 'base', 'group_hr_manager')
#        model_data = data_obj.browse(cr, uid, result_data, context=context)
#        group_data = group_object.browse(cr, uid, model_data.res_id, context)
#
#        work_email = []
#        user_ids = [user.id for user in group_data.users]
#        if 1 in user_ids:
#            user_ids.remove(1)
#        emp_ids = emp_obj.search(cr, uid, [('user_id', 'in', user_ids)])
#        for emp in emp_obj.browse(cr, uid, emp_ids, context=context):
##            manager_name += str(emp.name) + ", "
#            if not emp.work_email:
#                if emp.user_id.user_email and emp.user_id.user_email not in work_email:
#                    work_email.append(str(user.user_email))
#                else:
#                    raise osv.except_osv(_('Warning'), _('Email must be configured in %s HR manager !') % (emp.name))
#            elif emp.work_email not in work_email:
#                work_email.append(str(emp.work_email))
#
#        if not work_email:
#            raise osv.except_osv(_('Mail Error'), _('No Hr Manager found!'))
#        # Create report. Returns tuple (True,filename) if successfuly executed otherwise (False,exception)
#        report = self.create_report(cr, uid, ids, 'report.public.holidays', file_name)
#        if report[0]:
#            # Inserting file_data into dictionary with file_name as a key
#            attachments.append((file_name, report[1]))
#            email_body = self_rec.email_body
#            specific_email_body = email_body 
#
#            message_app  = mail_obj.build_email(
#                email_from=self.get_from(cr, uid, ids, context=context), 
#                email_to= work_email, 
#                subject='Holiday list',
#                body=specific_email_body or '', 
#                body_alternative=specific_email_body or '',
#                email_cc=None, 
#                email_bcc=None, 
#                reply_to=None, 
#                attachments=attachments, 
#                references = None, 
#                object_id=None, 
#                subtype='html', 
#                subtype_alternative=None, 
#                headers=None)
#            mail_obj.send_email(cr, uid, message=message_app, mail_server_id=mail_server_id, context=context)

        self.write(cr, uid, ids, {'state': 'validated'})
        return True
    
    def setstate_refuse(self, cr, uid, ids, context=None):
        '''
            Sets state to refused
        '''
        self.write(cr, uid, ids, {'state': 'refused'})
        return True
    
    def setstate_confirm(self, cr, uid, ids, context=None):
        '''
            Sets state to confirmed
        '''
        self.write(cr, uid, ids, {'state': 'confirmed'})
        return True
    
#    def create_report(self, cr, uid, res_ids, report_name=False, file_name=False):
#        '''
#            Creates report from report_name that contains records of res_ids 
#            using netsvc service and saves in report directory of module as file_name
#            
#            @param res_ids : List of record ids
#            @param report_name : Report name defined in .py file of report
#            @param file_name : Name of temporary file to store data   
#            @return: On success returns tuple (True,filename) otherwise tuple (False,execeotion)
#        '''
#        if not report_name or not res_ids:
#            return (False, Exception('Report name and Resources ids are required !'))
#        try:
#            service = netsvc.LocalService(report_name);
#            (result, format) = service.create(cr, uid, res_ids, {}, {})
#        except Exception, e:
#            return (False, str(e))
#        return (True, result)

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state <> 'draft':
                raise osv.except_osv(_('Warning!'),_('You cannot delete a public holiday which is not in draft state !'))
        return super(hr_holiday_public, self).unlink(cr, uid, ids, context)
    
hr_holiday_public()

class hr_holiday_lines(osv.osv):
    '''
       This model stores holiday lines
    '''
    _name = 'hr.holiday.lines'
    
    _description = 'Holiday Lines'
    
    _columns = {
        'holiday_date':fields.date('Date', help='Holiday date', required=True), 
        'name':fields.char('Reason', size=128, help='Reason for holiday'), 
        'day':fields.char('Day', size=16, help='Day'), 
        'holiday_id':fields.many2one('hr.holiday.public', 'Holiday List', help='Holiday list')
    }

    def init(self, cr):
        cr.execute("SELECT conname FROM pg_constraint where conname = 'hr_holiday_lines_date_uniq'")
        if cr.fetchall():
            cr.execute('ALTER TABLE hr_holiday_lines DROP CONSTRAINT hr_holiday_lines_date_uniq')
            cr.commit()
        return True

    def onchange_holiday_date(self, cr, uid, ids, holiday_date, context=None):
        '''
            This methods returns name of day of holiday_date  
        '''
        if holiday_date:
            daylist = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            parsed_date = parser.parse(holiday_date)
            day = parsed_date.weekday()
            return {'value': {'day' : daylist[day]}}
        else:
            return {'value': {}}

        
hr_holiday_lines()

class res_users(osv.osv):
    _inherit = 'res.users'

    def create(self, cr, uid, data, context=None):
        if context is None:
            context = {}
        context['noshortcut'] = True
        user_id = super(res_users, self).create(cr, uid, data, context=context)
        self.check_user_access(cr, uid, [user_id], context)
        data_obj = self.pool.get('ir.model.data')
        try:
            data_id = data_obj._get_id(cr, uid, 'crm', 'ir_ui_view_sc_calendar0')
            view_id  = data_obj.browse(cr, uid, data_id, context=context).res_id
            self.pool.get('ir.ui.view_sc').copy(cr, uid, view_id, default = {
                                        'user_id': user_id}, context=context)
        except:
            # Tolerate a missing shortcut. See product/product.py for similar code.
            logging.getLogger('orm').debug('Skipped meetings shortcut for user "%s"', data.get('name','<new'))
        return user_id

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        result = super(res_users, self).write(cr, uid, ids, vals, context=context)
        if type(ids) in [int, long]:
            ids = [ids]
        self.check_user_access(cr, uid, ids, context)
        return result

    def check_user_access(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        group_result = mod_obj.get_object(cr, uid, 'base', 'group_erp_manager')
        new_user_add = [user.id for user in group_result.users]
        group_result = mod_obj.get_object(cr, uid, 'base', 'group_system')
        system_user_add = [user.id for user in group_result.users]
        for user in self.browse(cr, uid, ids, context):
            if uid == 1:
                continue
            if user.id in new_user_add or user.id in system_user_add:
                raise osv.except_osv(_('Access Error'), _('You cannot give administrator access rights !'))
        return True

res_users()

class ir_cron(osv.osv):
    
    _inherit = 'ir.cron'
    
    _columns = {
                'name': fields.char('Name', size=256, required=True),
    }
ir_cron()
