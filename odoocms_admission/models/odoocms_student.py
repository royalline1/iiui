

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

class OdooCMSStudent(models.Model):
    _inherit = 'odoocms.student'
  
    application_id = fields.Many2one('odoocms.application', string="Application No")
    quota_id = fields.Many2one('odoocms.admission.quota','Student Quota', track_visibility='onchange')
  
    @api.multi
    def student_documents(self):
        self.ensure_one()
        if self.application_id.id:
            documents = self.env['odoocms.documents'].search([('application_ref', '=', self.application_id.id)])
            documents_list = documents.mapped('id')
            return {
                'domain': [('id', 'in', documents_list)],
                'name': _('Documents'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'odoocms.documents',
                'view_id': False,
                'context': {'default_application_ref': self.application_id.id},
                'type': 'ir.actions.act_window'
            }
