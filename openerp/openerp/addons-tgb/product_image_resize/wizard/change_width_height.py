# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 OpenERP SA (<http://openerp.com>).
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

import base64
import re
import threading
from openerp.tools.safe_eval import safe_eval as eval
from openerp import tools
import openerp.modules
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc,SUPERUSER_ID
import datetime
import time
import calendar

class change_width_height(osv.osv_memory):
    _name = 'change.width.height'
    
    _columns = {
        'width': fields.integer('Width', required=True),
        'height': fields.integer('Height', required=True),
    }
    
    def update_width_height(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        product_obj = self.pool.get('product.product')
        product_ids = context.get('active_ids',[])
        for product in product_obj.browse(cr, uid, product_ids):
            product_obj.write(cr, uid, [product.id], {
                 'image': tools.image_resize_image_big(product.image,size=(this.width,this.height))                               
            })
        return {'type': 'ir.actions.act_window_close'}
    
change_width_height()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: