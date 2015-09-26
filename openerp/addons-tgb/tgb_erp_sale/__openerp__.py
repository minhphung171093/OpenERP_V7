# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Enterprise Management Solution
#    risk_management Module
#    Copyright (C) 2014 OpenSur (comercial@opensur.com)
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
    'name': 'ERP Sale',
    'category': 'TGB',
    'author': 'tranhung07081989@gmail.com',
    'website' : '',
    'description': """""",
    'version': '1.0',
    'depends': ['sale','account','stock','account_accountant','product','account_voucher','account_cancel'],
    'data' : [
              'security/ir.model.access.csv',
              'wizard/edit_invoice_view.xml',
              'sale_view.xml', 
              'product_view.xml',
              'partner_view.xml',
              'voucher_view.xml',
              'invoice_view.xml',
                 ],
    'qweb' : [],
    'js' : [],
    'css' : [],
    'auto_install': True,
    'installable': True,
    'application': True,
}
