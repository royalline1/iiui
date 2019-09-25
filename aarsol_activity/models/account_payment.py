
from odoo import api, models, fields, _, SUPERUSER_ID
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import pdb

class AccountPayment(models.Model):
	_name = 'account.payment'
	_inherit = ['account.payment','mail.thread', 'mail.activity.mixin']

	state = fields.Selection([
			('draft', 'Draft'), ('approval','Approval'), ('approved','Approved'), 
			('posted', 'Posted'), ('sent', 'Sent'), ('reconciled', 'Reconciled'), ('cancelled', 'Cancelled')
		], readonly=True, default='draft', copy=False, string="Status")
	
	has_open_invoices = fields.Boolean(compute="_compute_open_invoice_ids",)
	
	@api.multi
	def name_get(self):
		result = []
		for payment in self:
			name = payment.name or ''
			name += (' - ' + payment.communication or '')
			result.append((payment.id, name))
		return result
	
	@api.multi
	def submit_for_approval(self, vals):
		for payment in self:
			self.state = 'approval'
			activity = self.env.ref('aarsol_activity.mail_act_payment_approval')
			payment.activity_schedule('aarsol_activity.mail_act_payment_approval',
			    user_id=activity.user_id.id or self.env.user.id)
	
	@api.multi
	def payment_approved(self):
		for payment in self:
			payment.state = 'approved'
	
	def action_validate_invoice_payment(self):
		if any(len(record.invoice_ids) != 1 for record in self):
			# For multiple invoices, there is account.register.payments wizard
			raise UserError(_("This method should only be called to process a single invoice's payment."))
		
		if self.payment_type == 'outbound' and self.partner_type == 'supplier':
			return {
				'name': _('Payment'),
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'account.payment',
				'view_id': False,
				'type': 'ir.actions.act_window',
				'domain': [('id', 'in', self.ids)],
			}
		else:
			return super(AccountPayment, self).action_validate_invoice_payment()
	
	@api.multi
	def post(self):
		""" Create the journal items for the payment and update the payment's state to 'posted'.
			A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
			and another in the destination reconcilable account (see _compute_destination_account_id).
			If invoice_ids is not empty, there will be one reconcilable move line per invoice to reconcile with.
			If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
		"""
		for rec in self:
			
			#if rec.state != 'draft':
			#	raise UserError(_("Only a draft payment can be posted."))
			
			if any(inv.state != 'open' for inv in rec.invoice_ids):
				raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
			
			# keep the name in case of a payment reset to draft
			if not rec.name:
				# Use the right sequence to set the name
				if rec.payment_type == 'transfer':
					sequence_code = 'account.payment.transfer'
				else:
					if rec.partner_type == 'customer':
						if rec.payment_type == 'inbound':
							sequence_code = 'account.payment.customer.invoice'
						if rec.payment_type == 'outbound':
							sequence_code = 'account.payment.customer.refund'
					if rec.partner_type == 'supplier':
						if rec.payment_type == 'inbound':
							sequence_code = 'account.payment.supplier.refund'
						if rec.payment_type == 'outbound':
							sequence_code = 'account.payment.supplier.invoice'
				rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(
					sequence_code)
				if not rec.name and rec.payment_type != 'transfer':
					raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))
			
			# Create the journal entry
			amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
			move = rec._create_payment_entry(amount)
			
			# In case of a transfer, the first journal entry created debited the source liquidity account and credited
			# the transfer account. Now we debit the transfer account and credit the destination liquidity account.
			if rec.payment_type == 'transfer':
				transfer_credit_aml = move.line_ids.filtered(
					lambda r: r.account_id == rec.company_id.transfer_account_id)
				transfer_debit_aml = rec._create_transfer_entry(amount)
				(transfer_credit_aml + transfer_debit_aml).reconcile()
			
			rec.write({'state': 'posted', 'move_name': move.name})
		return True
	
	@api.depends('invoice_ids', 'invoice_ids.state')
	def _compute_open_invoice_ids(self):
		for rec in self:
			has_open_invoices = False
			if any(inv.state == 'open' for inv in rec.invoice_ids):
				has_open_invoices = True
			rec.has_open_invoices = has_open_invoices
			
			
	@api.multi
	def button_payment_invoices(self):
		if self.partner_type == 'supplier':
			views = [(self.env.ref('account.invoice_supplier_tree').id, 'tree'),
			         (self.env.ref('account.invoice_supplier_form').id, 'form')]
		else:
			views = [(self.env.ref('account.invoice_tree').id, 'tree'),
			         (self.env.ref('account.invoice_form').id, 'form')]
		return {
			'name': _('Invoices for Payment'),
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'account.invoice',
			'view_id': False,
			'views': views,
			'type': 'ir.actions.act_window',
			'domain': [('id', 'in', [x.id for x in self.invoice_ids])],
		}
