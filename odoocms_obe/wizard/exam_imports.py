# -*- coding: utf-8 -*-
import time
import tempfile
import binascii
import xlrd
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime
from odoo.exceptions import Warning
from odoo import models, fields, exceptions, api, _

import logging

_logger = logging.getLogger(__name__)
from io import StringIO
import io
from openerp.exceptions import UserError, ValidationError
import pdb

# try:
#     import csv
# except ImportError:
#     _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class ExamImportWizard(models.TransientModel):
    _name = "odoocms.exam.import.wizard"
    _description = 'Exam Import Wizard'
    
    file = fields.Binary('File')
    # import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='xls')
    academic_session_id = fields.Many2one('odoocms.academic.session', 'Academic Session')
    batch_id = fields.Many2one('odoocms.batch', 'Batch')
    semseter_id = fields.Many2one('odoocms.academic.semester', 'Semester')
    class_id = fields.Many2one('odoocms.class', 'Class')
    
    @api.multi
    def import_exam_data(self):
        # """Load data from the CSV file."""
        # if self.import_option == 'csv':
        #     gr = 500
        # else:
        
        fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file))
        fp.seek(0)
        values = {}
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)
        class_code = sheet.col_values(0, 2, 3)

        class_rec = self.env['odoocms.class'].search([('code', 'in', class_code)])
        if not class_rec:
            raise UserError('Class not Found')

        students = sheet.col_values(0, 8)
        for col_num in range(2, sheet.ncols):  # From Column 2 to Last Column
            headers = sheet.col_values(col_num, 0, 6)  # Quiz, Quiz 1, Q1, 20, 10, CLO-1, 2019-01-01

            assessment_date = str(fields.Date.today())
            if sheet.cell(6, col_num).ctype == 3: # Date
                date_value = xlrd.xldate_as_tuple(sheet.cell_value(6, 2), workbook.datemode)
                assessment_date = date(*date_value[:3]).strftime('%Y-%m-%d')
            
            marks = sheet.col_values(col_num, 8)
            
            activity_type = self.env['odoocms.exam.activity.type'].search([('name', '=', headers[0])])
            if activity_type:
                activity_class_id = self.env['odoocms.exam.activity.class'].search(
                    [('class_id', '=', class_rec.id), ('activity_type_id', '=', activity_type.id)])
                
                clo_code = self.env['odoocms.obe.clocode'].search(
                    [('name', '=', headers[5])])
                
                clo_id = self.env['odoocms.obe.clos'].search(
                    [('class_id', '=', class_rec.id), ('code', '=', clo_code.id)])
                
                activity_rec = self.env['odoocms.exam.activity'].search(
                    [('activity_class_id', '=', activity_class_id.id),
                     ('class_id', '=', class_rec.id), ('code', '=', headers[2])]
                )
                if not activity_rec:
                    activity_vals = {
                        'name': headers[1],
                        'code': headers[2],
                        'activity_class_id': activity_class_id and activity_class_id.id or False,
                        'class_id': class_rec.id,
                        'date_activity': assessment_date,
                        'max_marks': headers[3],
                        'obe_weightage': headers[4],
                        'clo_id': clo_id.id,
                    }
                    activity_rec = self.env['odoocms.exam.activity'].create(activity_vals)
                
                for i in range(len(students)):
                    student = self.env['odoocms.student'].search([('id_number', '=', students[i])])
                    # For Summarization of Quizes, Assignments. Mid & Final
                    summary_rec = self.env['odoocms.exam.activity.summary'].search(
                        [('class_id', '=', class_rec.id), ('student_id', '=', student.id),
                         ('activity_class_id', '=', activity_class_id.id)])
                    
                    if not summary_rec:
                        summary_vals = {
                            'class_id': class_rec.id,
                            'student_id': student.id,
                            'activity_class_id': activity_class_id.id,
                        }
                        summary_rec = self.env['odoocms.exam.activity.summary'].create(summary_vals)
                    
                    # For summarization of CLOs
                    clo_rec = self.env['odoocms.activity.obe.summary'].search(
                        [('class_id', '=', class_rec.id), ('student_id', '=', student.id),
                         ('clo_id', '=', clo_id.id)])
                    
                    if not clo_rec:
                        summary_vals = {
                            'class_id': class_rec.id,
                            'student_id': student.id,
                            'clo_id': clo_id.id,
                        }
                        clo_rec = self.env['odoocms.activity.obe.summary'].create(summary_vals)
                    
                    activity_line = self.env['odoocms.exam.activity.line'].search([
                        ('student_id', '=', student.id), ('activity_id', '=', activity_rec.id)
                    ])
                    if activity_line:
                        data = {
                            'obtained_marks': marks[i],
                            'summary_id': summary_rec and summary_rec.id or False,
                            'clo_id': clo_rec and clo_rec.id or False,
                        }
                        activity_line.write(data)
                    else:
                        activity_line_vals = {
                            'student_id': student.id,
                            'activity_id': activity_rec.id,
                            'obtained_marks': marks[i],
                            'summary_id': summary_rec and summary_rec.id or False,
                            'clo_id': clo_rec and clo_rec.id or False,
                        }
                        activity_line = self.env['odoocms.exam.activity.line'].create(activity_line_vals)
        
        
        
        
        
        



