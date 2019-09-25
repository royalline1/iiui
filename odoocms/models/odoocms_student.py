from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import re
import pdb


class OdooCMSStudentTag(models.Model):
    _name = 'odoocms.student.tag'
    _description = 'Student Tag'

    name = fields.Char(string="Student Tag", required=True)
    color = fields.Integer(string='Color Index')
    student_ids = fields.Many2many('odoocms.student', 'student_tag_rel', 'tag_id', 'student_id', string='Students')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]

    
class OdooCMSStudent(models.Model):
    _name = 'odoocms.student'
    _description = 'Student'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'res.partner': 'partner_id'}
    _order = 'id_number'

    @api.depends('first_name','last_name')
    def _get_student_name(self):
        for student in self:
            student.name = (student.first_name or '') + ' ' + (student.last_name or '')

    first_name = fields.Char('First Name', required=True, track_visibility='onchange')
    last_name = fields.Char('Last Name', track_visibility='onchange')
    father_name = fields.Char(string="Father Name", track_visibility='onchange')
    cnic = fields.Char('CNIC', size=15, track_visibility='onchange')
    domicile_id = fields.Many2one('odoocms.domicile','Domicile',track_visibility='onchange')
    
    date_of_birth = fields.Date('Birth Date', required=True, track_visibility='onchange',
        default=lambda self: self.compute_previous_year_date(fields.Date.context_today(self)))
    gender = fields.Selection([('m', 'Male'), ('f', 'Female'), ('o', 'Other')], 'Gender', required=True, track_visibility='onchange')
    blood_group = fields.Selection(
        [('A+', 'A+ve'), ('B+', 'B+ve'), ('O+', 'O+ve'), ('AB+', 'AB+ve'),
         ('A-', 'A-ve'), ('B-', 'B-ve'), ('O-', 'O-ve'), ('AB-', 'AB-ve')],
        'Blood Group', track_visibility='onchange')
    religion_id = fields.Many2one('odoocms.religion', string="Religion", track_visibility='onchange')
    nationality = fields.Many2one('res.country', string='Nationality', ondelete='restrict', track_visibility='onchange')
    
    admission_no = fields.Char(string="Admission Number", readonly=True)
    id_number = fields.Char('Student ID', size=64, track_visibility='onchange')
    entryID = fields.Char('Entry ID', size=64)
    
    emergency_contact = fields.Char('Emergency Contact', track_visibility='onchange')
    emergency_mobile = fields.Char('Emergency Mobile', track_visibility='onchange')
    emergency_email = fields.Char('Emergency Email', track_visibility='onchange')
    emergency_address = fields.Char('Em. Address', track_visibility='onchange')
    emergency_city = fields.Char('Em. Street', track_visibility='onchange')

    
    visa_info = fields.Char('Visa Info', size=64)
    company_id = fields.Many2one('res.company', string='Company')
    
    is_same_address = fields.Boolean(string="Is same Address?", track_visibility='onchange')
    per_street = fields.Char()
    per_street2 = fields.Char()
    per_city = fields.Char()
    per_zip = fields.Char(change_default=True)
    per_state_id = fields.Many2one("res.country.state", string='Per State', ondelete='restrict',
        domain="[('country_id', '=?', per_country_id)]")
    per_country_id = fields.Many2one('res.country', string='Per. Country', ondelete='restrict')

    tag_ids = fields.Many2many('odoocms.student.tag', 'student_tag_rel','student_id', 'tag_id', string='Tag')
    
    partner_id = fields.Many2one('res.partner', 'Partner', required=True, ondelete="cascade")

    career_id = fields.Many2one('odoocms.career','Career', readonly=True, states={'draft': [('readonly', False)]})
    academic_session_id = fields.Many2one('odoocms.academic.session','Academic Session', readonly=True, states={'draft': [('readonly', False)]})
    program_id = fields.Many2one('odoocms.program','Academic Program', track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    campus_id = fields.Many2one('odoocms.campus','Campus',related='program_id.department_id.campus_id',store=True)
    study_scheme_id = fields.Many2one('odoocms.study.scheme','Study Scheme',compute='_get_study_scheme',store=True)
    academic_semester_id = fields.Many2one('odoocms.academic.semester','Current Academic Term', track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    semester_id = fields.Many2one('odoocms.semester','Current Semester', track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    academic_ids = fields.One2many('odoocms.student.academic', 'student_id', 'Academics')
    state = fields.Selection([
            ('draft', 'Draft'), ('enroll', 'Enroll'), ('elumni', 'Elumni'), ('cancel', 'Cancel'), ('suspend', 'Suspend'), ('freezed', 'Freezed'),
        ], 'Status', default='draft', track_visibility='onchange')
    reregister_credit_hours = fields.Integer(string="Credit Hours Allowed for Re-register", track_visibility='onchange')
    import_identifier = fields.Many2one('ir.model.data', 'Import Identifier', compute='_get_import_identifier',
        store=True)
    
    _sql_constraints = [
        ('admission_no', 'unique(admission_no)', "Another Student already exists with this Admission number!"),
    ]

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.id_number:
                name = record.id_number + ' - ' + name
            res.append((record.id, name))
        return res
    
    def get_student_id(self):
        if self.batch_id and self.batch_id.sequence_id:
            self.id_number = self.batch_id.sequence_id.next_by_id()
        
    @api.depends('academic_session_id','program_id')
    def _get_study_scheme(self):
        for rec in self:
            if rec.academic_session_id and rec.program_id:
                study_schemes = self.env['odoocms.study.scheme'].search(
                    [('academic_session_id', '=', rec.academic_session_id.id)])
                # , ('program_ids', 'in', rec.program_id.ids)
                for study_scheme in study_schemes:
                    if rec.program_id.id in study_scheme.program_ids.ids:
                        rec.study_scheme_id = study_scheme.id
                        break

    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            recs = self.search([('name', operator, name)] + (args or []), limit=limit)
            if not recs:
                recs = self.search([('id_number', operator, name)] + (args or []), limit=limit)
            return recs.name_get()
        return super(OdooCMSStudent, self).name_search(name, args=args, operator=operator, limit=limit)

    @api.model
    def create(self, vals):
        if vals.get('first_name',False) or vals.get('last_name',False):
            vals['name'] = vals.get('first_name','') + ' ' + vals.get('last_name','')
        res = super(OdooCMSStudent, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if vals.get('first_name', False) or vals.get('last_name', False):
            vals['name'] = vals.get('first_name', self.first_name) + ' ' + vals.get('last_name', self.last_name)
        res = super(OdooCMSStudent, self).write(vals)
        #if vals.get('id_number', False):
        #    self._get_import_identifier()
        return res

    @api.multi
    @api.constrains('cnic')
    def _check_cnic(self):
        for rec in self:
            cnic_com = re.compile('^[0-9+]{5}-[0-9+]{7}-[0-9]{1}$')
            a = cnic_com.search(rec.cnic)
            if a:
                return True
            else:
                raise UserError(_("CNIC Format is Incorrect. Format Should like this 00000-0000000-0"))
                
    @api.multi
    @api.constrains('date_of_birth')
    def _check_birthdate(self):
        for record in self:
            if record.date_of_birth > fields.Date.today():
                raise ValidationError(_(
                    "Birth Date can't be greater than Current Date!"))

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Students'),
            'template': '/odoocms/static/xls/odoocms_student.xlsx'
        }]

    @api.multi
    def create_student_user(self):
        group_portal = self.env.ref('base.group_portal')
        users_res = self.env['res.users']
        for record in self:
            if not record.user_id:
                data = {
                    #'name': record.name + ' ' + (record.last_name or ''),
                    'partner_id': record.partner_id.id,
                    'login': record.id_number or record.entryID or record.email,
                    'password': record.mobile or '654321',
                    'groups_id': group_portal,
                }
                user_id = users_res.create(data)
                record.user_id = user_id.id
                
    
    def compute_previous_year_date(self, strdate):
        tenyears = relativedelta(years=16)
        start_date = fields.Date.from_string(strdate)
        return fields.Date.to_string(start_date - tenyears)

    @api.multi
    @api.depends('id_number')
    def _get_import_identifier(self):
        for rec in self:
            identifier = self.env['ir.model.data'].search(
                [('model', '=', 'odoocms.student'), ('res_id', '=', rec.id)])
            if identifier:
                identifier.module = 'ST'
                identifier.name = rec.id_number or rec.id
            else:
                data = {
                    'name': rec.id_number or rec.id,
                    'module': 'ST',
                    'model': 'odoocms.student',
                    'res_id': rec.id,
                }
                identifier = self.env['ir.model.data'].create(data)

            rec.import_identifier = identifier.id
    
    @api.multi
    def lock(self):
        for rec in self:
            rec.state = 'enroll'

    def cron_account(self):
        recs = self.env['res.partner'].search(['|', ('property_account_receivable_id', '=', False), ('property_account_payable_id', '=', False)])
        for rec in recs:
            rec.property_account_receivable_id = 3
            rec.property_account_payable_id = 229

    def cron_pass(self):
        for rec in self:
            if rec.mobile:
                rec.mobile = rec.mobile.replace('-', '')
                if rec.user_id:
                    rec.user_id.password = rec.mobile
    
    
class OdooCMSStudentAcademic(models.Model):
    _name = 'odoocms.student.academic'
    _description = 'Student Academics'
    
    degree_level = fields.Selection([('matric', 'Matric'), ('inter', 'Intermediate')], 'Degree Level', required=1)
    degree = fields.Char('Degree', required=1)
    year = fields.Char('Passing Year')
    board = fields.Char('Board Name')
    subjects = fields.Char('Subjects')
    total_marks = fields.Integer('Total Marks', required=1)
    obtained_marks = fields.Integer('Obtained Marks', required=1)
    student_id = fields.Many2one('odoocms.student', 'Student')
    
    
class WizardStudentUser(models.TransientModel):
    _name = 'wizard.student.user'
    _description = "Create User for selected Student(s)"

    def _get_students(self):
        if self.env.context and self.env.context.get('active_ids'):
            return self.env.context.get('active_ids')
        return []

    student_ids = fields.Many2many('odoocms.student', default=_get_students, string='Students')

    @api.multi
    def create_user(self):
        active_ids = self.env.context.get('active_ids', []) or []
        records = self.env['odoocms.student'].browse(active_ids)
        records.create_student_user()
        
        
class OdooCmsStChangeStateRule(models.Model):
    _name = 'odoocms.student.change.state.rule'
    _description = "Reason for Changing Student State"

    name = fields.Text(string='Reason', help='Define the Reason To Change the State of Student')
