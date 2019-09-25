import pdb
import time
import datetime
from openerp import api, fields, models,_
from dateutil.relativedelta import relativedelta


class OdooCMSGenerateChallan(models.TransientModel):
	_name ='odoocms.generate.challan'
	_description = 'Generate Challan'
				
	@api.model	
	def _get_students(self):
		if self.env.context.get('active_model', False) == 'odoocms.student' and self.env.context.get('active_ids', False):
			return self.env.context['active_ids']
			
	student_ids = fields.Many2many('odoocms.student', string='Students',
		help="""Only selected students will be Processed.""",default=_get_students)
	receipt_type_ids = fields.Many2many('odoocms.receipt.type',string='Receipt For')
	academic_semester_id = fields.Many2one('odoocms.academic.semester','Academic Term')
	date_due = fields.Date('Due Date', default=(fields.Date.today() + relativedelta(days=7)))
	semester_required = fields.Boolean('Semester Required?', default=False)
	override_amount = fields.Boolean('Override Amount?', default=False)
	# state = fields.Selection([
	# 	('no','Not Required Yet'),('tobe','Needs to be Generated'),('generate','Generate Challan')],'Challan Action',default='no')
	override_line = fields.One2many('odoocms.challan.amount.override','challan_id','Override Lines')
	
	@api.onchange('receipt_type_ids')
	def onchange_receipt_type(self):
		self.semester_required = any([receipt.semester_required for receipt in self.receipt_type_ids])
		self.override_amount = any([receipt.override_amount for receipt in self.receipt_type_ids])
		if self.override_amount:
			for receipt in self.receipt_type_ids.filtered(lambda l: l.override_amount == True):
				for head in receipt.fee_head_ids:
					values = {
						'fee_head_id': head.id,
						'fee_head': head.id,
						'fee_amount': head.lst_price,
						'note': 'Test',
					}
					self.update({
						'override_line': [(0, 0, values)],
					})
					#return {'value': {'field': value}}
			
			
	@api.multi
	def generate_challan(self):
		invoices = self.env['account.invoice']
		for student in self.student_ids:
			# if self.state == 'no':
			# 	student.challan_status = 'no'
			# elif self.state == 'tobe':
			# 	student.challan_status = 'tobe'
			# elif self.state == 'generate':
			if self.academic_semester_id and \
				self.env['account.invoice'].search([
					('student_id','=',student.id),('academic_semester_id','=',self.academic_semester_id.id)]):
				continue
			invoices += student.generate_challan(
				semester=self.academic_semester_id, receipts=self.receipt_type_ids, date_due=self.date_due, override_line=self.override_line)
			
			student.challan_status = 'generate'
		
		if invoices:
			invoice_list = invoices.mapped('id')
			form_view = self.env.ref('odoocms_fee.odoocms_receipt_form')
			tree_view = self.env.ref('odoocms_fee.odoocms_receipt_tree')
			return {
				'domain': [('id', 'in', invoice_list)],
				'name': _('Invoices'),
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'account.invoice',
				'view_id': False,
				'views': [
					(tree_view and tree_view.id or False, 'tree'),
					(form_view and form_view.id or False, 'form'),
				],
				# 'context': {'default_class_id': self.id},
				'type': 'ir.actions.act_window'
			}
		else:
			return {'type': 'ir.actions.act_window_close'}


class OdooCMSChallanAmountOverride(models.TransientModel):
	_name = 'odoocms.challan.amount.override'
	_description = 'Challan Amount Override'
	
	fee_head_id = fields.Many2one('odoocms.fee.head', string='Fee')
	fee_head = fields.Integer()
	fee_amount = fields.Float('Amount')
	payment_type = fields.Selection([
		('admissiontime', 'Admission Time'),
		('permonth', 'Per Month'),
		('peryear', 'Per Year'),
		('persemester', 'Per Semester'),
		('onetime', 'One Time'),
	
	], string='Payment Type', related="fee_head_id.payment_type")
	fee_description = fields.Text('Description', related='fee_head_id.description_sale')
	note = fields.Char('Note')
	challan_id = fields.Many2one('odoocms.generate.challan', 'Challan')
	
	
class OdooCMSAdmissionChallan(models.TransientModel):
	_name = 'odoocms.admission.challan'
	_description = 'Admission Challan'
	
	@api.model
	def _get_applicants(self):
		applicants = []
		if self.env.context.get('active_model', False) == 'odoocms.application' \
				and self.env.context.get('active_ids', False):
			for rec in self.env['odoocms.application'].browse(self.env.context.get('active_ids')):
				applicants.append(rec.id)
			return applicants
	
	applicant_ids = fields.Many2many('odoocms.application', string='Applicants',
		help="""Fee Chalan for Only selected applicants will be generated.""", default=_get_applicants)
	# state = fields.Selection([
	# 	('no', 'Not Required Yet'), ('tobe', 'Needs to be Generated'),('generate', 'Generate')
	# ], 'Challan Status', default='no')
	
	@api.multi
	def generate_admission_challan(self):
		invoices = self.env['account.invoice']
		for applicant in self.applicant_ids:
			# if self.state == 'no':
			# 	applicant.challan_status = 'no'
			#
			# elif self.state == 'tobe':
			# 	applicant.challan_status = 'tobe'
			#
			# elif self.state == 'generate' and applicant.challan_status == 'tobe':
			invoices += applicant.generate_challan()
				
		applicant.challan_status = 'generate'
		invoice_list = invoices.mapped('id')
		return {
			'domain': [('id', 'in', invoice_list)],
			'name': _('Invoicess'),
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'account.invoice',
			'view_id': False,
			# 'context': {'default_class_id': self.id},
			'type': 'ir.actions.act_window'
		}
		
		#return {'type': 'ir.actions.act_window_close'}






