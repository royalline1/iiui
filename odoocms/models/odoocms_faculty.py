
from odoo import fields, models, api, _
import pdb

class OdooCMSFaculty(models.Model):
    _name = 'odoocms.faculty'
    _description = 'CMS Faculty'
    _inherit = ['mail.thread','mail.activity.mixin']
    
    name = fields.Char(string="Faculty", help="Faculty Name")
    code = fields.Char(string="Code", help="Faculty Code")
    department_ids = fields.One2many('odoocms.department', 'faculty_id', 'Departments')
    
    _sql_constraints = [
        ('code', 'unique(code)', "Code already exists "),]


class OdooCMSCampus(models.Model):
    _name = 'odoocms.campus'
    _description = 'CMS Campus'
    _inherit = ['mail.thread','mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', help='Campus City Code')
    shortcode = fields.Char('Short Code', help='Campus Short Code, Used in Student Registration number')
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    email = fields.Char()
    website = fields.Char()
    phone = fields.Char()   
    department_ids = fields.One2many('odoocms.department','campus_id','Departments')

    _sql_constraints = [
        ('code', 'unique(code)', "Code already exists "),]


class OdooCMSDepartment(models.Model):
    _name = 'odoocms.department'
    _description = 'CMS Department'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string="Name", help="Department Name", required=True)
    code = fields.Char(string="Code", help="Department Code", required=True)
    color = fields.Integer(string='Color Index')
    campus_id = fields.Many2one('odoocms.campus', 'Campus')
    faculty_id = fields.Many2one('odoocms.faculty', 'Faculty')
    program_ids = fields.One2many('odoocms.program', 'department_id', string="Programs")
    
    chairman_id = fields.Many2one("hr.employee", string="Chairman")
    professor_ids = fields.Many2many('hr.employee', 'department_professor_rel', 'department_id', 'professor_id',
                                     string="Professors")
    associate_professor_ids = fields.Many2many('hr.employee', 'department_associate_professor_rel', 'department_id',
                                               'associate_professor_id', string="Associate Professors")
    assistant_professor_ids = fields.Many2many('hr.employee', 'department_assistant_professor_rel', 'department_id',
                                               'assistant_professor_id', string="Assistant Professors")
    lecturer_ids = fields.Many2many('hr.employee', 'department_lecturer_rel', 'department_id', 'lecturer_id',
                                    string="Lecturers")
    lab_engineer_ids = fields.Many2many('hr.employee', 'department_lab_engineer_rel', 'department_id',
                                        'lab_engineer_id', string="Lab Engineers")
    visiting_faculty_ids = fields.Many2many('hr.employee', 'department_visiting_faculty_rel', 'department_id',
                                            'visiting_faculty_id', string="Visiting Faculty")
    assistant_dean_ids = fields.Many2many('hr.employee', 'department_assistant_dean_rel', 'department_id',
                                          'assistant_dean_id', string="Assistant Dean")
    coordinator_ids = fields.Many2many('hr.employee', 'department_coordinator_rel', 'department_id', 'coordinator_id',
                                       string="Coordinator")
    
    _sql_constraints = [
        ('code', 'unique(code)', "Code already exists"), ]
    
    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.code:
                name = record.code + ' - ' + name
            res.append((record.id, name))
        return res


class OdooCMSCareer(models.Model):
    _name = "odoocms.career"
    _description = "CMS Career"

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    color = fields.Integer(string='Color Index')
    

class OdooCMSProgram(models.Model):
    _name = "odoocms.program"
    _description = "CMS Program"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    short_code = fields.Char('Short Code',size=4)
    color = fields.Integer(string='Color Index')
    duration = fields.Char('Duration')
    credit_hours = fields.Integer('Credit Hours')
    department_id = fields.Many2one('odoocms.department', string="Department")
    career_id = fields.Many2one('odoocms.career', string="Career")
    faculty_id = fields.Many2one('odoocms.faculty', related='department_id.faculty_id', string="Faculty",store=True)
    scheme_ids = fields.Many2many('odoocms.study.scheme', 'scheme_program_rel', 'program_id', 'scheme_id',
        string='Study Schemes')
    user_ids = fields.Many2many('res.users','program_user_access_rel','program_id','user_id','Users',domain="[('share','=', False)]")
    
    import_identifier = fields.Many2one('ir.model.data', 'Import Identifier', compute='_get_import_identifier',
        store=True)
    
    _sql_constraints = [
        ('code', 'unique(code)', "Code already exists "),
        ('shortcode', 'unique(short_code,career_id)','Short code already exist for this Career')
    ]

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.department_id:
                name = name + ' - ' + record.department_id.campus_id.code
            res.append((record.id, name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            recs = self.search([('name', operator, name)] + (args or []), limit=limit)
            if not recs:
                recs = self.search([('code', operator, name)] + (args or []), limit=limit)
            return recs.name_get()
        return super(OdooCMSProgram, self).name_search(name, args=args, operator=operator, limit=limit)
    
    @api.multi
    @api.depends('code')
    def _get_import_identifier(self):
        for rec in self:
            name = rec.code or rec.id
            identifier = self.env['ir.model.data'].search(
                [('model', '=', 'odoocms.program'), ('res_id', '=', rec.id)])

            if identifier:
                identifier.module = 'PR'
                identifier.name = name
            else:
                data = {
                    'name': name,
                    'module': 'PR',
                    'model': 'odoocms.program',
                    'res_id': rec.id,
                }
                identifier = self.env['ir.model.data'].create(data)
    
            rec.import_identifier = identifier.id
            