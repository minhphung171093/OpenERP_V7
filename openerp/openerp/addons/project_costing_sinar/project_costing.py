from osv import fields, osv
from tools.translate import _
import netsvc
from datetime import datetime, timedelta
import datetime
from dateutil.relativedelta import relativedelta
import openerp.addons.decimal_precision as dp
import time
import tools

class project_finish_products(osv.osv):
    _name = 'project.finish.products'
    _discription = 'project finish products'
    
    _columns = { 
                 'product_id' : fields.many2one('product.product', 'Products',required=True),
                 'quantity' : fields.integer('Quantity', size= 128,required=True),
                 'done_quantity' : fields.integer('Done Quantity', size= 128,readonly=True),
                 'fin_prod_project_id' : fields.many2one('project.project', 'Project'),
                 'sale_order_id': fields.many2one('sale.order','Order Ref'),
                 'wizard_id' : fields.many2one('check.warehouse', 'Wizard'),
                }

project_finish_products()

class check_warehouse(osv.osv):
    _name = 'check.warehouse'
    _description ='Selecting Destination Warehouse'     
    _columns = {
                 'name': fields.char('Task Name', size=64),
                 'project_id': fields.many2one('project.project','Project'),
                 'assigned_id':fields.many2one('res.users','Assigned to'),
                 'planned_hours':fields.integer('Planned Hours',size=8),
                 'consume_location_id' : fields.many2one('stock.location', 'Consumed Products Location',required=True),
                 'deli_location_id' : fields.many2one('stock.location', 'Deliverables Products Location',required=True),
                 'project_finish_product_ids' : fields.one2many('project.finish.products','wizard_id','Finish Products',required=True),
                 }
     
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(check_warehouse, self).default_get(cr, uid, fields, context=context)        
        record_id = context and context.get('active_id', False) or False
        pick_obj = self.pool.get('project.project')
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        if pick:
            res.update({'project_id': pick.id})
        return res
                    
    def allow_to_send(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids,context=context)[0]
        pick_obj = self.pool.get('project.project')
        task_obj = self.pool.get('project.task')
        task_id = self.pool.get('project.task').create(cr,uid,{ 
                                                        'name' : obj.name,
                                                        'project_id' : obj.project_id.id,
                                                        'manager_id' : uid,
                                                        'user_id' : obj.assigned_id.id,
                                                        'planned_hours' : obj.planned_hours,
                                                        'consume_location_id':obj.consume_location_id.id,
                                                        'deli_location_id':obj.deli_location_id.id,
                                                        })
        if ids:
            pick_ids = pick_obj.search(cr, uid, [('id','=',obj.project_id.id)])
            for pick in pick_obj.browse(cr, uid, pick_ids):
                if pick.project_finish_product_ids:
                    for info in pick.project_finish_product_ids:
                        self.pool.get("task.finish.products").create(cr,uid, { 
                                                                    'product_id' : info.product_id.id,
                                                                    'quantity' : info.quantity,
                                                                    'fin_prod_task_id' : task_id,
                                                                    })                    
            for line in obj.project_finish_product_ids:
                new_qty = line.quantity
                if new_qty > 0:
                    self.pool.get("task.consume.products").create(cr,uid, { 
                                                                         'product_id' : line.product_id.id,
                                                                         'quantity' : new_qty,
                                                                         'plan_qty' : new_qty,
                                                                         'used_qty' : new_qty,
                                                                         'con_prod_task_id':task_id,
                                                                         'state':'done',
                                                                        })
        
        ######### Code Written By Prakash Patil ################################
        qty, estimated_qty, consumed_qty = 0, 0, 0
        inventory_obj = self.pool.get("project.inventory.info")
        for data in self.browse(cr, uid, ids):
            for idata in data.project_finish_product_ids:
                inventory_ids = inventory_obj.search(cr, uid, [('inventory_id','=',data.project_id.id), ('product_id','=',idata.product_id.id)])
                project_id = idata.fin_prod_project_id.id
                task_ids = task_obj.search(cr, uid, [('project_id','=',project_id)])
                for tsk in task_obj.browse(cr, uid, task_ids):
                    if tsk.state == 'done':
                        qty = idata.quantity
                    else:
                        qty = 0
                if inventory_ids:
                    for inv in inventory_obj.browse(cr, uid, inventory_ids):
                        inv_id = inv.id
                        estimated_qty = inv.estimated_qty
                        consumed_qty = inv.consumed_qty
                    inventory_obj.write(cr, uid, inv_id, 
                                    {
                                'estimated_qty' : estimated_qty + idata.quantity,
                                'consumed_qty' : consumed_qty + qty,
                                     })
                else:
                    inventory_obj.create(cr, uid, {
                                        'inventory_id' : obj.project_id.id,
                                        'product_id' : idata.product_id.id,
                                        'usage_qty' : 0,
                                        'estimated_qty' : idata.quantity,
                                        'consumed_qty' : 0,
                                                   })
        return { 'type':'ir.actions.act_window_close'}

check_warehouse()

class project_assign_products(osv.osv):
    _name = "project.assign.products"
    _columns = {
                'name': fields.char('Quantity',size=64,required=True),
                'product_id': fields.many2one('product.product','Products'),
                }
    
project_assign_products()

class sale_order(osv.osv):
    _inherit="sale.order"
    _description = "Sale Order Customization"
        
    def _get_actual_amt(self,cr,uid,ids,args1,args2,context=None):
        res = {}
        total = 0
        obj = self.browse(cr, uid, ids)[0]
        for line in obj.invoice_ids:
            total = total + line.amount_total
            res[obj.id] = total
        return res
    
    def _get_variation_amt(self,cr,uid,ids,args1,args2,context=None):
        res = {}
        obj = self.browse(cr, uid, ids)[0]
        total = obj.actual_amt - obj.amount_total
        res[obj.id] = total
        return res 

    _columns = {  
                 'sale_project_id':fields.many2one('project.project','Project',readonly=True, states={'draft': [('readonly', False)]}),
                 'create_project': fields.boolean('Create New Project',readonly=True, states={'draft': [('readonly', False)]}),
                 'start_date': fields.date('Expected Start Date'),
                 'end_date': fields.date('Expected End Date'),
                 'variation_amt':fields.function(_get_variation_amt, method=True, type="float", string="Variation Amount", store=True),
                 'actual_amt':fields.function(_get_actual_amt, method=True, type="float", string="Actual Amount", store=True),
               }
    
#     _defaults = {
#         'order_policy': 'prepaid',
#                  }
    
    def _check_date(self, cr, uid, ids, context=None):
        for val in self.browse(cr, uid, ids, context=context):
            if val.create_project:
                if val.start_date >= val.end_date:
                    return False
        return True
    
    _constraints = [
        (_check_date, 'Expected Start Date should be smaller than Expected End Date!!!', ['end_date'])
    ]
    
    def action_button_confirm(self, cr, uid, ids, context=None):
        res = super(sale_order, self).action_button_confirm(cr, uid, ids, context)
        for val in self.browse(cr, uid, ids, context=context):
            if val.create_project:
                if val.order_policy != 'prepaid':
                    self.create_project(cr, uid, ids, context)
        return res
    
    def onchange_project_id(self, cr, uid,ids,project_id):
        if not project_id:
            return {}
        else:
            data = self.pool.get('project.project').browse(cr, uid,project_id)
            partner_id=data.partner_id
            if partner_id:
                part = partner_id.id
                addr = self.pool.get('res.partner').address_get(cr, uid, [part], ['delivery', 'invoice', 'contact'])
                part = self.pool.get('res.partner').browse(cr, uid, part)
                pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
                payment_term = part.property_payment_term and part.property_payment_term.id or False
                fiscal_position = part.property_account_position and part.property_account_position.id or False
                dedicated_salesman = part.user_id and part.user_id.id or uid
                val = {
                       'partner_id':partner_id.id,
                       'partner_invoice_id': addr['invoice'],
                       'partner_order_id': addr['contact'],
                       'partner_shipping_id': addr['delivery'],
                       'payment_term': payment_term,
                       'fiscal_position': fiscal_position,
                       'user_id': dedicated_salesman,
                }
                if pricelist:
                    val['pricelist_id'] = pricelist
                return {'value':val}
        return {}
    
    def action_invoice_create(self, cr, uid, ids, grouped=False, states=None, date_invoice=False, context=None):
        data = super(sale_order, self).action_invoice_create(cr, uid, ids, grouped, states, date_invoice, context)
        for my_id in self.browse(cr, uid, ids, context=context):
            if my_id.create_project or my_id.sale_project_id:
                if my_id.state == 'progress':
                        self.create_project(cr, uid, ids, context)
        return data
    
    def action_ship_create(self, cr, uid, ids, context=None):
        res = super(sale_order, self).action_ship_create(cr, uid, ids, context)
        for my_id in self.browse(cr, uid, ids):
            if my_id.create_project or my_id.sale_project_id:
                if my_id.state == 'progress':
                    self.create_project(cr, uid, ids, context)
        return res

    def create_project(self,cr, uid, ids,context=None):
        sale_obj = self.browse(cr,uid,ids)     
        for lst in sale_obj:
            project_id = 0
            if not lst.sale_project_id:
                """ create project for customer """
                project= self.pool.get('project.project')
                project_id = project.create(cr, uid, {
                                                      'name' :lst.name+"_"+self.pool.get('ir.sequence').get(cr, uid, 'project.project'),
                                                      'partner_id' : lst.partner_id.id,
                                                      'contact_id' : lst.partner_invoice_id.id,
                                                      'pricelist_id' : lst.pricelist_id.id,
                                                      'to_invoice':1,
                                                      'sale_id': sale_obj[0].id,
                                                      })
                project_obj = project.browse(cr,uid,project_id)
                self.write(cr, uid, ids, {'sale_project_id' : project_id})
                self.pool.get('account.analytic.account').write(cr, uid,[project_obj.analytic_account_id.id], {'type':'view'})
                budget_obj = self.pool.get("crossovered.budget")
                budget_obj.create(cr, uid, {
                                        'name':project_obj.name,
                                        'code':project_obj.name,
                                        'date_from':lst.start_date,
                                        'date_to':lst.end_date,
                                        'project_id':project_obj.id,
                                        })

            else:
                project_id = lst.sale_project_id.id
                """finish Product lines Created """
        
            if project_id > 0:
                for obj in self.browse(cr,uid,ids):
                    for line in obj.order_line:
                        self.pool.get("project.finish.products").create(cr,uid, { 
                                                                                'product_id' : line.product_id.id,
                                                                                'quantity' : line.product_uom_qty,
                                                                                'fin_prod_project_id' : project_id,
                                                                                'sale_order_id': obj.id
                                                                               })
            return True
        
sale_order()

class project(osv.osv):
    _inherit="project.project"
    _description = "Project Pragmatic"

    _columns={
                'project_finish_product_ids' : fields.one2many('project.finish.products','fin_prod_project_id','Finish Products',readonly=True),
                'sale_ids':fields.one2many('sale.order','sale_project_id','Sale Order Ref', readonly=True),
                'purchase_ids':fields.one2many('purchase.order','purchase_project_id','Purchase Order Ref', readonly=True, domain=[('state','!=','draft')]),
                'project_task_ids':fields.one2many('project.task', 'project_id', 'Project Tasks', readonly=True),
                'product_used_ids':fields.one2many('project.inventory.info', 'inventory_id', 'Inventory Usage', readonly=True),
              }
    
    def action_process(self, cr, uid, ids, context=None):
        if context is None: context = {}
        context = dict(context, active_ids=ids, active_model=self._name)
        partial_id = self.pool.get("project.task").create(cr, uid, {}, context=context)
        return {
            'name':_("Products to Process"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'project.task',
            'res_id': 4,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': context,
        }

project()

class project_task(osv.osv):
    _inherit="project.task"
    _description = "Project Task Pragmatic"
    
    def create(self, cr, uid, vals, context=None):
        inventory_obj = self.pool.get("project.inventory.info")
        if type(context) == dict and vals.has_key('analytic_account_id'):
            context.update(analytic_account_id=vals['analytic_account_id'])
        res = super(project_task, self).create(cr, uid, vals, context=context)
        if vals['project_id'] != False:
            acc_obj = self.pool.get('account.analytic.account')
            project_obj = self.pool.get('project.project').browse(cr,uid,vals['project_id'])
            if project_obj.analytic_account_id.type == 'view':
                data = {
                        'name': vals['name'],
                        'parent_id': project_obj.analytic_account_id.id, 
                        'type': 'normal',
                        'partner_id': project_obj.partner_id.id,
                        'pricelist_id': project_obj.pricelist_id.id,
                        'task_ref_id': res,
                        }
                ana_acc_id = acc_obj.create(cr, uid, data)
                self.write(cr, uid, res,{'analytic_account_id':ana_acc_id})
                
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        if vals.has_key('project_id'):
            if vals['project_id']!= False:
                project_obj = self.pool.get('project.project').browse(cr,uid,vals['project_id'])
                acc_obj = self.pool.get('account.analytic.account')
                acc_id = acc_obj.search(cr, uid, [('task_ref_id', '=',ids[0])])                
                if acc_id:
                    acc_obj.write(cr,uid,acc_id,{
                                                  'name': vals['name'],
                                                  'parent_id': project_obj.analytic_account_id.id,
                                                  'partner_id': project_obj.partner_id.id,
                                                  'pricelist_id': project_obj.pricelist_id.id,
                                                  })
        
        return super(project_task, self).write(cr, uid, ids, vals, context=context)
    
    _columns={
              
              'task_finish_product_ids' : fields.one2many('task.finish.products','fin_prod_task_id','Finish Products'),
              'task_consume_product_ids' : fields.one2many('task.consume.products','con_prod_task_id','Consumed Products'),
              'consume_location_id' : fields.many2one('stock.location', 'Consumed Products Location', required=True),
              'deli_location_id' : fields.many2one('stock.location', 'Deliverables Products Location', required=True),
              'product_journal_id' : fields.many2one('account.analytic.journal', 'Product Analytic Journal'),
              'analytic_account_id' : fields.many2one('account.analytic.account', 'Analytic Account'),
              'sale_order_id': fields.many2one('sale.order','Order Ref'),
      }
    
    def onchange_project(self, cr, uid, id, project_id, context=None):
        res = super(project_task, self).onchange_project(cr, uid,id, project_id, context)
        if project_id and res:
            project_obj = self.pool.get('project.project').browse(cr,uid,project_id)
            if project_obj.analytic_account_id:
                res['value']['analytic_account_id'] = project_obj.analytic_account_id.id
        return res
    
    def get_journal(self, cr, uid, context=None):
        rec = self.pool.get('account.analytic.journal').search(cr,uid,[('code','=','TP')])
        if rec:
            rec = rec[0]
        if not rec:
            rec = False
        return rec
        
    _defaults ={
               'product_journal_id': get_journal
               }
    
    def unlink(self, cr, uid, ids, context=None):
        my_objs = self.browse(cr,uid,ids)
        for my_obj in my_objs:
            if my_obj.state == 'draft':
                for finish_product_line in my_obj.task_finish_product_ids:
                    for fin_prod_in_project in my_obj.project_id.project_finish_product_ids:
                        if fin_prod_in_project.product_id.id == finish_product_line.product_id.id:
                            pass            
            elif my_obj.state in ('open','pending','cancel'):
                if my_obj.task_consume_product_ids:
                    raise osv.except_osv(_('Operation Not Permitted !'), _('You can not delete tasks. I suggest you to delete consumed products First.'))
                if my_obj.work_ids:
                    raise osv.except_osv(_('Operation Not Permitted !'), _('You can not delete tasks. I suggest you to delete Task work First.'))                
                for finish_product_line in my_obj.task_finish_product_ids:
                    for fin_prod_in_project in my_obj.project_id.project_finish_product_ids:
                        if fin_prod_in_project.product_id.id == finish_product_line.product_id.id:
                            pass
            elif my_obj.state == 'done' and my_obj.project_id:
                raise osv.except_osv(_('Operation Not Permitted !'), _('You can not delete tasks As it is in done state'))        
        return super(project_task, self).unlink(cr, uid, ids, context=context)
    
    def do_open(self, cr, uid, ids, *args):
        res = super(project_task,self).do_open(cr, uid, ids, *args)
        my_obj = self.browse(cr,uid,ids)[0]
        move_obj = self.pool.get('stock.move')        
        if my_obj.task_finish_product_ids:
            for line in my_obj.task_finish_product_ids:
                source = line.product_id.product_tmpl_id.property_stock_production.id                
                data = {
                        'name':'PROD:' + my_obj.name,
                        'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'product_id': line.product_id.id,
                        'product_qty': line.quantity,
                        'product_uom': line.product_id.uom_id.id,
                        'location_id': source,
                        'location_dest_id': my_obj.deli_location_id.id,
                        'state': 'waiting',
                        'company_id': my_obj.company_id.id,
                        'finish_product_id': line.id,
                    }
                res_final_id = move_obj.create(cr, uid, data)
        return True
    
    def action_close(self, cr, uid, ids, context=None):
        inventory_obj = self.pool.get("project.inventory.info")
        res = super(project_task,self).action_close(cr, uid, ids,context)        
        con_prod_ids = self.pool.get('task.consume.products').search(cr, uid, [('con_prod_task_id', '=',ids[0])])
        move_obj = self.pool.get('stock.move')
        move_id = move_obj.search(cr, uid, [('consumed_product_id', 'in',con_prod_ids)])        
        fin_prod_ids = self.pool.get('task.finish.products').search(cr, uid, [('fin_prod_task_id', '=',ids[0])])
        move_id1 = move_obj.search(cr, uid, [('finish_product_id', 'in',fin_prod_ids)])        
        for x in move_id1:
            move_id.append(x)
        move_obj.write(cr,uid,move_id,{'state':'done'})        
        my_obj = self.browse(cr,uid,ids)[0]
        if my_obj.project_id:
            if my_obj.project_id.project_finish_product_ids:
                for line in my_obj.project_id.project_finish_product_ids:
                    for task_fin_prod_line in my_obj.task_finish_product_ids:
                        if line.product_id.id == task_fin_prod_line.product_id.id:
                            done_qty = line.done_quantity + task_fin_prod_line.quantity
                            self.pool.get('project.finish.products').write(cr,uid,line.id,{'done_quantity':done_qty}) 
                            
        ########### Code Written By Prakash Patil ######################################
        con_qty = 0
        for data in my_obj.task_consume_product_ids:
            project_id = my_obj.project_id.id
            con_qty = data.used_qty
            inventory_ids = inventory_obj.search(cr, uid, [('inventory_id','=',project_id), ('product_id','=',data.product_id.id)])
            for inv in inventory_obj.browse(cr, uid, inventory_ids):
                consumed_qty = inv.consumed_qty
                inventory_obj.write(cr, uid, inv.id,
                                    {
                                'consumed_qty' : con_qty + consumed_qty,
                                     })
        return True
    
project_task()

class project_work(osv.osv):
    _inherit = "project.task.work"
    
    def create(self, cr, uid, vals, *args, **kwargs):
        res = super(project_work,self).create(cr, uid, vals, *args, **kwargs)
        obj_timesheet = self.pool.get('hr.analytic.timesheet')
        task_obj = self.pool.get('project.task')
        context = kwargs.get('context', {})
        if not context.get('no_analytic_entry',False):
            obj_task = task_obj.browse(cr, uid, vals['task_id'])
            line_name = '%s: %s' % (tools.ustr(obj_task.name), tools.ustr(vals['name']) or '/')
            line_list = obj_timesheet.search(cr,uid,[('name','=',line_name)])
            for rec in line_list:
                analytic_line_obj = obj_timesheet.browse(cr, uid, rec)
                if analytic_line_obj.account_id.type == 'view':
                    acc_obj = self.pool.get('account.analytic.account')
                    acc_id = acc_obj.search(cr, uid, [('task_ref_id', '=',vals['task_id'])])
                    if acc_id:
                        acc_id = acc_id[0]
                        obj_timesheet.write(cr, uid, [rec], {'account_id': acc_id,'task_id':vals['task_id'],'task_time_ref_id':res}, context=context)
                    else:
                        obj_timesheet.write(cr, uid, [rec], {'task_id':vals['task_id'],'task_time_ref_id':res}, context=context)
        return res
    
    _columns={
              'invoice_line_amt' : fields.integer('Invoice Line Amt'),
             }
            
project_work()

class account_analytic_account(osv.osv):
    _inherit = 'account.analytic.account'
    _description = 'Analytic Account'
    
    _columns={
              'task_ref_id' : fields.many2one('project.task', 'Task Ref'),
    }

account_analytic_account()

class task_finish_products(osv.osv):
    _name = 'task.finish.products'
    _discription = 'task finish products'
    
    _columns = { 
                 'product_id' : fields.many2one('product.product', 'Products',required=True,readonly=True),
                 'quantity' : fields.integer('Used Quantity', size= 128,required=True,readonly=True),
                 'fin_prod_task_id' : fields.many2one('project.task', 'task Id'),
                }
    
task_finish_products()

class task_consume_products(osv.osv):
    _name = 'task.consume.products'
    _discription = 'task consume products'
    
    def create(self, cr, uid, vals, *args, **kwargs):
        parent_obj = self.pool.get('project.task').browse(cr,uid,vals['con_prod_task_id'])
        product_obj=self.pool.get('product.template').browse(cr,uid,vals['product_id'])
        if product_obj.type=='service':
            pass
        else: 
            if not parent_obj.consume_location_id:
                raise osv.except_osv(_('Warning!'), _('Consumed location is not defined'))
            result = self.pool.get('stock.location')._product_value(cr,uid,ids=[parent_obj.consume_location_id.id], field_names=['stock_real'], arg=0, context={'product_id': vals['product_id']})
            if result[parent_obj.consume_location_id.id]['stock_real'] < vals['quantity']:
                pass
        vals['state']='open'
        res = super(task_consume_products,self).create(cr, uid, vals, *args, **kwargs)
        self.create_stock_move(cr, uid, [res], vals)
        if kwargs:
            self.create_analytic_line(cr, uid, [res], vals, kwargs)
        else:
            self.create_analytic_line(cr, uid, [res], vals)
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        my_obj = self.browse(cr,uid,ids)[0]
        parent_obj = self.pool.get('project.task').browse(cr,uid,my_obj.con_prod_task_id.id)
        if vals.has_key('product_id'):
            result = self.pool.get('stock.location')._product_value(cr,uid,ids=[parent_obj.consume_location_id.id], field_names=['stock_real'], arg=0, context={'product_id': vals['product_id']})
            product_obj=self.pool.get('product.template').browse(cr,uid,vals['product_id'])
        
            if product_obj.type=='service':
                pass
            else: 
                if result[parent_obj.consume_location_id.id]['stock_real'] < vals['quantity']:
                    pass
            vals['state']='open'
            self.create_stock_move(cr, uid, ids, vals)
        self.create_analytic_line(cr, uid, ids, vals)
        return super(task_consume_products, self).write(cr, uid, ids, vals, context=context)
    
    def unlink(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        move_id = move_obj.search(cr, uid, [('consumed_product_id', '=',ids[0])])
        move_obj.write(cr,uid,move_id,{'state':'cancel'})        
        ana_acc_line = self.pool.get('hr.analytic.timesheet')
        rec_ids = ana_acc_line.search(cr, uid, [('task_cons_prod_ref_id', '=',ids[0])])
        ana_acc_line.unlink(cr,uid,rec_ids)        
        return super(task_consume_products, self).unlink(cr, uid, ids, context=context)
    
    def create_stock_move(self,cr,uid,ids,vals):
        task_id = 0
        if vals.has_key('con_prod_task_id'):
            task_id = vals['con_prod_task_id']
        else:
            my_obj = self.browse(cr,uid,ids)[0]
            task_id = my_obj.con_prod_task_id.id            
        parent_obj = self.pool.get('project.task').browse(cr,uid,task_id)
        if vals.has_key('product_id'):
            product_obj = self.pool.get('product.product').browse(cr,uid,vals['product_id'])        
            dest = product_obj.product_tmpl_id.property_stock_production.id
        move_obj = self.pool.get('stock.move')        
        if vals.has_key('con_prod_task_id'):
            data = {
                    'name':'PROD:' + parent_obj.name,
                    'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'product_id': vals['product_id'],
                    'product_qty': vals['quantity'],
                    'product_uom': product_obj.uom_id.id,
                    'location_id': parent_obj.consume_location_id.id,
                    'location_dest_id': dest,
                    'state': 'assigned',
                    'company_id': parent_obj.company_id.id,
                    'consumed_product_id': ids[0],
                }
            res_final_id = move_obj.create(cr, uid, data)
        else:
            move_id = move_obj.search(cr, uid, [('consumed_product_id', '=',ids[0])])
            move_obj.write(cr,uid,move_id,{'product_qty':vals['quantity']})
        return True
    
    def create_analytic_line(self,cr,uid,ids,vals,kwargs=None):
        my_obj = self.browse(cr,uid,ids)[0]        
        task_id = 0
        prod_id = 0
        amount = 0
        if vals.has_key('con_prod_task_id'):
            task_id = vals['con_prod_task_id']
        else:
            my_obj = self.browse(cr,uid,ids)[0]
            task_id = my_obj.con_prod_task_id.id
        parent_obj = self.pool.get('project.task').browse(cr,uid,task_id)        
        acc_obj = self.pool.get('account.analytic.account')
        acc_id = acc_obj.search(cr, uid, [('task_ref_id', '=',parent_obj.id)])
        if acc_id:
            acc_id = acc_id[0]
        else:
            if kwargs:
                acc_id = kwargs['context']['analytic_account_id']        
        a = my_obj.product_id.product_tmpl_id.property_account_expense.id
        if not a:
            a = my_obj.product_id.categ_id.property_account_expense_categ.id
            if not a:
                raise osv.except_osv(_('Bad Configuration !'),
                        _('No product and product category property account defined on the related employee.\nFill in the timesheet tab of the employee form.'))
        if vals.has_key('con_prod_task_id'):
            if parent_obj.project_id:
                to_invoice = parent_obj.project_id.to_invoice.id
            else:
                to_invoice = ''
            data = {
                    'name': parent_obj.name + " : " + my_obj.product_id.name,
                    'amount': 0.0,
                    'account_id': acc_id,
                    'general_account_id': a,
                    'journal_id': parent_obj.product_journal_id.id,
                    'product_id': my_obj.product_id.id,
                    'unit_amount': my_obj.quantity,
                    'product_uom_id': my_obj.product_id.uom_id.id,
                    'task_cons_prod_ref_id':my_obj.id,
                    'to_invoice': to_invoice,
                    'task_id':parent_obj.id
                    }
            rec = self.pool.get('hr.analytic.timesheet').create(cr,uid,data)
            amount = data['unit_amount']
            prod_id = data['product_id']
            journal_id = data['journal_id']
        else:
            if vals.has_key('product_id'):
                prod_id = vals['product_id']
            if vals.has_key('quantity'):
                amount = vals['quantity']
            journal_id = parent_obj.product_journal_id.id
            rec = self.pool.get('hr.analytic.timesheet').search(cr, uid, [('task_cons_prod_ref_id', '=',ids[0])])
            rec = rec[0]
        unit = False
        obj_timesheet = self.pool.get('hr.analytic.timesheet')
        amount_unit = obj_timesheet.on_change_unit_amount(cr, uid, rec,
            prod_id, amount, False, unit,journal_id, context=None)
        if amount_unit and 'amount' in amount_unit.get('value',{}):
            updv = { 'amount': amount_unit['value']['amount'] }
            obj_timesheet.write(cr, uid, [rec], updv, context=None)
        return True
    
    _columns = { 
                 'product_id' : fields.many2one('product.product', 'Products',required=True),
                 'quantity' : fields.integer('Quantity', size= 128,required=True),
                 'invoice_line_amt': fields.integer('Invoice Amount', size= 128),
                 'plan_qty' : fields.integer('Estimated Quantity', size= 128,readonly=True,required=True,states={'open':[('readonly',True)],'draft':[('readonly',False)]}),
                 'used_qty' : fields.integer('Used Quantity', size= 128,required=True),
                 'con_prod_task_id' : fields.many2one('project.task', 'Task Id'),
                 'state': fields.selection([('draft', 'Draft'),('open', 'Open'),('invoiced', 'Invoiced')], 'State', readonly=True, required=True),
                 }
    
    _defaults={
               'state': lambda *a: 'draft',
               }
    
    def on_change_plan_qty(self,cr,uid,ids,plan_qty):
        result = {}
        result['quantity'] = plan_qty
        result['used_qty'] = plan_qty
        return {'value': result}
    
    def on_change_used_qty(self,cr,uid,ids,used_qty):
        result = {}
        result['quantity'] = used_qty
        return {'value': result}
    
task_consume_products()

class account_analytic_line(osv.osv):

    _inherit = 'account.analytic.line'
    _description = 'Analytic Account line'
    
    _columns={
              'task_time_ref_id' : fields.many2one('project.task.work', 'Task Work Ref'),
              'task_cons_prod_ref_id' : fields.many2one('task.consume.products', 'Task Consumed Product Ref'),
              'task_id' : fields.many2one('project.task', 'Project Task'),
    }

account_analytic_line()

class hr_analytic_timesheet(osv.osv):

    _inherit = 'hr.analytic.timesheet'
    _description = 'HR Analytic Timesheet Inherited'
    
    _columns={
              }

hr_analytic_timesheet()

class stock_move(osv.osv):
    _inherit = 'stock.move'
    _discription = 'inherit stock move class'
    
    _columns = { 
                'consumed_product_id' : fields.many2one('task.consume.products', 'Consumed Product',readonly=True),
                'finish_product_id' : fields.many2one('task.finish.products', 'Finish Product',readonly=True),
                }
    
stock_move()

class hr_timesheet_invoice_create(osv.osv_memory):

    _inherit = 'hr.timesheet.invoice.create'
    _description = 'Create invoice from timesheet'
    _columns = {
                }

hr_timesheet_invoice_create()

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _discription = 'inherit account invoice class'
    
    _columns = { 
                'task_id' : fields.many2one('project.task', 'Ref Project Task ID'),
                'desc_of_charges' : fields.text('Desc. Of Charges'),
                'pro_status' : fields.char('Project Status', readonly=True),
                'disc': fields.float('Discount (%)', digits_compute= dp.get_precision('Discount')),
                'inv_line_tax_id': fields.many2many('account.tax', 'account_invoice_tax_rel_info', 'invoice_line_id', 'tax_id', 'Taxes', domain=[('parent_id','=',False)]),
                }
    
    _defaults = {
         'disc' : 0.0        
                 }
    
    def create(self, cr, uid, vals, context=None):
        if vals and vals.has_key('inv_line_tax_id') and vals.has_key('disc'):
            tax = vals['inv_line_tax_id']
            discount = vals['disc']
            for i in range(len(vals['invoice_line'])):
                vals['invoice_line'][i][2]['invoice_line_tax_id'] = tax
                vals['invoice_line'][i][2]['discount'] = discount
        return super(account_invoice, self).create(cr, uid, vals, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if not type(ids) is list:
            ids = [ids]

        invoice_line_obj = self.pool.get("account.invoice.line")
        inv_line_ids = invoice_line_obj.search(cr, uid, [('invoice_id','=',ids[0])])
        if vals:
            if vals.has_key('disc'):
                invoice_line_obj.write(cr, uid, inv_line_ids, {'discount':vals['disc']}, context=context)
            if vals.has_key('inv_line_tax_id'):
                invoice_line_obj.write(cr, uid, inv_line_ids, {'invoice_line_tax_id':vals['inv_line_tax_id']}, context=context)
            for data in self.browse(cr, uid, ids, context=context):
                tax = data.inv_line_tax_id
                discount = data.disc
            if vals.has_key('invoice_line'):
                for i in range(len(vals['invoice_line'])):
                    if vals['invoice_line'][i][0] == 0:
                        vals['invoice_line'][i][2]['discount'] = discount
                        vals['invoice_line'][i][2]['tax'] = tax
        return super(account_invoice, self).write(cr, uid, ids, vals, context=context)
    
    def invoice_validate(self, cr, uid, ids, context=None):
        tax_obj = self.pool.get("tax.invoice")
        tax_line_obj = self.pool.get("tax.invoice.line")
        di = {}
        res = super(account_invoice, self).invoice_validate(cr, uid, ids, context=context)
        for data in self.browse(cr, uid, ids):
            li = [dt.id for dt in data.inv_line_tax_id]
            di['inv_id'] = data.id
            di['partner_id'] = data.partner_id.id
            di['currency_id'] = data.currency_id.id
            di['company_id'] = data.company_id.id
            di['date_invoice'] = data.date_invoice
            di['disc'] = data.disc
            di['state'] = 'draft'
            di['inv_line_tax_id'] = [(6, 0, li)] 
            di['amount_untaxed'] = data.amount_untaxed
            di['amount_tax'] = data.amount_tax
            di['vat'] = (data.amount_tax * 10)/100
            di['amount_total'] = data.amount_total
            di['residual'] = data.residual
            tax_id = tax_obj.create(cr, uid, di, context=context)
            for info in data.invoice_line:
                tax_line_obj.create(cr, uid, {
                        'invoice_id':tax_id,
                        'product_id':info.product_id.id,
                        'uos_id':info.uos_id.id,
                        'account_id':info.account_id.id,
                        'price_unit':info.price_unit,
                        'price_subtotal':info.price_subtotal,
                        'quantity':info.quantity
                                 }, context=context)                
        return res
            
account_invoice()
         
class purchase_order(osv.osv):
    _inherit = "purchase.order"
    _description = "Purchase Order Customization"
    
    _columns = {
        'purchase_project_id':fields.many2one('project.project','Project',readonly=True, states={'draft': [('readonly', False)]}),
        'po_history_ids':fields.one2many('purchase.history', 'history_id', 'PO History', readonly=True),
        'disc': fields.float('Discount (%)', digits_compute= dp.get_precision('Discount')),

                }
    
    _defaults = {
        'invoice_method' : 'picking',
                 }
    
    def create(self, cr, uid, vals, context=None):
        line_obj = self.pool.get("purchase.order.line")
        res_id = super(purchase_order, self).create(cr, uid, vals, context=context)
        line_ids = line_obj.search(cr, uid, [('order_id','=',res_id)])
        if vals and vals.has_key('disc') and line_ids:
            line_obj.write(cr, uid, line_ids, {'discount': float(vals['disc'])})
        return res_id
        
    def write(self, cr, uid, ids, vals, context=None):
        po_history_obj = self.pool.get("purchase.history")
        product_obj = self.pool.get("product.product")
        pricelist_obj = self.pool.get("product.pricelist")
        project_obj = self.pool.get("project.project")
        warehouse_obj = self.pool.get("stock.warehouse")
        uom_obj = self.pool.get("product.uom")
        purchase_obj = self.pool.get("purchase.order.line")
        res_obj = self.pool.get("res.company")
        t = time.strftime('%Y-%m-%d %H:%M:%S')
        today_time = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
        line_ids = purchase_obj.search(cr, uid, [('order_id','=',ids[0])])
        if vals:
            try:
                for data in vals:
                    if data == 'order_line':
                        for j in range(len(vals['order_line'])):
                            if isinstance(vals['order_line'][j][2], dict):
                                if not vals['order_line'][j][1]:
                                    product_ids = product_obj.search(cr, uid, [('id','=',vals['order_line'][j][2]['product_id'])])
                                    prod_name = [info.name_template for info in product_obj.browse(cr, uid, product_ids) if product_ids]
                                    po_history_obj.create(cr, uid, {'history_id': ids[0], 'date':today_time, 'description':prod_name[0] +' Product is added in order line.'})
                                if vals['order_line'][j][1]:
                                    purchase_ids = purchase_obj.search(cr, uid, [('id','=',vals['order_line'][j][1])])
                                    prod_name = [info.product_id.name_template for info in purchase_obj.browse(cr, uid, purchase_ids) if purchase_ids]
                                    for i in range(len(vals['order_line'][j][2].items())):
                                        if vals['order_line'][j][2].items()[i][0] != 'taxes_id':
                                            if str(vals['order_line'][j][2].items()[i][0]) == 'product_qty':
                                                po_history_obj.create(cr, uid, {'history_id': ids[0], 'date':today_time, 'description':prod_name[0] +' product quantity '
                                                                +' changed to '+str(vals['order_line'][j][2].items()[i][1])})
                                            if str(vals['order_line'][j][2].items()[i][0]) == 'product_id':
                                                po_history_obj.create(cr, uid, {'history_id': ids[0], 'date':today_time, 'description':prod_name[0] +' product name '
                                                                +' changed to '+str(vals['order_line'][j][2]['name'])})
                                            if str(vals['order_line'][j][2].items()[i][0]) == 'price_unit':
                                                po_history_obj.create(cr, uid, {'history_id': ids[0], 'date':today_time, 'description':prod_name[0] +' Product Price '
                                                                +' changed to '+str(vals['order_line'][j][2].items()[i][1])})
                                            if str(vals['order_line'][j][2].items()[i][0]) == 'date_planned':
                                                po_history_obj.create(cr, uid, {'history_id': ids[0], 'date':today_time, 'description':prod_name[0] +' Product Scheduled Date '
                                                                +' changed to '+str(vals['order_line'][j][2].items()[i][1])})
                                            if str(vals['order_line'][j][2].items()[i][0]) == 'product_uom':
                                                uom_ids = uom_obj.search(cr, uid, [('id','=',vals['order_line'][j][2].items()[i][0])])
                                                uom = [um.name for um in uom_obj.browse(cr, uid, uom_ids)]
                                                po_history_obj.create(cr, uid, {'history_id': ids[0], 'date':today_time, 'description':prod_name[0] +' Product UOM '
                                                                 +' changed to '+uom[0]})
                    if data == 'partner_id':
                        res_ids = self.pool.get("res.partner").search(cr, uid, [('id','=',vals[data])])
                        partner_name = [res.name for res in self.pool.get("res.partner").browse(cr, uid, res_ids)]
                        po_history_obj.create(cr, uid, {'history_id': ids[0], 'date':today_time, 'description': 'Supplier' + ' changed to '+str(partner_name[0])})
                    if data == 'date_order':
                        po_history_obj.create(cr, uid, {'history_id': ids[0], 'date':today_time, 'description': 'Order Date' + ' changed to '+vals[data]})
                    if data == 'partner_ref' and vals[data] != False:
                        po_history_obj.create(cr, uid, {'history_id': ids[0], 'date':today_time, 'description': 'Supplier Reference' + ' changed to '+vals[data]})
                    if data == 'partner_ref' and vals[data] == False:
                        po_history_obj.create(cr, uid, {'history_id': ids[0], 'date':today_time, 'description':'Supplier Reference' +' is removed from purchase order.'})
                    if data == 'pricelist_id':
                        price_ids = pricelist_obj.search(cr, uid, [('id','=',vals[data])])
                        price = [pr.name for pr in pricelist_obj.browse(cr, uid, price_ids)]
                        po_history_obj.create(cr, uid, {'history_id': ids[0], 'date':today_time, 'description': 'Pricelist' + ' changed to '+str(price[0])})
                    if data == 'warehouse_id' and vals[data] != False:
                        warehouse_ids = warehouse_obj.search(cr, uid, [('id','=',vals[data])])
                        ware = [pr.name for pr in warehouse_obj.browse(cr, uid, warehouse_ids)]
                        po_history_obj.create(cr, uid, {'history_id': ids[0], 'date':today_time, 'description': 'Destination Warehouse' + ' changed to '+str(ware[0])})
                    if data == 'warehouse_id' and vals[data] == False:
                        po_history_obj.create(cr, uid, {'history_id': ids[0], 'date':today_time, 'description':'Destination Warehouse' +' is removed from purchase order.'})
                    if data == 'origin' and vals[data] != False:
                        po_history_obj.create(cr, uid, {'history_id': ids[0], 'date':today_time, 'description': 'Source Document' + ' changed to '+vals[data]})
                    if data == 'origin' and vals[data] == False:
                        po_history_obj.create(cr, uid, {'history_id': ids[0], 'date':today_time, 'description':'Source Document' +' is removed from purchase order.'})
                    if data == 'purchase_project_id' and vals[data] != False:
                        info_ids = self.search(cr, uid, [('id','=', ids[0])])
                        for dt in self.browse(cr, uid, info_ids):
                            so = dt.purchase_project_id.name
                        po_history_obj.create(cr, uid, {'history_id': ids[0], 'date':today_time, 'description': 'Previous Project Name ' +so})
                    if data == 'purchase_project_id' and vals[data] == False:
                        po_history_obj.create(cr, uid, {'history_id': ids[0], 'date':today_time, 'description':'Project' +' is removed from purchase order.'})
                    if data == 'company_id':
                        res_ids = res_obj.search(cr, uid, [('id','=',vals[data])])
                        res = [info.name for info in res_obj.browse(cr, uid, res_ids)]
                        po_history_obj.create(cr, uid, {'history_id': ids[0], 'date':today_time, 'description': 'Comapany' + ' changed to '+res[0]})
            except:
                print'We have got an error....'
            for info in self.browse(cr, uid, ids):
                name = info.name
            if '/' in name:
                name = name.split('/')[0]
            po_ids1 = po_history_obj.search(cr, uid, [('history_id','=',ids[0])])
            li = [data.id for data in po_history_obj.browse(cr, uid, po_ids1)]
            if li and len(li) < 10:
                vals['name'] = str(name) + '/00'+ str(len(li))
            if li and len(li) > 10:
                vals['name'] = str(name) + '/0'+ str(len(li))
            if vals and vals.has_key('disc'):
                purchase_obj.write(cr, uid, line_ids, {'discount': float(vals['disc'])})
        return super(purchase_order, self).write(cr, uid, ids, vals)
    
    def wkf_confirm_order(self, cr, uid, ids, context=None):
        res = super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context=context)
        task_obj = self.pool.get("project.task")
        inventory_obj = self.pool.get("project.inventory.info")
        for info in self.browse(cr, uid, ids):
            if info.purchase_project_id:
                for var in info.order_line:
                    task_ids = task_obj.search(cr, uid, [('project_id','=',info.purchase_project_id.id)])
                    estimated_qty, consumed_qty, qty = 0, 0, 0  
                    for task in task_obj.browse(cr, uid, task_ids):
                        for tdata in task.task_consume_product_ids:
                            if tdata.product_id.id == var.product_id.id:
                                estimated_qty += tdata.plan_qty
                                if tdata.state == 'done':
                                    consumed_qty += tdata.used_qty
                                else:
                                    consumed_qty = 0
                    inventory_ids = inventory_obj.search(cr, uid, [('product_id','=',var.product_id.id), ('inventory_id','=',info.purchase_project_id.id)])
                    if inventory_ids:
                        for inv in inventory_obj.browse(cr, uid, inventory_ids):
                            qty += inv.usage_qty
                        inventory_obj.write(cr, uid, inv.id, {
                                        'usage_qty' : qty + var.product_qty,
                                                   })
                    else:
                        inventory_obj.create(cr, uid, {
                                        'inventory_id' : info.purchase_project_id.id,
                                        'product_id' : var.product_id.id,
                                        'usage_qty' : var.product_qty,
                                        'estimated_qty' : estimated_qty,
                                        'consumed_qty' : consumed_qty,
                                                   })
        return res
        
purchase_order()   

class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"
    _description = "Purchase Order Line Customization"
    
    _columns = {
                }
    
    def unlink(self, cr, uid, ids, context=None):
        po_history_obj = self.pool.get("purchase.history")
        purchase_id = [line.order_id.id for line in self.browse(cr, uid, ids)]
        t = time.strftime('%Y-%m-%d %H:%M:%S')
        today_time = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
        if purchase_id:
            prod_name = [line.name for line in self.browse(cr, uid, ids)]
            po_history_obj.create(cr, uid, {'history_id': purchase_id[0], 'date':today_time, 'description':prod_name[0] +' Product is removed from order line.'})
        return super(purchase_order_line, self).unlink(cr, uid, ids, context=context)

purchase_order_line()
    
class purchase_history(osv.osv):
    _name = "purchase.history"
    _description = "Purchase Order History"
    
    _columns = {
        'history_id':fields.many2one('purchase.order', 'History Info'),
        'date':fields.datetime('Date & Time'),
        'description':fields.text('Description'),
                }
    
purchase_history() 
    
class crossovered_budget(osv.osv):
    _inherit = "crossovered.budget"
    _description = "Budget Customization"
    
    _columns = {
        'project_id': fields.many2one('project.project','Project'),
                }
    
crossovered_budget()

class crossovered_budget_lines(osv.osv):
    _inherit = "crossovered.budget.lines"
    
    def _theo(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = self._theo_amt(cr, uid, [line.id], context=context)[line.id]
            self.write(cr,uid,line.id,{'theoritical_amt':res[line.id]})
        return res
    
    _columns = {
                'theoritical_amount':fields.function(_theo, method=True, string='Theoretical Amount', type='float', digits_compute=dp.get_precision('Account')),
                'practical_amt':fields.float('Practical Amt'),
                'theoritical_amt':fields.float('Theoretical Amt'),
                }

crossovered_budget_lines()
    
class project_inventory_info(osv.osv):
    _name = "project.inventory.info"
    _description = "Project Inventory Info"
    
    _columns = {
        'inventory_id' : fields.many2one('project.project', 'Inventory ID'),
        'product_id' : fields.many2one('product.product', 'Product'),
        'usage_qty' : fields.integer('Usage Qty'),
        'estimated_qty' : fields.integer('Estimated Qty'),
        'consumed_qty' : fields.integer('Consumed Qty'),
                }  

project_inventory_info()   

class stock_picking_in(osv.osv):
    _inherit = "stock.picking.in"
    _description = "Incoming Shipments"
    
    _columns = {
                }
    
    def view_picking_shipment(self, cr, uid, ids, context=None):
        pick_obj = self.pool.get("stock.picking")
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        for data in self.browse(cr, uid, ids):
            purchase_id = data.purchase_id.id
        result = mod_obj.get_object_reference(cr, uid, 'stock', 'action_picking_tree4')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        obj = pick_obj.search(cr, uid, [('purchase_id','=',purchase_id)])
        del result['search_view_id']
        if len(obj)>1:
            result['domain'] = "[('id','in',["+','.join(map(str, obj))+"])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'stock', 'action_picking_tree4')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = obj and obj[0] or False
        return result
       
stock_picking_in()
        
