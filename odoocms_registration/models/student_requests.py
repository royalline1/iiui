import pdb
import calendar
from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class OdooCMSStudentSemesterFreeze(models.Model):
	_name = "odoocms.student.semester.freeze"
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = "Student Semester Freeze"
	_rec_name = 'student_id'
	
	READONLY_STATES = {
		'approve': [('readonly', True)],
		'done': [('readonly', True)],
		'cancel': [('readonly', True)],
	}
	
	student_id = fields.Many2one('odoocms.student', string="Student",states=READONLY_STATES)
	program_id = fields.Many2one(related='student_id.program_id' ,string='Academic Program')
	batch_id = fields.Many2one(related='student_id.batch_id' ,string='Class Batch')
	section_id = fields.Many2one(related='student_id.section_id' ,string='Class Section')
	academic_semester_id = fields.Many2one(related='student_id.academic_semester_id' ,string='Freeze Academic Term')
	semester_id  = fields.Many2one(related='student_id.semester_id' ,string='Current Semester')
	reason = fields.Text(string='Reason',states=READONLY_STATES)
	state = fields.Selection([('draft' ,'Draft') ,('approve' ,'Approved') ,('done' ,'Done'), ('cancel' ,'Canceled')]
		,default='draft' ,string="Status" ,track_visibility='onchange')
	
	def freeze_semester(self):
		if self.student_id.subject_ids:
			raise ValidationError("The Student have some Courses Registered, His Semester can not be freezed.")
		self.state = 'done'
		self.student_id.state = 'freezed'
		


class OdooCMSStudentSemesterUnFreeze(models.Model):
	_name = "odoocms.student.semester.unfreeze"
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = "Student Semester Unfreeze"
	
	READONLY_STATES = {
		'approve': [('readonly', True)],
		'done': [('readonly', True)],
		'cancel': [('readonly', True)],
	}

	student_id = fields.Many2one('odoocms.student', string="Student",states=READONLY_STATES)
	program_id = fields.Many2one(related='student_id.program_id',string='Academic Program')
	batch_id = fields.Many2one(related='student_id.batch_id',string='Class Batch')
	section_id = fields.Many2one(related='student_id.section_id',string='Class Section')
	academic_semester_id = fields.Many2one(related='student_id.academic_semester_id',string='Freeze Academic Term')
	semester_id  = fields.Many2one(related='student_id.semester_id',string='Current Semester')
	state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('done', 'Done'), ('cancel', 'Canceled')]
		, default='draft', string="Status", track_visibility='onchange')
	
	def unfreeze_semester(self):
		self.state = 'done'
		self.student_id.state = 'enroll'

