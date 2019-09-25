import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class OBECourseToPLOMappingReport(models.AbstractModel):
    _name = 'report.odoocms_obe.obe_course_to_plo_mapping_report'
    _description = 'OBE Course To Plo Mapping Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        batch_id = data['form']['batch_id'] and data['form']['batch_id'][0] or False
        semester1 = []
        semester2 = []
        semester3 = []
        semester4 = []
        semester5 = []
        semester6 = []
        semester7 = []
        semester8 = []
        plo_line_ids =[]
        if batch_id:
            batch = self.env['odoocms.batch'].search([('id', '=', batch_id)])
            if batch.study_scheme_id and batch.study_scheme_id.line_ids:
                for course in batch.study_scheme_id.line_ids:
                    if course.semester_id.number ==1:
                        course_plo = []
                        for i in course.clo_ids:
                            course_plo.append(i.plo_id.name)

                        line = {
                            'code': course.subject_id.code,
                            'name': course.subject_id.name,
                            'semester': course.semester_id.number,
                            'plo_id': course_plo,
                        }
                        semester1.append(line)
                    if course.semester_id.number ==2:
                        course_plo = []
                        for i in course.clo_ids:
                            course_plo.append(i.plo_id.name)

                        line = {
                            'code': course.subject_id.code,
                            'name': course.subject_id.name,
                            'semester': course.semester_id.number,
                            'plo_id': course_plo,
                        }
                        semester2.append(line)
                    if course.semester_id.number ==3:
                        course_plo = []
                        for i in course.clo_ids:
                            course_plo.append(i.plo_id.name)

                        line = {
                            'code': course.subject_id.code,
                            'name': course.subject_id.name,
                            'semester': course.semester_id.number,
                            'plo_id': course_plo,
                        }
                        semester3.append(line)
                    if course.semester_id.number ==4:
                        course_plo = []
                        for i in course.clo_ids:
                            course_plo.append(i.plo_id.name)

                        line = {
                            'code': course.subject_id.code,
                            'name': course.subject_id.name,
                            'semester': course.semester_id.number,
                            'plo_id': course_plo,
                        }
                        semester4.append(line)
                    if course.semester_id.number ==5:
                        course_plo = []
                        for i in course.clo_ids:
                            course_plo.append(i.plo_id.name)

                        line = {
                            'code': course.subject_id.code,
                            'name': course.subject_id.name,
                            'semester': course.semester_id.number,
                            'plo_id': course_plo,
                        }
                        semester5.append(line)
                    if course.semester_id.number ==6:
                        course_plo = []
                        for i in course.clo_ids:
                            course_plo.append(i.plo_id.name)

                        line = {
                            'code': course.subject_id.code,
                            'name': course.subject_id.name,
                            'semester': course.semester_id.number,
                            'plo_id': course_plo,
                        }
                        semester6.append(line)
                    if course.semester_id.number ==7:
                        course_plo = []
                        for i in course.clo_ids:
                            course_plo.append(i.plo_id.name)

                        line = {
                            'code': course.subject_id.code,
                            'name': course.subject_id.name,
                            'semester': course.semester_id.number,
                            'plo_id': course_plo,
                        }
                        semester7.append(line)
                    if course.semester_id.number ==8:
                        course_plo = []
                        for i in course.clo_ids:
                            course_plo.append(i.plo_id.name)

                        line = {
                            'code': course.subject_id.code,
                            'name': course.subject_id.name,
                            'semester': course.semester_id.number,
                            'plo_id': course_plo,
                        }
                        semester8.append(line)
            if batch.plo_ids:
                for plo in batch.plo_ids:
                    plo_line ={
                        'name': plo.name,
                        'id':plo.id,
                    }
                    plo_line_ids.append(plo_line)

            line_ids = {
                '1': semester1,
                '2': semester2,
                '3': semester3,
                '4': semester4,
                '5': semester5,
                '6': semester6,
                '7': semester7,
                '8': semester8,
            }

        report = self.env['ir.actions.report']._get_report_from_name('odoocms_obe.obe_course_to_plo_mapping_report')
        class_docs = self.env['odoocms.batch']
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'docs': class_docs,
            'date': str(fields.Datetime.now()),
            'line_ids': line_ids or False,
            'plo_line_ids': plo_line_ids or False,
        }
        return docargs
