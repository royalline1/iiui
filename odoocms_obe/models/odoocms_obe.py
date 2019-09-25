

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import pdb


# PEO
class OdooCMSOBEDomainLevel(models.Model):
    _name = 'odoocms.obe.domain.level'
    _description = 'OBE Domain Levels'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Level', required=True)
    parameter = fields.Char('Parameter', required=True)
    description = fields.Text('Description')
    learning_domain = fields.Selection([('cognitive','Cognitive'),('affective','Affective'),('psychomotor','Psychomotor')],'Learning Domain',required=True)

    
#PEO
class OdooCMSOBEPEOS(models.Model):
    _name = 'odoocms.obe.peos'
    _description = 'Program Educational Objectives'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Text('PEO', required=True)
    code = fields.Many2one('odoocms.obe.peocode', 'Code', required=True)
    program_id = fields.Many2one('odoocms.program', 'Program', required=True)
    department_id = fields.Many2one('odoocms.department','Department',related='program_id.department_id')
  

class OdooCMSOBEPEOSCode(models.Model):
    _name = 'odoocms.obe.peocode'
    _description = 'Program Objectives Codes'
    
    name = fields.Char('Code', size=128)
    

#PLOs
class OdooCMSOBEPLOS(models.Model):
    _name = 'odoocms.obe.plos'
    _description = 'Program Learning Outcomes'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name='code'

    name = fields.Char('PLO', required=True)
    code = fields.Many2one('odoocms.obe.plocode', 'Code', required=True)
    description = fields.Html('Description')
    program_id = fields.Many2one('odoocms.program', 'Program')
    department_id = fields.Many2one('odoocms.department', 'Department', related='program_id.department_id')
    batch_id = fields.Many2one('odoocms.batch', 'Batch')
    
    clo_ids = fields.One2many('odoocms.obe.clos','plo_id','CLOs')

    import_identifier = fields.Many2one('ir.model.data', 'Import Identifier', compute='_get_import_identifier', store=True)

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Program PLOs'),
            'template': '/odoocms_obe/static/xls/odoocms_obe_program_plos.xlsx'
        },
            {
                'label': _('Import Template for Batch PLOs'),
                'template': '/odoocms_obe/static/xls/odoocms_obe_batch_plos.xlsx'
            }
        ]
    
    @api.multi
    @api.depends('program_id','batch_id')
    def _get_import_identifier(self):
        for rec in self:
            name = rec.program_id and (rec.program_id.code+'-'+rec.code.name) or rec.batch_id and (rec.batch_id.code+'-'+rec.code.name) or rec.id
            identifier = self.env['ir.model.data'].search(
                [('model', '=', 'odoocms.obe.plos'), ('res_id', '=', rec.id)])
            
            if identifier:
                identifier.module = 'PLO'
                identifier.name = name
            else:
                data = {
                    'name': name,
                    'module': 'PLO',
                    'model': 'odoocms.obe.plos',
                    'res_id': rec.id,
                }
                identifier = self.env['ir.model.data'].create(data)
        
            rec.import_identifier = identifier.id


class OdooCMSOBEPLOSCode(models.Model):
    _name = 'odoocms.obe.plocode'
    _description = 'Program Outcomes Codes'
    
    name = fields.Char('Code', size=128)


#CLOs
class OdooCMSOBECLOS(models.Model):
    _name = 'odoocms.obe.clos'
    _description = 'Course Learning Outcomes'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'code'
    _order = 'code'

    def _get_plo_domain(self):
        domain = [('batch_id', '=', False)]
        if self.subject_id:
            program_id = self.subject_id.study_scheme_id.program_ids and self.subject_id.study_scheme_id.program_ids[0] or False
            if program_id:
                domain += [('program_id','=',program_id.id)]
       
        return domain

    @api.onchange('subject_id','code')
    def onchange_subject_id(self):
        domain = [('batch_id', '=', False)]
        if self.subject_id:
            program_id = self.subject_id.study_scheme_id.program_ids and self.subject_id.study_scheme_id.program_ids[0] or False
            if program_id:
                domain += [('program_id', '=', program_id.id)]
                return {
                    'domain': {'plo_id': domain}
                }
    
    code = fields.Many2one('odoocms.obe.clocode', 'CLO Code', required=True)
    description = fields.Html('Description', required=True)
    emphasis_level = fields.Many2one('odoocms.obe.emphasis.level', 'Emphasis Level')
    plo_id = fields.Many2one('odoocms.obe.plos', 'PLO', required=True, domain=lambda self: self._get_plo_domain())
    domain_id = fields.Many2one('odoocms.obe.domain.level','Domain Level')
    learning_domain = fields.Selection([('cognitive', 'Cognitive'), ('affective', 'Affective'), ('psychomotor', 'Psychomotor')], 'Learning Domain',
                                       related='domain_id.learning_domain',store=True)

    subject_id = fields.Many2one('odoocms.study.scheme.line', 'Subject')
    study_scheme_id = fields.Many2one('odoocms.study.scheme','Study Scheme',related='subject_id.study_scheme_id')
    class_id = fields.Many2one('odoocms.class','Course')
    
    exam_activity_ids = fields.One2many('odoocms.exam.activity','clo_id','Exam Activities')
    weightage = fields.Integer('Weightage', compute='_get_weightage',store=True)

    #import_identifier = fields.Many2one('ir.model.data', 'Import Identifier', compute='_get_import_identifier',store=True)
    import_identifier = fields.Many2one('ir.model.data', 'Import Identifier')
    
    @api.multi
    @api.depends('subject_id', 'class_id','code')
    def _get_import_identifier(self):
        for rec in self:
            name = rec.subject_id and \
                   (rec.subject_id.subject_id.code+'-'+rec.subject_id.study_scheme_id.code+'-'+rec.code.name) or \
                   rec.class_id and (rec.class_id.code+'-'+rec.code.name) or rec.id
            identifier = self.env['ir.model.data'].search(
                [('model', '=', 'odoocms.obe.clos'), ('res_id', '=', rec.id)])
            if identifier:
                identifier.module = 'CLO'
                identifier.name = name
            else:
                data = {
                    'name': name,
                    'module': 'CLO',
                    'model': 'odoocms.obe.clos',
                    'res_id': rec.id,
                }
                identifier = self.env['ir.model.data'].create(data)
        
            rec.import_identifier = identifier.id


    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Subject CLOs'),
            'template': '/odoocms_obe/static/xls/odoocms_obe_subject_clos.xlsx'
            },
            {
                'label': _('Import Template for Class CLOs'),
                'template': '/odoocms_obe/static/xls/odoocms_obe_class_clos.xlsx'
            }
        ]
    
    
    @api.multi
    @api.depends('exam_activity_ids','exam_activity_ids.obe_weightage')
    def _get_weightage(self):
        for clo in self:
            total = 0
            for activity in clo.exam_activity_ids:
                total += activity.obe_weightage
            clo.weightage = total

    
class OdooCMSOBECLOSCode(models.Model):
    _name = 'odoocms.obe.clocode'
    _description = 'Course Outcomes Codes'
    _order = 'name'
    
    name = fields.Char('Code', size=128)


class OdooCMSOBEEmphasisLevel(models.Model):
    _name = 'odoocms.obe.emphasis.level'
    _description = 'OBE Emphasis Level'
    
    name = fields.Char('Code', size=128)
    description = fields.Char('Description')
    factor = fields.Integer('Factor')
    
 
class OdooCMSProgram(models.Model):
    _inherit = "odoocms.program"
    
    plo_ids = fields.One2many('odoocms.obe.plos','program_id','PLOs')
   

class OdooCMSBatch(models.Model):
    _inherit = "odoocms.batch"
    
    plo_ids = fields.One2many('odoocms.obe.plos', 'batch_id', 'PLOs')
    clo_kpi = fields.Integer('CLO KPI', default=lambda self: self.env['ir.config_parameter'].sudo().get_param('odoocms_obe.clo_kpi'))
    
    def copy_plos(self):
        plos = self.env['odoocms.obe.plos'].search([('program_id','=',self.program_id.id),('batch_id','=',False)])
        for plo in plos:
            if not self.plo_ids.filtered(lambda l: l.code == plo.code):
                data = {
                    'name': plo.name,
                    'code': plo.code.id,
                    'description': plo.description,
                    'batch_id': self.id,
                }
                self.env['odoocms.obe.plos'].create(data)

                
class OdooCMSStudySchemeLine(models.Model):
    _inherit = 'odoocms.study.scheme.line'

    clo_ids = fields.One2many('odoocms.obe.clos', 'subject_id', 'CLOs', copy=True)
    
    
class OdooCMSClass(models.Model):
    _inherit = 'odoocms.class'

    clo_ids = fields.One2many('odoocms.obe.clos', 'class_id', 'CLOs')
    
    def copy_clos(self):
        clos = self.env['odoocms.obe.clos'].search([('subject_id','=',self.study_scheme_line_id.id),('class_id','=',False)])
        for clo in clos:
            if not self.clo_ids.filtered(lambda l: l.code == clo.code):
                data = {
                    'code': clo.code.id,
                    'description': clo.description,
                    'emphasis_level': clo.emphasis_level.id,
                    'plo_id': clo.plo_id.id,
                    'class_id': self.id,
                    'domain_id': clo.domain_id.id,
                }
                self.env['odoocms.obe.clos'].create(data)
                self.convert_to_current()

    @api.depends('exam_activity_class_ids','clo_ids')
    def convert_to_current(self):
        for rec in self:
            if rec.exam_activity_class_ids and rec.clo_ids and rec.state == 'draft':
                rec.state = 'current'
          

class OdooCMSExamActivity(models.Model):
    _inherit = 'odoocms.exam.activity'

    obe_weightage = fields.Float('OBE Weightage')
    clo_id = fields.Many2one('odoocms.obe.clos','CLO')
    domain_id = fields.Many2one('odoocms.obe.domain.level','Learning Domain',related='clo_id.domain_id',store=True)
    
    def generate_sheet(self):
        for student in self.class_id.student_ids:
            summary_rec = self.env['odoocms.exam.activity.summary'].search(
                [('class_id', '=', self.class_id.id), ('student_id', '=', student.id),
                 ('activity_class_id', '=', self.activity_class_id.id)])
    
            if not summary_rec:
                summary_vals = {
                    'class_id': self.class_id and self.class_id.id or False,
                    'student_id': student.id,
                    'activity_class_id': self.activity_class_id.id,
                }
                summary_rec = self.env['odoocms.exam.activity.summary'].create(summary_vals)
            data = {
                'activity_id': self.id,
                'student_id': student.id,
                'obtained_marks': 0,
                'summary_id': summary_rec and summary_rec.id or False,
            }
            self.env['odoocms.exam.activity.line'].create(data)

    def activity_result(self):
        form_view = self.env.ref('odoocms_obe.odoocms_exam_activity_form2')
        domain = [
            ('id', 'in', self.ids)]
        return {
            'name': _('Activity Result'),
            'domain': domain,
            'res_model': 'odoocms.exam.activity',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'form',
            'view_type': 'form',
            'views': [
                (form_view and form_view.id or False, 'form'),
            ],
            'res_id': self.id,
        }


class OdooCMSActivityOBESummary(models.Model):
    _name = 'odoocms.activity.obe.summary'
    _description = 'CMS Activity OBE Summary'
    _rec_name = 'clo_id'
    _order = 'clo_id'
    
    class_id = fields.Many2one('odoocms.class', string='Class')
    subject_id = fields.Many2one('odoocms.study.scheme.line', 'Subject', related='class_id.study_scheme_line_id',
                                 store=True)
    academic_semester_id = fields.Many2one('odoocms.academic.semester', string='Academic Termr',
                                           related='class_id.academic_semester_id', store=True)
    
    student_id = fields.Many2one('odoocms.student', string='Student')
    clo_id = fields.Many2one('odoocms.obe.clos', 'CLO')
    domain_id = fields.Many2one('odoocms.obe.domain.level','Learning Domain',related='clo_id.domain_id', store=True)
    semester_plo_id = fields.Many2one('odoocms.semester.obe.summary','Semester PLO',compute='_get_semester_plo', store=True)
    emphasis_level = fields.Many2one('odoocms.obe.emphasis.level', 'Emphasis Level',related='clo_id.emphasis_level',store=True)
    
    registration_id = fields.Many2one('odoocms.student.subject', 'Student Subject', compute='_get_student_subject', store=True)
    
    percentage = fields.Float('Percentage', compute='_get_percentage', store=True, group_operator = 'avg')
    activity_lines = fields.One2many('odoocms.exam.activity.line', 'clo_id', 'Activity Lines', )
    company_id = fields.Many2one('res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get())
    
    @api.depends('class_id', 'student_id')
    def _get_student_subject(self):
        for result in self:
            if result.student_id and result.class_id:
                class_id = self.env['odoocms.student.subject'].search([
                    ('student_id', '=', result.student_id.id), ('class_id', '=', result.class_id.id)])
                result.registration_id = class_id.id
    
    @api.depends('activity_lines', 'activity_lines.percentage')
    def _get_percentage(self):
        for result in self:
            total = 0
            for activity in result.activity_lines:
                total += activity.percentage * activity.activity_id.obe_weightage / 100.0
    
            
            result.percentage = total

    @api.multi
    @api.depends('clo_id')
    def _get_semester_plo(self):
        for rec in self:
            plo_id = rec.clo_id.plo_id
            sum_rec = self.env['odoocms.semester.obe.summary'].search([('student_semester_id','=',rec.registration_id.student_semester_id.id),('plo_id','=',plo_id.id)])
            if not sum_rec:
                data = {
                    'student_semester_id': rec.registration_id.student_semester_id.id,
                    'plo_id': plo_id.id,
                }
                sum_rec = self.env['odoocms.semester.obe.summary'].create(data)
            rec.semester_plo_id = sum_rec.id
                

class OdooCMSSemesterOBESummary(models.Model):
    _name = 'odoocms.semester.obe.summary'
    _description = 'Semester OBE Summary'
    _rec_name = 'plo_id'
    _order = 'plo_id'
   
    student_semester_id = fields.Many2one('odoocms.student.semester','Student Semester')
    student_id = fields.Many2one('odoocms.student','Student',related='student_semester_id.student_id',store=True)
    academic_semester_id = fields.Many2one('odoocms.academic.semester','Academic Term', related='student_semester_id.academic_semester_id',store=True)
    
    plo_id = fields.Many2one('odoocms.obe.plos', 'PLO')
    
    plo_points = fields.Float('Points', compute='_get_percentage', store=True)
    plo_level = fields.Float('Level', compute='_get_percentage', store=True)
    percentage = fields.Float('Percentage', compute='_get_percentage', store=True, group_operator = 'avg')
    
    student_obe_summary_id = fields.Many2one('odoocms.student.obe.summary','Student OBE Summary', compute='_get_student_obe_summary', store=True)
    semester_activity_summary_ids = fields.One2many('odoocms.activity.obe.summary','semester_plo_id','CLOs Summary')

    @api.depends('plo_id', 'student_id')
    def _get_student_obe_summary(self):
        for rec in self:
            if rec.student_id and rec.plo_id:
                student_obe_summary = self.env['odoocms.student.obe.summary'].search([
                    ('student_id', '=', rec.student_id.id), ('plo_id', '=', rec.plo_id.id)])
                if not student_obe_summary:
                    data = {
                        'student_id': rec.student_id.id,
                        'plo_id': rec.plo_id.id,
                    }
                    student_obe_summary = self.env['odoocms.student.obe.summary'].create(data)
                rec.student_obe_summary_id = student_obe_summary.id
                
    @api.depends('semester_activity_summary_ids', 'semester_activity_summary_ids.percentage')
    def _get_percentage(self):
        for rec in self:
            total = cnt = 0
            for activity in rec.semester_activity_summary_ids:
                total += activity.percentage * activity.clo_id.emphasis_level.factor
                cnt += activity.clo_id.emphasis_level.factor
                
            rec.plo_points = total
            rec.plo_level = cnt
            rec.percentage = total / (cnt or 1)


class OdooCMSStudentOBESummary(models.Model):
    _name = 'odoocms.student.obe.summary'
    _description = 'Student OBE Summary'
    _rec_name = 'plo_id'
    _order = 'plo_id'
    
    student_id = fields.Many2one('odoocms.student', 'Student')
    plo_id = fields.Many2one('odoocms.obe.plos', 'PLO')

    plo_points = fields.Float('Points', compute='_get_percentage', store=True)
    plo_level = fields.Float('Level', compute='_get_percentage', store=True)
    percentage = fields.Float('Percentage', compute='_get_percentage', store=True, group_operator = 'avg')

    semester_plo_ids = fields.One2many('odoocms.semester.obe.summary','student_obe_summary_id','Student PLOs')

    @api.depends('semester_plo_ids', 'semester_plo_ids.percentage')
    def _get_percentage(self):
        for rec in self:
            total = cnt = 0
            for line in rec.semester_plo_ids:
                total += line.plo_points
                cnt += line.plo_level
        
            rec.plo_points = total
            rec.plo_level = cnt
            rec.percentage = total / (cnt or 1)
    
    
class OdooCMSExamActivityLine(models.Model):
    _inherit = 'odoocms.exam.activity.line'

    clo_id = fields.Many2one('odoocms.activity.obe.summary', 'Activity CLO Summary')
    domain_id = fields.Many2one('odoocms.obe.domain.level',related='clo_id.domain_id',store=True)
    

class OdooCMSStudentSubject(models.Model):
    _inherit = "odoocms.student.subject"

    obe_activity_ids = fields.One2many('odoocms.activity.obe.summary', 'registration_id','OBE Activities')

    
class OdooCMSStudentSemester(models.Model):
    _inherit = "odoocms.student.semester"
    
    plo_ids = fields.One2many('odoocms.semester.obe.summary','student_semester_id')
    
    
class OdooCMSStudent(models.Model):
    _inherit = 'odoocms.student'

    plo_ids = fields.One2many('odoocms.student.obe.summary', 'student_id', 'PLOs Summary')

