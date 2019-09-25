import pdb
import calendar
from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class OdooCMSrequestStubjectWithdraw(models.Model):
	_name = "odoocms.request.subject.withdraw"
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = "Student Subject Withdraw "

	student_id = fields.Many2one('odoocms.student', string="Student",track_visibility='onchange')
	program_id = fields.Many2one(related='student_id.program_id',string='Academic Program')
	batch_id = fields.Many2one(related='student_id.batch_id',string='Class Batch')
	section_id = fields.Many2one(related='student_id.section_id',string='Class Section')
	academic_semester_id = fields.Many2one(related='student_id.academic_semester_id',string='Freeze Academic Term')
	semester_id  = fields.Many2one(related='student_id.semester_id',string='Current Semester')
	subject_id  = fields.Many2one('odoocms.subject',string='withdraw Subject',track_visibility='onchange')
	reason = fields.Text(string='Reason')
	state = fields.Selection([('draft','Draft'),('approv','Approved'),('done','Done')],default='draft',string="Status",track_visibility='onchange')

