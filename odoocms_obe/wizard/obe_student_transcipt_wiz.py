import pdb
import time
from odoo import api, fields, models, _, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class OBEStudentTranscriptWiz(models.TransientModel):
    _name = 'obe.student.transcript.wiz'
    _description = 'OBE Student Transcript Report Wizard'

    @api.model
    def _get_student(self):
        student_id = self.env['odoocms.student'].browse(self._context.get('active_id', False))
        if student_id:
            return student_id.id
        return True

    student_id = fields.Many2one('odoocms.student', 'Applicant', default=_get_student)

    @api.multi
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'odoocms.student',
            'form': data
        }

        return self.env.ref('odoocms_obe.action_report_obe_student_transcript').report_action(self, data=datas,
                                                                                                 config=False)





