# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
import csv


class res_partner(osv.osv):
    _inherit = 'res.partner'
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context={}, count=False):
        if context and context.get('parent_user'):
            user = self.pool.get('res.users').browse(cr,uid,uid)
            if user.parent_user:
                user_list = self.pool.get('res.users').search(cr,uid,[('parent_user','=',user.parent_user.id)])
            if args:
                for arg in args:
                    if arg == 'user_ids':
                        arg[2] = user_list
        res= super(res_partner,self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
        return res
res_partner()


class res_users(osv.osv):
    _inherit = 'res.users'

    def name_get(self,cr, user, ids, context={}):
        if context.get('parent_user'):
            user = 1
        return super(res_users, self).name_get(cr,user,ids,context=context)

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context={}, count=False):
        if context.get('parent_user'):
            uid = 1
        res= super(res_users,self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
        return res

    def create(self, cr, uid, vals, context={}):
        id = super(res_users, self).create(cr, uid, vals, context)
        if not vals.get('parent_user', False):
            self.write(cr, uid, id, {'parent_user': id})
        return id

    def write(self, cr, uid, ids, vals, context={}):
        if vals.get('user_list'):
            return super(res_users, self).write(cr, 1, ids, vals, context)
        this_user = super(res_users,self).write(cr,uid,ids,vals,context=context)
        all_user = []
        if not isinstance(ids,list):
            ids = [ids]
        for user in self.browse(cr,uid,ids):
            all_user.extend(self.search(cr,uid,[('parent_user','=',user.parent_user.id),('parent_user','!=',None)]))
        if vals.get('company_id'):
            vals.pop('company_id')
        if vals.get('login'):
            vals.pop('login')
        if vals.get('company_ids'):
            vals.pop('company_ids')
        if vals.get('name'):
            vals.pop('name')
        if vals.get('parent_user'):
            vals.pop('parent_user')
        super(res_users,self).write(cr,uid,all_user,vals,context=context)
        return this_user



    _columns = {
        'parent_user': fields.many2one('res.users','Parent User'),
        'user_list':fields.many2one('res.users','Switch To User')
    }

    def get_xml_id(self,cr,uid,group_id,context=None):
        model_data_id = self.pool.get('ir.model.data').search(cr,uid,[('model','=','res.groups'),('res_id','=',group_id)])
        if model_data_id:
            model_data = self.pool.get('ir.model.data').browse(cr,uid,model_data_id[0])
            return model_data.module+'.'+model_data.name

    def get_import_file(self,cr,uid,ids,context=None):
        login = False
        password = False
        for user in self.browse(cr,1,ids):
            if user.user_list:
                if user.user_list.parent_user and user.user_list.parent_user == user.parent_user:
                    login = user.user_list.login
                    password = user.user_list.password
        return {
            'type': 'ir.actions.client',
            'tag': 'reload_login',
            'params':{'login':login,'password':password,'dbname':cr.dbname},
        }
    def get_import_file2(self,cr,uid,ids,context=None):
        read_file_path = "C:\Users\Administrator\Desktop\\User Access List.csv"
        result_file_path  = "C:\Users\Administrator\Desktop\\User Access List-import.csv"
        f = open(read_file_path, 'rb')
        c = csv.reader(f, delimiter=';', quotechar='"')
        group_list = ['Sales','Project','Knowledge','Warehouse','Manufacturing',
                      'Accounting & Finance',	'Purchase Requisition',
                      'Purchases',	'Human Resources',	'Sharing',		'Multi Currencies',
                      'Costing Method',	'Analytic Accounting',	'Sales Pricelists',
                      'Purchase Pricelists',	'Manage Multiple Units of Measure',
                      'Manage Properties of Product',
                      'Manage Product Packaging',	'Check Total on supplier invoices',	'Pro-forma Invoices',
                      'Manage Serial Numbers',	'Manage Logistic Serial Numbers',
                      'Manage Multiple Locations and Warehouses',
                      'Manage Inventory valuation',	'Analytic Accounting for Purchases',
                      'Enable Invoicing Delivery orders',	'View Online Payment Options',
                      "Task's Work on Tasks",
                      'Mandatory use of templates in contracts'	,
                      'Analytic Accounting for Sales',	'Discount on lines',	'Addresses in Sales Orders',
                      'Enable Invoicing Sales order lines',
                      'Task Delegation	Time Estimation on Tasks',
                      'Notes / Fancy mode',
                      'Manage Fund Raising',
                      'Attendances',
                      'Manage Routings',
                      'Multi Companies',	'Technical Features',
                      'Contact Creation	Anonymous',	'Accounting / Payments','Portal',
                      'Survey/User']
        group_list2 = {}
        for app, kind, gs in self.pool.get('res.groups').get_groups_by_application(cr, uid, context):
            if app and app.name in group_list:
                index = group_list.index(app.name)
                temp_list = {}
                for group in gs:
                    xml_id = self.get_xml_id(cr,uid,group.id)
                    if 'user' in group.name or 'User' in group.name:
                        temp_list['user'] = xml_id
                    elif 'manager' in group.name or 'Manager' in group.name:
                        temp_list['manager'] = xml_id
                    else:
                        temp_list['other'] = xml_id
                group_list2[index] = temp_list
            for group in gs:
                if group.name in group_list:
                    xml_id = self.get_xml_id(cr,uid,group.id)
                    index = group_list.index(group.name)
                    group_list2[index] = {'other':xml_id}
        user_list = {}
        user_company = False
        for r in c:
            r = [x.decode('windows-1252').strip() for x in r]
            if r[1] != '':
                user_group = ''
                for i in range(4,53):
                    if r[i] != '':
                        group_external_id = group_list2.get(i-4)
                        if group_external_id:
                            if r[3] == 'U':
                                group_external_id = group_external_id.get('user') or group_external_id.get('other') or group_external_id.get('manager')
                            elif r[3] == 'S' or r[3] == 'M':
                                group_external_id = group_external_id.get('manager') or group_external_id.get('user') or group_external_id.get('other')
                            else:
                                group_external_id = group_external_id.get('other') or group_external_id.get('user') or group_external_id.get('manager')
                            user_group = user_group + ',' + group_external_id
                if not user_list.get(r[1]):
                    user_list[r[1]] = [r[53],r[1],r[53],'1',user_group[1:],user_company,main_company,r[53]]
                else:
                    user_list[r[1]+'-'+main_company] = [r[53]+'-'+main_company,r[1]+'-'+main_company,r[53]+'-'+main_company,'1',user_group[1:],user_company,main_company,r[53]]
            else:
                if r[0]:
                    user_company = r[0]
                    main_company = user_company
                if r[0] == 'Super user/Admin':
                    user_company = 'VKMCS,S3,TVAP,SSVKC,EP'
                    main_company = 'VKMCS'
        with open(result_file_path, 'wb') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=';',
                                    quotechar='"')
            spamwriter.writerow(['external id','name','login','password','groups/external id','companies','company','parent_user/external id'])
            for key in user_list.keys():
                spamwriter.writerow(user_list[key])
        return True
res_users()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

