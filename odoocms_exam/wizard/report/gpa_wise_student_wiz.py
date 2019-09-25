import pdb
import time
from odoo import api, fields, models, _, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class GPAWiseStudentReportWiz(models.TransientModel):
    _name = 'gpa.wise.student.wiz'
    _description = 'GPA Wise Students Wiz'

    # @api.model
    # def _get_program(self):
    #     student_id = self.env['odoocms.student'].browse(self._context.get('active_id', False))
    #     if student_id:
    #         return student_id.id
    #     return True

    register_id = fields.Many2one('odoocms.admission.register', 'Academic Career', required=True)
    academic_semester_id = fields.Many2one('odoocms.academic.semester', 'Academic Term', required=True)
    program_id = fields.Many2one('odoocms.program', 'Program', required=True)
    semester_id = fields.Many2one('odoocms.semester', 'Semester', required=True)
    gpa = fields.Integer("GPA Threshold", required=True)

    @api.multi
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'form': data
        }

        return self.env.ref('odoocms_exam.action_report_gpa_wise_student').with_context(landscape=True).report_action(self, data=datas,config=False)





