
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from dateutil.relativedelta import relativedelta
from odoo.tools.safe_eval import safe_eval
import pdb


class OdooCMSStudent(models.Model):
    _inherit = 'odoocms.student'

    feemerit = fields.Selection([
        ('regular','Regular'),('self','Self Finance'),('rationalized','Rationalized')
    ],'Fee Merit', default='regular')
    challan_status = fields.Selection([
            ('no','Not Required Yet'),('tobe','Needs to be Generated'),
            ('generate','Generated'),('paid','Paid')
        ],'Challan Status',default='no',track_visibility='onchange')
    
    hostel_facility = fields.Boolean('Hostel Facility')
    hostel_cubical = fields.Boolean('Cubical')
    fee_structure_ids = fields.One2many('odoocms.fee.structure.student','student_id',string='Fee Lines')
    receipt_ids = fields.One2many('account.invoice','student_id','Fee Receipts')
    
    def generate_challan(self, semester, receipts, date_due, override_line=False, view=False): #, override_line=False
        fee_structure = self.env['odoocms.fee.structure'].search([('academic_session_id','=',self.academic_session_id.id)])
        lines = []
        invoices = self.env['account.invoice']
        payment_types = ['persemester','onetime']
        
        semester_number = self.env['odoocms.semester.scheme'].search([
            ('academic_session_id','=',self.academic_session_id.id),
            ('academic_semester_id','=',semester.id)
        ]).semester_id.number
       
        if semester_number % 2 == 1 or not semester:
            payment_types.append('peryear')

        fee_head_ids = receipts.mapped('fee_head_ids').ids
        fee_lines = fee_structure.line_ids.filtered(
            lambda l: l.fee_head_id.id in fee_head_ids
                and l.payment_type in payment_types
                and (not l.program_ids or self.program_id.id in l.program_ids.ids)
                and (not l.semester_ids or semester_number in l.semester_ids.ids)
        )
       
        # and l.applied_to == 'all'
        
        #if self.feemerit == 'self':
        #    fee_lines += fee_structure.line_ids.filtered(lambda l: l.applied_to == 'self')
        #elif self.feemerit == 'rationalized':
        #    fee_lines += fee_structure.line_ids.filtered(lambda l: l.applied_to == 'rationalized')
        
        analytic_tags = self.env['account.analytic.tag']
        analytic_tags += self.program_id.department_id.campus_id.analytic_tag_id
        analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in analytic_tags]

        if not fee_structure.journal_id.sequence_id:
            raise UserError(_('Please define sequence on the journal related to this invoice.'))

        date_invoice = fields.Date.context_today(self)
        #date_due = date_invoice + relativedelta(days=15)
        
        sequence = fee_structure.journal_id.sequence_id
        new_name = sequence.with_context(ir_sequence_date=date_invoice).next_by_id()

        for line in fee_lines:
            name = line.fee_head_id.product_id.name
            #if not line.domain or self.env['odoocms.student'].search(safe_eval(line.domain)).filtered(lambda l: l.id == self.id):
            if not line.domain or self.env['odoocms.student'].search(safe_eval(line.domain)+[('id','=',self.id)]):
                override_fee_line = override_line.filtered(lambda l: l.fee_head_id.id == line.fee_head_id.id)
                student_fee_line = self.fee_structure_ids.filtered(lambda l: l.fee_head_id.id == line.fee_head_id.id)
                fee_line = {
                    # override_fee_line and override_fee_line.fee_amount \
                    #                         or
                    'price_unit': override_fee_line and override_fee_line.fee_amount \
                        or (student_fee_line and student_fee_line.fee_amount or line.fee_amount),
                    'quantity': 1.00,
                    'product_id': line.fee_head_id.product_id.id,
                    'name': name,
                    'account_id': line.fee_head_id.property_account_income_id.id,
                    'account_analytic_id': line.fee_head_id.account_analytic_id,
                    'analytic_tag_ids': analytic_tag_ids,
                    'fee_head_id': line.fee_head_id.id,
                }
                lines.append([0,0,fee_line])
 
        data = {
            'student_id': self.id,
            'partner_id': self.partner_id.id,
            'fee_structure_id': fee_structure.id,
            'program_id': self.program_id.id,
            'academic_semester_id': semester and semester.id or False,
            'is_fee': True,
            'is_cms': True,
            'student_name': self.partner_id.name,
            'invoice_line_ids': lines,
            'journal_id': fee_structure.journal_id.id,
            'number': new_name,
            'date_invoice': date_invoice,
            'date_due': date_due,
            'state': 'sent',
        }
        invoices += self.env['account.invoice'].create(data)
        
        if view:
            invoice_list = invoices.mapped('id')
            form_view = self.env.ref('odoocms_fee.odoocms_receipt_form')
            tree_view = self.env.ref('odoocms_fee.odoocms_receipt_tree')
            return {
                'domain': [('id', 'in', invoice_list)],
                'name': _('Invoicess'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.invoice',
                'view_id': False,
                'views': [(form_view and form_view.id or False, 'form'),
                          (tree_view and tree_view.id or False, 'tree')],
                #'context': {'default_class_id': self.id},
                'type': 'ir.actions.act_window'
            }
        else:
            return invoices


class OdooCMSApplication(models.Model):
    _inherit = 'odoocms.application'
    
    feemerit = fields.Selection([
        ('regular', 'Regular'), ('self', 'Self Finance'), ('rationalized', 'Rationalized')
    ], 'Fee Merit', default='regular')
    challan_status = fields.Selection([
        ('no', 'Not Required Yet'), ('tobe', 'Needs to be Generated'),
        ('generate', 'Generated'), ('paid', 'Paid')
    ], 'Challan Status', default='no', track_visibility='onchange')
    
    hostel_facility = fields.Boolean('Hostel Facility')
    hostel_cubical = fields.Boolean('Cubical')
    
    def generate_challan(self, view=False):
        fee_structure = self.env['odoocms.fee.structure'].search(
            [('academic_session_id', '=', self.academic_session_id.id)])
        lines = []
        invoices = self.env['account.invoice']
        payment_types = ['admissiontime','persemester']
        #current_semester_number = self.semester_id.number
        next_semester_number = 1   #current_semester_number + 1
        
        if next_semester_number % 2 == 1:
            payment_types.append('peryear')
        
        fee_lines = fee_structure.line_ids.filtered(
            lambda l: l.payment_type in payment_types
                      and (not l.program_ids or self.program_id.id in l.program_ids.ids)
                      and (not l.semester_ids or next_semester_number in l.semester_ids.ids)
        )
       

        analytic_tags = self.env['account.analytic.tag']
        analytic_tags += self.program_id.department_id.campus_id.analytic_tag_id
        analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in analytic_tags]

        if not fee_structure.journal_id.sequence_id:
            raise UserError(_('Please define sequence on the journal related to this invoice.'))

        date_invoice = fields.Date.context_today(self)
        date_due = date_invoice + relativedelta(days=15)

        sequence = fee_structure.journal_id.sequence_id
        new_name = sequence.with_context(ir_sequence_date=date_invoice).next_by_id()
        
        for line in fee_lines:
            # name = line.fee_type.product_id.description_sale
            # if not name:
            #    name = line.fee_type.product_id.name
            name = line.fee_head_id.product_id.name
            
            #if not line.applied_if or eval('self.' + line.applied_if.name):
            #if not line.domain or self.env['odoocms.application'].search([(line.domain + [('id', '=', self.id)])]):
            fee_line = {
                'price_unit': line.fee_amount,
                'quantity': 1.00,
                'product_id': line.fee_head_id.product_id.id,
                'name': name,
                'account_id': line.fee_head_id.property_account_income_id.id,
                #'account_analytic_id': line.fee_head_id.account_analytic_id,
                'analytic_tag_ids': line.fee_head_id.analytic_tag_ids.ids,
            }
            lines.append([0, 0, fee_line])
        
        data = {
            'applicant_id': self.id,
            'partner_id': 1,  #self.partner_id.id,
            'fee_structure_id': fee_structure.id,
            'program_id': self.program_id.id,
            'is_fee': True,
            'is_cms': True,
            'student_name': self.name + '-' + self.last_name,
            'invoice_line_ids': lines,
            'journal_id': fee_structure.journal_id.id,
            'number': new_name,
            'date_invoice': date_invoice,
            'date_due': date_due,
            'state': 'sent',
        }
        invoices += self.env['account.invoice'].create(data)
        
        if view:
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
                'views': [(form_view and form_view.id or False, 'form'),
                          (tree_view and tree_view.id or False, 'tree')],
                # 'context': {'default_class_id': self.id},
                'type': 'ir.actions.act_window'
            }
        else:
            return invoices
