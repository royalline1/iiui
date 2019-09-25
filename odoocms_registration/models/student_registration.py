
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import pdb


class OdooCMSStudentSubject(models.Model):
    _name = "odoocms.student.subject"
    _description = "Student Course Details"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'student_id'

    READONLY_STATES = {
        'current': [('readonly', True)],
        'lock': [('readonly', True)],
        'done': [('readonly', True)],
    }

    student_id = fields.Many2one('odoocms.student', 'Student', ondelete="cascade")
    program_id = fields.Many2one('odoocms.program', 'Program',related='student_id.program_id',store=True)
    academic_session_id = fields.Many2one('odoocms.academic.session', 'Academic Session',related='student_id.academic_session_id',store=True)
    semester_id = fields.Many2one('odoocms.semester', 'Semester')
    
    class_id = fields.Many2one('odoocms.class', 'Class', ondelete="restrict")
    academic_semester_id = fields.Many2one('odoocms.academic.semester', 'Term',related='class_id.academic_semester_id',store=True)
    subject_id = fields.Many2one('odoocms.study.scheme.line','Subject',related='class_id.study_scheme_line_id',store=True)
    student_semester_id = fields.Many2one('odoocms.student.semester','Student Semester')
    
    credits = fields.Float(string='Credit Hours', default=1.0, help="Credits for this Subject"
        , required=True, states=READONLY_STATES)
    course_code = fields.Char('Course Code', required=True, states=READONLY_STATES)
    course_name = fields.Char('Course Name', required=True, states=READONLY_STATES)
    is_freeze = fields.Boolean()
    
    state = fields.Selection([
        ('draft', 'Draft'), ('current', 'Current'), ('done', 'Done'), ('lock', 'Locked')
    ], 'Status', related='class_id.state', store=True)
    
    _sql_constraints = [
        ('unique_student_semester_course',
         'unique(student_id,academic_semester_id,subject_id)',
         'Student can take a course once in an Academic Term!'),
    ]

    @api.onchange('subject_id')
    def onchagene_subject(self):
        subject = self.subject_id
        self.credits = subject.weightage
        self.course_code = subject.code
        self.course_name = subject.name
        
    @api.model
    def create(self,vals):
        rec = super(OdooCMSStudentSubject, self).create(vals)
        sem = self.env['odoocms.student.semester']
        st_sem = sem.search([('student_id', '=', rec.student_id.id), ('academic_semester_id', '=', rec.academic_semester_id.id), ])
        if not st_sem:
            data = {
                'student_id': rec.student_id.id,
                'academic_semester_id': rec.academic_semester_id.id,
                'semester_id': rec.semester_id.id,
            }
            st_sem = sem.create(data)
        rec.student_semester_id = st_sem.id
        return rec


class OdooCMSStudentSemester(models.Model):
    _name = "odoocms.student.semester"
    _description = "Student Semester Details"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'semester_id'

    student_id = fields.Many2one('odoocms.student', 'Student', ondelete="cascade")
    program_id = fields.Many2one('odoocms.program', 'Program', related='student_id.program_id', store=True)
    academic_session_id = fields.Many2one('odoocms.academic.session', 'Academic Session',
                                          related='student_id.academic_session_id', store=True)
    academic_semester_id = fields.Many2one('odoocms.academic.semester', 'Term')
    semester_id = fields.Many2one('odoocms.semester','Semester')
    state = fields.Selection([('draft', 'Draft'), ('current', 'Current'), ('done', 'Done')], 'Status',
                             compute='_get_status', store=True)
    student_subject_ids = fields.One2many('odoocms.student.subject','student_semester_id','Semester Subjects')

    _sql_constraints = [
        ('unique_student_semester',
         'unique(student_id,academic_semester_id)',
         'Student can enroll once in an Academic Term!'),
    ]

    @api.depends('student_subject_ids', 'student_subject_ids.state')
    def _get_status(self):
        for rec in self:
            if any([subject.class_id.state == 'done' for subject in rec.student_subject_ids]):
                rec.state = 'done'
            else:
                rec.state = 'current'
                

class OdooCMSStudent(models.Model):
    _inherit = 'odoocms.student'

    batch_id = fields.Many2one('odoocms.batch', 'Class Batch', track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    section_id = fields.Many2one('odoocms.batch.section', 'Class Section', track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    semester_ids = fields.One2many('odoocms.student.semester','student_id','Results (Semester)', domain=[('state','=','done')])
    current_semester_ids = fields.One2many('odoocms.student.semester', 'student_id', 'Semesters',
        domain=[('state', 'in', ('draft','current'))])
    subject_ids = fields.One2many('odoocms.student.subject','student_id','Registered Subjects',
        domain=[('state','in',('draft','current','lock'))])
    result_subject_ids = fields.One2many('odoocms.student.subject', 'student_id', 'Subjects Result', domain=[('state', '=', 'done')])
    
    def register_course(self, academic_semester, scheme_line, st_semester,class_id=False):
        subject_class = self.env['odoocms.student.subject'].search([
            ('student_id', '=', self.id), ('academic_semester_id', '=', academic_semester.id), ('subject_id', '=', scheme_line.id)])
        
        if subject_class:
            if not subject_class.student_semester_id:
                subject_class.student_semester_id = st_semester
            return subject_class
    
        if not class_id:
            class_id = self.env['odoocms.class'].search([
                ('section_id', '=', self.section_id.id), ('study_scheme_line_id', '=', scheme_line.id)])
        
            if not class_id:
                raise ValidationError("""Class not defined for Subject: %s \n Section: %s \n Batch: %s""" % (
                    scheme_line.subject_id.name, self.section_id.name, self.batch_id.name))
            
        data = {
            'student_id': self.id,
            'academic_semester_id': academic_semester.id,
            'semester_id': self.semester_id.id,
            'subject_id': scheme_line.id,
            'class_id': class_id.id,
            'student_semester_id': st_semester.id,
            'credits': class_id.weightage,
            'course_code': class_id.course_code,
            'course_name': class_id.course_name,
        }
        return self.env['odoocms.student.subject'].create(data)
     
    def prereq_satisfy(self, prereq):
        pass
    
    def register_courses(self, new_semester , view=False):
        reg = self.env['odoocms.student.subject']
        sem = self.env['odoocms.student.semester']
        for student in self:
            if student.state != 'enroll':
                return False
            # If Student does not have any academic semester
            if not student.academic_semester_id:
                semester_scheme = self.env['odoocms.semester.scheme'].search([
                    ('academic_session_id', '=', student.academic_session_id.id),
                    ('academic_semester_id', '=', new_semester.id)
                ])
                if not semester_scheme:
                    raise ValidationError("""Semester Scheme not defined for Session: %s \n Term: %s \n Student: %s """ % (
                        student.academic_session_id.name, new_semester.name, student.name))
                if semester_scheme.semester_id.number > 1:
                    raise ValidationError("""Direct Registration is not possible for Semester: %s \n Term: %s \n Student: %s """ % (
                        semester_scheme.semester_id.name, new_semester.name, student.name))
                student.academic_semester_id = semester_scheme.academic_semester_id.id
                student.semester_id = semester_scheme.semester_id.id
                
            # If Student Academic Semester and reistration semester are same
            elif student.academic_semester_id.id == new_semester.id:
                semester_scheme = self.env['odoocms.semester.scheme'].search([
                    ('academic_session_id', '=', student.academic_session_id.id),
                    ('academic_semester_id', '=', new_semester.id)
                ])
                if not student.semester_id:
                    if semester_scheme.semester_id.number > 1:
                        raise ValidationError("""Direct Registration is not possible for Semester: %s \n Term: %s \n Student: %s """ % (
                            semester_scheme.semester_id.name, new_semester.name, student.name))
                    student.semester_id = semester_scheme.semester_id.id

            # If Student Academic Semester and reistration semester are not same
            elif student.academic_semester_id.id != new_semester.id:
                semester_scheme = self.env['odoocms.semester.scheme'].search([
                    ('academic_session_id', '=', student.academic_session_id.id),
                    ('academic_semester_id', '=', new_semester.id)
                ])
                if not semester_scheme:
                    raise ValidationError("""Semester Scheme not defined for Session: %s \n Term: %s \n Student: %s """ % (
                        student.academic_session_id.name, new_semester.name, student.name))
    
                if not student.semester_id:
                    raise ValidationError("""Direct Promotion is not possible for Semester: %s \n Term: %s \n Student: %s """ % (
                        semester_scheme.semester_id.name, new_semester.name, student.name))
    
                current_semester_number = student.semester_id.number
                next_semester_number = current_semester_number + 1
                next_semester = self.env['odoocms.semester'].search([('number', '=', next_semester_number)])
                if not next_semester:
                    return False
    
                next_semester_scheme = self.env['odoocms.semester.scheme'].search([
                    ('academic_session_id', '=', student.academic_session_id.id),
                    ('semester_id', '=', next_semester.id)
                ])
    
                if semester_scheme.semester_id.number != next_semester_scheme.semester_id.number:
                    raise ValidationError("""Promotion is not possible: \nFrom Semester: %s (%s) \nTo Semester: %s (%s) \nStudent: %s """ % (
                        student.academic_semester_id.name, student.semester_id.name,
                        semester_scheme.academic_semester_id.name, semester_scheme.semester_id.name, student.name))
                
                student.academic_semester_id = new_semester.id
                student.semester_id = next_semester.id

            st_sem = sem.search([('student_id', '=', student.id), ('academic_semester_id', '=', new_semester.id),])
            if not st_sem:
                data = {
                    'student_id': student.id,
                    'academic_semester_id': new_semester.id,
                    'semester_id': student.semester_id.id,
                }
                st_sem = sem.create(data)

            for line in student.study_scheme_id.line_ids.filtered(lambda l: l.academic_semester_id.id == student.academic_semester_id.id and l.subject_type == 'compulsory'):
                prereq = True
                if line.prereq_ids:
                    for prereq_id in line.prereq_ids:
                        if not self.prereq_satisfy(prereq_id):
                            prereq = False
                if prereq:
                    reg += student.register_course(new_semester,line,st_sem)
                    if line.coreq_course:
                        reg += student.register_course(new_semester, line.coreq_course, st_sem)
        
        if view:
            reg_list = reg.mapped('id')
            return {
                'domain': [('id', 'in', reg_list)],
                'name': _('Student Registration'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'odoocms.student.subject',
                'view_id': False,
                'type': 'ir.actions.act_window'
            }
        else:
            return reg

    @api.one
    def get_possible_classes(self, new_semester):
        student = self
        if student.state != 'enroll':
            return {
                'comp_class_ids': [],
                'elec_class_ids': [],
                'offered_f': [],
                'offered_r': [],
            }
        
        registered_student_subject_ids = student.subject_ids.filtered(lambda l: l.academic_semester_id.id == new_semester.id)
        registered_scheme_line_ids = registered_student_subject_ids.mapped('subject_id')
    
        comp_scheme_line_ids = student.study_scheme_id.line_ids.filtered(
            lambda l: l.academic_semester_id.id == new_semester.id and l.subject_type == 'compulsory')
    
        comp_scheme_line_ids -= registered_scheme_line_ids
    
        for line in comp_scheme_line_ids:
            prereq = True
            for prereq_id in line.prereq_ids:
                if not student.prereq_satisfy(prereq_id):
                    prereq = False
            if not prereq:
                comp_scheme_line_ids -= line
    
        comp_class_ids = new_semester.class_ids.filtered(
            lambda l: l.study_scheme_line_id.id in comp_scheme_line_ids.ids and l.section_id.id == student.section_id.id)
    
        elec_scheme_line_ids = self.env['odoocms.study.scheme.line']
        placeholder_scheme_line_ids = student.study_scheme_id.line_ids.filtered(
            lambda l: l.academic_semester_id.id == new_semester.id and l.subject_type == 'placeholder')
        if placeholder_scheme_line_ids:
            elec_scheme_line_ids = student.study_scheme_id.line_ids.filtered(
                lambda l: l.subject_type == 'elective' and l.elective_type.id in placeholder_scheme_line_ids.mapped('elective_type').ids)
        elec_class_ids = new_semester.class_ids.filtered(
            lambda l: l.study_scheme_line_id.id in elec_scheme_line_ids.ids)
    
        failed_grades = self.env['ir.config_parameter'].sudo().get_param('odoocms.failed_grades')
        failed_subject_ids = student.result_subject_ids.filtered(
            lambda l: l.grade in failed_grades.split(',')).mapped('subject_id').mapped('subject_id')
        offered_f = new_semester.class_ids.filtered(lambda l: l.study_scheme_line_id.subject_id.id in failed_subject_ids.ids)
    
        repeat_grades_allowed = self.env['ir.config_parameter'].sudo().get_param('odoocms.repeat_grades_allowed')
        repeat_grades_allowed_time = self.env['ir.config_parameter'].sudo().get_param('odoocms.repeat_grades_allowed_time')
        repeat_grades_allowed_no = self.env['ir.config_parameter'].sudo().get_param('odoocms.repeat_grades_allowed_no')
    
        repeat_subject_ids = student.result_subject_ids.filtered(
            lambda l: l.grade in repeat_grades_allowed.split(',')).mapped('subject_id').mapped('subject_id')  # student.subject -> scheme line -> subject
    
        for line in repeat_subject_ids:
            if len(student.result_subject_ids.filtered(
                    lambda l: l.subject_id.subject_id.id == line.id and l.grade not in failed_grades.split(','))) >= int(repeat_grades_allowed_no):
                repeat_subject_ids -= line
        for line in repeat_subject_ids:
            if len(student.result_subject_ids.filtered(
                    lambda l: l.subject_id.subject_id.id == line.id and l.grade not in failed_grades.split(',')
                              and l.semester_id.number < (student.semester_id.number - int(repeat_grades_allowed_time)))) > 0:
                repeat_subject_ids -= line
    
        offered_r = new_semester.class_ids.filtered(lambda l: l.study_scheme_line_id.subject_id.id in repeat_subject_ids.ids)
    
        return {
            'comp_class_ids': comp_class_ids,
            'elec_class_ids': elec_class_ids,
            'offered_f': offered_f,
            'offered_r': offered_r,
        }
    
    
class OdooCMSAcademicSemester(models.Model):
    _inherit = 'odoocms.academic.semester'

    subject_ids = fields.One2many('odoocms.student.subject', 'academic_semester_id', 'Subjects')