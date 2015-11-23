{
    'name': 'Project Management with Cost Accounting',
    'version': '0.1',
    'category': 'Project Management Modules',
    'description': """
                    Project Management with Cost Accounting
 
        """,
    'author': 'Son Pham & Ho Di',

    'depends': ['base',
                'stock',
                'project_timesheet',
                'sale',
                'purchase',
#                'purchase_discount',
                'account',
                'account_budget'
                ],
    'init_xml': [],
    'update_xml': [
                   'report/project_budget_report_view.xml',
                   'wizard/create_task_wizard.xml',
                   'security/ir.model.access.csv',
                   'project_costing_view.xml',
                   'tax_invoice_view.xml',
                   'report/project_task_report_view.xml'
                   ],
    'demo_xml': [],
    'installable': True,
    'active': False
    }
