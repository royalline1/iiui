import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class SemesterWisePLOAttainmentReport(models.AbstractModel):
    _name = 'report.odoocms_obe.semester_wise_plo_attainment_report'
    _description = 'Semesters Wise PLO Attainment Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        program_id = data['form']['program_id'] and data['form']['program_id'][0] or False
        batch_id = data['form']['batch_id'] and data['form']['batch_id'][0] or False
        academic_semester_id = data['form']['academic_semester_id'] and data['form']['academic_semester_id'][0] or False
        line_ids = []

        if program_id and batch_id and academic_semester_id:
            students = self.env['odoocms.student'].search([('program_id','=',program_id),('batch_id','=',batch_id)])
            for student in students:
                line = {
                    'student_id' : student.id_number,
                    'student_name' : student.first_name + " " + student.last_name,
                    'PLO-1' : '-',
                    'PLO-2': '-',
                    'PLO-3': '-',
                    'PLO-4': '-',
                    'PLO-5': '-',
                    'PLO-6': '-',
                    'PLO-7': '-',
                    'PLO-8': '-',
                    'PLO-9': '-',
                    'PLO-10': '-',
                    'PLO-11': '-',
                    'PLO-12': '-',
                }
                semester_plo_ids = self.env['odoocms.semester.obe.summary'].search([('student_id','=',student.id),('academic_semester_id','=',academic_semester_id)])
                for plo_id in semester_plo_ids:
                    line[plo_id.plo_id.code.name] = round(plo_id.percentage,2)
                line_ids.append(line)
        res = {
            'lines': line_ids,
        }
        report = self.env['ir.actions.report']._get_report_from_name('odoocms_obe.semester_wise_plo_attainment_report')
        class_docs = self.env['odoocms.semester.obe.summary']
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'docs': class_docs,
            'date': str(fields.Datetime.now()),
            'rep_data': res or False,
        }
        return docargs
