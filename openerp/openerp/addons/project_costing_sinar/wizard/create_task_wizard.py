import netsvc
import time
import operator
from osv import osv,fields
from tools.translate import _

class create_task_wizard(osv.osv_memory):
    _name = 'create.task.wizard'
    _description = 'Create Task Wizard'
   
    def default_get(self, cr, uid, fields, context=None):
        """
         To get default values for the object.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary with default values for all field in ``fields``
        """
        if context is None:
            context = {}
        res = super(create_task_wizard, self).default_get(cr, uid, fields, context=context)
        record_id = context and context.get('active_id', False) or False
        project_obj = self.pool.get('project.project').browse(cr, uid, record_id)
        if project_obj:
            for line in project_obj.project_finish_product_ids:
                return_id = 'return%s'%(line.id)
                res[return_id] = line.remain_qty
                
                
        return res

    def view_init(self, cr, uid, fields_list, context=None):
        print "KKK>>>>>>>>>>>>>",fields_list
        """
         Creates view dynamically and adding fields at runtime.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return: New arch of view with new columns.
        """
        if context is None:
            context = {}
        res = super(create_task_wizard, self).view_init(cr, uid, fields_list, context=context)
        record_id = context and context.get('active_id', False)
        if record_id:
            project_obj = self.pool.get('project.project').browse(cr, uid, record_id)
            valid_lines = 0
            for line in project_obj.project_finish_product_ids:
                if line.remain_qty > 0:
                    
                    valid_lines += 1
                print "KKK>>>???????",self._columns
                if 'action_state' not in self._columns:
                    self._columns['name'] = fields.char(string='Task Summary',size=64, required=True)
                    self._columns['sale_id'] = fields.many2one('sale.order',string='Sale Order Id',required=True)
                    print"actionactionaction>>>>>>>>>>>>",self._columns
                if 'return%s'%(line.id) not in self._columns:
                    self._columns['return%s'%(line.id)] = fields.float(string=line.product_id.name, required=True)
                    print"returnreturn>>>>>>>>>>>>",self._columns
                    
            if not valid_lines:
                raise osv.except_osv(_('Warning !'), _("There are no products available to create task from wizard!"))
        return res

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        """
         Changes the view dynamically
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return: New arch of view.
        """
        res = super(create_task_wizard, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar,submenu=False)
        record_id = context and context.get('active_id', False)
        print "record_id",record_id
        active_model = context.get('active_model')
        print "active_model",active_model
        if  active_model != 'project.project':
            return res
        if record_id:
            #print "aarch_lst------------->>",arch_lst
            project_obj = self.pool.get('project.project').browse(cr, uid, record_id)
            return_history = {}
            res['fields'].clear()
            arch_lst=['<?xml version="1.0"?>', '<form string="%s">' % _('Return lines'), '<label string="%s" colspan="4"/>' % _('Fill all information with quantities of products develop by this task.')]
            arch_lst.append('<field name="name"/>\n<newline/>')
            res['fields']['name']={'string':_('Task Summary'), 'type':'char','size': 64,'required':True,}
            arch_lst.append('<field name="sale_id"/>\n<newline/>')
            res['fields']['sale_id']={'string':_('Sale Order'), 'type':'many2one','relation':'sale.order','required':True,}
            arch_lst.append('<separator string="Product Details"/>\n<newline/>')
            print "project_obj",project_obj
            for m in project_obj.project_finish_product_ids:
                print "m",m
                arch_lst.append('<field name="return%s"/>\n<newline/>' % (m.id,))
                res['fields']['return%s' % m.id]={'string':m.product_id.name, 'type':'float', 'required':True}
                res.setdefault('returns', []).append(m.id)
           # arch_lst.append('<field name="name1"/>')
            arch_lst.append('<group col="2" colspan="4">')
            arch_lst.append('<button icon="gtk-cancel" special="cancel" string="Cancel" />')
            arch_lst.append('<button name="create_task" string="Process" colspan="1" type="object" icon="gtk-apply" />')
            arch_lst.append('</group>')
            arch_lst.append('</form>')
            res['arch'] = '\n'.join(arch_lst)
            print "resresres------------->>",res
        return res
    
    def create_task(self, cr, uid, ids, context=None):
        #raise osv.except_osv(_('Warning !'), _("HIIIIIIIIIII"))
        record_id = context and context.get('active_id', False)
        data = self.read(cr, uid, ids[0])
       
        #data.name
        print "HERE IS DATA OF ------------->",data
        task= self.pool.get('project.task')
       # raise osv.except_osv(_('Warning !'), _(record_id))
        for make in self.browse(cr, uid, ids, context=context):
            hh = make
            raise osv.except_osv(_('Warning !'), _(hh))
            task_id = task.create(cr, uid, {
                                      'name' :data['name1'],
                                      'project_id' : record_id,
                                      'sale_order_id':data['sale_id']
                                      })
            print "task_id",task_id
        obj = self.pool.get('project.project').browse(cr,uid,record_id)
        for line in obj.project_finish_product_ids:
            print "HI quty is ----->>>>",str(line.id)
            #data['return'+str(line.id)+']'
            new_qty = data['return1']
            print "new_qty",new_qty
            if new_qty > 0:
                if (line.remain_qty - new_qty) < 0:
                    raise osv.except_osv(_('Warning !'), _("Quantity of Product '%s' is not valid!"% line.product_id.name))
                self.pool.get("task.finish.products").create(cr,uid, { 
                                                                     'product_id' : line.product_id.id,
                                                                     'quantity' : new_qty,
                                                                     'fin_prod_task_id' : task_id,
                                                                     
                                                                    })
                remain_qty = line.remain_qty - new_qty
                self.pool.get("project.finish.products").write(cr,uid,line.id,{'remain_qty':remain_qty})
        return {'type':'ir.actions.act_window_close'}

create_task_wizard()