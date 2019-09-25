
from odoo import fields, models, _, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools.safe_eval import safe_eval
import pdb
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class OdooCMSAdmissionApplication(models.Model):
	_name = 'odoocms.application'
	_description = 'Applications for the admission'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_order = 'id desc'
	
	READONLY_STATES = {
		'approve': [('readonly', True)],
		'open': [('readonly', True)],
		'done': [('readonly', True)],
		'reject': [('readonly', True)],
	}
	
	@api.depends('first_name', 'last_name')
	def _get_applicant_name(self):
		for applicant in self:
			applicant.name = (applicant.first_name or '') + ' ' + (applicant.last_name or '')
	
	domicile = fields.Char(string='Domicile',states=READONLY_STATES)
	first_name = fields.Char(string='First Name', help="First name of Student",states=READONLY_STATES)
	last_name = fields.Char(string='Last Name', help="Last name of Student",states=READONLY_STATES)
	name = fields.Char('Name',compute='_get_applicant_name',store=True)
	cnic = fields.Char(string='CNIC')
	image = fields.Binary(string='Image', attachment=True, help="Provide the image of the Student")

	email = fields.Char(string='Email')
	phone = fields.Char(string='Phone')
	mobile = fields.Char(string='Mobile')
	
	father_name = fields.Char(string="Father Name")
	religion_id = fields.Many2one('odoocms.religion', string="Religion")

	date_of_birth = fields.Date(string="Date Of Birth")
	gender = fields.Selection([('m', 'Male'), ('f', 'Female'), ('o', 'Other')],
		string='Gender', default='m', track_visibility='onchange')  # char
	blood_group = fields.Selection(
		[('A+', 'A+ve'), ('B+', 'B+ve'), ('O+', 'O+ve'), ('AB+', 'AB+ve'),
		 ('A-', 'A-ve'), ('B-', 'B-ve'), ('O-', 'O-ve'), ('AB-', 'AB-ve')],
		'Blood Group', default='A+', track_visibility='onchange')
	nationality = fields.Many2one('res.country', string='Nationality', ondelete='restrict',
		help="Select the Nationality")
	
	
	application_no = fields.Char(string='Application  No', copy=False, readonly=True, index=True, 
		default=lambda self: _('New'))
	application_date = fields.Datetime('Application Date', copy=False,states=READONLY_STATES,
		default=lambda self: fields.Datetime.now())
		
	active = fields.Boolean(string='Active', default=True)
	company_id = fields.Many2one('res.company', string='Institute', default=lambda self: self.env.user.company_id)
	
	

	street = fields.Char(string='Street', help="Enter the First Part of Address")
	street2 = fields.Char(string='Street2', help="Enter the Second Part of Address")
	city = fields.Char(string='City', help="Enter the City Name")
	zip = fields.Char(change_default=True)
	state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
		domain="[('country_id', '=?', country_id)]")
	country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', help="Select the Country")
	
	is_same_address = fields.Boolean(string="Permanent Address same as above", default=False, help="Tick the field if the Present and permanent address is same")
	per_street = fields.Char(string='Per. Street', help="Enter the First Part of Permanenet Address")
	per_street2 = fields.Char(string='Per. Street2', help="Enter the First Part of Permanent Address")
	per_city = fields.Char(string='Per. City', help="Enter the City Name of Permanent Address")
	per_zip = fields.Char(change_default=True)
	per_state_id = fields.Many2one("res.country.state", string='Per State', ondelete='restrict',
		domain="[('country_id', '=?', per_country_id)]")
	per_country_id = fields.Many2one('res.country', string='Per. Country', ondelete='restrict', help="Select the Country")

	description = fields.Text(string="Note")

	# class_id = fields.Many2one('odoocms.class', string="Class")
	
	document_count = fields.Integer(compute='_document_count', string='# Documents')
	verified_by = fields.Many2one('res.users', string='Verified by', help="The Document is Verified By")
	reject_reason = fields.Many2one('odoocms.application.reject.reason', string='Reject Reason',
		help="Reason of Application rejection")

	register_id = fields.Many2one('odoocms.admission.register', 'Admission Register',states=READONLY_STATES)
	academic_session_id = fields.Many2one('odoocms.academic.session','Academic Session',related='register_id.academic_session_id',store=True)
	career_id = fields.Many2one('odoocms.career','Career',related='register_id.career_id',store=True)
	
	academic_ids = fields.One2many('odoocms.application.academic','application_id','Academics',states=READONLY_STATES)
	preference_ids = fields.One2many('odoocms.application.preference', 'application_id', 'Preferences',states=READONLY_STATES)
	
	ssc_marks = fields.Integer('SSC Marks',compute='_get_marks',store=True)
	inter_marks = fields.Integer('Inter Marks',compute='_get_marks',store=True)
	inter_total_marks = fields.Integer('Inter Total Marks', compute='_get_marks', store=True)
	repeat_times = fields.Integer('Repeat/Improvement Times',states=READONLY_STATES)
	
	is_additional = fields.Boolean('Is Additional Subject',states=READONLY_STATES)
	is_hafiz = fields.Boolean('Is Hafiz-e-Quran?',states=READONLY_STATES)
	
	entryID = fields.Char('Entry ID',states=READONLY_STATES)
	entry_score = fields.Integer('Entry Score',states=READONLY_STATES)
	user_id = fields.Many2one('res.users','Login User')
	
	improvement_deduction = fields.Integer('Improvement',compute='_get_adjustments', store=True)
	additional_deduction = fields.Integer('Additional Subject',compute='_get_adjustments', store=True)
	hafiz_marks = fields.Integer('Hafiz-e-Quran',compute='_get_adjustments', store=True)
	adjusted_score = fields.Integer('Adjusted Score',compute='_get_adjustments', store=True)
	
	ssc_percentage = fields.Float('SSC Percentage',compute='_get_marks', digits=(8, 3), store=True)
	inter_percentage = fields.Float('Intermediate Percentage', compute='_get_adjustments', digits=(8, 3), store=True)
	entry_percentage = fields.Float('Entry', compute='_get_merit_score', digits=(8, 3), store=True)
	
	merit_score = fields.Float('Merit Score', compute='_get_merit_score',digits=(8, 3), store=True)
	merit_number = fields.Integer('Merit Number')
	
	# branch_code = fields.Text('Branch Code')
	# voucher_no = fields.Text('Voucher Number')
	# submission_date = fields.Date(string="Submission Date")
	# amount = fields.Integer('Voucher Amount')
	
	program_id = fields.Many2one('odoocms.program', 'Offered Program')
	preference = fields.Integer('Preference')
	student_id = fields.Many2one('odoocms.student', 'Student')
	
	locked = fields.Boolean('Locked', default=False)
	state = fields.Selection(
		[('draft', 'Draft'), ('confirm', 'Confirm'), ('submit', 'Submit'), ('verification', 'Verify'),
		 ('approve', 'Approve'), ('open', 'Open'),
		 ('reject', 'Reject'), ('done', 'Done'), ], string='Status',
		default='draft', track_visibility='onchange')
	
	merit_ids = fields.One2many('odoocms.application.merit','application_id','Merit Lists')
	
	@api.multi
	def name_get(self):
		return [(rec.id, (rec.name or '') + '-' + (rec.last_name or '')) for rec in self]
	
	@api.model
	def create(self, vals):        
		if vals.get('application_no', _('New')) == _('New'):
			vals['application_no'] = self.env['ir.sequence'].next_by_code('odoocms.application') or _('New')
		res = super(OdooCMSAdmissionApplication, self).create(vals)
		return res

	@api.multi
	def unlink(self):        
		for rec in self:
			if rec.state != 'reject':
				raise ValidationError(_("Application can only be deleted after Rejecting it"))
		
	@api.depends('inter_marks','repeat_times','is_additional','is_hafiz')
	def _get_adjustments(self):
		for rec in self:
			rec.improvement_deduction = -1 * min(rec.repeat_times*10,20) if rec.repeat_times and rec.repeat_times > 0 else 0
			rec.additional_deduction = -10 if rec.is_additional else 0
			rec.hafiz_marks = 20 if rec.is_hafiz else 0
			rec.adjusted_score = rec.inter_marks + rec.improvement_deduction + rec.additional_deduction + rec.hafiz_marks
			rec.inter_percentage = (100.00 * rec.adjusted_score) / (rec.inter_total_marks or 1100) * 4
	
	@api.depends('ssc_marks', 'adjusted_score', 'entry_score')
	def _get_merit_score(self):
		for rec in self:
			rec.entry_percentage = 100.0 * rec.entry_score / 800 * 5
			rec.merit_score = rec.ssc_percentage + rec.inter_percentage + rec.entry_percentage
	
	@api.depends('academic_ids','academic_ids.obtained_marks', 'academic_ids.total_marks', 'academic_ids.degree_level')
	def _get_marks(self):
		for rec in self:
			for academic in rec.academic_ids:
				if academic.degree_level and academic.total_marks and academic.obtained_marks:
					if academic.degree_level == 'matric':
						academic.application_id.ssc_marks = academic.obtained_marks
						academic.application_id.ssc_percentage = (100.00 * academic.obtained_marks) / academic.total_marks
					if academic.degree_level == 'inter':
						academic.application_id.inter_marks = academic.obtained_marks
						academic.application_id.inter_total_marks = academic.total_marks



	@api.multi
	def send_to_verify(self):
		for rec in self:
			#document_ids = self.env['odoocms.documents'].search([('application_ref', '=', rec.id)])
			#if not document_ids:
			#	raise ValidationError(_('No Documents provided'))
			rec.write({'state': 'verification'})

	
	@api.multi
	def reject_application(self):        
		for rec in self:
			rec.write({
				'state': 'reject'
			})

	#@api.multi
	#@api.constrains('birth_date')
	#def _check_birthdate(self):
	#    for record in self:
	#        if record.birth_date > fields.Date.today():
	#            raise ValidationError(_(
	#                "Birth Date can't be greater than current date!"))

	#@api.multi
	#@api.constrains('register_id', 'application_date')
	#def _check_admission_register(self):
	#    for rec in self:
	#        start_date = fields.Date.from_string(rec.register_id.start_date)
	#        end_date = fields.Date.from_string(rec.register_id.end_date)
	#        application_date = fields.Date.from_string(rec.application_date)
	#        if start_date > application_date  or application_date > end_date:
	#            raise ValidationError(_(
	#                "Application Date should be between Start Date & \
	#                End Date of Admission Register."))

	@api.multi
	def application_verify(self):
		for rec in self:
			document_ids = self.env['odoocms.documents'].search([('application_ref', '=', rec.id)])
			if document_ids:
				doc_status = document_ids.mapped('state')
				if all(state in ('done', 'returned') for state in doc_status):
					rec.write({
						'verified_by': self.env.uid,
						'state': 'approve'
					})
				else:
					raise ValidationError(_('All Documents are not Verified Yet, '
						'Please complete the verification'))
			
			#else:
			#	raise ValidationError(_('No Documents provided'))
			rec.write({'state': 'approve'})

	@api.multi
	def _document_count(self):
		for rec in self:
			document_ids = self.env['odoocms.documents'].search([('application_ref', '=', rec.id)])
			rec.document_count = len(document_ids)
	
	def _get_fee_amount(self):
		fee_structure = self.env['odoocms.fee.structure'].search(
			[('academic_session_id', '=', self.academic_session_id.id)])
		payment_types = ['admissiontime','persemester','peryear']
		
		receipts = self.env['odoocms.receipt.type'].browse([1,6])
		fee_head_ids = receipts.mapped('fee_head_ids').ids
		fee_lines = fee_structure.line_ids.filtered(
			lambda l: l.fee_head_id.id in fee_head_ids
				and l.payment_type in payment_types
				and (not l.program_ids or self.program_id.id in l.program_ids.ids)
				and (not l.semester_ids or 1 in l.semester_ids.ids)
		)
		
		total = 0.0
		for line in fee_lines:
			if not line.domain or self.env['odoocms.student'].search(safe_eval(line.domain) + [('id', '=', self.id)]):
				total += line.fee_amount
		
		paid = 0.0
		prev_lists = self.env['odoocms.application.merit'].search([('application_id','=',self.id)])
		for lst in prev_lists:
			paid += lst.amount
		return total - paid
		
	
	@api.multi
	def document_view(self):
		self.ensure_one()
		domain = [
			('application_ref', '=', self.id)]
		return {
			'name': _('Documents'),
			'domain': domain,
			'res_model': 'odoocms.documents',
			'type': 'ir.actions.act_window',
			'view_id': False,
			'view_mode': 'tree,form',
			'view_type': 'form',
			'help': _('''<p class="oe_view_nocontent_create">
				Click to Create for New Documents
				</p>'''),
			'limit': 80,
			'context': "{'default_application_ref': '%s'}" % self.id
		}
	
	@api.multi
	def create_student(self, view=False):
		for rec in self:
			semester = self.env['odoocms.semester'].search([('number', '=', 1)], limit=1)
			values = {
				'name': rec.name,
				'first_name': rec.first_name,
				'last_name': rec.last_name,
				'father_name': rec.father_name,
				
				'cnic': rec.cnic,
				'gender': rec.gender,
				'date_of_birth': rec.date_of_birth,
				'blood_group': rec.blood_group,
				'religion_id': rec.religion_id.id,
				'nationality': rec.nationality.id,
				
				'email': rec.email,
				'mobile': rec.mobile,
				'phone': rec.phone,
				'image': rec.image,
				
				'id_number': rec.entryID,
				'entryID': rec.entryID,
				'user_id': rec.user_id.id,
				
				'street': rec.street,
				'street2': rec.street2,
				'city': rec.city,
				'zip': rec.zip,
				'state_id': rec.state_id.id,
				'country_id': rec.country_id.id,
				
				'is_same_address': rec.is_same_address,
				'per_street': rec.per_street,
				'per_street2': rec.per_street2,
				'per_city': rec.per_city,
				'per_zip': rec.per_zip,
				'per_state_id': rec.per_state_id.id,
				'per_country_id': rec.per_country_id.id,
				
				'application_id': rec.id,
				'is_student': True,
				'career_id': rec.career_id.id,
				'program_id': rec.program_id.id,
				'academic_session_id': rec.academic_session_id.id,
				'academic_semester_id': rec.register_id.academic_semester_id.id,
				'semester_id': 0, #semester.id,
				
				# 'admission_no': ,
				'company_id': rec.company_id.id,
			}
			if not rec.is_same_address:
				pass
			else:
				values.update({
					'per_street': rec.street,
					'per_street2': rec.street2,
					'per_city': rec.city,
					'per_zip': rec.zip,
					'per_state_id': rec.state_id.id,
					'per_country_id': rec.country_id.id,
				})
			
			student = self.env['odoocms.student'].create(values)
			rec.write({
				'state': 'done',
				'student_id': student.id,
			})
		
		if view:
			return {
				'name': _('Student'),
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'odoocms.student',
				'type': 'ir.actions.act_window',
				'res_id': student.id,
				'context': self.env.context
			}
		else:
			return student
	
	@api.multi
	def create_application_user(self):
		group_portal = self.env.ref('base.group_portal')
		users_res = self.env['res.users']
		for record in self:
			if not record.user_id:
				data = {
					'name': record.first_name + ' ' + (record.last_name or ''),
					#'partner_id': record.partner_id.id,
					'login': record.entryID or record.email,
					'password': record.mobile or record.entryID or '123456',
					'groups_id': group_portal,
				}
				user_id = users_res.create(data)
				record.user_id = user_id.id


class OdooCMSApplicationRejectReason(models.Model):
	_name = 'odoocms.application.reject.reason'
	_description = 'Reject Reasons'

	name = fields.Char(string="Reason", required=True,
		help="Possible Reason for rejecting the Applications")
	code = fields.Char(string='Code')


class OdoocmsMeritList(models.Model):
	_name = 'odoocms.merit.list'
	_description = 'Merit List'
	_order = 'number'
	
	name = fields.Char('List Name')
	code = fields.Char('Code')
	number = fields.Integer('Number')
	
	
class OdoocmsMeritRegister(models.Model):
	_name = 'odoocms.merit.register'
	_description = 'Merit Register'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_order = 'register_id desc, merit_list_number desc'
	
	register_id = fields.Many2one('odoocms.admission.register', 'Application Register')
	name = fields.Char('List Name')
	date_list = fields.Date('Merit List Date')
	merit_list_id = fields.Many2one('odoocms.merit.list','Merit List')
	merit_list_number = fields.Integer('List Number', related='merit_list_id.number',store=True)
	remarks = fields.Text('Remarks')
	
	next_merit_register_id = fields.Many2one('odoocms.merit.register','Next Merit Register')
	prev_merit_register_id = fields.Many2one('odoocms.merit.register', 'Prev Merit Register')
	merit_application_ids = fields.One2many('odoocms.application.merit', 'merit_register_id', string='Merit Detail')
	
	
class OdoocmsApplicationMerit(models.Model):
	_name = 'odoocms.application.merit'
	_description = 'Application Merit'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_rec_name = 'application_id'
	_order = 'merit_register_id, merit_number, merit_list_number desc'
	
	merit_register_id = fields.Many2one('odoocms.merit.register', 'Merit Register', ondelete='cascade')
	merit_list_number = fields.Integer('List Number', related='merit_register_id.merit_list_id.number', store=True)
	register_id = fields.Many2one('odoocms.admission.register','Admission Register',related='merit_register_id.register_id')
	application_id = fields.Many2one('odoocms.application', string='Applicant')
	entryID = fields.Char('Entry ID', related='application_id.entryID',store=True)
	program_id = fields.Many2one('odoocms.program', string='Program')
	preference = fields.Integer('Preference')
	merit_number = fields.Integer('Merit No.')
	program_merit_number = fields.Integer('Program Merit No.')
	date_interview = fields.Datetime('Interview Date & Time')
	amount = fields.Float('Fee Amount')
	locked = fields.Boolean('Locked',default=False)
	comments = fields.Text('Comments',readonly=True, states={'draft': [('readonly', False)]})
	state = fields.Selection([
		('draft','Draft'),('done','Done'),('cancel','Cancel'),('reject','Rejected'),('absent','Absent')
	],'Status',default='draft')
	line_ids = fields.One2many('odoocms.application.merit.line','application_merit_id','Preferences')
	
	next_merit_app_id = fields.Many2one('odoocms.application.merit', 'Next Merit')
	prev_merit_app_id = fields.Many2one('odoocms.application.merit', 'Prev Merit')
	
	_sql_constraints = [
		('application_merit', 'unique(application_id,merit_register_id)', "Another Merit already exists with this Application and Merit List!"), ]
		
	
class OdoocmsApplicationMeritLine(models.Model):
	_name = 'odoocms.application.merit.line'
	_description = 'Application Merit Line'
	
	application_merit_id = fields.Many2one('odoocms.application.merit', 'Merit Application', ondelete='cascade')
	merit_register_id = fields.Many2one('odoocms.merit.register','Merit Register', related='application_merit_id.merit_register_id')
	application_id = fields.Many2one('odoocms.application', string='Applicant',related='application_merit_id.application_id')
	program_id = fields.Many2one('odoocms.program', string='Program')
	preference = fields.Integer('Preference')
	program_merit_number = fields.Integer('Program Merit No.')
	seats = fields.Integer('Seats')
	selected = fields.Boolean('Selected')
	
	
class OdoocmsApplicationPreference(models.Model):
	_name = 'odoocms.application.preference'
	_description = 'Application Preference'
	_order = 'application_id desc, preference'
	
	application_id = fields.Many2one('odoocms.application', string='Applicant')
	program_id = fields.Many2one('odoocms.program', string='Program')
	preference = fields.Integer(string='Preference')
	
	_sql_constraints = [
		('application_program', 'unique(application_id,program_id)', "Another Preference already exists with this Application and Program!"), ]

	
class OdooCMSAdmissionApplicationAcademic(models.Model):
	_name = 'odoocms.application.academic'
	_description = 'Applications Academics'
	
	degree_level = fields.Selection([('matric','Matric'),('inter','Intermediate')],'Degree Level',required=1)
	degree = fields.Char('Degree',required=1)
	year = fields.Char('Passing Year')
	board = fields.Char('Board Name')
	subjects = fields.Char('Subjects')
	total_marks = fields.Integer('Total Marks',required=1)
	obtained_marks = fields.Integer('Obtained Marks',required=1)
	application_id = fields.Many2one('odoocms.application','Applicant')


class OdooCMSAdmissionApplicationDocuments(models.Model):
	_name = 'odoocms.application.documents'
	_description = 'Applications Documents'
	
	application_id = fields.Many2one('odoocms.application', string='Applicant')
	matric_scaned_copy = fields.Binary('Scanned Copy of Matric')
	matric_scaned_copy_name = fields.Text('Scanned Copy of Matric Name')
	matric_scaned_copy_size = fields.Text('Scanned Copy of Matric Size')
	
	inter_scaned_copy = fields.Binary('Scanned Copy of Inter')
	inter_scaned_copy_name = fields.Text('Scanned Copy of Inter Name')
	inter_scaned_copy_size = fields.Text('Scanned Copy of Inter Size')
	
	domicile_scaned_copy = fields.Binary('Scanned Copy of Domicile')
	domicile_scaned_copy_name = fields.Text('Scanned Copy of Domicile Name')
	domicile_scaned_copy_size = fields.Text('Scanned Copy of Domicile Size')
	
	prc_scaned_copy = fields.Binary('Scanned Copy of PRC')
	prc_scaned_copy_name = fields.Text('Scanned Copy of PRC Name')
	prc_scaned_copy_size = fields.Text('Scanned Copy of PRC Size')
	
	hafiz_scaned_copy = fields.Binary('Scanned Copy of Hafiz-e-Quran')
	hafiz_scaned_copy_name = fields.Text('Scanned Copy of Hafiz-e-Quran Name')
	hafiz_scaned_copy_size = fields.Text('Scanned Copy of Hafiz-e-Quran Size')


class OdoocmsAdmissionConfirmFee(models.Model):
	_name = 'odoocms.admission.confirm.fee'
	_description = 'Admission confirm Fee'
	
	entryID = fields.Char('Entry ID',readonly=True, states={'draft': [('readonly', False)]})
	application_id = fields.Many2one('odoocms.application', string='Applicant',compute='_get_application',store=True)
	merit_id = fields.Many2one('odoocms.application.merit','Merit')
	date_paid = fields.Date('Date',readonly=True, states={'draft': [('readonly', False)]})
	amount = fields.Float('Amount',readonly=True, states={'draft': [('readonly', False)]})
	state = fields.Selection([('draft','Draft'),('done','Done')],'Status',default='draft',readonly=True, states={'draft': [('readonly', False)]})
	
	@api.depends('entryID')
	def _get_application(self):
		for rec in self:
			if rec.entryID:
				application = self.env['odoocms.application'].search([('entryID','=',rec.entryID)])
				if application:
					rec.application_id = application.id
	
	@api.model
	def get_import_templates(self):
		return [{
			'label': _('Import Template for Admission Confirm Fee'),
			'template': '/odoocms_admission/static/xls/odoocms_admission_confirm_fee.xls'
		}]

	
class OdooCMSAdmissionHafizQuranResult(models.Model):
	_name = 'odoocms.application.hafiz.quran.result'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = 'Hafiz Quran Result'

	name = fields.Char('Name',required=1)
	total_marks = fields.Integer('Total Marks', required=1)
	obtained_marks = fields.Integer('Obtained Marks', required=1)
	application_id = fields.Many2one('odoocms.application', 'Applicant')
	date = fields.Datetime('Date')
	
	
class OdoocmsApplicationMeritLine(models.Model):
	_name = 'odoocms.condidate.verification'
	_description = 'Application Candidate Verification'

	name = fields.Char(string='Name')
	cnic = fields.Char('CNIC', required = True)
	mobile = fields.Char(string='Mobile', required = True)
	is_verified = fields.Boolean('Is Verified')


class OdoocmsApplicationBoard(models.Model):
	_name = 'odoocms.application.board'
	_description = 'Education Board'

	name = fields.Char(string='Name')
	sh_name = fields.Char(string='Short Name')
	code = fields.Char('Code')


class OdoocmsApplicationPassingYear(models.Model):
	_name = 'odoocms.application.passing.year'
	_description = 'Application Passing Year'

	name = fields.Char(string='Name',required = True)
	code = fields.Char(string='code')