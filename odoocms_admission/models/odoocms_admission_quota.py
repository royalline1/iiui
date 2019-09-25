
from odoo import fields, models, api


class OdooCMSAdmissionAllocation(models.Model):
    _name ='odoocms.admission.allocation'
    _description ='CMS Admission allocation'
    
    name = fields.Char(string='Name',required=True)
    code = fields.Char(string='Code')
    career_id = fields.Many2one('odoocms.career','Career',required=True)
    academic_session_id = fields.Many2one('odoocms.academic.session','Academic Session',required=True)
    seat_ids = fields.One2many('odoocms.admission.allocation.line','allocation_id',string='Allocation Seats')


class OdooCMSAdmissionAllocationLine(models.Model):
    _name ='odoocms.admission.allocation.line'
    _description='CMS Admission Allocation Line'
    
    program_id = fields.Many2one('odoocms.program',string='Program',required=True)
    seats = fields.Integer(string='No Of Seats', required=True)
    allocation_id = fields.Many2one('odoocms.admission.allocation',string='Allocation',required=True)
    category = fields.Selection([
        ('open_merit', 'Open Merit'),('self_finance','Self Finance'),
        ('self_sudtained','Self Sustained'),('quota','Quota')
    ])
    quota_id = fields.Many2one('odoocms.admission.quota','Quota')

    _sql_constraints = [
        ('seats_allocation_unique', 'unique(allocation_id,program_id,category)', "Duplicate Entry of Seats Allocation!"),
    ]


class OdooCMSAdmissionQuota(models.Model):
    _name = 'odoocms.admission.quota'
    _description = 'CMS Admission Quota'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')