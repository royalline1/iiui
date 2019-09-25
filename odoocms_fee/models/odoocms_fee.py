
from odoo import models, fields, api, _
import pdb


class OdooCMSReceiptType(models.Model):
    _name = 'odoocms.receipt.type'
    _description = 'Fee Receipt Type'
    
    name = fields.Char('Name')
    code = fields.Char('Code')
    fee_head_ids = fields.Many2many('odoocms.fee.head','receipt_type_fee_head_rel','receipt_type_id','fee_head_id','Fee Heads')
    semester_required = fields.Boolean('Semester Required?', default=False)
    override_amount = fields.Boolean('Override Amount?', default=False)
    sequence = fields.Integer()
    
    
class OdooCMSFeeCategory(models.Model):
    _name = 'odoocms.fee.category'
    _parent_name = 'parent_id'
    _parent_store = True
    _description='Fee Category'

    name = fields.Char('Name', index=True, required=True, translate=True,
        help='Create a fee category suitable for your institution.'
            ' Like Institutuinal, Hostel, Transportation, Arts and Sports, etc')
    code = fields.Char('Code')
    sequence = fields.Integer()
    parent_id = fields.Many2one('odoocms.fee.category','Parent Cateory', index=True, ondelete='cascade')
    parent_path = fields.Char(index=True)
    head_ids = fields.One2many('odoocms.fee.head','category_id','Fee Heads')
    
    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.parent_id:
                name = record.parent_id.name + ' - ' + name
            res.append((record.id, name))
        return res


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    is_fee = fields.Boolean('Is Educational fee?')
    
    
class OdooCMSFeeHead(models.Model):
    _name = 'odoocms.fee.head'
    _description = 'Fee Head'
    _inherits = {'product.product': 'product_id'}
    
    payment_type = fields.Selection([
        ('admissiontime', 'Admission Time'),
        ('permonth', 'Per Month'),
        ('peryear', 'Per Year'),
        ('persemester', 'Per Semester'),
        ('onetime', 'One Time'),
    ], string='Payment Type', default='persemester',
        help='Payment type describe how much a payment effective.'
             ' Like, bus fee per month is 2000, sports fee per year is 3000, etc')
    
    category_id = fields.Many2one('odoocms.fee.category', string='Category', required=True,
                                  default=lambda self: self.env['odoocms.fee.category'].search([], limit=1))
    product_id = fields.Many2one('product.product', 'Product', required=True, ondelete="cascade")
    refund = fields.Boolean('Refund-able?')
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    sequence = fields.Integer()
    
    @api.model
    def create(self, vals):
        vals.update({
            'is_fee': True,
        })
        res = super(OdooCMSFeeHead, self).create(vals)
        return res


class OdooCMSFeeStructure(models.Model):
    _name = 'odoocms.fee.structure'
    _description = 'Fee Structure'

    #@api.one
    #@api.depends('line_ids.fee_amount')
    #def compute_total(self):
    #    self.amount_total = sum(line.fee_amount for line in self.line_ids)

    company_currency_id = fields.Many2one('res.currency', compute='get_company_id', readonly=True, related_sudo=False)
    name = fields.Char('Name', required=True)
    comment = fields.Text('Additional Information')
    academic_session_id = fields.Many2one('odoocms.academic.session', string='Academic Session', required=True)
    career_id = fields.Many2one('odoocms.career', string="Career", required=True)
    journal_id = fields.Many2one('account.journal', string='Journal', required=True,
        help='Setting up of unique Journal for each Structure help to distinguish Account entries of each Structure ')
    #amount_total = fields.Float('Amount', currency_field='company_currency_id', required=True, compute='compute_total')
    
    line_ids = fields.One2many('odoocms.fee.structure.line', 'fee_structure_id', string='Fee Types', copy=True)
    sequence = fields.Integer()

    _sql_constraints = [
        ('session_career', 'unique(academic_session_id,career_id)', "Another Structure already exists with this Session and Career!"), ]
    

class OdooCMSFeeStructureLine(models.Model):
    _name = 'odoocms.fee.structure.line'
    _description = 'Fee Structure Line'
    
    category_id = fields.Many2one('odoocms.fee.category', string='Category', required=True)
    fee_head_id = fields.Many2one('odoocms.fee.head', string='Fee', required=True)
    fee_amount = fields.Float('Amount',  required=True)
    payment_type = fields.Selection([
        ('admissiontime', 'Admission Time'),
        ('permonth', 'Per Month'),
        ('peryear', 'Per Year'),
        ('persemester', 'Per Semester'),
        ('onetime', 'One Time'),
    ], string='Payment Type', related="fee_head_id.payment_type")
    fee_description = fields.Text('Description', related='fee_head_id.description_sale')
    fee_structure_id = fields.Many2one('odoocms.fee.structure', string='Fee Structure', ondelete='cascade', index=True)
    program_ids = fields.Many2many('odoocms.program','fee_line_program_rel','fee_line_id','program_id','Programs')
    semester_ids = fields.Many2many('odoocms.semester','fee_line_semester_rel','fee_line_id','semester_id','Semesters')
    domain = fields.Char('Domain Rule')
    sequence = fields.Integer()
    

class OdooCMSFeeStructureStudent(models.Model):
    _name = 'odoocms.fee.structure.student'
    _description = 'Fee Structure Student'
    
    category_id = fields.Many2one('odoocms.fee.category', string='Category', required=True)
    fee_head_id = fields.Many2one('odoocms.fee.head', string='Fee', required=True)
    fee_amount = fields.Float('Amount', required=True)
    payment_type = fields.Selection([
        ('admissiontime', 'Admission Time'),
        ('permonth', 'Per Month'),
        ('peryear', 'Per Year'),
        ('persemester', 'Per Semester'),
        ('onetime', 'One Time'),
    
    ], string='Payment Type', related="fee_head_id.payment_type")
    fee_description = fields.Text('Description', related='fee_head_id.description_sale')
    note = fields.Char('Note')
    student_id = fields.Many2one('odoocms.student','Student')

    _sql_constraints = [
        ('feehead_student', 'unique(fee_head_id,student_id)', "Another Fee Line already exists with this Head and Student!"), ]

    @api.onchange('student_id','fee_head_id')
    def onchange_receipt_type(self):
        if self.student_id and self.fee_head_id:
            fee_structure = self.env['odoocms.fee.structure'].search([('academic_session_id','=',self.student_id.academic_session_id.id)])
            fee_line = fee_structure.line_ids.filtered(lambda l: l.fee_head_id.id == self.fee_head_id.id)
            if fee_line:
                self.fee_amount = fee_line.fee_amount
    

class OdooCmsCampus(models.Model):
    _inherit = 'odoocms.campus'
    
    analytic_tag_id = fields.Many2one('account.analytic.tag','Analytic Tag')

    
class InheritJournal(models.Model):
    _inherit = 'account.journal'

    is_fee = fields.Boolean('Is Educational fee?', default=False)

    @api.multi
    def action_create_new_fee(self):
        view = self.env.ref('odoocms_fee.receipt_form')
        ctx = self._context.copy()
        ctx.update({'journal_id': self.id, 'default_journal_id': self.id})
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view.id, 'form')],
            'res_model': 'account.invoice',
            'view_id': view.id,
            'context': ctx,
            'type': 'ir.actions.act_window',
        }

#access_odoocms_fee_payed_lines_account_user,odoocms.fee.payed.lines.account.user,odoocms_fee.model_payed_lines,account.group_account_user,1,1,1,0
#access_odoocms_fee_payed_lines_account_manager,odoocms.fee.payed.line.account.manager,odoocms_fee.model_payed_lines,account.group_account_manager,1,1,1,1
