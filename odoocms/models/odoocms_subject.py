import pdb
import calendar
from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class OdooCMSSubjectElectiveType(models.Model):
    _name = 'odoocms.subject.elective.type'
    _description = 'Subject Elective Type'

    name = fields.Char(string='Name', required=True, help="Elective Type Name")
    code = fields.Char(string="Code", required=True, help="Elective Type Code")
    elective_ids = fields.One2many('odoocms.study.scheme.line','elective_type','Elective Subjects')
    
    
class OdooCMSSubject(models.Model):
    _name = 'odoocms.subject'
    _description = 'CMS Subject'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True, help="Subject Name")
    code = fields.Char(string="Code", required=True, help="Subject Code")
    career_id = fields.Many2one('odoocms.career', 'Career')
    type = fields.Selection([('compulsory', 'Compulsory'), ('elective', 'Elective'), ('placeholder', 'Elective Placeholder')],
        string='Type', default="compulsory", help="Choose the type of the Subject")

    lecture = fields.Integer("Contact Hours")
    lab = fields.Integer("Lab")
    weightage = fields.Float(string='Credit Hours', default=1.0, help="Weightage for this Subject")
    
    description = fields.Text(string='Description')
    outline = fields.Text('Outline')
    suggested_books = fields.Text('Suggested Books')
            
    _sql_constraints = [
        ('code', 'unique(code, id)', "Another Subject already exists with this Code!"),]

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.code:
                name = record.code + ' - ' + name
            res.append((record.id, name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            recs = self.search([('name', operator, name)] + (args or []), limit=limit)
            if not recs:
                recs = self.search([('code', operator, name)] + (args or []), limit=limit)
            return recs.name_get()
        return super(OdooCMSSubject, self).name_search(name, args=args, operator=operator, limit=limit)
    
    @api.constrains('weightage','lab','lecture')
    def check_weightage(self):
        for rec in self:
            if rec.weightage <= 0:
                raise ValidationError(_('Weightage must be Positive'))
            if rec.lecture < 0:
                raise ValidationError(_('Contact Hours must be Zero or Positive'))
            if rec.lab < 0:
                raise ValidationError(_('Lab Hours must be Zero or Positive'))

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Subjects'),
            'template': '/odoocms/static/xls/odoocms_subject.xls'
        }]


class OdooCMSStudyScheme(models.Model):
    _name = "odoocms.study.scheme"
    _description = "CMS Study Scheme"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', copy=False)
    sequence = fields.Integer('Sequence')
    career_id = fields.Many2one("odoocms.career", string="Career", required=True)
    faculty_id = fields.Many2one('odoocms.faculty',string='Faculty', required=True)
    academic_session_id = fields.Many2one('odoocms.academic.session','Academic Session', copy=False)
    program_ids = fields.Many2many('odoocms.program','scheme_program_rel','scheme_id','program_id',string='Programs', copy=True)
    line_ids = fields.One2many('odoocms.study.scheme.line','study_scheme_id',string='Study Scheme', copy=True)
    
    _sql_constraints = [
        ('code', 'unique(code)', "Code already exists for another Study Scheme"),]

    
class OdooCMSStudySchemeLine(models.Model):
    _name = 'odoocms.study.scheme.line'
    _description = 'CMS Study Scheme Line'
    _rec_name = 'subject_id'
    _order = 'semester_id'
   
    semester_id = fields.Many2one('odoocms.semester',string="Semester")
    subject_type = fields.Selection([
        ('compulsory','Compulsory'),('elective','Elective'),('placeholder','Elective Placeholder')
        ], 'Course Type',default='compulsory')
    elective_type = fields.Many2one('odoocms.subject.elective.type', 'Elective Type')
    
    academic_semester_id = fields.Many2one('odoocms.academic.semester', 'Term',copy=False)
    subject_id = fields.Many2one('odoocms.subject',string='Subject', required=True)

    lecture = fields.Integer("Contact Hours", required=True)
    lab = fields.Integer("Lab Hours", required=True)
    weightage = fields.Float(string='Credit Hours', default=1.0, help="Weightage for this Subject")
    course_code = fields.Char('Course Code')
    course_name = fields.Char('Course Name')
    
    study_scheme_id = fields.Many2one('odoocms.study.scheme',string="Study Scheme",required=True)
    career_id = fields.Many2one("odoocms.career", string="Career", related='study_scheme_id.career_id', store=True)
    faculty_id = fields.Many2one(related='study_scheme_id.faculty_id',string='Faculty',store=True,copy=False)
    
    new_course = fields.Boolean('New Course')
    change_in_course = fields.Boolean('Change In Course')
    
    prereq_course = fields.Boolean('Prerequisite Course')
    prereq_ids = fields.Many2many('odoocms.study.scheme.line','scheme_prereq_subject_rel','subject_id1','subject_id2', string='Prerequisite Courses',copy=False)
    coreq_course = fields.Many2one('odoocms.study.scheme.line','CO-Req Course')
    # import_identifier = fields.Many2one('ir.model.data', 'Import Identifier', compute='_get_import_identifier', store=True) #

    _sql_constraints = [
        ('unique_subject', 'unique(study_scheme_id,subject_id,semester_id)', "Subject already exists in Study Scheme"), ]

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = record.subject_id.name
            if record.subject_id.code:
                name = record.subject_id.code + ' - ' + name
            res.append((record.id, name))
        return res
    
    @api.onchange('subject_id')
    def onchagene_subject(self):
        subject = self.subject_id
        self.weightage = subject.weightage 
        self.lecture = subject.lecture
        self.lab = subject.lab
        self.course_code = subject.code
        self.course_name = subject.name

    @api.onchange('subject_type')
    def onchagene_subject_type(self):
        if self.subject_type == 'placeholder':
            sub_domain = [('type','=','placeholder')]
        else:
            sub_domain = [('type', '!=', 'placeholder')]
            
        return {
            'domain': {
                'subject_id': sub_domain
            },
            'value': {
                'subject_id': False,
            }
        }

    # @api.multi
    # @api.depends('study_scheme_id','subject_id','academic_semester_id')
    # def _get_import_identifier(self):
    #     for rec in self:
    #         name = (rec.study_scheme_id.code or '') + '-' + (rec.academic_semester_id.code and rec.academic_semester_id.code or str(rec.semester_id.number)) + '-' + (rec.subject_id.code or '')
    #         identifier = self.env['ir.model.data'].search(
    #             [('model', '=', 'odoocms.study.scheme.line'), ('res_id', '=', rec.id)])
    #
    #         if identifier:
    #             identifier.module = 'PR'
    #             identifier.name = name
    #         else:
    #             data = {
    #                 'name': name,
    #                 'module': 'SS',
    #                 'model': 'odoocms.study.scheme.line',
    #                 'res_id': rec.id,
    #             }
    #             identifier = self.env['ir.model.data'].create(data)
    #
    #         rec.import_identifier = identifier.id
    
    @api.model
    def create(self, vals):
        if vals.get('elective', False):
            vals['semester_id'] = False
        return super(OdooCMSStudySchemeLine, self).create(vals)
        
    @api.multi
    def write(self, vals):
        if vals.get('elective',False):
            vals['semester_id'] = False
        ret = super(OdooCMSStudySchemeLine,self).write(vals)
        # prereq = vals.get('prereq_course',False)
        # if prereq:
        #     self.subject_id.prereq_course = True
        # else:
        #     scheme_subs = self.env['odoocms.study.scheme.line'].search([('subject_id','=',self.subject_id.id)])
        #     if scheme_subs and len(scheme_subs) == 1:
        #         self.subject_id.prereq_course = False
        return ret  		   

