import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class StudentProvisionalCertificate(models.AbstractModel):
    _name = 'report.odoocms_exam.gpa_wise_student_report'
    _description = 'GPA wise Students Report'

    @api.model
    def _get_report_values(self, docsid, data=None):

        company_id = self.env.user.company_id
        academic_semester_id = data['form']['academic_semester_id'] and data['form']['academic_semester_id'][0] or False
        program_id = data['form']['program_id'] and data['form']['program_id'][0] or False
        semester_id = data['form']['semester_id'] and data['form']['semester_id'][0] or False
        gpa = data['form']['gpa'] and data['form']['gpa'] or False

        today = date.today()
        today = today.strftime("%B %d, %Y")

        student = self.env['odoocms.student'].search([])
        if academic_semester_id and program_id and semester_id and gpa:
            student = self.env['odoocms.student'].search([('academic_semester_id', '=', academic_semester_id),('program_id', '=', program_id),
                                                          ('cgpa', '>', gpa)
                                                          ])

        report = self.env['ir.actions.report']._get_report_from_name('odoocms_exam.gpa_wise_student_report')
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'student': student or False,
            'company_id':company_id or False,
            'gpa': gpa or False,
            'today':today or False,
        }
        return docargs
