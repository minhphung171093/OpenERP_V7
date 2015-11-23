# -*- coding: utf-8 -*-

from osv import osv, fields
from tools.translate import _
import base64
import xlwt
from cStringIO import StringIO
from datetime import datetime
import tools
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

LEAVE_STATE = {'draft':'New', 'confirm':'Waiting Pre-Approval','refuse':'Refused', 'validate1':'Waiting Final Approval', 'validate':'Approved', 'cancel':'Cancelled'}
LEAVE_REQUEST = {'remove': 'Leave Request', 'add':'Allocation Request'}
PAYSLIP_STATE ={"draft":"Draft", "verify":"Waiting", "done":"Done", "cancel":"Rejected"}

class export_employee_data_record_xls(osv.osv_memory):

    _name = 'export.employee.data.record.xls'

    _columns = {
        "file":fields.binary("Click On Save As Button To Download File", readonly=True),
        "name":fields.char("Name" , size=32, readonly=True, invisible=True)
    }

    def _get_employee_summary_data(self, cr, uid, context=None):
        if context is None:
            context = {}
        employee_obj = self.pool.get('hr.employee')
        payslip_obj = self.pool.get('hr.payslip')
        contract_obj = self.pool.get('hr.contract')
        workbook = xlwt.Workbook()
        font = xlwt.Font()
        font.bold = True
        user_lang = self.pool.get('res.users').browse(cr, uid, uid, context).context_lang
        lang_obj = self.pool.get('res.lang')
        lang_ids = lang_obj.search(cr, uid, [('code', '=', user_lang)])
        date_format = "%d/%m/%Y"
        month_year_format = "%m/%Y"
        date_time_format = "%d/%m/%Y %H:%M:%S"
        if lang_ids:
            lang_data = lang_obj.browse(cr, uid, lang_ids[0])
            date_format = lang_data.date_format
            date_time_format = lang_data.date_format + " " + lang_data.time_format
        header = xlwt.easyxf('font: name Arial, bold on, height 200; align: wrap off;')
        style = xlwt.easyxf('align: wrap off')
        number_format = xlwt.easyxf('align: wrap off')
        number_format.num_format_str = '#,##0.00'
        personal_information = False
        emp_note_row = emp_payslip_row = emp_contract_row = emp_edu_info_row = emp_edu_skill_row = emp_lang_row = emp_extra_info_row = emp_ref_row = emp_notification_row = emp_info_row = emp_per_info_row = emp_appraisal_row = emp_family_row = emp_emphistory_row = emp_nat_ser_row = emp_bank_row = emp_leave_row = emp_training_row = emp_job_row = emp_immigration_row = emp_categories_row = 0
        emp_info_col = emp_per_info_col = emp_appraisal_col = emp_notification_col = emp_extra_info_col = 0
        if context and context.get('datas') and context.get('datas')['employee_ids']:
            if context.get('datas')['user_id'] or context.get('datas')['active'] or context.get('datas')['department'] or context.get('datas')['direct_manager'] or context.get('datas')['indirect_manager']:
                emp_info_ws = workbook.add_sheet('Employee Information')
                emp_info_ws.col(emp_info_col).width = 6000
                emp_info_ws.write(emp_info_row, emp_info_col, 'Employee Name', header)
                if context.get('datas')['user_id']:
                    emp_info_col += 1
                    emp_info_ws.col(emp_info_col).width = 5000
                    emp_info_ws.write(emp_info_row, emp_info_col, 'User', header)
                if context.get('datas')['active']:
                    emp_info_col += 1
                    emp_info_ws.col(emp_info_col).width = 5000
                    emp_info_ws.write(emp_info_row, emp_info_col, 'Active', header)
                if context.get('datas')['department']:
                    emp_info_col += 1
                    emp_info_ws.col(emp_info_col).width = 5000
                    emp_info_ws.write(emp_info_row, emp_info_col, 'Department', header)
                if context.get('datas')['direct_manager']:
                    emp_info_col += 1
                    emp_info_ws.col(emp_info_col).width = 5000
                    emp_info_ws.write(emp_info_row, emp_info_col, 'Direct Manager', header)
                if context.get('datas')['indirect_manager']:
                    emp_info_col += 1
                    emp_info_ws.col(emp_info_col).width = 5000
                    emp_info_ws.write(emp_info_row, emp_info_col, 'Indirect Manager', header)

            #Employee Personal Information
            if context.get('datas').get('identification_id') or context.get('datas').get('passport_id') or context.get('datas').get('otherid') \
                or context.get('datas').get('gender') or context.get('datas').get('martial') or context.get('datas').get('nationality') \
                or context.get('datas').get('dob') or context.get('datas').get('pob') or context.get('datas').get('age') \
                or context.get('datas').get('home_address') or context.get('datas').get('country_id') or context.get('datas').get('state_id') \
                or context.get('datas').get('city_id') or context.get('datas').get('phone') or context.get('datas').get('mobile') \
                or context.get('datas').get('email') or context.get('datas').get('race_id') or context.get('datas').get('dialet') \
                or context.get('datas').get('religion') or context.get('datas').get('driving_licence') or context.get('datas').get('own_car') \
                or context.get('datas').get('emp_type_id'):
                personal_information = True
            if personal_information:
                emp_personal_info_ws = workbook.add_sheet('Personal Information')
                emp_per_info_col = 0
                emp_personal_info_ws.col(emp_per_info_col).width = 6000
                emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Employee Name : ', header)
                if context.get('datas')['identification_id']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Identification', header)
                if context.get('datas')['passport_id']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Passport No', header)
                if context.get('datas')['otherid']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Other ID', header)
                
                if context.get('datas')['gender']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Gender', header)
                if context.get('datas')['martial']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Marital Status', header)
                if context.get('datas')['nationality']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Nationality', header)
                if context.get('datas')['dob']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Birthdate', header)
                if context.get('datas')['pob']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Place Of Birth', header)
                if context.get('datas')['age']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Age', header)
                
                if context.get('datas')['home_address']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Home Address', header)
                if context.get('datas')['country_id']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Country', header)
                if context.get('datas')['state_id']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'State', header)
                if context.get('datas')['city_id']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'City', header)
                if context.get('datas')['phone']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Phome', header)
                if context.get('datas')['mobile']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Mobile', header)
                if context.get('datas')['email']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Email', header)
                
                if context.get('datas')['race_id']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Race', header)
                if context.get('datas')['dialet']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Dialet', header)
                if context.get('datas')['religion']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Religion', header)
                if context.get('datas')['driving_licence']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Driving Licence', header)
                if context.get('datas')['own_car']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Car', header)
                if context.get('datas')['emp_type_id']:
                    emp_per_info_col += 1
                    emp_personal_info_ws.col(emp_per_info_col).width = 6000
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, 'Type Of ID', header)
            
            #Evaluation
            if context.get('datas')['evaluation_plan_id'] or context.get('datas')['evaluation_date']:
                emp_appraisal_ws = workbook.add_sheet('Appraisal')
                emp_appraisal_ws.col(emp_appraisal_col).width = 6000
                emp_appraisal_ws.write(emp_appraisal_row, emp_appraisal_col, 'Employee Name', header)
                if context.get('datas')['evaluation_plan_id']:
                    emp_appraisal_col += 1
                    emp_appraisal_ws.col(emp_appraisal_col).width = 6000
                    emp_appraisal_ws.write(emp_appraisal_row, emp_appraisal_col, 'Appraisal', header)
                if context.get('datas')['evaluation_date']:
                    emp_appraisal_col += 1
                    emp_appraisal_ws.col(emp_appraisal_col).width = 6000
                    emp_appraisal_ws.write(emp_appraisal_row, emp_appraisal_col, 'Next Appraisal Date', header)
            
            #Notification
            if context.get('datas')['emp_noty_leave'] or context.get('datas')['pending_levae_noty'] or context.get('datas')['receive_mail_manager']:
                emp_notification_ws = workbook.add_sheet('Notification')
                emp_notification_ws.col(emp_notification_col).width = 6000
                emp_notification_ws.write(emp_notification_row, emp_notification_col, 'Employee Name', header)
                if context.get('datas')['emp_noty_leave']:
                    emp_notification_col += 1
                    emp_notification_ws.col(emp_notification_col).width = 15000
                    emp_notification_ws.write(emp_notification_row, emp_notification_col, 'Receiving email notifications of employees who are on leave? :', header)
                if context.get('datas')['pending_levae_noty']:
                    emp_notification_col += 1
                    emp_notification_ws.col(emp_notification_col).width = 15000
                    emp_notification_ws.write(emp_notification_row, emp_notification_col, 'Receiving email notifications of Pending Leaves Notification Email? :', header)
                if context.get('datas')['receive_mail_manager']:
                    emp_notification_col += 1
                    emp_notification_ws.col(emp_notification_col).width = 15000
                    emp_notification_ws.write(emp_notification_row, emp_notification_col, 'Receiving email notifications of 2nd Reminder to Direct / Indirect Managers? :', header)
            
            #Extra Information
            if context.get('datas')['health_condition'] or context.get('datas')['bankrupt'] or context.get('datas')['suspend_employment'] or context.get('datas')['court_law'] or context.get('datas')['about']:
                emp_extra_info_ws = workbook.add_sheet('Extra Information')
                emp_extra_info_ws.col(emp_extra_info_col).width = 6000
                emp_extra_info_ws.write(emp_extra_info_row, emp_extra_info_col, 'Employee Name', header)
                if context.get('datas')['health_condition']:
                    emp_extra_info_col += 1
                    emp_extra_info_ws.col(emp_extra_info_col).width = 15000
                    emp_extra_info_ws.write(emp_extra_info_row, emp_extra_info_col, 'Are you suffering from any physical disability or illness that requires you to be medication for a prolonged period? ', header)
                if context.get('datas')['bankrupt']:
                    emp_extra_info_col += 1
                    emp_extra_info_ws.col(emp_extra_info_col).width = 15000
                    emp_extra_info_ws.write(emp_extra_info_row, emp_extra_info_col, 'Have you ever been declared a bankrupt?', header)
                if context.get('datas')['suspend_employment']:
                    emp_extra_info_col += 1
                    emp_extra_info_ws.col(emp_extra_info_col).width = 15000
                    emp_extra_info_ws.write(emp_extra_info_row, emp_extra_info_col, 'Have you ever been dismissed or suspended from employement? ', header)
                if context.get('datas')['court_law']:
                    emp_extra_info_col += 1
                    emp_extra_info_ws.col(emp_extra_info_col).width = 15000
                    emp_extra_info_ws.write(emp_extra_info_row, emp_extra_info_col, 'Have you ever been convicted in a court of law in any country? ', header)
                if context.get('datas')['about']:
                    emp_extra_info_col += 1
                    emp_extra_info_ws.col(emp_extra_info_col).width = 15000
                    emp_extra_info_ws.write(emp_extra_info_row, emp_extra_info_col, 'About Yourself', header)
            if context.get('datas')['reference_ids']:
                emp_ref_ws = workbook.add_sheet('References')
                emp_ref_ws.col(0).width = 6000
                emp_ref_ws.write(emp_ref_row, 0, 'Employee Name', header)
                emp_ref_ws.col(1).width = 6000
                emp_ref_ws.write(emp_ref_row, 1, 'Name', header)
                emp_ref_ws.col(2).width = 6000
                emp_ref_ws.write(emp_ref_row, 2, 'Relationship', header)
                emp_ref_ws.col(3).width = 6000
                emp_ref_ws.write(emp_ref_row, 3, 'Contact No', header)
                emp_ref_ws.col(4).width = 6000
                emp_ref_ws.write(emp_ref_row, 4, 'Years Known', header)
            #Educational Information
            if context.get('datas')['edu_ids'] :
                emp_edu_info_ws = workbook.add_sheet('Educational Information')
                emp_edu_info_ws.col(0).width = 6000
                emp_edu_info_ws.write(emp_edu_info_row, 0, 'Employee Name', header)
                emp_edu_info_ws.col(1).width = 6000
                emp_edu_info_ws.write(emp_edu_info_row, 1, 'Education Level', header)
                emp_edu_info_ws.col(2).width = 6000
                emp_edu_info_ws.write(emp_edu_info_row, 2, 'Name & Country Of School', header)
                emp_edu_info_ws.col(3).width = 6000
                emp_edu_info_ws.write(emp_edu_info_row, 3, 'Period', header)
                emp_edu_info_ws.col(4).width = 6000
                emp_edu_info_ws.write(emp_edu_info_row, 4, 'Certificate Obtained', header)
            if context.get('datas')['language_ids']:
                emp_lang_ws = workbook.add_sheet('Language Proficiency')
                emp_lang_ws.col(0).width = 6000
                emp_lang_ws.write(emp_lang_row, 0, 'Employee Name', header)
                emp_lang_ws.col(1).width = 6000
                emp_lang_ws.write(emp_lang_row, 1, 'Language', header)
                emp_lang_ws.col(2).width = 6000
                emp_lang_ws.write(emp_lang_row, 2, 'Spoken', header)
                emp_lang_ws.col(3).width = 6000
                emp_lang_ws.write(emp_lang_row, 3, 'Written', header)
            if context.get('datas')['com_prog_know'] or context.get('datas')['shorthand'] or context.get('datas')['courses'] or context.get('datas')['typing'] or context.get('datas')['other_know']:
                emp_edu_skill_ws = workbook.add_sheet('Computer Knowledge and Skills')
                emp_edu_info_col = 0
                emp_edu_skill_ws.col(emp_edu_info_col).width = 6000
                emp_edu_skill_ws.write(emp_edu_skill_row, emp_edu_info_col, 'Employee Name', header)
                if context.get('datas')['com_prog_know']:
                    emp_edu_info_col += 1
                    emp_edu_skill_ws.col(emp_edu_info_col).width = 6000
                    emp_edu_skill_ws.write(emp_edu_skill_row, emp_edu_info_col, 'Computer Program Knowledge ', header)
                if context.get('datas')['shorthand']:
                    emp_edu_info_col += 1
                    emp_edu_skill_ws.col(emp_edu_info_col).width = 6000
                    emp_edu_skill_ws.write(emp_edu_skill_row, emp_edu_info_col, 'Shorthand', header)
                if context.get('datas')['courses']:
                    emp_edu_info_col += 1
                    emp_edu_skill_ws.col(emp_edu_info_col).width = 6000
                    emp_edu_skill_ws.write(emp_edu_skill_row, emp_edu_info_col, 'Courses ', header)
                if context.get('datas')['typing']:
                    emp_edu_info_col += 1
                    emp_edu_skill_ws.col(emp_edu_info_col).width = 6000
                    emp_edu_skill_ws.write(emp_edu_skill_row, emp_edu_info_col, 'Typing', header)
                if context.get('datas')['other_know']:
                    emp_edu_info_col += 1
                    emp_edu_skill_ws.col(emp_edu_info_col).width = 6000
                    emp_edu_skill_ws.write(emp_edu_skill_row, emp_edu_info_col, 'Other Knowledge & Skills', header)
            
            if context.get('datas')['family_ids']:
                emp_family_ws = workbook.add_sheet('Family Particulars')
                emp_family_ws.col(0).width = 6000
                emp_family_ws.col(1).width = 6000
                emp_family_ws.col(2).width = 6000
                emp_family_ws.col(3).width = 6000
                emp_family_ws.col(4).width = 6000
                emp_family_ws.col(5).width = 6000
                emp_family_ws.col(6).width = 6000
                emp_family_ws.col(7).width = 6000
                emp_family_ws.write(emp_family_row, 0, 'Employee Name', header)
                emp_family_ws.write(emp_family_row, 1, 'Name', header)
                emp_family_ws.write(emp_family_row, 2, 'Relationship', header)
                emp_family_ws.write(emp_family_row, 3, 'Date Of Birth', header)
                emp_family_ws.write(emp_family_row, 4, 'Occupation', header)
                emp_family_ws.write(emp_family_row, 5, 'Address', header)
                emp_family_ws.write(emp_family_row, 6, 'Contact', header)
                emp_family_ws.write(emp_family_row, 7, 'Phone', header)
            
            if context.get('datas')['employment_history_ids']:
                emp_emphistory_ws = workbook.add_sheet('Employment History')
                emp_emphistory_ws.col(0).width = 6000
                emp_emphistory_ws.col(1).width = 6000
                emp_emphistory_ws.col(2).width = 6000
                emp_emphistory_ws.col(3).width = 6000
                emp_emphistory_ws.col(4).width = 6000
                emp_emphistory_ws.col(5).width = 6000
                emp_emphistory_ws.col(6).width = 15000
                emp_emphistory_ws.col(7).width = 15000
                emp_emphistory_ws.col(8).width = 15000
                emp_emphistory_ws.write(emp_emphistory_row, 0, 'Employee Name', header)
                emp_emphistory_ws.write(emp_emphistory_row, 1, 'Current/Last Company', header)
                emp_emphistory_ws.write(emp_emphistory_row, 2, 'From Date', header)
                emp_emphistory_ws.write(emp_emphistory_row, 3, 'End Date', header)
                emp_emphistory_ws.write(emp_emphistory_row, 4, 'Basic Salary', header)
                emp_emphistory_ws.write(emp_emphistory_row, 5, 'Last Drawn', header)
                emp_emphistory_ws.write(emp_emphistory_row, 6, 'Designation', header)
                emp_emphistory_ws.write(emp_emphistory_row, 7, 'Job Responsibility', header)
                emp_emphistory_ws.write(emp_emphistory_row, 8, 'Reason For Leaving', header)
            
            if context.get('datas')['job_title'] or context.get('datas')['emp_status'] \
                or context.get('datas')['join_date'] \
                or context.get('datas')['confirm_date'] \
                or context.get('datas')['date_changed'] \
                or context.get('datas')['changed_by'] \
                or context.get('datas')['date_confirm_month']:
                
                emp_job_ws = workbook.add_sheet('Job')
                emp_job_col = 0
                emp_job_ws.col(emp_job_col).width = 6000
                emp_job_ws.write(emp_job_row, emp_job_col, 'Employee Name', header)
                if context.get('datas')['job_title']:
                    emp_job_col += 1
                    emp_job_ws.col(emp_job_col).width = 6000
                    emp_job_ws.write(emp_job_row, emp_job_col, 'Job Title', header)
                if context.get('datas')['emp_status']:
                    emp_job_col += 1
                    emp_job_ws.col(emp_job_col).width = 6000
                    emp_job_ws.write(emp_job_row, emp_job_col, 'Employment Status', header)
                if context.get('datas')['join_date']:
                    emp_job_col += 1
                    emp_job_ws.col(emp_job_col).width = 6000
                    emp_job_ws.write(emp_job_row, emp_job_col, 'Join Date', header)
                if context.get('datas')['confirm_date']:
                    emp_job_col += 1
                    emp_job_ws.col(emp_job_col).width = 6000
                    emp_job_ws.write(emp_job_row, emp_job_col, 'Date Confirmation', header)
                if context.get('datas')['date_changed']:
                    emp_job_col += 1
                    emp_job_ws.col(emp_job_col).width = 6000
                    emp_job_ws.write(emp_job_row, emp_job_col, 'Date Changed', header)
                if context.get('datas')['changed_by']:
                    emp_job_col += 1
                    emp_job_ws.col(emp_job_col).width = 6000
                    emp_job_ws.write(emp_job_row, emp_job_col, 'Changed By', header)
                if context.get('datas')['date_confirm_month']:
                    emp_job_col += 1
                    emp_job_ws.col(emp_job_col).width = 6000
                    emp_job_ws.write(emp_job_row, emp_job_col, 'Date Confirmation Month', header)
            
            if context.get('datas')['category_ids']:
                emp_categories_ws = workbook.add_sheet('Categories')
                emp_categories_ws.col(0).width = 6000
                emp_categories_ws.col(1).width = 6000
                emp_categories_ws.col(2).width = 6000
                emp_categories_ws.write(emp_categories_row, 0, 'Employee Name', header)
                emp_categories_ws.write(emp_categories_row, 1, 'Category', header)
                emp_categories_ws.write(emp_categories_row, 2, 'Parent Category', header)
            
            #Immigration
            if context.get('datas')['immigration_ids']:
                emp_immigration_ws = workbook.add_sheet('Immigration')
                emp_immigration_ws.col(0).width = 6000
                emp_immigration_ws.col(1).width = 6000
                emp_immigration_ws.col(2).width = 6000
                emp_immigration_ws.col(3).width = 6000
                emp_immigration_ws.col(4).width = 6000
                emp_immigration_ws.col(5).width = 6000
                emp_immigration_ws.col(6).width = 6000
                emp_immigration_ws.col(7).width = 6000
                emp_immigration_ws.col(8).width = 6000
                emp_immigration_ws.write(emp_immigration_row, 0, 'Employee Name', header)
                emp_immigration_ws.write(emp_immigration_row, 1, 'Document', header)
                emp_immigration_ws.write(emp_immigration_row, 2, 'Number', header)
                emp_immigration_ws.write(emp_immigration_row, 3, 'Issue Date', header)
                emp_immigration_ws.write(emp_immigration_row, 4, 'Expiry Date', header)
                emp_immigration_ws.write(emp_immigration_row, 5, 'Eligible Status', header)
                emp_immigration_ws.write(emp_immigration_row, 6, 'Eligible Review Date', header)
                emp_immigration_ws.write(emp_immigration_row, 7, 'Issue By', header)
                emp_immigration_ws.write(emp_immigration_row, 8, 'Comment', header)
            
            #Trainig Workshop
            if context.get('datas')['tarining_ids']:
                emp_training_ws = workbook.add_sheet('Training Workshop')
                emp_training_ws.col(0).width = 6000
                emp_training_ws.col(1).width = 6000
                emp_training_ws.col(2).width = 6000
                emp_training_ws.col(3).width = 6000
                emp_training_ws.col(4).width = 15000
                emp_training_ws.write(emp_training_row, 0, 'Employee Name', header)
                emp_training_ws.write(emp_training_row, 1, 'Training Workshop', header)
                emp_training_ws.write(emp_training_row, 2, 'Institution', header)
                emp_training_ws.write(emp_training_row, 3, 'Date', header)
                emp_training_ws.write(emp_training_row, 4, 'Comment', header)
            
            #Leave History
            if context.get('datas')['emp_leave_ids']:
                emp_leave_ws = workbook.add_sheet('Leave History')
                emp_leave_ws.col(0).width = 6000
                emp_leave_ws.col(1).width = 9000
                emp_leave_ws.col(2).width = 3000
                emp_leave_ws.col(3).width = 6000
                emp_leave_ws.col(4).width = 6000
                emp_leave_ws.col(5).width = 6000
                emp_leave_ws.col(6).width = 6000
                emp_leave_ws.write(emp_leave_row, 0, 'Employee Name', header)
                emp_leave_ws.write(emp_leave_row, 1, 'Description', header)
                emp_leave_ws.write(emp_leave_row, 2, 'Year', header)
                emp_leave_ws.write(emp_leave_row, 3, 'Start Date', header)
                emp_leave_ws.write(emp_leave_row, 4, 'End Date', header)
                emp_leave_ws.write(emp_leave_row, 5, 'Request Type', header)
                emp_leave_ws.write(emp_leave_row, 6, 'Leave Type', header)
                emp_leave_ws.write(emp_leave_row, 7, 'Number Of Days', header)
                emp_leave_ws.write(emp_leave_row, 8, 'State', header)
                emp_leave_ws.write(emp_leave_row, 9, 'Reason', header)
            
            #Bank Details
            if context.get('datas')['bank_detail_ids']:
                emp_bank_ws = workbook.add_sheet('Bank Details')
                emp_bank_ws.col(0).width = 6000
                emp_bank_ws.col(1).width = 6000
                emp_bank_ws.col(2).width = 6000
                emp_bank_ws.col(3).width = 6000
                emp_bank_ws.col(4).width = 6000
                emp_bank_ws.col(5).width = 6000
                emp_bank_ws.write(emp_bank_row, 0, 'Employee Name', header)
                emp_bank_ws.write(emp_bank_row, 1, 'Name Of Bank', header)
                emp_bank_ws.write(emp_bank_row, 2, 'Bank Code', header)
                emp_bank_ws.write(emp_bank_row, 3, 'Branch Code', header)
                emp_bank_ws.write(emp_bank_row, 4, 'Bank Account Number', header)
                emp_bank_ws.write(emp_bank_row, 5, 'Beneficiary Name', header)
            
            #National Services
            if context.get('datas')['national_service_ids']:
                emp_nat_ser_ws = workbook.add_sheet('National Services')
                emp_nat_ser_ws.col(0).width = 6000
                emp_nat_ser_ws.col(1).width = 6000
                emp_nat_ser_ws.col(2).width = 6000
                emp_nat_ser_ws.col(3).width = 6000
                emp_nat_ser_ws.col(4).width = 6000
                emp_nat_ser_ws.write(emp_nat_ser_row, 0, 'Employee Name', header)
                emp_nat_ser_ws.write(emp_nat_ser_row, 1, 'National Service', header)
                emp_nat_ser_ws.write(emp_nat_ser_row, 2, 'Rank', header)
                emp_nat_ser_ws.write(emp_nat_ser_row, 3, 'Unit', header)
                emp_nat_ser_ws.write(emp_nat_ser_row, 4, 'Reservist Status', header)
            
            #Notes
            if context.get('datas')['notes']:
                emp_note_ws = workbook.add_sheet('Notes')
                emp_note_ws.col(0).width = 6000
                emp_note_ws.col(1).width = 15000
                emp_note_ws.write(emp_note_row, 0, 'Employee Name', header)
                emp_note_ws.write(emp_note_row, 1, 'Note', header)
            #Payslip
            if context.get('datas')['payslip']:
                emp_payslip_ws = workbook.add_sheet('Payroll - Payslips')
                emp_payslip_ws.col(0).width = 6000
                emp_payslip_ws.col(2).width = 16000
                emp_payslip_ws.write(emp_payslip_row, 0, 'Employee Name', header)
                emp_payslip_ws.write(emp_payslip_row, 1, 'Reference', header)
                emp_payslip_ws.write(emp_payslip_row, 2, 'Description', header)
                emp_payslip_ws.write(emp_payslip_row, 3, 'Date from', header)
                emp_payslip_ws.write(emp_payslip_row, 4, 'Date to', header)
                emp_payslip_ws.write(emp_payslip_row, 5, 'Amount', header)
                emp_payslip_ws.write(emp_payslip_row, 6, 'State', header)

            #Contract
            if context.get('datas')['contract']:
                emp_contract_ws = workbook.add_sheet('Contract')
                emp_contract_ws.col(0).width = 6000
                emp_contract_ws.col(1).width = 6000
                emp_contract_ws.col(5).width = 6000
                emp_contract_ws.col(6).width = 6000
                emp_contract_ws.write(emp_contract_row, 0, 'Employee Name', header)
                emp_contract_ws.write(emp_contract_row, 1, 'Reference', header)
                emp_contract_ws.write(emp_contract_row, 2, 'Wage', header)
                emp_contract_ws.write(emp_contract_row, 3, 'Start date', header)
                emp_contract_ws.write(emp_contract_row, 4, 'End date', header)
                emp_contract_ws.write(emp_contract_row, 5, 'Salary structure', header)
                emp_contract_ws.write(emp_contract_row, 6, 'Commission Structure', header)

            for emp in employee_obj.browse(cr, uid, context.get('datas')['employee_ids']):
                if context.get('datas')['user_id'] or context.get('datas')['active'] or context.get('datas')['department'] \
                        or context.get('datas')['direct_manager'] or context.get('datas')['indirect_manager']:
                    emp_info_row += 1
                    emp_info_col = emp_per_info_col = 0
                    emp_info_ws.write(emp_info_row, emp_info_col, tools.ustr(emp.name or ''), style)
                    if context.get('datas')['user_id']:
                        emp_info_col += 1
                        emp_info_ws.write(emp_info_row, emp_info_col, tools.ustr(emp.user_id.name or ''), style)
                    if context.get('datas')['active']:
                        emp_info_col += 1
                        emp_info_ws.write(emp_info_row, emp_info_col, tools.ustr(emp.active or ''), style)
                    if context.get('datas')['department']:
                        emp_info_col += 1
                        emp_info_ws.write(emp_info_row, emp_info_col, tools.ustr(emp.department_id.name or ''), style)
                    if context.get('datas')['direct_manager']:
                        emp_info_col += 1
                        emp_info_ws.write(emp_info_row, emp_info_col, tools.ustr(emp.parent_id.name or ''), style)
                    if context.get('datas')['indirect_manager']:
                        emp_info_col += 1
                        emp_info_ws.write(emp_info_row, emp_info_col, tools.ustr(emp.parent_id2.name or ''), style)
                #Employee Personal Information
                if personal_information:
                    emp_per_info_row += 1
                    emp_per_info_col = 0
                    emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.name or ''), style)
                    if context.get('datas')['identification_id']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.identification_id or ''), style)
                    if context.get('datas')['passport_id']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.passport_id or ''), style)
                    if context.get('datas')['otherid']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.otherid or ''), style)
                    
                    if context.get('datas')['gender']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.gender or ''), style)
                    if context.get('datas')['martial']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.marital or ''), style)
                    if context.get('datas')['nationality']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.country_id or ''), style)
                    if context.get('datas')['dob']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.birthday and datetime.strptime(emp.birthday, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format) or ''), style)
                    if context.get('datas')['pob']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.place_of_birth or ''), style)
                    if context.get('datas')['age']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.age or ''), style)
                    
                    if context.get('datas')['home_address']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.address_home_id or ''), style)
                    if context.get('datas')['country_id']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.emp_country_id.name or ''), style)
                    if context.get('datas')['state_id']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.emp_state_id.name or ''), style)
                    if context.get('datas')['city_id']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.emp_city_id.name or ''), style)
                    if context.get('datas')['phone']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.work_phone or ''), style)
                    if context.get('datas')['mobile']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.mobile_phone or ''), style)
                    if context.get('datas')['email']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.work_email or ''), style)
                    
                    if context.get('datas')['race_id']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.race_id.name or ''), style)
                    if context.get('datas')['dialet']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.dialect or ''), style)
                    if context.get('datas')['religion']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.religion_id.name or ''), style)
                    if context.get('datas')['driving_licence']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.driving_licence or ''), style)
                    if context.get('datas')['own_car']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.car or ''), style)
                    if context.get('datas')['emp_type_id']:
                        emp_per_info_col += 1
                        emp_personal_info_ws.write(emp_per_info_row, emp_per_info_col, tools.ustr(emp.employee_type_id.name or ''), style)
                
                #Appraisal
                if context.get('datas')['evaluation_plan_id'] or context.get('datas')['evaluation_date']:
                    emp_appraisal_row += 1
                    emp_appraisal_col = 0
                    emp_appraisal_ws.write(emp_appraisal_row, emp_appraisal_col, tools.ustr(emp.name), style)
                    if context.get('datas')['evaluation_plan_id']:
                        emp_appraisal_col += 1
                        emp_appraisal_ws.write(emp_appraisal_row, emp_appraisal_col, tools.ustr(emp.evaluation_plan_id.name or ''), style)
                    if context.get('datas')['evaluation_date']:
                        emp_appraisal_col += 1
                        emp_appraisal_ws.write(emp_appraisal_row, emp_appraisal_col, emp.evaluation_date and datetime.strptime(emp.evaluation_date, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format) or '', style)
                
                #Notification
                if context.get('datas')['emp_noty_leave'] or context.get('datas')['pending_levae_noty'] or context.get('datas')['receive_mail_manager']:
                    emp_notification_row += 1
                    emp_notification_col = 0
                    emp_notification_ws.write(emp_notification_row, emp_notification_col, tools.ustr(emp.name or ''), style)
                    if context.get('datas')['emp_noty_leave']:
                        emp_notification_col += 1
                        emp_notification_ws.write(emp_notification_row, emp_notification_col, tools.ustr(emp.is_daily_notificaiton_email_send or ''), style)
                    if context.get('datas')['pending_levae_noty']:
                        emp_notification_col += 1
                        emp_notification_ws.write(emp_notification_row, emp_notification_col, tools.ustr(emp.is_pending_leave_notificaiton or ''), style)
                    if context.get('datas')['receive_mail_manager']:
                        emp_notification_col += 1
                        emp_notification_ws.write(emp_notification_row, emp_notification_col, tools.ustr(emp.is_all_final_leave), style)
                
                #Extra Information
                if context.get('datas')['health_condition'] or context.get('datas')['bankrupt'] or context.get('datas')['suspend_employment'] or context.get('datas')['court_law'] or context.get('datas')['about']:
                    emp_extra_info_col = 0
                    emp_extra_info_row += 1
                    emp_extra_info_ws.write(emp_extra_info_row, emp_extra_info_col, tools.ustr(emp.name or ''), style)
                    if context.get('datas')['health_condition']:
                        emp_extra_info_col += 1
                        helath_condition = ''
                        if emp.physical_stability:
                            helath_condition = 'Yes'
                        if emp.physical_stability_no:
                            helath_condition = 'No'
                        emp_extra_info_ws.write(emp_extra_info_row, emp_extra_info_col, tools.ustr(helath_condition or ''), style)
                    if context.get('datas')['bankrupt']:
                        emp_extra_info_col += 1
                        bankrupt = ''
                        if emp.bankrupt_b:
                            bankrupt = 'Yes'
                        if emp.bankrupt_no:
                            bankrupt = 'No'
                        emp_extra_info_ws.write(emp_extra_info_row, emp_extra_info_col, tools.ustr(bankrupt or ''), style)
                    if context.get('datas')['suspend_employment']:
                        emp_extra_info_col += 1
                        supspend = ''
                        if emp.dismissed_b:
                            supspend = 'Yes'
                        if emp.dismissed_no:
                            supspend = 'No'
                        emp_extra_info_ws.write(emp_extra_info_row, emp_extra_info_col, tools.ustr(supspend or ''), style)
                    if context.get('datas')['court_law']:
                        emp_extra_info_col += 1
                        court = ''
                        if emp.court_b:
                            court = "Yes"
                        if emp.court_no:
                            court = "No"
                        emp_extra_info_ws.write(emp_extra_info_row, emp_extra_info_col, tools.ustr(court or ''), style)
                    if context.get('datas')['about']:
                        emp_extra_info_col += 1
                        emp_extra_info_ws.write(emp_extra_info_row, emp_extra_info_col, tools.ustr(emp.about or ''), style)

                if context.get('datas')['reference_ids']:
                    for reference in emp.reference_ids:
                        emp_ref_row += 1
                        emp_ref_ws.write(emp_ref_row, 0, tools.ustr(emp.name or ''), style)
                        emp_ref_ws.write(emp_ref_row, 1, tools.ustr(reference.name or ''), style)
                        emp_ref_ws.write(emp_ref_row, 2, tools.ustr(reference.relationship or ''), style)
                        emp_ref_ws.write(emp_ref_row, 3, tools.ustr(reference.contact_no or ''), style)
                        emp_ref_ws.write(emp_ref_row, 4, tools.ustr(reference.yrd_knw or ''), style)

                #Educational Information
                if context.get('datas')['com_prog_know'] or context.get('datas')['shorthand'] or context.get('datas')['courses'] or context.get('datas')['typing'] or context.get('datas')['other_know']:
                    emp_edu_skill_row += 1
                    emp_edu_skill_ws.write(emp_edu_skill_row, 0, tools.ustr(emp.name or ''), style)
                    if context.get('datas')['com_prog_know']:
                        emp_edu_skill_ws.write(emp_edu_skill_row, 1, tools.ustr(emp.comp_prog_knw or ''), style)
                    if context.get('datas')['shorthand']:
                        emp_edu_skill_ws.write(emp_edu_skill_row, 2, tools.ustr(emp.shorthand or ''), style)
                    if context.get('datas')['courses']:
                        emp_edu_skill_ws.write(emp_edu_skill_row, 3, tools.ustr(emp.course or ''), style)
                    if context.get('datas')['typing']:
                        emp_edu_skill_ws.write(emp_edu_skill_row, 4, tools.ustr(emp.typing or ''), style)
                    if context.get('datas')['other_know']:
                        emp_edu_skill_ws.write(emp_edu_skill_row, 5, tools.ustr(emp.other_know or ''), style)
                if context.get('datas')['edu_ids']:
                    for edu in emp.edu_ids:
                        emp_edu_info_row += 1
                        emp_edu_info_ws.write(emp_edu_info_row, 0, tools.ustr(emp.name or ''), style)
                        emp_edu_info_ws.write(emp_edu_info_row, 1, tools.ustr(edu.edu_level.type or ''), style)
                        emp_edu_info_ws.write(emp_edu_info_row, 2, tools.ustr(edu.edu_school or ''), style)
                        emp_edu_info_ws.write(emp_edu_info_row, 3, tools.ustr(edu.period or ''), style)
                        emp_edu_info_ws.write(emp_edu_info_row, 4, tools.ustr(edu.edu_certificate or ''), style)
                if context.get('datas')['language_ids']:
                    for language in emp.language_ids:
                        emp_lang_row += 1
                        emp_lang_ws.write(emp_lang_row, 0, tools.ustr(emp.name or ''), style)
                        emp_lang_ws.write(emp_lang_row, 1, tools.ustr(language.lang_name_id.name or ''), style)
                        emp_lang_ws.write(emp_lang_row, 2, tools.ustr(language.spoken or ''), style)
                        emp_lang_ws.write(emp_lang_row, 3, tools.ustr(language.written or ''), style)
                #Family Particulars
                if context.get('datas')['family_ids']:
                    for family in emp.relative_ids:
                        emp_family_row += 1
                        emp_family_ws.write(emp_family_row, 0, tools.ustr(emp.name or ''), style)
                        emp_family_ws.write(emp_family_row, 1, tools.ustr(family.name or ''), style)
                        emp_family_ws.write(emp_family_row, 2, tools.ustr(family.relationship_id.name or ''), style)
                        emp_family_ws.write(emp_family_row, 3, family.date_of_birth  and datetime.strptime(family.date_of_birth, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format) or '', style)
                        emp_family_ws.write(emp_family_row, 4, tools.ustr(family.occupation or ''), style)
                        emp_family_ws.write(emp_family_row, 5, tools.ustr(family.address or ''), style)
                        emp_family_ws.write(emp_family_row, 6, tools.ustr(family.contact or ''), style)
                        emp_family_ws.write(emp_family_row, 7, tools.ustr(family.emr_telephone or ''), style)
                #Employment History 
                if context.get('datas')['employment_history_ids']:
                    for emp_histoy in emp.employment_history_ids:
                        emp_emphistory_row += 1
                        emp_emphistory_ws.write(emp_emphistory_row, 0, tools.ustr(emp.name or ''), style)
                        emp_emphistory_ws.write(emp_emphistory_row, 1, tools.ustr(emp_histoy.company), style)
                        emp_emphistory_ws.write(emp_emphistory_row, 2, emp_histoy.from_date and datetime.strptime(emp_histoy.from_date, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format) or '', style)
                        emp_emphistory_ws.write(emp_emphistory_row, 3, emp_histoy.to_date and datetime.strptime(emp_histoy.to_date, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format) or '', style)
                        emp_emphistory_ws.write(emp_emphistory_row, 4, tools.ustr(emp_histoy.salary_starting), style)
                        emp_emphistory_ws.write(emp_emphistory_row, 5, tools.ustr(emp_histoy.salry_last), style)
                        emp_emphistory_ws.write(emp_emphistory_row, 6, tools.ustr(emp_histoy.designation), style)
                        emp_emphistory_ws.write(emp_emphistory_row, 7, tools.ustr(emp_histoy.responsibility), style)
                        emp_emphistory_ws.write(emp_emphistory_row, 8, tools.ustr(emp_histoy.reason), style)
                #Job
                if context.get('datas')['job_title'] or context.get('datas')['emp_status'] \
                    or context.get('datas')['join_date'] \
                    or context.get('datas')['confirm_date'] \
                    or context.get('datas')['date_changed'] \
                    or context.get('datas')['changed_by'] \
                    or context.get('datas')['date_confirm_month']:
                    for job in emp.history_ids:
                        emp_job_col = 0
                        emp_job_row += 1
                        emp_job_ws.write(emp_job_row, emp_job_col, tools.ustr(emp.name or ''), style)
                        if context.get('datas')['job_title']:
                            emp_job_col += 1
                            emp_job_ws.write(emp_job_row, emp_job_col, tools.ustr(job.job_id.name or ''), style)
                        if context.get('datas')['emp_status']:
                            emp_job_col += 1
                            emp_job_ws.write(emp_job_row, emp_job_col, tools.ustr(job.emp_status or ''), style)
                        if context.get('datas')['join_date']:
                            emp_job_col += 1
                            emp_job_ws.write(emp_job_row, emp_job_col, job.join_date and datetime.strptime(job.join_date, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format) or '', style)
                        if context.get('datas')['confirm_date']:
                            emp_job_col += 1
                            emp_job_ws.write(emp_job_row, emp_job_col, job.confirm_date and datetime.strptime(job.confirm_date, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format) or '', style)
                        if context.get('datas')['date_changed']:
                            emp_job_col += 1
                            emp_job_ws.write(emp_job_row, emp_job_col, job.date_changed and datetime.strptime(job.date_changed, DEFAULT_SERVER_DATETIME_FORMAT).strftime(date_format) or '', style)
                        if context.get('datas')['changed_by']:
                            emp_job_col += 1
                            emp_job_ws.write(emp_job_row, emp_job_col, tools.ustr(job.user_id.name or ''), style)
                        if context.get('datas')['date_confirm_month']:
                            emp_job_col += 1
                            emp_job_ws.write(emp_job_row, emp_job_col, job.confirm_date and datetime.strptime(job.confirm_date, DEFAULT_SERVER_DATE_FORMAT).strftime(month_year_format) or '', style)
                #Categories
                if context.get('datas')['category_ids']:
                    for category in emp.category_ids:
                        emp_categories_row += 1
                        emp_categories_ws.write(emp_categories_row, 0, tools.ustr(emp.name or ''), style)
                        emp_categories_ws.write(emp_categories_row, 1, tools.ustr(category.name or ''), style)
                        emp_categories_ws.write(emp_categories_row, 2, tools.ustr(category.parent_id.name or ''), style)
                #Immigration
                if context.get('datas')['immigration_ids']:
                    for immigration in emp.immigration_ids:
                        emp_immigration_row += 1
                        emp_immigration_ws.write(emp_immigration_row, 0, tools.ustr(emp.name or ''), style)
                        emp_immigration_ws.write(emp_immigration_row, 1, tools.ustr(immigration.documents or ''), style)
                        emp_immigration_ws.write(emp_immigration_row, 2, tools.ustr(immigration.number or ''), style)
                        emp_immigration_ws.write(emp_immigration_row, 3, immigration.issue_date and datetime.strptime(immigration.issue_date, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format) or '', style)
                        emp_immigration_ws.write(emp_immigration_row, 4, immigration.exp_date and datetime.strptime(immigration.exp_date, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format) or '', style)
                        emp_immigration_ws.write(emp_immigration_row, 5, tools.ustr(immigration.eligible_status or ''), style)
                        emp_immigration_ws.write(emp_immigration_row, 6, immigration.eligible_review_date and datetime.strptime(immigration.eligible_review_date, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format) or '', style)
                        emp_immigration_ws.write(emp_immigration_row, 7, tools.ustr(immigration.issue_by or ''), style)
                        emp_immigration_ws.write(emp_immigration_row, 8, tools.ustr(immigration.comments or ''), style)
                #Trainig Workshop
                if context.get('datas')['tarining_ids']:
                    if emp.training_ids:
                        for training in emp.training_ids:
                            emp_training_row += 1
                            emp_training_ws.write(emp_training_row, 0, tools.ustr(emp.name or ''), style)
                            emp_training_ws.write(emp_training_row, 1, tools.ustr(training.tr_title or ''), style)
                            emp_training_ws.write(emp_training_row, 2, tools.ustr(training.tr_institution or ''), style)
                            emp_training_ws.write(emp_training_row, 3, training.tr_date and datetime.strptime(training.tr_date, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format) or '', style)
                            emp_training_ws.write(emp_training_row, 4, tools.ustr(training.comments or ''), style)
                    else:
                        emp_training_row += 1
                        emp_training_ws.write(emp_training_row, 0, tools.ustr(emp.name or ''), style)
                        emp_training_ws.write(emp_training_row, 1, '', style)
                        emp_training_ws.write(emp_training_row, 2, '', style)
                        emp_training_ws.write(emp_training_row, 3, '', style)
                        emp_training_ws.write(emp_training_row, 4, '', style)
                
                #Leave History
                if context.get('datas')['emp_leave_ids']:
                    for leave in emp.employee_leave_ids:
                        emp_leave_row += 1
                        emp_leave_ws.write(emp_leave_row, 0, tools.ustr(emp.name or ''), style)
                        emp_leave_ws.write(emp_leave_row, 1, tools.ustr(leave.name or ''), style)
                        emp_leave_ws.write(emp_leave_row, 2, tools.ustr(leave.fiscal_year_id and leave.fiscal_year_id.name or ''), style)
                        emp_leave_ws.write(emp_leave_row, 3, leave.date_from and datetime.strptime(leave.date_from.split(' ')[0], DEFAULT_SERVER_DATE_FORMAT).strftime(date_format) or '', style)
                        emp_leave_ws.write(emp_leave_row, 4, leave.date_to and datetime.strptime(leave.date_to.split(' ')[0], DEFAULT_SERVER_DATE_FORMAT).strftime(date_format) or '', style)
                        emp_leave_ws.write(emp_leave_row, 5, tools.ustr(LEAVE_REQUEST.get(leave.type, '')), style)
                        emp_leave_ws.write(emp_leave_row, 6, tools.ustr(leave.holiday_status_id.name2 or ''), style)
                        emp_leave_ws.write(emp_leave_row, 7, tools.ustr(leave.number_of_days_temp or ''), style)
                        emp_leave_ws.write(emp_leave_row, 8, tools.ustr(LEAVE_STATE.get(leave.state, '')), style)
                        emp_leave_ws.write(emp_leave_row, 9, tools.ustr(leave.rejection or ''), style)
                #Bank Details
                if context.get('datas')['bank_detail_ids']:
                    for bank in emp.bank_detail_ids:
                        emp_bank_row += 1
                        emp_bank_ws.write(emp_bank_row, 0, tools.ustr(emp.name or ''), style)
                        emp_bank_ws.write(emp_bank_row, 1, tools.ustr(bank.bank_name or ''), style)
                        emp_bank_ws.write(emp_bank_row, 2, tools.ustr(bank.bank_code or ''), style)
                        emp_bank_ws.write(emp_bank_row, 3, tools.ustr(bank.branch_code or ''), style)
                        emp_bank_ws.write(emp_bank_row, 4, tools.ustr(bank.bank_ac_no or ''), style)
                        emp_bank_ws.write(emp_bank_row, 5, tools.ustr(bank.beneficiary_name or ''), style)
                #National Services
                if context.get('datas')['national_service_ids']:
                    for national in emp.national_service_ids:
                        emp_nat_ser_row += 1
                        emp_nat_ser_ws.write(emp_nat_ser_row, 0, tools.ustr(emp.name or ''), style)
                        emp_nat_ser_ws.write(emp_nat_ser_row, 1, tools.ustr(national.name or ''), style)
                        emp_nat_ser_ws.write(emp_nat_ser_row, 2, tools.ustr(national.rank or ''), style)
                        emp_nat_ser_ws.write(emp_nat_ser_row, 3, tools.ustr(national.unit or ''), style)
                        emp_nat_ser_ws.write(emp_nat_ser_row, 4, tools.ustr(national.reser_status_id or ''), style)
                
                #Notes
                if context.get('datas')['notes']:
                    emp_note_row += 1
                    emp_note_ws.write(emp_note_row, 0, tools.ustr(emp.name or ''), style)
                    emp_note_ws.write(emp_note_row, 1, tools.ustr(emp.notes or ''), style)

                #Payslip
                if context.get('datas')['payslip']:
                    payslip_ids = payslip_obj.search(cr, uid, [('employee_id', '=', emp.id)])
                    for payslip in payslip_obj.browse(cr, uid, payslip_ids):
                        net_amount = 0.0
                        for line in payslip.line_ids:
                            if line.code == "NET":
                                net_amount = line.amount
                        emp_payslip_row += 1
                        emp_payslip_ws.write(emp_payslip_row, 0, tools.ustr(emp.name or ''), style)
                        emp_payslip_ws.write(emp_payslip_row, 1, tools.ustr(payslip.number or ''), style)
                        emp_payslip_ws.write(emp_payslip_row, 2, tools.ustr(payslip.name or ''), style)
                        emp_payslip_ws.write(emp_payslip_row, 3, payslip.date_from and datetime.strptime(payslip.date_from, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format) or '', style)
                        emp_payslip_ws.write(emp_payslip_row, 4, payslip.date_to and datetime.strptime(payslip.date_to, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format) or '', style)
                        emp_payslip_ws.write(emp_payslip_row, 5, net_amount, number_format)
                        emp_payslip_ws.write(emp_payslip_row, 6, tools.ustr(PAYSLIP_STATE.get(payslip.state, '')), style)

                if context.get('datas')['contract']:
                    contract_ids = contract_obj.search(cr, uid, [('employee_id', '=', emp.id)])
                    for contract in contract_obj.browse(cr, uid, contract_ids):
                        emp_contract_row += 1
                        emp_contract_ws.write(emp_contract_row, 0, tools.ustr(emp.name or ''), style)
                        emp_contract_ws.write(emp_contract_row, 1, tools.ustr(contract.name or ''), style)
                        emp_contract_ws.write(emp_contract_row, 2, contract.wage, number_format)
                        emp_contract_ws.write(emp_contract_row, 3, contract.date_start and datetime.strptime(contract.date_start, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format) or '', style)
                        emp_contract_ws.write(emp_contract_row, 4, contract.date_end and datetime.strptime(contract.date_end, DEFAULT_SERVER_DATE_FORMAT).strftime(date_format) or '', style)
                        emp_contract_ws.write(emp_contract_row, 5, tools.ustr(contract.struct_id and contract.struct_id.name or ''), style)
                        emp_contract_ws.write(emp_contract_row, 6, tools.ustr(contract.commission_id and contract.commission_id.name or ''), style)

        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        return base64.b64encode(data)

    _defaults = {
        'name': "Employee Summary.xls",
        'file': _get_employee_summary_data
    }
export_employee_data_record_xls()

class export_employee_summary_wiz(osv.osv_memory):

    _name = 'export.employee.summary.wiz'

    def onchange_personal_information(self, cr, uid, ids, personal_information):
        
        if personal_information == True:
            return {'value': {'identification_id': True,
                              'passport_id': True,
                              'otherid': True,
                              'gender': True,
                              'martial': True,
                              'nationality': True,
                              'dob': True,
                              'pob': True,
                              'age': True,
                              'home_address': True,
                              'country_id': True,
                              'state_id': True,
                              'city_id': True,
                              'phone': True,
                              'mobile': True,
                              'email': True,
                              'race_id': True,
                              'dialet': True,
                              'religion': True,
                              'driving_licence': True,
                              'own_car': True,
                              'emp_type_id': True,
                    }}
        else:
            return {'value': {'identification_id': False,
                              'passport_id': False,
                              'otherid': False,
                              'gender': False,
                              'martial': False,
                              'nationality': False,
                              'dob': False,
                              'pob': False,
                              'age': False,
                              'home_address': False,
                              'country_id': False,
                              'state_id': False,
                              'city_id': False,
                              'phone': False,
                              'mobile': False,
                              'email': False,
                              'race_id': False,
                              'dialet': False,
                              'religion': False,
                              'driving_licence': False,
                              'own_car': False,
                              'emp_type_id': False,
                    }}

    _columns = {
        'employee_ids': fields.many2many('hr.employee', 'ihrms_hr_employee_export_summary_rel','emp_id','employee_id','Employee Name', required=False),
        'user_id': fields.boolean('User'),
        'active': fields.boolean('Active'),
        'department': fields.boolean('Department'),
        'direct_manager': fields.boolean('Direct Manager'),
        'indirect_manager': fields.boolean('Indirect Manager'),
        'personal_information': fields.boolean('Personal Information'),
        'identification_id': fields.boolean('Identification'),
        'passport_id': fields.boolean('Passport'),
        'otherid': fields.boolean('Other ID'),
        'gender': fields.boolean('Gender'),
        'martial': fields.boolean('Martial Status'),
        'nationality': fields.boolean('Nationality'),
        'dob': fields.boolean('Date Of Birth'),
        'pob': fields.boolean('Place Of Birth'),
        'age': fields.boolean('Age'),
        'home_address': fields.boolean('Home Address'),
        'country_id': fields.boolean('Country'),
        'state_id': fields.boolean('State'),
        'city_id': fields.boolean('City'),
        'phone': fields.boolean('Phone'),
        'mobile': fields.boolean('Mobile'),
        'email': fields.boolean('Email'),
        'race_id': fields.boolean('Race'),
        'dialet': fields.boolean('Dialet'),
        'religion': fields.boolean('Religion'),
        'driving_licence': fields.boolean('Driving Licence Class'),
        'own_car': fields.boolean('Do Your Own Car'),
        'emp_type_id': fields.boolean('Type Of ID'),
        'evaluation_plan_id': fields.boolean('Appraisal Plan'),
        'evaluation_date': fields.boolean('Next Appraisal Date'),
        'family_ids': fields.boolean('Family Particulars'),
        'employment_history_ids': fields.boolean('Employment History'),
        'edu_ids': fields.boolean('Education'),
        'language_ids': fields.boolean('Language'),
        'com_prog_know': fields.boolean('Computer Program Knowledge'),
        'shorthand': fields.boolean('Shorthand'),
        'courses': fields.boolean('Courses Taken'),
        'typing': fields.boolean('Typing'),
        'other_know': fields.boolean('Other Knowledge & Skills'),
        'job_title': fields.boolean('Job Title'),
        'emp_status': fields.boolean('Employment Status'),
        'join_date': fields.boolean('Joined Date'),
        'confirm_date': fields.boolean('Confirmation Date'),
        'date_changed': fields.boolean('Date Changed'),
        'changed_by': fields.boolean('Changed By'),
        'date_confirm_month': fields.boolean('Date Confirm Month'),
        'category_ids': fields.boolean('Categories'),
        'immigration_ids': fields.boolean('Immigration'),
        'tarining_ids': fields.boolean('Training Workshop'),
        'emp_leave_ids': fields.boolean('Leave History'),
        'health_condition': fields.boolean('Are you suffering from any physical disability or illness that requires you to be medication for a prolonged period?'),
        'court_law': fields.boolean('Have you ever been convicted in a court of law in any country?'),
        'suspend_employment': fields.boolean('Have you ever been dismissed or suspended from employement?'),
        'bankrupt': fields.boolean('Have you ever been declared a bankrupt?'),
        'reference_ids': fields.boolean('References'),
        'about': fields.boolean('About Yourself'),
        'emp_noty_leave': fields.boolean('Receiving email notifications of employees who are on leave?'),
        'pending_levae_noty': fields.boolean('Receiving email notifications of Pending Leaves Notification Email?'),
        'receive_mail_manager': fields.boolean('Receiving email notifications of 2nd Reminder to Direct / Indirect Managers?'),
        'bank_detail_ids': fields.boolean('Bank Details'),
        'national_service_ids': fields.boolean('National Service'),
        'notes': fields.boolean('Notes'),
        'payslip': fields.boolean('Payslips'),
        'contract': fields.boolean('Contract'),
    }

    def export_employee_summary_xls(self, cr, uid, ids, context):
        context.update({'active_test': False})
        data = self.read(cr, uid, ids, context=context)[0]
        context.update({'datas': data})
        return {
            'name': _('Binary'),
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'export.employee.data.record.xls',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }
export_employee_summary_wiz()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: