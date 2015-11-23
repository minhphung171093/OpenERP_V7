{

    "name" : "Leaves Management Extension",
    "version" : "1.432",
    "author" :"Sơn Pham & Di Ho",
    "website" : "",
    "category": "Human Resources",
    "description" : 
    '''
    Module to manage leave request approval.
    Documents can attached with a leave request.
    Calculate remaining leaves and carry forward to the next year.
    Carry forwarded leaves period.
    Public holiday lists and pdf report directly emailed to employees.
    ''',
    "depends" : [
        "hr_holidays",
        "hr_attendance",
        "hr_recruitment",
        "hr_evaluation",
        "hr_contract",
#        "prestige_hr_applicant_extended",
        "account"
    ],
    "init_xml": [],
    "update_xml": [
#        "security/group.xml",
        "wizard/hr_refuse_leave_view.xml",
        "hr_holiday_ex_view.xml",
        "wizard/inactive_wizard_view.xml",
        "board_hr_holidays_view.xml",
#        "security/ir.model.access.csv",
        "report/public_holiday_rml.xml",
#        "hr_holiday_ex_data.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
