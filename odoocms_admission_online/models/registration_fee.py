from odoo import fields, models, _, api
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo.exceptions import ValidationError


class OdooCMSAdmissionFee(models.Model):
	_name = 'odoocms.admission.fee'
	_description = 'Admission  Fee'
	
	branch_code = fields.Char(string='Branch Code', help="Banch Code")
	voucher_no = fields.Char(string='Voucher Number', help="voucher Number")
	applicant_name = fields.Char(string='Applicant Name', help="Applicant name on voucher")
	submission_date = fields.Date(string="Submission Date")
	amount = fields.Integer('Voucher Amount')
	is_used = fields.Boolean(string="Already Used", default=False)
	
	@api.model
	def get_import_templates(self):
		return [{
			'label': _('Import Template for Admission Fee'),
			'template': '/odoocms_admission_online/static/xls/odoocms_admission_fee.xlsx'
		}]
	
	
class OdooCMSEntryTestResult(models.Model):
	_name = 'odoocms.entrytest.result'
	_description = 'Entry Test Result'
	_rec_name = 'applicantID'
	
	picture = fields.Binary('Image', help="Provide the image of the Student")
	cnic = fields.Char('CNIC')
	applicantID = fields.Char(string='Applicant ID', help="Applicant Test ID")
	applicant_name = fields.Char(string='Applicant Name')
	test_date = fields.Date(string="Test Date")
	test_score = fields.Integer('Test Score')
	
	@api.model
	def get_import_templates(self):
		return [{
			'label': _('Import Template for Entry Test Result'),
			'template': '/odoocms_admission_online/static/xls/odoocms_entrytest_result.xlsx'
		}]