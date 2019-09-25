
import datetime
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.tools import float_is_zero, float_compare
from odoo.tools.safe_eval import safe_eval
import pdb

class OdooCMSFeeReceipts(models.Model):
    _inherit = 'account.invoice'

    number = fields.Char(related='move_id.name', store=True, readonly=False, copy=False)
    student_id = fields.Many2one('odoocms.student', string='Student', readonly=True, states={'draft': [('readonly', False)]})
    student_name = fields.Char(string='Name', related='student_id.partner_id.name', store=True)

    program_id = fields.Many2one('odoocms.program','Program',readonly=True, states={'draft': [('readonly', False)]})
    applicant_id = fields.Many2one('odoocms.application', 'Applicant',readonly=True, states={'draft': [('readonly', False)]})
    fee_structure_id = fields.Many2one('odoocms.fee.structure', string='Fee Structure',readonly=True, states={'draft': [('readonly', False)]})
    batch_id = fields.Many2one('odoocms.batch','student_id.batch_id',store=True)
    academic_semester_id = fields.Many2one('odoocms.academic.semester','Academic Term')
    is_fee = fields.Boolean('Is Fee', default=False)
    is_cms = fields.Boolean('CMS Receipt?',default=False)
    fee_paid = fields.Boolean('Is Fee Paid', default=False)
    
    back_invoice = fields.Many2one('account.invoice','Back Invoice')
    forward_invoice = fields.Many2one('account.invoice','Forward Invoice')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('open', 'Open'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False,
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
             " * The 'Open' status is used when user creates invoice, an invoice number is generated. It stays in the open status till the user pays the invoice.\n"
             " * The 'In Payment' status is used when payments have been registered for the entirety of the invoice in a journal configured to post entries at bank reconciliation only, and some of them haven't been reconciled with a bank statement line yet.\n"
             " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
             " * The 'Cancelled' status is used when user cancel invoice.")

    @api.multi
    def add_follower(self, partners, subtype_ids=None):
        self.message_subscribe(partner_ids=partners.ids, subtype_ids=subtype_ids)

    @api.multi
    def add_followers(self, partners):
        mt_comment = self.env.ref('mail.mt_comment').id
        
        self.add_follower(partners, [mt_comment,])
        if self.student_id and self.student_id.user_id:
            self.add_follower(self.student_id.user_id.partner_id, [mt_comment,])

    @api.model
    def create(self, values):
        invoice = super(OdooCMSFeeReceipts,
                         self.with_context(mail_create_nolog=True, mail_create_nosubscribe=True)).create(values)
        invoice.sudo().add_followers(self.env.user.partner_id)
        return invoice

    @api.multi
    def action_invoice_send(self):
        for inv in self:
            inv.state = 'sent'

    @api.multi
    def action_invoice_open(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        to_open_invoices = self.filtered(lambda inv: inv.state == 'sent')
        to_open_invoices.write({'state':'draft'})
        return super(OdooCMSFeeReceipts,self).action_invoice_open()

    def _get_refund_common_fields(self):
        return super(OdooCMSFeeReceipts, self)._get_refund_common_fields() + \
               ['student_id', 'applicant_id','program_id','fee_structure_id','is_fee','is_cms']

    @api.multi
    def _get_report_base_filename(self):
        self.ensure_one()
        return self.type == 'out_invoice' and self.state == 'draft' and _('Draft Invoice') or \
               self.type == 'out_invoice' and self.state in ('open', 'sent', 'in_payment', 'paid') and _('Invoice - %s') % (
                   self.number) or \
               self.type == 'out_refund' and self.state == 'draft' and _('Credit Note') or \
               self.type == 'out_refund' and _('Credit Note - %s') % (self.number) or \
               self.type == 'in_invoice' and self.state == 'draft' and _('Vendor Bill') or \
               self.type == 'in_invoice' and self.state in ('open', 'in_payment', 'paid') and _('Vendor Bill - %s') % (
                   self.number) or \
               self.type == 'in_refund' and self.state == 'draft' and _('Vendor Credit Note') or \
               self.type == 'in_refund' and _('Vendor Credit Note - %s') % (self.number)

    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']
    
        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids.filtered(lambda line: line.account_id):
                raise UserError(_('Please add at least one invoice line.'))
            
            if inv.move_id:
                continue
                
            
            if not inv.date_invoice:
                inv.write({'date_invoice': fields.Date.context_today(self)})
            if not inv.date_due:
                inv.write({'date_due': inv.date_invoice})
            company_currency = inv.company_id.currency_id
        
            
        
            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()
        
            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.compute_invoice_totals(company_currency, iml)
        
            name = inv.name or ''
            if inv.payment_term_id:
                totlines = \
                inv.payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.date_invoice)[0]
                res_amount_currency = total_currency
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency._convert(t[1], inv.currency_id, inv.company_id,
                                                                    inv._get_currency_rate_date() or fields.Date.today())
                    else:
                        amount_currency = False
                
                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency
                
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)
        
            line = inv.finalize_invoice_move_lines(line)
        
            date = inv.date or inv.date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': inv.journal_id.id,
                'date': date,
                'narration': inv.comment,
            }
            
            #Added this IF
            if inv.number:
                move_vals['name'] = inv.number

            # Added the If and Else Condition
            #if inv.fee_paid:
            #    move_vals = {
            #        'line_ids': line,
            #    }
            #    inv.move_id.write(move_vals)
            #    move.post(invoice=inv)
            #else:
            move = account_move.create(move_vals)
            
            # Pass invoice in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            #if not inv.is_fee:
            move.post(invoice=inv)
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.write(vals)
        return True
    
    @api.multi
    def action_invoice_paid(self):
        # lots of duplicate calls to action_invoice_paid, so we remove those already paid
        to_pay_invoices = self.filtered(lambda inv: inv.state != 'paid')
        if to_pay_invoices.filtered(lambda inv: inv.state not in ('open', 'in_payment')):
            raise UserError(_('Invoice must be validated in order to set it to register payment.'))
        if to_pay_invoices.filtered(lambda inv: not inv.reconciled):
            raise UserError(
                _('You cannot pay an invoice which is partially paid. You need to reconcile payment entries first.'))
    
        for invoice in to_pay_invoices:
            if any([move.journal_id.post_at_bank_rec and move.state == 'draft' for move in
                    invoice.payment_move_line_ids.mapped('move_id')]):
                invoice.write({'state': 'in_payment'})
            else:
                invoice.write({'state': 'paid'})
                
                if invoice.student_id:
                    student = invoice.student_id
                    student.challan_status = 'paid'
                
                elif invoice.applicant_id:
                    applicant = invoice.applicant_id
                    first_semester_number = 1

                    first_semester = self.env['odoocms.semester'].browse(first_semester_number)
                    first_semester_scheme = self.env['odoocms.semester.scheme'].search([
                        ('academic_session_id', '=', applicant.academic_session_id.id),
                        ('semester_id', '=', first_semester.id)
                    ])
                    
                    student = applicant.create_student()
                    student.academic_semester_id = first_semester_scheme.academic_semester_id.id
                    student.semester_id = first_semester.id
                    #student.register_courses(first_semester_scheme)
                    applicant.challan_status = 'paid'
                    student.challan_status = 'paid'
                    

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    fee_head_id = fields.Many2one('odoocms.fee.head','Fee Head')
    fee_category_id = fields.Many2one('odoocms.fee.category','Fee Category',related='fee_head_id.category_id',store=True)
    
    
class OdooCMSFeePayment(models.Model):
    _name = 'odoocms.fee.payment'
    _description = 'Fee Payment'
    
    date = fields.Date('Date',required=True,readonly=True, states={'draft': [('readonly', False)]})
    description = fields.Char('Description',readonly=True, states={'draft': [('readonly', False)]})
    amount = fields.Float('Amount',required=True,readonly=True, states={'draft': [('readonly', False)]})
    doc_no = fields.Text('DOC No',readonly=True, states={'draft': [('readonly', False)]})
    student_code = fields.Text('Student Code',readonly=True, states={'draft': [('readonly', False)]})
    receipt_number = fields.Text('Receipt No',required=True,readonly=True, states={'draft': [('readonly', False)]})
    journal_id = fields.Many2one('account.journal','Journal',required=True,readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft','Draft'),('done','Done'),('error','Error')],'Status',default='draft',readonly=True, states={'draft': [('readonly', False)]})

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Student Fee Payments'),
            'template': '/odoocms_fee/static/xls/fee_collection.xlsx'
        }]
    
                    
class AccountInvoiceRefund(models.TransientModel):
    _inherit = "account.invoice.refund"

    @api.multi
    def compute_refund(self, mode='refund'):
        inv_obj = self.env['account.invoice']
        inv_tax_obj = self.env['account.invoice.tax']
        inv_line_obj = self.env['account.invoice.line']
        context = dict(self._context or {})
        xml_id = False
    
        for form in self:
            created_inv = []
            date = False
            description = False
            for inv in inv_obj.browse(context.get('active_ids')):
                if inv.state in ['draft', 'cancel']:
                    raise UserError(_('Cannot create credit note for the draft/cancelled invoice.'))
                if inv.reconciled and mode in ('cancel', 'modify'):
                    raise UserError(_(
                        'Cannot create a credit note for the invoice which is already reconciled, invoice should be unreconciled first, then only you can add credit note for this invoice.'))
            
                date = form.date or False
                description = form.description or inv.name
                refund = inv.refund(form.date_invoice, date, description, inv.journal_id.id)
            
                created_inv.append(refund.id)
                if mode in ('cancel', 'modify'):
                    movelines = inv.move_id.line_ids
                    to_reconcile_ids = {}
                    to_reconcile_lines = self.env['account.move.line']
                    for line in movelines:
                        if line.account_id.id == inv.account_id.id:
                            to_reconcile_lines += line
                            to_reconcile_ids.setdefault(line.account_id.id, []).append(line.id)
                        if line.reconciled:
                            line.remove_move_reconcile()
                    refund.action_invoice_open()
                    for tmpline in refund.move_id.line_ids:
                        if tmpline.account_id.id == inv.account_id.id:
                            to_reconcile_lines += tmpline
                    to_reconcile_lines.filtered(lambda l: l.reconciled == False).reconcile()
                    if mode == 'modify':
                        invoice = inv.read(inv_obj._get_refund_modify_read_fields())
                        invoice = invoice[0]
                        del invoice['id']
                        invoice_lines = inv_line_obj.browse(invoice['invoice_line_ids'])
                        invoice_lines = inv_obj.with_context(mode='modify')._refund_cleanup_lines(invoice_lines)
                        tax_lines = inv_tax_obj.browse(invoice['tax_line_ids'])
                        tax_lines = inv_obj._refund_cleanup_lines(tax_lines)
                        invoice.update({
                            'type': inv.type,
                            'date_invoice': form.date_invoice,
                            'state': 'draft',
                            'number': False,
                            'invoice_line_ids': invoice_lines,
                            'tax_line_ids': tax_lines,
                            'date': date,
                            'origin': inv.origin,
                            'fiscal_position_id': inv.fiscal_position_id.id,
                        })
                        for field in inv_obj._get_refund_common_fields():
                            if inv_obj._fields[field].type == 'many2one':
                                invoice[field] = invoice[field] and invoice[field][0]
                            else:
                                invoice[field] = invoice[field] or False
                        inv_refund = inv_obj.create(invoice)
                        body = _(
                            'Correction of <a href=# data-oe-model=account.invoice data-oe-id=%d>%s</a><br>Reason: %s') % (
                               inv.id, inv.number, description)
                        inv_refund.message_post(body=body)
                        if inv_refund.payment_term_id.id:
                            inv_refund._onchange_payment_term_date_invoice()
                        created_inv.append(inv_refund.id)
                xml_id = inv.type == 'out_invoice' and inv.is_cms and 'odoocms_fee.action_odoocms_receipt_refund' or \
                         inv.type == 'out_invoice' and 'account.action_invoice_out_refund' or \
                         inv.type == 'out_refund' and inv.is_cms and 'odoocms_fee.action_odoocms_receipt' or \
                         inv.type == 'out_refund' and 'account.action_invoice_tree1' or \
                         inv.type == 'in_invoice' and 'account.action_invoice_in_refund' or \
                         inv.type == 'in_refund' and 'account.action_invoice_tree2'

        if xml_id:
            #result = self.env.ref('account.%s' % (xml_id)).read()[0]
            result = self.env.ref('%s' % (xml_id)).read()[0]
            if mode == 'modify':
                # When refund method is `modify` then it will directly open the new draft bill/invoice in form view
                if inv_refund.type == 'in_invoice':
                    view_ref = self.env.ref('account.invoice_supplier_form')
                else:
                    if inv_refund.is_cms:
                        view_ref = self.env.ref('odoocms_fee.odoocms_receipt_form')
                    else:
                        view_ref = self.env.ref('account.invoice_form')
                result['views'] = [(view_ref.id, 'form')]
                result['res_id'] = inv_refund.id
            else:
                invoice_domain = safe_eval(result['domain'])
                invoice_domain.append(('id', 'in', created_inv))
                result['domain'] = invoice_domain
            return result
        return True

                    

