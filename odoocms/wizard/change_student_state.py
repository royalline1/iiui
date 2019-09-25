import pdb
import time
import datetime
from openerp import api, fields, models,_
from dateutil.relativedelta import relativedelta


class OdooCMSChangeStudentState(models.TransientModel):
	_name ='odoocms.student.state.change'
	_description = 'Change Student State'
				
	@api.model	
	def _get_students(self):
		if self.env.context.get('active_model', False) == 'odoocms.student' and self.env.context.get('active_ids', False):
			return self.env.context['active_ids']
			
	student_ids = fields.Many2many('odoocms.student', string='Students',
		help="""Only selected students will be Processed.""",default=_get_students)
	state = fields.Selection(
		[('cancel', 'Cancel'), ('suspend', 'Suspend'),('elumni', 'Elumni'), ('enroll', 'Enroll'),], string='Status',
		default='suspend')
	rule_id = fields.Many2one('odoocms.student.change.state.rule', string = "Reason",)

	@api.multi
	def change_student_state(self):
		student_search = self.env['odoocms.student'].search([])
		for student in self.student_ids:
			if (student.state == 'done' and (self.state in ('suspend', 'cancel'))):
				student_search.sudo().update({'state': self.state})
			elif (student.state in ('suspend', 'cancel') and self.state == 'enroll'):
				student_search.sudo().update({'state': 'done'})
		return {'type': 'ir.actions.act_window_close'}



