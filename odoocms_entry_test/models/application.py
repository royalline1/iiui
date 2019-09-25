from odoo import fields, models, _, api
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo.exceptions import ValidationError


class OdooCMSEntryTest(models.Model):
	_name = 'odoocms.entrytest'
	_description = 'Entry Test'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	
	name = fields.Char(string='Name')
	code = fields.Char(string='Code')
	date_start = fields.Date(string="Registration Start Date")
	date_end = fields.Date(string="Registration End Date")
	date_test = fields.Date(string="Date of Entry Test")
	active = fields.Boolean(string="Is Active", default=False)
	career_id = fields.Many2one('odoocms.career', 'Career ID')
	header_one = fields.Text('First Header')
	header_two = fields.Text('Second Header')
	header_three = fields.Text('Third Header')

	
class OdooCMSEntryTestFee(models.Model):
	_name = 'odoocms.entrytest.fee'
	_description = 'Fee for Entry Test'
	_rec_name = 'sequence_no'
	
	sequence_no = fields.Char(string='Sequence Number', help="Bank Sequence Number")
	branch_code = fields.Char(string='Branch Code')
	submission_date = fields.Date(string="Submission Date")
	mobile = fields.Char(string="Phone Number")
	entrytest_id = fields.Many2one('odoocms.entrytest', 'EntryTest ID')
	is_used = fields.Boolean('Is Used?')
	
	_sql_constraints = [
		('sequence_no', 'unique(sequence_no)', "Another Record already exists with this Sequence Number!"),
	]
	
	@api.model
	def get_import_templates(self):
		return [{
			'label': _('Import Template for Entry Test Fee'),
			'template': '/odoocms_entry_test/static/xls/odoocms_entrytest_fee.xlsx'
		}]


class OdooCMSEntryTestCenter(models.Model):
	_name = 'odoocms.entrytest.center'
	_description = 'Test Center'
	
	name = fields.Char(string='City Name')
	code = fields.Char(string='Code')
	capacity = fields.Integer('Capacity')
	location = fields.Char(string='Location')
	date_test = fields.Date('Test Date')
	time_slot = fields.Char('Time Slot')
	application_ids = fields.One2many('odoocms.entrytest.application','center_id','Applications')
	
	@api.model
	def get_import_templates(self):
		return [{
			'label': _('Import Template for Entry Test Centers'),
			'template': '/odoocms_entry_test/static/xls/odoocms_entrytest_center.xlsx'
		}]
	
	
class OdooCMSEntryTestCenterSequance(models.Model):
	_name = 'odoocms.entrytest.center.sequence'
	_description = 'Test Center Sequence'
	
	center_id = fields.Many2one('odoocms.entrytest.center', 'Center Id')
	entrytest_id = fields.Many2one('odoocms.entrytest', 'EntryTest Id')
	hssc_group = fields.Selection([('pre_eng', 'Pre Engineering'), ('ics', 'ICS')],
		string='degree', default='ics')  # char
	entryID_from = fields.Text('ID Range Start')
	entryID_to = fields.Text('ID Range End')
	active = fields.Boolean(string="Is Active", default=False)

class OdooCMSEntryTestApplication(models.Model):
	_name = 'odoocms.entrytest.application'
	_description = 'Application for Entry Test'
	
	name = fields.Char(string='Candidate Name', help="Name of Candidate")
	entryID = fields.Integer(string='Entry Test ID')
	father_name = fields.Char(string='Father Name')
	guardian_name = fields.Char(string='Guardian Name', help="Applicant name on voucher")
	guardian_cnic = fields.Char(string='Guardian CNIC')
	date_of_birth = fields.Date(string="Date of Birth")
	gender = fields.Selection([ ('male', 'Male'),('female', 'Female'),],'Gender', default='male')
	cnic = fields.Char(string='CNIC')
	mobile = fields.Char(string="Mobile")
	email = fields.Char(string='Email')
	guardian_number = fields.Char(string='Father/Guardian Contact Number')
	image = fields.Binary(string="Applicant Image")
	
	domicile = fields.Char(string='Domicile')
	district = fields.Char(string='District')
	
	street = fields.Char(string='Street', help="Enter the First Part of Address")
	street2 = fields.Char(string='Street2', help="Enter the Second Part of Address")
	
	is_same_address = fields.Boolean(string="Is Same Address", default=False, help="Tick the field if the Present and permanent address is same")
	per_street = fields.Char(string='Per. Street', help="Enter the First Part of Permanenet Address")
	per_street2 = fields.Char(string='Per. Street2', help="Enter the First Part of Permanent Address")
	
	ssc_total_marks = fields.Integer('SSC Total Marks')
	ssc_obtained_marks = fields.Integer('SSC Obtained Marks')
	ssc_passing_year = fields.Char(string='SSC Passing Year')
	ssc_board = fields.Text(string='SSC Board')
	
	hssc_total_marks = fields.Integer('HSSC Total Marks')
	hssc_obtained_marks = fields.Integer('HSSC Obtained Marks')
	hssc_passing_year = fields.Char(string='HSSC Passing Year')
	hssc_board = fields.Text(string='HSSC Board')
	hssc_group = fields.Char(string='HSSC Group')
	
	center_id = fields.Many2one('odoocms.entrytest.center', 'Test Center')
	# state = fields.Char(string='state', default="draft")
	state = fields.Selection(
		[('draft', 'Draft'), ('confirm', 'Confirm'),('submit', 'Submit'),('verification', 'Verify'), ('approve', 'Approve'),
		 ('reject', 'Reject'), ('done', 'Done'),], string='Status',
		default='draft')
	
	@api.model
	def get_import_templates(self):
		return [{
			'label': _('Import Template for Entry Test Applications'),
			'template': '/odoocms_entry_test/static/xls/odoocms_entrytest_application.xlsx'
		}]

class OdooCMSEntryTestInstructions(models.Model):
	_name = 'odoocms.entrytest.instruction'
	_description = 'Test Instructions'
	
	name = fields.Text('Instruction')
	code = fields.Char('Instruction Code')
	active = fields.Boolean(string="Is Active", default=False)
	
	
	