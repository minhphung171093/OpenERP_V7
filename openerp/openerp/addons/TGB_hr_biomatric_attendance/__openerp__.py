# -*- coding: utf-8 -*-

{
    "name" : "TGB Biomatric Attendance Import",
    "version" : "0.1",
    "author" : "Son Pham",
    "category" : "Report",
    "depends" : [
                 'hr_holiday_extended',
                 'payroll_extended',
                 'timesheet_extended'
                 ],
    "description": "TGB Biomatric Attendance Import",
    "data": [
                'attendance_import.xml',
                'time_table_view.xml',
             ],
    'installable': True,
}
