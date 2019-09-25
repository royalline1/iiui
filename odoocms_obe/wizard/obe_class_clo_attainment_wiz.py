import pdb
import time
from odoo import api, fields, models, _, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class OBEClassCLOAttainmentWiz(models.TransientModel):
    _name = 'obe.class.clo.attainment.wiz'
    _description = 'OBE Class CLO Attainment Report Wizard'


    academic_session_id = fields.Many2one('odoocms.academic.session', 'Session')
    batch_id = fields.Many2one('odoocms.batch', 'Batch')
    semester_id = fields.Many2one('odoocms.academic.semester', 'Term')
    class_id = fields.Many2one('odoocms.class', 'Class')

    @api.multi
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'odoocms.batch',
            'form': data
        }

        return self.env.ref('odoocms_obe.action_report_obe_class_clo_attainment').with_context(landscape=True).report_action(self, data=datas,config=False)





