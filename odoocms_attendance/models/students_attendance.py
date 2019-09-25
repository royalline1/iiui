
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import pdb


class OdooCMSClassAttendance(models.Model):
    _name = 'odoocms.class.attendance'
    _description = 'Student Attendance Register'

    name = fields.Char(string='Name', default='New')
    class_id = fields.Many2one('odoocms.class', string='Class')
    academic_semester_id = fields.Many2one('odoocms.academic.semester', string='Academic Year',
                                           related='class_id.academic_semester_id', store=True)
    faculty_id = fields.Many2one('odoocms.faculty.staff', string='Faculty')
    date_att = fields.Date(string='Date', default=fields.Date.today, required=True)
    attendance_created = fields.Boolean(string='Attendance Created')
    all_marked = fields.Boolean(string='All students are present')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], default='draft')
    attendance_line = fields.One2many('odoocms.class.attendance.line', 'attendance_id', string='Attendance Line')
   
    @api.model
    def create(self, vals):
        attendance_obj = self.env['odoocms.class.attendance']
        class_id = vals.get('class_id')
        date_att = vals.get('date')
        already_created_attendance = attendance_obj.search(
            [('class_id', '=', class_id), ('date_att', '=', date_att)])
        if already_created_attendance:
            class_rec = self.env['odoocms.class'].browse(class_id)
            raise ValidationError(
                _('Attendance Register of %s is already created for %s', ) % (class_rec.name, date_att))
        res = super(OdooCMSClassAttendance, self).create(vals)
        return res

    @api.multi
    def create_attendance_line(self,ignore=False):
        self.name = str(self.date)
        attendance_line_obj = self.env['odoocms.class.attendance.line']
        students = self.class_id.student_ids
        if len(students) < 1 and not ignore:
            raise UserError(_('There are no students in this Class Section'))
        for student in students:
            data = {
                'name': self.name,
                'attendance_id': self.id,
                'student_id': student.student_id.id,
                'student_name': student.student_id.name,
                'class_id': self.class_id.id,
                'date_att': self.date,
            }
            attendance_line_obj.create(data)
        self.attendance_created = True

    @api.multi
    def mark_all_present(self):
        for records in self.attendance_line:
            records.present = True
        self.all_marked = True

    @api.multi
    def unmark_all_present(self):
        for records in self.attendance_line:
            records.present = False
        self.all_marked = False
     
    @api.multi
    def attendance_done(self):
        for records in self.attendance_line:
            records.state = 'done'
        self.state = 'done'

    @api.multi
    def set_to_draft(self):
        for records in self.attendance_line:
            records.state = 'draft'
        self.state = 'draft'


class OdooCMSClassAttendanceLine(models.Model):
    _name = 'odoocms.class.attendance.line'
    _description = 'Student Attendance'

    name = fields.Char(string='Name')
    attendance_id = fields.Many2one('odoocms.class.attendance', string='Attendance ID')
    student_id = fields.Many2one('odoocms.student', string='Student')
    student_name = fields.Char(string='Student Name', related='student_id.name', store=True)
    class_id = fields.Many2one('odoocms.class', string='Class', required=True)

    date_att = fields.Date(string='Date', required=True)
    present = fields.Boolean(string='Present')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string='State', default='draft')
    academic_semester_id = fields.Many2one('odoocms.academic.semester', string='Academic Term', related='class_id.academic_semester_id', store=True)
