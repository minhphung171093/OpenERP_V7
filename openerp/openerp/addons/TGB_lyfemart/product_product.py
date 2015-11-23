# -*- coding: utf-8 -*-
__author__ = 'Phamkr'
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import base64
import os
class product_product(osv.osv):
    _inherit='product.product'


    def create(self, cr, uid, vals, context=None):
        new_id = super(product_product, self).create(cr, uid, vals, context=context)
        print 'we have image', vals.get('image')
        if vals.get('image'):
            self.create_image(vals.get('image'),new_id)
        return new_id

    def write(self, cr, uid,ids, vals, context=None):
        return_ids = super(product_product, self).write(cr, uid,ids, vals, context=context)
        for product in self.browse(cr,uid,ids):
            if product.image:
                self.create_image(product.image,product.id)
        return return_ids

    def create_image(self,image,id):
        if image:
            from PIL import Image
            def is_jpg(filename):
                try:
                    i=Image.open(filename)
                    return i.format =='JPEG'
                except IOError:
                    return False
            imgdata = base64.b64decode(image)
            filename = '/opt/openerp/lyfemart_img/%s.jpg'%str(id)  # I assume you have a way of picking unique filenames
            with open(filename, 'wb') as f:
                f.write(imgdata)
                f.close()
                if not is_jpg(filename):
                    os.remove(filename)
                    filename = '/opt/openerp/lyfemart_img/%s.png'%str(id)
                    with open(filename, 'wb') as f2:
                        f2.write(imgdata)
                        f2.close()
                print 'new file', filename
        return True


    def update_image_path(self,cr,uid,ids,context=None):
        product_list_ids = self.search(cr,uid,[])
        for product in self.browse(cr,uid,product_list_ids):
            if product.image:
                self.create_image(product.image,product.id)
product_product()