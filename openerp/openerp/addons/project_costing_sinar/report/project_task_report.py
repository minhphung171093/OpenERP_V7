from osv import fields,osv
import tools

class report_project_task_product_user(osv.osv):
    _name = "report.project.task.product.user"
    _description = "Consumed Product Tasks by user and project"
    _auto = False
    _columns = {
        'name': fields.char('Task Summary', size=128, readonly=True),
        'consume_product': fields.char('Consumed Product', size=128, readonly=True),
        'used_qty': fields.integer('Product Consumed Quantity'),
#        'consume_time': fields.char('Consumed Time', size=128, readonly=True),
        'day': fields.char('Day', size=128, readonly=True),
        'year': fields.char('Year', size=64, required=False, readonly=True),
        'user_id': fields.many2one('res.users', 'Assigned To', readonly=True),
        'date_start': fields.date('Starting Date',readonly=True),
#        'no_of_days': fields.integer('# of Days', size=128, readonly=True),
        'date_end': fields.date('Ending Date', readonly=True),
        'date_deadline': fields.date('Deadline', readonly=True),
        'project_id': fields.many2one('project.project', 'Project', readonly=True),
#        'hours_planned': fields.float('Planned Hours', readonly=True),
#        'hours_effective': fields.float('Effective Hours', readonly=True),
#        'hours_delay': fields.float('Avg. Plan.-Eff.', readonly=True),
#        'remaining_hours': fields.float('Remaining Hours', readonly=True),
        'progress': fields.float('Progress', readonly=True, group_operator='avg'),
        'planned_amt': fields.float('Product Cost', readonly=True),
#        'time_cost': fields.float('Project Time Cost', readonly=True),
        
        
#        'total_hours': fields.float('Total Hours', readonly=True),
#        'closing_days': fields.float('Days to Close', digits=(16,2), readonly=True, group_operator="avg",
#                                       help="Number of Days to close the task"),
#        'opening_days': fields.float('Days to Open', digits=(16,2), readonly=True, group_operator="avg",
#                                       help="Number of Days to Open the task"),
#        'delay_endings_days': fields.float('Overpassed Deadline', digits=(16,2), readonly=True),
        'nbr': fields.integer('# of tasks', readonly=True),
        'priority' : fields.selection([('4','Very Low'), ('3','Low'), ('2','Medium'), ('1','Urgent'),
                                       ('0','Very urgent')], 'Priority', readonly=True),
        'month':fields.selection([('01','January'), ('02','February'), ('03','March'), ('04','April'), ('05','May'), ('06','June'), ('07','July'), ('08','August'), ('09','September'), ('10','October'), ('11','November'), ('12','December')], 'Month', readonly=True),
        'state': fields.selection([('draft', 'Draft'), ('open', 'In Progress'), ('pending', 'Pending'), ('cancelled', 'Cancelled'), ('done', 'Done')],'State', readonly=True),
        'company_id': fields.many2one('res.company', 'Company', readonly=True, groups="base.group_multi_company"),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
#        'general_budget_id': fields.many2one('account.budget.post', 'Budgetary Position',required=True),
        'type_id': fields.many2one('project.task.type', 'Stage', readonly=True),
        'product_id': fields.many2one('product.product', 'Product', readonly=True),
        'task_cons_prod_ref_id': fields.many2one('task.consume.products', 'Consume Product/Time', readonly=True),
    }
    _order = 'name desc, project_id'

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'report_project_task_product_user')
        cr.execute("""
            CREATE view report_project_task_product_user as
              SELECT
                    (select 1 ) AS nbr,
                    a.id, 
                    to_char(date_start, 'YYYY') as year,
                    to_char(date_start, 'MM') as month,
                    to_char(date_start, 'YYYY-MM-DD') as day,
                    date_trunc('day',t.date_start) as date_start,
                    date_trunc('day',t.date_end) as date_end,
                    to_date(to_char(t.date_deadline, 'dd-MM-YYYY'),'dd-MM-YYYY') as date_deadline,
                    t.user_id,
                    progress as progress,
                    t.project_id,
                    t.state,
                    t.priority,
                    t.name as name,
                    t.company_id,
                    a.name as consume_product,
                    c.used_qty as used_qty, 
                    c.invoice_line_amt as planned_amt,
                    t.partner_id
                    FROM project_task t, account_analytic_line a,task_consume_products c
                    where t.id = a.task_id and  a.task_cons_prod_ref_id = c.id and c.con_prod_task_id = t.id
                   
              
                GROUP BY
                    a.id,
                    progress,
                    year,
                    month,
                    day,
                    date_start,
                    date_end,
                    date_deadline,
                    t.user_id,
                    t.project_id,
                    t.state,
                    t.priority,
                    t.name,
                    t.company_id,
                    t.partner_id,
                    consume_product,
                    planned_amt,
                    used_qty
                    
        """)

report_project_task_product_user()

class report_project_task_time_user(osv.osv):
    _name = "report.project.task.time.user"
    _description = "Consumed Product Tasks by user and project"
    _auto = False
    _columns = {
        'name': fields.char('Task Summary', size=128, readonly=True),
#        'consume_product': fields.char('Consumed Product', size=128, readonly=True),
        'consume_time': fields.char('Task Work', size=128, readonly=True),
        'time_spent': fields.float('Time Spent', size=128, readonly=True),
        'day': fields.char('Day', size=128, readonly=True),
        'year': fields.char('Year', size=64, required=False, readonly=True),
        'user_id': fields.many2one('res.users', 'Assigned To', readonly=True),
        'date_start': fields.date('Starting Date',readonly=True),
#        'no_of_days': fields.integer('# of Days', size=128, readonly=True),
        'date_end': fields.date('Ending Date', readonly=True),
        'date_deadline': fields.date('Deadline', readonly=True),
        'project_id': fields.many2one('project.project', 'Project', readonly=True),
#        'hours_planned': fields.float('Planned Hours', readonly=True),
#        'hours_effective': fields.float('Effective Hours', readonly=True),
#        'hours_delay': fields.float('Avg. Plan.-Eff.', readonly=True),
#        'remaining_hours': fields.float('Remaining Hours', readonly=True),
        'progress': fields.float('Progress', readonly=True, group_operator='avg'),
#        'planned_amt': fields.float('Product Cost', readonly=True),
        'time_cost': fields.float('Project Time Cost', readonly=True),
        
        
#        'total_hours': fields.float('Total Hours', readonly=True),
#        'closing_days': fields.float('Days to Close', digits=(16,2), readonly=True, group_operator="avg",
#                                       help="Number of Days to close the task"),
#        'opening_days': fields.float('Days to Open', digits=(16,2), readonly=True, group_operator="avg",
#                                       help="Number of Days to Open the task"),
#        'delay_endings_days': fields.float('Overpassed Deadline', digits=(16,2), readonly=True),
        'nbr': fields.integer('# of tasks', readonly=True),
        'priority' : fields.selection([('4','Very Low'), ('3','Low'), ('2','Medium'), ('1','Urgent'),
                                       ('0','Very urgent')], 'Priority', readonly=True),
        'month':fields.selection([('01','January'), ('02','February'), ('03','March'), ('04','April'), ('05','May'), ('06','June'), ('07','July'), ('08','August'), ('09','September'), ('10','October'), ('11','November'), ('12','December')], 'Month', readonly=True),
        'state': fields.selection([('draft', 'Draft'), ('open', 'In Progress'), ('pending', 'Pending'), ('cancelled', 'Cancelled'), ('done', 'Done')],'State', readonly=True),
        'company_id': fields.many2one('res.company', 'Company', readonly=True, groups="base.group_multi_company"),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
#        'general_budget_id': fields.many2one('account.budget.post', 'Budgetary Position',required=True),
        'type_id': fields.many2one('project.task.type', 'Stage', readonly=True),
        'product_id': fields.many2one('product.product', 'Product', readonly=True),
        'task_cons_prod_ref_id': fields.many2one('task.consume.products', 'Consume Product/Time', readonly=True),
    }
    _order = 'name desc, project_id'

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'report_project_task_time_user')
        cr.execute("""
            CREATE view report_project_task_time_user as
              SELECT
                    (select 1 ) AS nbr,
                    a.id, 
                    to_char(date_start, 'YYYY') as year,
                    to_char(date_start, 'MM') as month,
                    to_char(date_start, 'YYYY-MM-DD') as day,
                    date_trunc('day',t.date_start) as date_start,
                    date_trunc('day',t.date_end) as date_end,
                    to_date(to_char(t.date_deadline, 'dd-MM-YYYY'),'dd-MM-YYYY') as date_deadline,
                    t.user_id,
                    progress as progress,
                    t.project_id,
                    t.state,
                    t.priority,
                    t.name as name,
                    t.company_id,
                    d.name as consume_time,
                    d.invoice_line_amt as time_cost,
                    d.hours as time_spent,
                    t.partner_id
                    FROM project_task t, account_analytic_line a,project_task_work d
                    where t.id = a.task_id and
                    t.id = d.task_id and d.id = a.task_time_ref_id
              
                GROUP BY
                    a.id,
                    progress,
                    year,
                    month,
                    day,
                    date_start,
                    date_end,
                    date_deadline,
                    t.user_id,
                    t.project_id,
                    t.state,
                    t.priority,
                    t.name,
                    t.company_id,
                    t.partner_id,
                    consume_time,
                    time_cost,
                    time_spent
                    
        """)

report_project_task_time_user()






#cr.execute("""
#            CREATE view report_budget_project_task_user as
#              SELECT
#                    (select 1 ) AS nbr,
#                    t.id as id,
#                    to_char(date_start, 'YYYY') as year,
#                    to_char(date_start, 'MM') as month,
#                    to_char(date_start, 'YYYY-MM-DD') as day,
#                    date_trunc('day',t.date_start) as date_start,
#                    date_trunc('day',t.date_end) as date_end,
#                    to_date(to_char(t.date_deadline, 'dd-MM-YYYY'),'dd-MM-YYYY') as date_deadline,
#--                    sum(cast(to_char(date_trunc('day',t.date_end) - date_trunc('day',t.date_start),'DD') as int)) as no_of_days,
#                    abs((extract('epoch' from (t.date_end-t.date_start)))/(3600*24))  as no_of_days,
#                    t.user_id,
#                    progress as progress,
#                    t.project_id,
#                    t.state,
#                    t.effective_hours as hours_effective,
#                    t.priority,
#                    t.name as name,
#                    t.company_id,
#                    t.partner_id,
#                    t.type_id,
#                    remaining_hours as remaining_hours,
#                    total_hours as total_hours,
#                    t.delay_hours as hours_delay,
#                    planned_hours as hours_planned,
#                    (extract('epoch' from (t.date_end-t.create_date)))/(3600*24)  as closing_days,
#                    (extract('epoch' from (t.date_start-t.create_date)))/(3600*24)  as opening_days,
#                    abs((extract('epoch' from (t.date_deadline-t.date_end)))/(3600*24))  as delay_endings_days
#              FROM project_task t
#
#                GROUP BY
#                    t.id,
#                    remaining_hours,
#                    t.effective_hours,
#                    progress,
#                    total_hours,
#                    planned_hours,
#                    hours_delay,
#                    year,
#                    month,
#                    day,
#                    create_date,
#                    date_start,
#                    date_end,
#                    date_deadline,
#                    t.user_id,
#                    t.project_id,
#                    t.state,
#                    t.priority,
#                    name,
#                    t.company_id,
#                    t.partner_id,
#                    t.type_id
#
#        """)
