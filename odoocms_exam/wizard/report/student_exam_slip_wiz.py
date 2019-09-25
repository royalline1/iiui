import pdb
import time
from odoo import api, fields, models, _, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class StudentExamSlipWiz(models.TransientModel):
    _name = 'student.exam.slip.wiz'
    _description = 'Students Exam Slip Wiz'

    # @api.model
    # def _get_program(self):
    #     student_id = self.env['odoocms.student'].browse(self._context.get('active_id', False))
    #     if student_id:
    #         return student_id.id
    #     return True

    batch_id = fields.Many2one('odoocms.batch', 'Batch', required=True)
    academic_semester_id = fields.Many2one('odoocms.academic.semester', 'Academic Term', required=True)
    @api.multi
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'form': data
        }

        return self.env.ref('odoocms_exam.action_report_student_exam_slip').with_context(landscape=False).report_action(self, data=datas,config=False)





