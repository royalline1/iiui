import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class StudentExamSlip(models.AbstractModel):
    _name = 'report.odoocms_exam.student_exam_slip_report'
    _description = 'Student Exam Slip Report'

    @api.model
    def _get_report_values(self, docsid, data=None):

        company_id = self.env.user.company_id
        batch_id = data['form']['batch_id'] and data['form']['batch_id'][0] or False
        academic_semester_id = data['form']['academic_semester_id'] and data['form']['academic_semester_id'][0] or False

        today = date.today()
        today = today.strftime("%B %d, %Y")

        students_list = []
        if batch_id and academic_semester_id:
            students = self.env['odoocms.student'].search([('batch_id', '=', batch_id),('academic_semester_id', '=', academic_semester_id)])
            if students:
                for st in students:
                    balance = 0
                    invoice = self.env['account.invoice'].search([('student_id', '=', st.id), ('state', '=', 'open')])
                    for inv in invoice:
                        balance += sum(inv.residual for i in inv)
                    personal_info = {
                        "name":st.name,
                        "id_number":st.id_number,
                        "father":st.father_name,
                        "career":st.career_id.name,
                        "term":st.academic_semester_id.name,
                        "program":st.program_id.name,
                        "department": st.program_id.department_id.name,
                        "semester": st.semester_id.name,
                        "image": st.image,
                        "balance": " "+ str(balance),
                    }
                    subject_list = []
                    for sub in students.subject_ids:
                        subject = {
                            "code": sub.subject_id.subject_id.code,
                            "name": sub.subject_id.subject_id.name
                        }
                        subject_list.append(subject)
                    line = {
                        'personal_info':personal_info,
                        'subject_info': subject_list,
                    }
                    students_list.append(line)
        report = self.env['ir.actions.report']._get_report_from_name('odoocms_exam.student_exam_slip_report')
        docargs = {
            'doc_ids': [],
            'data': data['form'],
            'company_id':company_id or False,
            'today':"Date: "+today or False,
            'students_list':students_list or False,
        }
        return docargs
