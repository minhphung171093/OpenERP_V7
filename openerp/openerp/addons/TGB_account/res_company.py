# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

import os

import openerp
from openerp import SUPERUSER_ID, tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval as eval
from openerp.tools import image_resize_image


class res_company(osv.osv):
    _inherit = "res.company"
    _description = 'Companies'
    _order = 'name'

    def onchange_paper_format(self, cr, uid, ids, paper_format, context=None):
        res = {}
        if paper_format == 'us_letter':
            return {'value': res}
        return {'value': res}

    def default_get(self, cr, uid, fields, context=None):
        res = super(res_company, self).default_get(cr, uid, fields, context=context)
        res['rml_header'] = self._get_header(cr, uid, [])
        return res

    def _get_header(self, cr, uid, ids):
        return """

<header>
    <pageTemplate>
        <frame id="first" x1="1.3cm" y1="3.0cm" height="23.8cm" width="19.0cm"/>
         <stylesheet>
            <!-- Set here the default font to use for all <para> tags -->
            <paraStyle name='Normal' fontName="DejaVu Sans" fontSize="6.0" leading="10" alignment="LEFT" spaceBefore="0.0" spaceAfter="0.0"/>
            <paraStyle name="main_footer" fontSize="8.0" alignment="CENTER"/>
            <paraStyle name="main_header" fontSize="8.0" leading="10" alignment="LEFT" spaceBefore="0.0" spaceAfter="0.0"/>
              <paraStyle name="main_header2" fontSize="12" leading="10" alignment="LEFT" spaceBefore="0.0" spaceAfter="0.0"/>
         </stylesheet>
        <pageGraphics>
            <!-- Set here the default font to use for all <drawString> tags -->
            <setFont name="DejaVu Sans" size="8"/>
            <!-- You Logo - Change X,Y,Width and Height -->
            <image x="13cm" y="26.2cm" height="80.0" width="60.0" >[[ company.logo or removeParentNode('image') ]]</image>
            <fill color="black"/>
            <stroke color="black"/>

            <!-- page header -->
         <place x="15.3cm" y="27.3cm" height="1.8cm" width="15.0cm">
                        <para style="main_header2">[[ company.partner_id.name or  '' ]]</para>
            </place>
            <place x="15.3cm" y="26.8cm" height="1.8cm" width="15.0cm">
                <para style="main_header">[[  display_address(company.partner_id) or  '' ]]</para>
            </place>

     <place x="15.3cm" y="25.7cm" height="1.8cm" width="15.0cm">
                <para>Tel:[[ company.partner_id.phone or '' ]] Fax:[[ company.partner_id.fax or '' ]]</para>
            </place>
 <place x="15.3cm" y="25.4cm" height="1.8cm" width="15.0cm">
                <para>Email: [[ company.partner_id.email or '' ]]</para>
            </place>
 <place x="15.3cm" y="25.1cm" height="1.8cm" width="15.0cm">
                <para>[[ company.partner_id.website or '' ]]</para>
            </place>
        </pageGraphics>
    </pageTemplate>
</header>"""

    _columns = {
        'rml_header': fields.text('RML Header', required=True),
        'gst_registry': fields.char('GST Registration No', size=64),
    }