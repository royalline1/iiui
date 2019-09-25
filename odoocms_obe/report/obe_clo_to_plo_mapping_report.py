import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class OBECLOToPLOMappingReport(models.AbstractModel):
    _name = 'report.odoocms_obe.obe_clo_to_plo_mapping_report'
    _description = 'OBE CLO to PLO Mapping Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        batch_id = data['form']['batch_id'] and data['form']['batch_id'][0] or False
        course_id = data['form']['course_id'] and data['form']['course_id'][0] or False

        clo_line_ids = []
        plo_line_ids =[]
        if course_id and batch_id:
            course = self.env['odoocms.study.scheme.line'].search([('id', '=', course_id)])
            batch = self.env['odoocms.batch'].search([('id', '=', batch_id)])

            if course.clo_ids:
                for clo in course.clo_ids:
                    clo_line = {
                        'name': clo.description,
                        'plo': clo.plo_id.name,
                    }
                    clo_line_ids.append(clo_line)

            if batch.plo_ids:
                for plo in batch.plo_ids:
                    plo_line ={
                        'name': plo.name,
                        'id':plo.id,
                    }
                    plo_line_ids.append(plo_line)

        report = self.env['ir.actions.report']._get_report_from_name('odoocms_obe.obe_clo_to_plo_mapping_report')
        class_docs = self.env['odoocms.batch']
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'docs': class_docs,
            'clo_line_ids': clo_line_ids or False,
            'plo_line_ids': plo_line_ids or False,
            'batch': batch or False,
            'course': course or False,
        }
        return docargs
