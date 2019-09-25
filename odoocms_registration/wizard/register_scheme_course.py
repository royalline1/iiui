import pdb
import time
import datetime
from openerp import api, fields, models,_
from dateutil.relativedelta import relativedelta


class OdooCMSRegisterSchemeCourse(models.TransientModel):
	_name ='odoocms.register.scheme.course'
	_description = 'Register Scheme Course'
				
	@api.model	
	def _get_students(self):
		if self.env.context.get('active_model', False) == 'odoocms.student' and self.env.context.get('active_ids', False):
			return self.env.context['active_ids']
			
	student_ids = fields.Many2many('odoocms.student', string='Students',
		help="""Only selected students will be Processed.""",default=_get_students)
	
	academic_semester_id = fields.Many2one('odoocms.academic.semester','Academic Term')
	
	@api.multi
	def register_scheme(self):
		registration = self.env['odoocms.student.subject']
		for student in self.student_ids:
			reg = student.register_courses(self.academic_semester_id)
			if reg:
				registration += reg
		
		if registration:
			reg_list = registration.mapped('id')
			return {
				'domain': [('id', 'in', reg_list)],
				'name': _('Student Registration'),
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'odoocms.student.subject',
				'view_id': False,
				# 'context': {'default_class_id': self.id},
				'type': 'ir.actions.act_window'
			}
		else:
			return {'type': 'ir.actions.act_window_close'}



