import pdb
import time
import datetime
from openerp import api, fields, models,_


class OdooCMSProcessFeePayment(models.TransientModel):
	_name ='odoocms.process.fee.payment'
	_description = 'Process Fee Payment'
				
	@api.model	
	def _get_payments(self):
		
		if self.env.context.get('active_model', False) == 'odoocms.fee.payment' and self.env.context.get('active_ids', False):
			return self.env.context['active_ids']
			
	payment_ids = fields.Many2many('odoocms.fee.payment', string='Students',
		help="""Only selected Payments will be Processed.""",default=_get_payments)
	
	@api.multi
	def process_payment(self):
		for payment in self.payment_ids:
			invoice = self.env['account.invoice'].search([('number','=',payment.receipt_number)])
			if invoice:
				due_date = fields.Date.from_string(invoice.date_due)
				payment_date = fields.Date.from_string(payment.date)
				days = (payment_date-due_date).days
				if days > 0:
					analytic_tags = self.env['account.analytic.tag']
					analytic_tags += invoice.student_id.program_id.department_id.campus_id.analytic_tag_id
					analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in analytic_tags]
					fee_line = {
						'price_unit': 100,
						'quantity': days,
						#'product_id': line.invoice_line.product_id.id,
						'name': 'Late Payment',
						'account_id': 232,  # Have to change
						'analytic_tag_ids': analytic_tag_ids,
						'invoice_id': invoice.id
					}
					self.env['account.invoice.line'].create(fee_line)
					
				invoice_ids = [(4, invoice.id, None)]
				data = {
					'payment_type': 'inbound',
					'payment_method_id': '1',
					'partner_type': 'customer',
					'currency_id': invoice.journal_id.currency_id.id,
					'partner_id': invoice.student_id and invoice.student_id.partner_id.id or invoice.applicant_id and invoice.applicant_id.partner_id.id,
					'payment_date': payment.date,
					'communication': payment.receipt_number,
					'amount': payment.amount,
					'journal_id': payment.journal_id.id,
					'invoice_ids': invoice_ids,
				}
				if invoice.state == 'sent':
					invoice.state = 'draft'
					invoice.action_invoice_open()
				
				pay_rec = self.env['account.payment'].create(data)
				pay_rec.action_validate_invoice_payment()
				payment.state = 'done'
			else:
				payment.state = 'error'
			
			
			#invoice_list = invoices.mapped('id')
			#return {
			#	'domain': [('id', 'in', invoice_list)],
			#	'name': _('Invoicess'),
			#	'view_type': 'form',
			#	'view_mode': 'tree,form',
			#	'res_model': 'account.invoice',
			#	'view_id': False,
			#	# 'context': {'default_class_id': self.id},
			#	'type': 'ir.actions.act_window'
			#}
		
		return {'type': 'ir.actions.act_window_close'}

