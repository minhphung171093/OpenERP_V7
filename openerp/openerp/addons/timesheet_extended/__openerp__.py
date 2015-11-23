# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Serpent Consulting Services (<http://www.serpentcs.com>).
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

{
    "name": "Timesheet",
    "version": "1.0",
    "depends": ["hr_attendance","hr_timesheet_sheet","hr_payroll", "sale"],
    "author": "Son Pham & Di Ho",
    "category": "Human Resources",
    "website" : "",
    "description": """
    This module provide :
    @ Groups :
        (1) Roster Planning Manager/User
        (2) Timesheet Manager/user
        
    @ Meeting : (Can Access Roster Planning Manager /User)
        >> Roster User Creating Their meeting/planning whenever he/she confirm it than
           It set to Waiting for approval state.
        >> If Roster Manager Will approve it Than It Comes In  Done state.
        
    @ Scheduler :
        >> Starting of Every New Month Scheduler will Create Timehseet for All Users of Those 
        are in Done State In Previous Month. 
        
    @ Timesheet :(Can Access Timesheet Manager /User)
        >> When Employee Confirm their timesheet than Direct Manager getting mail that the Timesheet of 
        particular User is ready for Pre-Approval.
        >> When Direct Manager Pre-Approving that Timesheet than Indirect manager get mail that Timesheet
        of Particular User is ready for Final-Approval and Than Manager Approving it.
        >> All Manager can Refuse & Set to Draft the Timesheet.
        >> If Timesheet has been set to Draft Than Particular Employee getting mail That Your timesheet 
        is in Draft set so you set it pre-approval state.
        
    """,
    'data': [
        'roster_timesheet_view.xml',
        'security/roster_security.xml',
        'security/ir.model.access.csv',
        'roster_timesheet_schedular.xml',
        'ppd_timesheet_workflow.xml'
    ],
    'installable': True,
    'auto_install':False,
}