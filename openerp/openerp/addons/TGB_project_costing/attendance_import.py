# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
import netsvc
import datetime
import openerp.addons.decimal_precision as dp
import time
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from dateutil.relativedelta import relativedelta
import pytz
import psycopg2
from openerp.osv import orm, fields

class attendance_import(orm.TransientModel):
    _inherit = 'base_import.import'
    _name = 'attendance.import'

    def do(self, cr, uid, ids,context=None):
        cr.execute('SAVEPOINT import')

        record = self.browse(cr, uid, ids, context=context)[0]
        rows_to_import = self._read_csv(record,{'quoting':'"','separator':','})
        for row in rows_to_import:
            print row
        try:
            cr.execute('RELEASE SAVEPOINT import')
        except psycopg2.InternalError:
            pass

        return True

