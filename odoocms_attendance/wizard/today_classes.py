import pdb
import time
import datetime
from openerp import api, fields, models,_
from dateutil.relativedelta import relativedelta


class OdooCMSTimetableTodayClass(models.TransientModel):
	_name ='odoocms.timetable.today.class'
	_description = 'Generate Todays Classes'
	
	date_class = fields.Date('Class Date',default=lambda self: fields.Date.today())
	
	@api.multi
	def generate_classes(self):
		att_classes = self.env['odoocms.class.attendance']
		schedules = self.env['odoocms.timetable.schedule'].search([('week_day','=',self.date_class.weekday())])
		for schedule in schedules:
			data = {
				'class_id': schedule.subject_id.id,
				'faculty_id': schedule.faculty_id.id,
				'date': self.date_class,
			}
			att_class = self.env['odoocms.class.attendance'].create(data)
			att_class.create_attendance_line(ignore=True)
			att_classes += att_class
		
		if att_classes:
			class_list = att_classes.mapped('id')
			return {
				'domain': [('id', 'in', class_list)],
				'name': _('Scheduled Classes'),
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'odoocms.class.attendance',
				'view_id': False,
				# 'context': {'default_class_id': self.id},
				'type': 'ir.actions.act_window'
			}
		else:
			return {'type': 'ir.actions.act_window_close'}



