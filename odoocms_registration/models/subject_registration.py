
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import pdb

class OdooCMSSubjectRegistration(models.Model):
    _name = "odoocms.subject.registration"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    READONLY_STATES = {
        'approved': [('readonly', True)],
        'rejected': [('readonly', True)],
    }
    
    name = fields.Char('Name', readonly=True, default='New')
    student_id = fields.Many2one('odoocms.student', 'Student', required=True, states=READONLY_STATES, track_visibility='onchange')
    program_id = fields.Many2one('odoocms.program', 'Program', related='student_id.program_id',store=True)
    academic_semester_id = fields.Many2one('odoocms.academic.semester', 'Term', required=True, states=READONLY_STATES, track_visibility='onchange')

    registered_subject_ids = fields.Many2many('odoocms.class', 'class_subject_registered_rel', 'register_id', 'class_id',
            string="Registered Subjects", states=READONLY_STATES, track_visibility='onchange',compute='get_subjects2',store=True)
    compulsory_subject_ids = fields.Many2many('odoocms.class', 'class_subject_compulsory_rel', 'register_id', 'class_id',
            string="Compulsory Subjects", states=READONLY_STATES, track_visibility='onchange')
    elective_subject_ids = fields.Many2many('odoocms.class', 'class_subject_elective_rel', 'register_id', 'class_id',
            string="Elective Subjects", states=READONLY_STATES, track_visibility='onchange')
    failed_subject_ids = fields.Many2many('odoocms.class', 'class_subject_failed_rel', 'register_id', 'class_id',
            string="Failed Subjects", states=READONLY_STATES, track_visibility='onchange')
    to_improve_subject_ids = fields.Many2many('odoocms.class', 'class_subject_improve_rel', 'register_id', 'class_id',
            string="To Improve Subjects", states=READONLY_STATES, track_visibility='onchange')
    
    state = fields.Selection([
        ('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='draft', string='Status', copy=False, track_visibility='onchange')
    
    @api.multi
    def action_reset_draft(self):
        self.state = 'draft'

    @api.multi
    def action_reject(self):
        self.state = 'rejected'
        
    @api.depends('student_id', 'academic_semester_id')
    def get_subjects2(self):
        res = {}
        record = self
        if record.student_id and record.academic_semester_id:
            registered_class_ids = record.student_id.subject_ids.filtered(
                lambda l: l.academic_semester_id.id == record.academic_semester_id.id).mapped('class_id')
            self.registered_subject_ids = [(6, 0, registered_class_ids.ids)]
        
    @api.onchange('student_id','academic_semester_id')
    def get_subjects(self):
        res = {}
        record = self
        if record.student_id and record.academic_semester_id:
            student = record.student_id
            new_semester = record.academic_semester_id
            
            record.compulsory_subject_ids = False
            record.elective_subject_ids = False
            record.failed_subject_ids = False
            record.to_improve_subject_ids = False

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
                
                # student.academic_semester_id = semester_scheme.academic_semester_id.id
                # student.semester_id = semester_scheme.semester_id.id

            # If Student Academic Semester and reistration semester are same
            elif student.academic_semester_id.id == new_semester.id:
                semester_scheme = self.env['odoocms.semester.scheme'].search([
                    ('academic_session_id', '=', student.academic_session_id.id),
                    ('academic_semester_id', '=', new_semester.id)
                ])
                if not semester_scheme:
                    raise ValidationError("""Semester Scheme not defined for Session: %s \n Term: %s \n Student: %s """ % (
                        student.academic_session_id.name, new_semester.name, student.name))
                
                if not student.semester_id:
                    if semester_scheme.semester_id.number > 1:
                        raise ValidationError("""Direct Registration is not possible for Semester: %s \n Term: %s \n Student: %s """ % (
                            semester_scheme.semester_id.name, new_semester.name, student.name))
                    # student.semester_id = semester_scheme.semester_id.id

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
                        student.academic_semester_id.name,student.semester_id.name,
                        semester_scheme.academic_semester_id.name, semester_scheme.semester_id.name, student.name))
    
                # student.academic_semester_id = new_semester.id
                # student.semester_id = next_semester.id

            classes = student.get_possible_classes(new_semester)[0]
            #record.registered_subject_ids = [(6, 0, registered_class_ids.ids)]
            
            res['domain'] = {
                'compulsory_subject_ids': [('id', 'in', classes['comp_class_ids'].ids)],
                'elective_subject_ids': [('id', 'in', classes['elec_class_ids'].ids)],
                'failed_subject_ids': [('id', 'in', classes['offered_f'].ids)],
                'to_improve_subject_ids': [('id', 'in', classes['offered_r'].ids)],
            }
        return res
            
    @api.multi
    def action_approve(self):
        reg = self.env['odoocms.student.subject']
        sem = self.env['odoocms.student.semester']
        for record in self:
            st_sem = sem.search([('student_id', '=', record.student_id.id), ('academic_semester_id', '=', record.academic_semester_id.id), ])
            if not st_sem:
                data = {
                    'student_id': record.student_id.id,
                    'academic_semester_id': record.academic_semester_id.id,
                    'semester_id': record.semester_id.id,
                }
                st_sem = sem.create(data)
        
            subject_ids = record.compulsory_subject_ids + record.elective_subject_ids + record.failed_subject_ids + record.to_improve_subject_ids
            for class_sub in subject_ids:
                line = class_sub.study_scheme_line_id
                prereq = True
                if line.prereq_ids:
                    for prereq_id in line.prereq_ids:
                        if not record.student_id.prereq_satisfy(prereq_id):
                            prereq = False
                if prereq:
                    reg += record.student_id.register_course(record.academic_semester_id, line, st_sem, class_sub)
                    if line.coreq_course:
                        reg += record.student_id.register_course(record.academic_semester_id, line.coreq_course, st_sem, class_sub)
                record.state = 'approved'
                
        reg_list = reg.mapped('id')
        return {
            'domain': [('id', 'in', reg_list)],
            'name': _('Student Registration'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'odoocms.student.subject',
            'view_id': False,
            # 'context': {'default_class_id': self.id},
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def action_submitted(self):
        self.state = 'submitted'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('odoocms.subject.registration') or '/'
        return super(OdooCMSSubjectRegistration, self).create(vals)
