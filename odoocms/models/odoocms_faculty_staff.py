from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class OdooCMSFacultyStaffTag(models.Model):
    _name = 'odoocms.faculty.staff.tag'
    _description = 'Faculty Staff Tag'

    name = fields.Char(string="Faculty Tag", required=True)
    color = fields.Integer(string='Color Index')
    faculty_staff_ids = fields.Many2many('odoocms.faculty.staff', 'faculty_staff_tag_rel', 'tag_id', 'faculty_staff_id', string='Teachers')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]


class OdooCMSFacultyStaffPosition(models.Model):
    _name = 'odoocms.faculty.staff.position'
    _description = 'Faculty Staff Position'

    name = fields.Char(string="Label", required=True) #label
    code = fields.Char(string="Reference", required=True) #reference


class OdooCMSFacultyStaff(models.Model):
    _name = 'odoocms.faculty.staff'
    _description = 'CMS Faculty'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'res.partner': 'partner_id'}

    @api.depends('first_name', 'last_name')
    def _get_faculty_name(self):
        for faculty in self:
            faculty.name = (faculty.first_name or '') + ' ' + (faculty.last_name or '')
            
    code = fields.Char(string="Code", readonly=True)
    first_name = fields.Char(string='First Name')
    last_name = fields.Char(string='Last Name')
    name = fields.Char('Faculty Name', compute='_get_faculty_name', store=True)
    date_of_birth = fields.Date(string="Date Of birth")
    father_name = fields.Char(string="Father")

    nationality = fields.Many2one('res.country', 'Nationality')
    employee_id = fields.Many2one('hr.employee', string="Related Employee")
    emergency_contact = fields.Many2one('res.partner', 'Emergency Contact')
    #degree = fields.Many2one('hr.recruitment.degree', string="Degree", Help="Select your Highest degree")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        string='Gender', required=True, default='male', track_visibility='onchange')
    blood_group = fields.Selection([('a+', 'A+'), ('a-', 'A-'), ('b+', 'B+'), ('o+', 'O+'), ('o-', 'O-'),
        ('ab-', 'AB-'), ('ab+', 'AB+')],
        string='Blood Group', required=True, default='a+', track_visibility='onchange')

    tag_ids = fields.Many2many('odoocms.faculty.staff.tag', 'faculty_staff_tag_rel', 'faculty_staff_id', 'tag_id', string='Tag')
    subject_ids = fields.Many2many('odoocms.subject', string='Subject(s)', track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', 'Partner', required=True, ondelete="cascade")
    
    login = fields.Char('Login', related='partner_id.user_id.login', readonly=1)
    last_login = fields.Datetime('Latest Connection', readonly=1, related='partner_id.user_id.login_date')

    unitimeId = fields.Integer()
    position_id = fields.Many2one('odoocms.faculty.staff.position','Position')
    department_id = fields.Many2one('odoocms.department','Department')
    
    def sync_unitime_odoo(self, instructors):
        for instructor in instructors:
            position = self.env['odoocms.faculty.staff.position'].search([('code','=',instructor['position']['reference'])])
            if not position:
                position = self.env['odoocms.faculty.staff.position'].create({
                    'name': instructor['position']['label'],
                    'code': instructor['position']['reference'],
                })
            dept = self.env['odoocms.department'].search([('code','=',instructor['deptcode'])])
            data = {
                'unitimeId': instructor['unitimeId'],
                'first_name': instructor['first_name'],
                'last_name': instructor['last_name'],
                'name': instructor.get('first_name','') + ' ' + instructor.get('last_name',''),
                'position_id': position.id,
                'department_id': dept.id,
            }
            pattern = self.env['odoocms.faculty.staff'].search([('unitimeId', '=', instructor['unitimeId'])])
            if pattern:
                pattern.write(data)
            else:
                pattern = self.env['odoocms.faculty.staff'].create(data)

    
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
    def create(self, vals):
        vals['faculty_id'] = self.env['ir.sequence'].next_by_code('odoocms.faculty.staff')
        res = super(OdooCMSFacultyStaff, self).create(vals)
        return res
    
    @api.multi
    @api.constrains('date_of_birth')
    def _check_birthdate(self):
        for record in self:
            if record.date_of_birth > fields.Date.today():
                raise ValidationError(_(
                    "Birth Date can't be greater than Current Date!"))

    @api.multi
    def create_employee(self):
        for record in self:
            vals = {
                'name': record.name,
                'country_id': record.nationality.id,
                'gender': record.gender,
                'address_home_id': record.partner_id.id,
                'birthday': record.date_of_birth,
                'image': record.image,
                'work_phone': record.phone,
                'work_mobile': record.mobile,
                'work_email': record.email,
            }
            emp_id = self.env['hr.employee'].create(vals)
            record.write({'employee_id': emp_id.id})
            record.partner_id.write({'employee': True})

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Faculty Staff'),
            'template': '/odoocms/static/xls/odoocms_faculty_staff.xls'
        }]


class WizardFacultyUser(models.TransientModel):
    _name = "wizard.faculty.user"
    _description = "Create User for selected Faculty(s)"

    def _get_faculties(self):
        if self.env.context and self.env.context.get('active_ids'):
            return self.env.context.get('active_ids')
        return []

    faculty_ids = fields.Many2many('odoocms.faculty.staff', default=_get_faculties, string='Faculties')

    @api.multi
    def create_faculty_user(self):
        group_portal = self.env.ref('base.group_portal')
        active_ids = self.env.context.get('active_ids', []) or []
        records = self.env['odoocms.faculty.staff'].browse(active_ids)
        self.env['res.users'].create_user(records, group_portal)
        
        
class WizardFacultyEmployee(models.TransientModel):
    _name = 'wizard.faculty.employee'
    _description = "Create Employee and User of Faculty"

    user_boolean = fields.Boolean("Want to create User too ?", default=True)

    @api.multi
    def create_employee(self):
        for record in self:
            active_id = self.env.context.get('active_ids', []) or []
            faculty = self.env['odoocms.faculty.staff'].browse(active_id)
            faculty.create_employee()
            if record.user_boolean and not faculty.user_id:
                group_portal = self.env.ref('base.group_portal')
                self.env['res.users'].create_user(faculty, group_portal)
                faculty.employee_id.user_id = faculty.user_id