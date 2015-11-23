# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


class falcon_custom_list1(osv.osv):
    _name = "falcon.custom.list1"
    _description = "Falcon Custom List1"
    _columns = {
        'name': fields.char('Custom list Name', size=25),
    }
falcon_custom_list1()

class falcon_custom_list2(osv.osv):
    _name = "falcon.custom.list2"
    _description = "Falcon Custom List2"
    _columns = {
        'name': fields.char('Custom list Name', size=25),
    }
falcon_custom_list2()

class falcon_custom_list3(osv.osv):
    _name = "falcon.custom.list3"
    _description = "Falcon Custom List3"
    _columns = {
        'name': fields.char('Custom list Name', size=25),
    }
falcon_custom_list3()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

