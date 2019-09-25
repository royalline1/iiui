import pdb
import calendar
from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)

# 4 Years
class OdooCMSAcademicSession(models.Model):
    _name = 'odoocms.academic.session'
    _description = 'Academic Session'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence'

    # @api.model
    # def create(self, vals):
    #    vals['sequence'] = self.env['ir.sequence'].next_by_code('odoocms.academic.session')
    #    res = super(OdooCMSAcademicSession, self).create(vals)
    #    return res
    
    @api.multi
    def unlink(self):
        for rec in self:
            raise ValidationError(_("Academic Session can not be deleted, You only can Archive it."))
    
    name = fields.Char(string='Name', required=True, help='Name of Academic Session')
    code = fields.Char(string='Code', help='Code of Academic Session',copy=False)
    description = fields.Text(string='Description', help="Description about the Academic Session")
    sequence = fields.Integer(string='Sequence', required=True, default=10)
    date_start = fields.Date(string='Date Start', required=True, help='Starting Date of Academic Session')
    date_end = fields.Date(string='Date End', required=True, help='Ending of Academic Session')
    
    active = fields.Boolean('Active', default=True,
                            help="If Unchecked, it will allow you to hide the Academic Session without removing it.")
    
    _sql_constraints = [
        ('code', 'unique(code)', "Code already exists for another Academic Session!"),
    ]
    
    @api.constrains('date_start', 'date_end')
    def validate_date(self):
        for rec in self:
            start_date = fields.Date.from_string(rec.date_start)
            end_date = fields.Date.from_string(rec.date_end)
            if start_date >= end_date:
                raise ValidationError(_('Start Date must be Anterior to End Date'))


# Year
class OdooCMSAcademicCalendar(models.Model):
    _name = 'odoocms.academic.calendar'
    _description = 'Academic Calendar'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence'

    # @api.model
    # def create(self, vals):
    #    vals['sequence'] = self.env['ir.sequence'].next_by_code('odoocms.academic.calendar')
    #    res = super(OdooCMSAcademicCalendar, self).create(vals)
    #    return res
    
    @api.multi
    def unlink(self):
        for rec in self:
            raise ValidationError(_("Academic Calendar can not be deleted, You only can Archive it."))
    
    name = fields.Char(string='Name', required=True, help='Name of Academic Calendar')
    code = fields.Char(string='Code', help='Code of Academic Calendar',copy=False)
    description = fields.Text(string='Description', help="Description about the Academic Calendar")
    sequence = fields.Integer(string='Sequence', required=True, default=10)
    date_start = fields.Date(string='Date Start', required=True, help='Starting Date of Academic Calendar')
    date_end = fields.Date(string='Date End', required=True, help='Ending of Academic Calendar')
    academic_semester_ids = fields.One2many('odoocms.academic.semester', 'academic_calendar_id', 'Academic Terms')
    active = fields.Boolean('Active', default=True,
                            help="If Unchecked, it will allow you to hide the Academic Calendar without removing it.")
    
    _sql_constraints = [
        ('code', 'unique(code)', "Code already exists for another Academic Calendar!"),
    ]
    
    @api.constrains('date_start', 'date_end')
    def validate_date(self):
        for rec in self:
            start_date = fields.Date.from_string(rec.date_start)
            end_date = fields.Date.from_string(rec.date_end)
            if start_date >= end_date:
                raise ValidationError(_('Start Date must be Anterior to End Date'))


class OdooCMSAcademicSemester(models.Model):
    _name = 'odoocms.academic.semester'
    _description = 'Term'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence'
    
    #@api.model
    #def create(self, vals):
    #    vals['sequence'] = self.env['ir.sequence'].next_by_code('odoocms.academic.semester')
    #    res = super(OdooCMSAcademicSemester, self).create(vals)
    #    return res
    
    @api.multi
    def unlink(self):
        for rec in self:
            raise ValidationError(_("Academic Term can not be deleted, You only can Archive it."))
    
    name = fields.Char(string='Name', required=True, help='Name of Term')
    code = fields.Char(string='Code', help='Code of Term',copy=False)
    description = fields.Text(string='Description', help="Description about the Term")
    sequence = fields.Integer(string='Sequence', required=True, default=50)
    academic_calendar_id = fields.Many2one('odoocms.academic.calendar','Academic Calendar')
    semester_ids = fields.Many2many('odoocms.semester','academic_semester_semester_rel','academic_semester_id','semester_id','Semesters')
    
    date_start = fields.Date(string='Date Start', required=True, help='Starting Date of Term')
    date_end = fields.Date(string='Date End', required=True, help='Ending of Term')
    
    planning_ids = fields.One2many('odoocms.academic.semester.planning','academic_semester_id','Events')
    
    active = fields.Boolean('Active', default=True,
        help="If Unchecked, it will allow you to hide the Term without removing it.")
    
    _sql_constraints = [
        ('code', 'unique(code)', "Code already exists for another Term!"),
    ]
    
    @api.constrains('date_start', 'date_end')
    def validate_date(self):
        for rec in self:
            start_date = fields.Date.from_string(rec.date_start)
            end_date = fields.Date.from_string(rec.date_end)
            if start_date >= end_date:
                raise ValidationError(_('Start Date must be Anterior to End Date'))


class OdooCmsSemester(models.Model):
    _name = "odoocms.semester"
    _description = "Semester"
    
    name = fields.Char("Semester", required=True)
    code = fields.Char('Code')
    number = fields.Integer('Number', required=True)
    sequence = fields.Integer('Sequence')


class OdooCMSAcademicSemesterPlanning(models.Model):
    _name = 'odoocms.academic.semester.planning'
    _description = 'Term Planning'
    _order = 'sequence desc'

    name = fields.Char(string='Label', required=True, help='Name of Calendar Activity')
    sequence = fields.Integer(string='Sequence', required=True, default=50)
    academic_semester_id = fields.Many2one('odoocms.academic.semester', 'Academic Term')
    
    date_start = fields.Date(string='Date Start', required=True, help='Starting Date of Activity')
    date_end = fields.Date(string='Date End', required=True, help='Ending of Activity')

    @api.constrains('date_start', 'date_end')
    def validate_date(self):
        for rec in self:
            start_date = fields.Date.from_string(rec.date_start)
            end_date = fields.Date.from_string(rec.date_end)
            if start_date >= end_date:
                raise ValidationError(_('Start Date must be Anterior to End Date'))
    
    
class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.onchange('user_id')
    def onchange_user(self):
        if self.user_id:
            self.work_email = self.user_id.email
            self.identification_id = False

    @api.onchange('address_id')
    def onchange_address_id(self):
        if self.address_id:
            self.work_phone = self.address_id.phone
            self.mobile_phone = self.address_id.mobile
            

class ResUsers(models.Model):
    _inherit = "res.users"

    program_ids = fields.Many2many('odoocms.program', 'program_user_access_rel', 'user_id', 'program_id', 'Programs')
    
    @api.multi
    def create_user(self, records, user_group=None):
        for rec in records:
            if not rec.user_id:
                user_vals = {
                    'name': rec.name,
                    'login': rec.email or rec.name,
                    'partner_id': rec.partner_id.id,
                    'password': rec.mobile or '123456',
                    'groups_id': user_group,
                }
                user_id = self.create(user_vals)
                rec.user_id = user_id
                #if user_group:
                #    user_group.users = user_group.users + user_id
