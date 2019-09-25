
from odoo import fields, models, api
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import pdb


class OdooCMSCloseRegisterWizard(models.TransientModel):
    _name = 'odoocms.close.register.wizard'
    _description = 'Close Register Wizard'

    @api.model
    def _get_register(self):
        if self._context.get('active_model', False) == 'odoocms.admission.register' and self._context.get('active_id', False):
            return self.env['odoocms.admission.register'].browse(self._context.get('active_id', False))
        
    register_id = fields.Many2one('odoocms.admission.register', string='Register',default=_get_register, required=True)
    merit_register_id = fields.Many2one('odoocms.merit.register','Merit Register',related='register_id.merit_register_id')
    
    total_seats = fields.Integer('Total Seats',compute='_get_list')
    locked_seats = fields.Integer('Locked Seats',compute='_get_list')
    comment = fields.Char()
    remarks = fields.Text('Remarks',default='Please bring your Documents along with Fee')
    
    section_detail = fields.Html("Sections Detail")

    @api.depends('register_id')
    def _get_list(self):
        if self.register_id:
            if self.register_id.merit_register_id:
                if any([app.state == 'draft' for app in self.register_id.merit_register_id.merit_application_ids]):
                    self.comment = "Please Process %s first before Closing Register." % (self.register_id.merit_register_id.merit_list_id.name,)
                    
            allocation_id = self.env['odoocms.admission.allocation'].search([
                ('academic_session_id','=',self.register_id.academic_session_id.id),('career_id','=',self.register_id.career_id.id)
            ])
            self.total_seats = sum(program.seats for program in allocation_id.seat_ids)
            self.locked_seats  = self.register_id.application_ids.search_count([('locked','=',True)])
           
            # table - bordered
            section_detail = """
                <table class="table"><tbody>
                    <tr>
                        <th>Batch Name</th>
                        <th>Batch Code</th>
                        <th>Sections</th>
                        <th>Classes/Subjects</th>
                    </tr>
            """
            for batch in self.register_id.academic_session_id.batch_ids:
                section_detail += """
                    <tr>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    </tr>
                """ % (batch.name, batch.code,len(batch.section_ids),len(batch.section_ids.mapped('class_ids')))
            section_detail += """</tbody></table>"""
            self.section_detail = section_detail
            
    def close_register(self):
        for app in self.merit_register_id.merit_application_ids.filtered(lambda l: l.state == 'done'):
            applicant = app.application_id
            student = applicant.create_student()
            batch = self.register_id.academic_session_id.batch_ids.filtered(lambda l: l.program_id.id == app.program_id.id)
            if not batch:
                raise UserError('Batch not defined for Program: %s' % (app.program_id.name,))
            if not batch.section_ids:
                raise UserError('Sections not defined for Batch: %s' % (batch.name,))

            sno = (app.program_merit_number-1) % len(batch.section_ids)
            section = batch.section_ids[sno]
            
            student.write({
                'batch_id': batch.id,
                'section_id': section.id,
            })
            
            student.register_courses(self.register_id.academic_semester_id)
            if not student.user_id:
                student.create_student_user()
            self.register_id.state = 'done'