import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class OBEClassCLOAttainmentReport(models.AbstractModel):
    _name = 'report.odoocms_obe.obe_class_clo_attainment_report'
    _description = 'OBE Class CLO Attainment Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        if data and data.get('form', False):
            class_id = data['form']['class_id'] and data['form']['class_id'][0] or False
            student_class = self.env['odoocms.class'].browse(class_id)
        elif docsid:
            student_class = self.env['odoocms.class'].browse(docsid[0])

        student = self.env['odoocms.student.subject']
        if student_class:
            student = self.env['odoocms.student.subject'].search([('class_id', '=', student_class.id)])

        report = self.env['ir.actions.report']._get_report_from_name('odoocms_obe.obe_class_clo_attainment_report')
        class_docs = self.env['odoocms.batch']
        docargs = {
            'students': student or False,
            'class_id': student_class or False,
        }
        return docargs
