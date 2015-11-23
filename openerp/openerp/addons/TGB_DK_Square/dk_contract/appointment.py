# -*- coding: utf-8 -*-
__author__ = 'Phamkr'
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.addons.point_of_sale import point_of_sale
import logging
from openerp import tools
import openerp.addons.decimal_precision as dp
_logger = logging.getLogger(__name__)


class package_booking(osv.osv):
    _name = 'package.booking'
    _columns={
        'partner_id':fields.many2one('res.partner','Customer',required=True,domain=[('customer','=',True)]),
        'user_id':fields.many2one('res.users','Assigned User'),
        'date':fields.datetime('Schedule Date'),
        'contract_id':fields.many2one('dk.contract','Contract'),
        'location_of_service':fields.char('Location of Service',size=255),
        'note':fields.text('Note',),
    }
package_booking()

