
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import pdb

class OdooCMSSemesterScheme(models.Model):
    _name = 'odoocms.semester.scheme'
    _description = 'Semester Scheme'
    _order = 'academic_semester_sequence'

    sequence = fields.Integer('Sequence')
    academic_semester_sequence = fields.Integer('Semester Seq.',related='academic_semester_id.sequence')
    academic_session_id = fields.Many2one('odoocms.academic.session','Academic Session')
    academic_semester_id = fields.Many2one('odoocms.academic.semester', 'Academic Term', required=True)
    semester_id = fields.Many2one('odoocms.semester', string="Semester", required=True)
    state = fields.Selection([('draft','Draft'),('approve','Approved')],'Status',default='draft')
    
    _sql_constraints = [
        ('session_academic_semester_unique', 'unique(academic_session_id, academic_semester_id)', "Study Scheme already exists in Academic Term"),
        ('session_semester_unique', 'unique(academic_session_id, semester_id)',
         "Study Scheme already exists in Academic Term"),
    ]

    @api.multi
    def name_get(self):
        return [(rec.id, rec.academic_session_id.code + '-' + rec.academic_semester_id.code) for rec in self]
    
    def approve_scheme(self):
        for rec in self:
            study_schemes = self.env['odoocms.study.scheme'].search([('academic_session_id','=',rec.academic_session_id.id)])
            for study_scheme in study_schemes:
                for line in study_scheme.line_ids.filtered(lambda l: l.semester_id.id == rec.semester_id.id):
                    line.academic_semester_id = rec.academic_semester_id.id
            self.state = 'approve'

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'approve':
                raise ValidationError(_("Approved Semester Scheme can not be deleted."))
        super(OdooCMSSemesterScheme, self).unlink()

    
class OdooCMSAcademicSemester(models.Model):
    _inherit = 'odoocms.academic.semester'
    
    semester_scheme_ids = fields.One2many('odoocms.semester.scheme','academic_semester_id','Study Scheme')
    class_ids = fields.One2many('odoocms.class','academic_semester_id','Classes')


class OdooCMSAcademicSession(models.Model):
    _inherit = 'odoocms.academic.session'
    
    semester_scheme_ids = fields.One2many('odoocms.semester.scheme', 'academic_session_id', 'Study Scheme')
    batch_ids = fields.One2many('odoocms.batch','academic_session_id','Batches')
    

class OdooCMSBatch(models.Model):
    _name = "odoocms.batch"
    _description = "CMS Batch"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence'
    
    name = fields.Char(string='Batch Name', required=True)
    code = fields.Char(string='Code', copy=False)
    color = fields.Integer(string='Color Index')
    sequence = fields.Integer('Sequence')
    department_id = fields.Many2one('odoocms.department', string="Department", required=True)
    career_id = fields.Many2one('odoocms.career', string="Career", required=True)
    program_id = fields.Many2one('odoocms.program', string="Program", required=True)
    academic_session_id = fields.Many2one('odoocms.academic.session','Academic Session', required=True)
    academic_semester_id = fields.Many2one('odoocms.academic.semester', 'Current Semester')
    study_scheme_id = fields.Many2one('odoocms.study.scheme','Study Scheme', required=True)
    reregister_credit_hours = fields.Integer(string="Credit Hours Allowed for Re-register")
    section_ids = fields.One2many('odoocms.batch.section', 'batch_id', string='Sections')
    student_ids = fields.One2many('odoocms.student','batch_id','Students')

    sequence_id = fields.Many2one('ir.sequence', string='ID Sequence',
        help="This field contains the information related to the registration numbering of the Student.",
        copy=False)
    sequence_number_next = fields.Integer(string='Next Number',
        help='The next sequence number will be used for the next Student Registration in the Batch.',
        compute='_compute_seq_number_next',
        inverse='_inverse_seq_number_next')
    
    _sql_constraints = [
        ('code', 'unique(code)', "Code already exists for some other Batch"),
    ]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            recs = self.search([('name', operator, name)] + (args or []), limit=limit)
            if not recs:
                recs = self.search([('code', operator, name)] + (args or []), limit=limit)
            return recs.name_get()
        return super(OdooCMSBatch, self).name_search(name, args=args, operator=operator, limit=limit)

    @api.multi
    # do not depend on 'sequence_id.date_range_ids', because
    # sequence_id._get_current_sequence() may invalidate it!
    @api.depends('sequence_id.use_date_range', 'sequence_id.number_next_actual')
    def _compute_seq_number_next(self):
        for batch in self:
            if batch.sequence_id:
                sequence = batch.sequence_id._get_current_sequence()
                batch.sequence_number_next = sequence.number_next_actual
            else:
                batch.sequence_number_next = 1

    @api.multi
    def _inverse_seq_number_next(self):
        for batch in self:
            if batch.sequence_id and batch.sequence_number_next:
                sequence = batch.sequence_id._get_current_sequence()
                sequence.sudo().number_next = batch.sequence_number_next

    @api.model
    def _get_sequence_prefix(self, code):
        prefix = code.upper()
        return prefix    # + '/%(range_year)s/'

    @api.model
    def _create_sequence(self, vals, refund=False):
        code = vals.get('code',False)
        if not code:
            code = self.code
        prefix = self._get_sequence_prefix(code)
        seq_name = code
        seq = {
            'name': _('%s Sequence') % seq_name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': 4,
            'number_increment': 1,
            #'use_date_range': True,
        }
        if 'company_id' in vals:
            seq['company_id'] = vals['company_id']
        seq = self.env['ir.sequence'].create(seq)
        #seq_date_range = seq._get_current_sequence()
        #seq_date_range.number_next = refund and vals.get('refund_sequence_number_next', 1) or vals.get('sequence_number_next', 1)
        seq.number_next = vals.get('sequence_number_next', 1)
        return seq
    
    @api.model
    def create(self, vals):
        if not vals.get('sequence_id'):
            vals.update({'sequence_id': self.sudo()._create_sequence(vals).id})
        batch = super(OdooCMSBatch, self).create(vals)
        return batch
        
    @api.multi
    def write(self, vals):
        for batch in self:
            batch = super(OdooCMSBatch, self).write(vals)
            if not self.sequence_id:
                self.sequence_id = self.sudo()._create_sequence(vals).id
    
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.student_ids:
                raise ValidationError(_("Batch maps with Students and can not be deleted, You only can Archive it."))
        super(OdooCMSBatch, self).unlink()
        
    def generate_classes(self):
        class_ids = self.env['odoocms.class']
        for batch in self:
            for section in batch.section_ids:
                semester_scheme = self.env['odoocms.semester.scheme'].search([('academic_session_id','=',batch.academic_session_id.id),('academic_semester_id','=',batch.academic_semester_id.id)])
                if not semester_scheme:
                    raise ValidationError('Semester Scheme is not defined for %s and %s' % (batch.academic_session_id.name,batch.academic_semester_id.name,))
               
                for subject in self.study_scheme_id.line_ids.filtered(lambda l: l.semester_id.id == semester_scheme.semester_id.id and l.subject_type == 'compulsory'):
                    class_exist = self.env['odoocms.class'].search([('section_id','=',section.id),('academic_semester_id','=',batch.academic_semester_id.id),('study_scheme_line_id','=',subject.id)])
                    if not class_exist:
                        data = {
                            'name': subject.subject_id.name + '-' + section.code,
                            'code': subject.subject_id.code + '-' + section.code,
                            'class_nature': 'lecture',
                            'academic_session_id': batch.academic_session_id.id,
                            'batch_id': batch.id,
                            'section_id': section.id,
                            'academic_semester_id': batch.academic_semester_id.id,
                            'study_scheme_line_id': subject.id,
                            'career_id': batch.career_id.id,
                            'strength': section.strength,
                            'class_room_id': section.class_room_id.id,
                            'class_type': 'regular',
                            'lecture':  subject.lecture,
                            'lab': subject.lab,
                            'weightage': subject.weightage,
                            'course_code': subject.course_code,
                            'course_name': subject.course_name,
                        }
                        class_id = self.env['odoocms.class'].create(data)
                        class_id.onchange_classtype_batch()
                        class_id.onchagene_scheme_line()
                        class_ids += class_id
                        
        if class_ids:
            class_list = class_ids.mapped('id')
            return {
                'domain': [('id', 'in', class_list)],
                'name': _('Classes'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'odoocms.class',
                'view_id': False,
                #'context': {'default_class_id': self.id},
                'type': 'ir.actions.act_window'
            }


class OdooCMSBatchSection(models.Model):
    _name = "odoocms.batch.section"
    _description = "CMS Class Section"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence'
    
    sequence = fields.Integer('Sequence')
    name = fields.Char(string='Section Name', required=True)
    code = fields.Char(string='Code', required=True)
    color = fields.Integer(string='Color Index')
    strength = fields.Integer('Max Strength')
    batch_id = fields.Many2one('odoocms.batch','Program Batch')

    student_ids = fields.One2many('odoocms.student', 'section_id', string='Students')
    class_ids = fields.One2many('odoocms.class','section_id', 'Classes')
    class_room_id = fields.Many2one('odoocms.room', 'Class Room')
    student_count = fields.Integer(string='Students Count', compute='_get_student_count')

    _sql_constraints = [
        ('code', 'unique(code)', "Code already exists for another Section"), ]

    def _get_student_count(self):
        for rec in self:
            student_count = len(rec.student_ids)
            rec.update({
                'student_count': student_count
            })

    @api.constrains('strength')
    def validate_strength(self):
        for rec in self:
            if rec.strength <= 0:
                raise ValidationError(_('Strength must be a Non-Zero value'))

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.student_ids:
                raise ValidationError(_("Section maps with Students and can not be deleted, You only can Archive it."))
        super(OdooCMSBatchSection, self).unlink()

    
class OdooCMSClass(models.Model):
    _name = 'odoocms.class'
    _description = 'CMS Class'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'ac_sem_seq, ac_ses_seq'

    READONLY_STATES = {
        'current': [('readonly', True)],
        'lock': [('readonly', True)],
        'done': [('readonly', True)],
    }
    
    name = fields.Char(string='Name', required=True, help="Class Name",states=READONLY_STATES)
    code = fields.Char(string="Code", required=True, help="Code",states=READONLY_STATES)
    class_nature = fields.Selection([('lecture', 'Lecture'), ('lab', 'Lab')], default='lecture'
        , string="Lecture/Lab",states=READONLY_STATES)
    description = fields.Text(string='Description')

    academic_session_id = fields.Many2one('odoocms.academic.session', 'Academic Session',required=True,states=READONLY_STATES)
    ac_ses_seq = fields.Integer('Session Seq.',related='academic_session_id.sequence',store=True)
    
    class_type = fields.Selection([
        ('regular','Regular'),('elective','Elective'),('special','Special')
        ],'Class Type',default='regular',states=READONLY_STATES)
    batch_id = fields.Many2one('odoocms.batch','Class Batch',states=READONLY_STATES)
    section_id = fields.Many2one('odoocms.batch.section','Class Section',states=READONLY_STATES)
    study_scheme_id = fields.Many2one('odoocms.study.scheme', 'Study Scheme',states=READONLY_STATES)
    
    academic_semester_id = fields.Many2one('odoocms.academic.semester', 'Academic Term',required=True,states=READONLY_STATES)
    ac_sem_seq = fields.Integer('Semester Seq.',related='academic_semester_id.sequence', store=True)
    
    study_scheme_line_id = fields.Many2one('odoocms.study.scheme.line', 'Subject',required=True,states=READONLY_STATES)
    career_id = fields.Many2one('odoocms.career', 'Career', related='study_scheme_line_id.career_id')

    lecture = fields.Integer("Contact Hours", required=True,states=READONLY_STATES)
    lab = fields.Integer("Lab Hours", required=True,states=READONLY_STATES)
    weightage = fields.Float(string='Credit Hours', default=1.0, help="Weightage for this Subject"
        , required=True,states=READONLY_STATES)
    course_code = fields.Char('Course Code', required=True,states=READONLY_STATES)
    course_name = fields.Char('Course Name', required=True,states=READONLY_STATES)

    strength = fields.Integer(string='Max. Class Strength', help="Total Max Strength of the Class")
    faculty_staff_id = fields.Many2one('odoocms.faculty.staff', string='Class Faculty')
    
    student_ids = fields.One2many('odoocms.student.subject', 'class_id', string='Students')
    class_room_id = fields.Many2one('odoocms.room', 'Class Room')
    student_count = fields.Integer(string='Students Count', compute='_get_student_count')
    
    state = fields.Selection([
        ('draft','Draft'),('current','Current'),('done','Done'),('lock','Locked')
        ],'Status',default='draft')
    
    _sql_constraints = [
        ('code_semester', 'unique(code,academic_semester_id)', "Another Class already exists in this Session with same code!"), ]

    @api.onchange('class_type','batch_id','academic_semester_id')
    def onchange_classtype_batch(self):
        res = {}
        rec = self
        
        if rec.class_type in ('regular','elective'):
            rec.study_scheme_id = rec.batch_id.study_scheme_id.id
        else:
            rec.study_scheme_id = False

        if rec.class_type in ('special','elective'):
            rec.section_id = False

        lines = self.env['odoocms.study.scheme.line']
        if rec.batch_id and rec.academic_semester_id:
            if rec.class_type == 'regular':
                lines = rec.study_scheme_id.line_ids.filtered(
                    lambda l: l.academic_semester_id.id == rec.academic_semester_id.id and l.subject_type == 'compulsory')
            elif rec.class_type == 'elective':
                lines = rec.study_scheme_id.line_ids.filtered(lambda l: l.subject_type == 'elective')
            elif rec.class_type == 'special':
                lines = rec.study_scheme_id.line_ids.filtered(lambda l: l.subject_type != 'placeholder')
        res['domain'] = {
            'study_scheme_line_id': [('id', 'in',lines.ids)],
        }
        return res

    @api.onchange('study_scheme_line_id')
    def onchagene_scheme_line(self):
        subject = self.study_scheme_line_id
        self.weightage = subject.weightage
        self.lecture = subject.lecture
        self.lab = subject.lab
        self.course_code = subject.course_code
        self.course_name = subject.course_name
        
    @api.multi
    def name_get(self):
        return [(rec.id, rec.batch_id.code + '-' + rec.code + '-' + rec.name) for rec in self]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            recs = self.search([('name', operator, name)] + (args or []), limit=limit)
            if not recs:
                recs = self.search([('code', operator, name)] + (args or []), limit=limit)
            return recs.name_get()
        return super(OdooCMSClass, self).name_search(name, args=args, operator=operator, limit=limit)
    
    def lock_class(self):
        self.state = 'lock'
        
    def unlock_class(self):
        self.state = 'current'
        
    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Class Section'),
            'template': '/odoocms_registration/static/xls/odoocms_class.xls'
        }]
    
    
    @api.multi
    def view_students(self):
        self.ensure_one()
        
        students_list = self.student_ids.mapped('student_id')
        return {
            'domain': [('id', 'in', students_list.ids)],
            'name': _('Students'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'odoocms.student',
            'view_id': False,
            'context': {'default_class_id': self.id},
            'type': 'ir.actions.act_window'
        }
    
    def _get_student_count(self):
        for rec in self:
            student_count = len(rec.student_ids)
            rec.update({
                'student_count': student_count
            })
    
    @api.constrains('strength')
    def validate_strength(self):
        for rec in self:
            if rec.strength <= 0:
                raise ValidationError(_('Strength must be a Non-Zero value'))

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.student_ids:
                raise ValidationError(_("Students are registered in the Class, and can not be deleted; You only can Archive it."))
        super(OdooCMSClass, self).unlink()


class OdooCMSStudyScheme(models.Model):
    _inherit = 'odoocms.study.scheme'
    
    class_ids = fields.One2many('odoocms.class', 'study_scheme_id', 'Classes')
    batch_ids = fields.One2many('odoocms.batch', 'study_scheme_id', 'Batches')
    
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.batch_ids:
                raise ValidationError(_("Scheme Line maps with Batches and can not be deleted, You only can Archive it."))
            if rec.class_ids:
                raise ValidationError(_("Scheme Line maps with Classes and can not be deleted, You only can Archive it."))
        
        super(OdooCMSStudyScheme, self).unlink()
        
        
class OdooCMSStudySchemeLine(models.Model):
    _inherit = 'odoocms.study.scheme.line'
    
    class_ids = fields.One2many('odoocms.class','study_scheme_id','Classes')
    registration_ids = fields.One2many('odoocms.student.subject', 'subject_id', 'Registrations')

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.class_ids:
                raise ValidationError(_("Scheme Line maps with Classes and can not be deleted, You only can Archive it."))
            if rec.registration_ids:
                raise ValidationError(_("Scheme Line maps with Student Registrations and can not be deleted, You only can Archive it."))

        super(OdooCMSStudySchemeLine, self).unlink()