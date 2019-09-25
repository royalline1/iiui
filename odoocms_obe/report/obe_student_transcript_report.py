import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class OBEStudentTransciptReport(models.AbstractModel):
    _name = 'report.odoocms_obe.obe_student_transcript_report'
    _description = 'OBE Student Transcript Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        if data and data.get('form', False):
            student_id = data['form']['student_id'] and data['form']['student_id'][0] or False
            student = self.env['odoocms.student'].browse(student_id)
        elif docsid:
            student = self.env['odoocms.student'].browse(docsid[0])
        
        line_ids = []
        if student:
            plos = self.env['odoocms.obe.plos'].search([('program_id', '=', student.program_id.id)])
            for plo in plos:
                line = {
                    'code':plo.code.name,
                    'plo': plo.code.name + " - " + plo.name,
                    'percentage': '-',
                }
                line_ids.append(line)
            for l in line_ids:
                for plo_id in student.plo_ids:
                    if plo_id.plo_id.code.name == l['code']:
                        l['percentage'] = round(plo_id.percentage)
            res = {
                'lines': line_ids,
            }
        
        docargs = {
            'date': str(fields.Datetime.now()),
            'student' : student or False,
            'rep_data': res or False,
        }
        return docargs
