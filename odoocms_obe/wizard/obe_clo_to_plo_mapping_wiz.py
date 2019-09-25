import pdb
import time
from odoo import api, fields, models, _, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class OBECLOToPloMappingWiz(models.TransientModel):
    _name = 'obe.clo.to.plo.mapping.wiz'
    _description = 'OBE CLO to PLO Mapping Report Wizard'

    # @api.model
    # def _get_student(self):
    #     student_id = self.env['odoocms.student'].browse(self._context.get('active_id', False))
    #     if student_id:
    #         return student_id.id
    #     return True

    # student_id = fields.Many2one('odoocms.student', 'Applicant', default=_get_student)
    batch_id = fields.Many2one('odoocms.batch', 'Batch')
    study_scheme_id = fields.Many2one('odoocms.study.scheme', 'Study Scheme', related='batch_id.study_scheme_id',
                                 store=True)
    semester = fields.Selection(
        [('1', 'First'), ('2', '2nd'), ('3', 'Third'), ('4', 'Fourth'), ('5', '5th'), ('6', '6th'), ('7', 'Seventh'),('8', 'Eight')],
        string='Semester', default='1')
    course_id = fields.Many2one('odoocms.study.scheme.line', 'Course')

    @api.multi
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'odoocms.batch',
            'form': data
        }

        return self.env.ref('odoocms_obe.action_report_obe_clo_to_plo_mapping').with_context(landscape=True).report_action(self, data=datas,config=False)





