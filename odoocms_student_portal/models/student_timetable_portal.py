import base64
from collections import OrderedDict

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.tools import image_resize_image
from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
from odoo.addons.web.controllers.main import Binary
import json
import pdb


class CustomerPortal(CustomerPortal):
	def _prepare_portal_layout_values(self):
		values = super(CustomerPortal, self)._prepare_portal_layout_values()
		partner = request.env.user.partner_id
		Student = request.env['odoocms.student']
		
		student_count = Student.search_count([('partner_id','=', partner.id)])
		values.update({
			'student_count': student_count,
		})
		return values

	# **************************Custom method for getting timetable of one day*************************
	def get_timetable(self, day_schedule_ids):
		empty_line = {
			'period': "",
			'course': "",
			'faculty': "",
			'time_from': "",
			'time_to': ",",
			'col_span': 1,
		}
		pre_line_ends = 0  # reference of previous time slot
		day_timetable = []
		for rec in day_schedule_ids:
			line = {
				'period': rec.period_id.name,
				'course': rec.subject_id.study_scheme_line_id.subject_id.name,
				'faculty': rec.subject_id.faculty_staff_id.name,
				'time_from': rec.time_from,
				'time_to': rec.time_to,
			}

			# this is to get col span
			time_line = [8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0]
			line_from = 0;
			line_to = 0;
			span = 0
			for i in range(0, len(time_line)):
				if (time_line[i]) == rec.time_from:
					line_from = i
				elif (time_line[i]) == rec.time_to:
					line_to = i

			# append black list where time slot doesn't exists
			new_start_from = pre_line_ends
			pre_line_ends = line_to
			for j in range(new_start_from, line_from):
				day_timetable.append(empty_line)

			span = line_to - line_from
			line['col_span'] = span
			day_timetable.append(line)
		return day_timetable

	# **************************END Custom method for getting timetable of one day*************************

	@http.route(['/my/timetable'], type='http', auth="user", website=True)
	def portal_student_timetable(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
		# values = self._prepare_portal_layout_values()
		partner = request.env.user.partner_id
		
		student = request.env['odoocms.student'].sudo().search([('partner_id','=',partner.id)])
		days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday','Saturday', 'Sunday']
		time_slots = ['08:00-09:00', '09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-01:00', '01:00-02:00', '02:00-03:00', '03:00-04:00', '04:00-05:00']
		rec = {
			"monday":[],
			'tuesday':[],
			'wed':[],
			'thr':[],
			'fri':[],
			'sat':[],
			'sun':[]
		}

		if student:
			timetable = request.env['odoocms.timetable'].sudo().search(
				[('program_id', '=', student.program_id.id), ('batch_id', '=', student.batch_id.id),('academic_semester_id', '=', student.academic_semester_id.id), ('section_id', '=', student.section_id.id)])
			if timetable:
				monday_schedule_ids = timetable[0].timetable_mon.sorted(key=lambda r: r.time_from)
				tuesday_schedule_ids = timetable[0].timetable_tue.sorted(key=lambda r: r.time_from)
				wednesday_schedule_ids = timetable[0].timetable_wed.sorted(key=lambda r: r.time_from)
				thursday_schedule_ids = timetable[0].timetable_thu.sorted(key=lambda r: r.time_from)
				friday_schedule_ids = timetable[0].timetable_fri.sorted(key=lambda r: r.time_from)
				saturday_schedule_ids = timetable[0].timetable_sat.sorted(key=lambda r: r.time_from)
				sun_schedule_ids = timetable[0].timetable_sun.sorted(key=lambda r: r.time_from)
				rec = {
					"monday": self.get_timetable(monday_schedule_ids),
					'tuesday': self.get_timetable(tuesday_schedule_ids),
					'wed': self.get_timetable(wednesday_schedule_ids),
					'thr': self.get_timetable(thursday_schedule_ids),
					'fri': self.get_timetable(friday_schedule_ids),
					'sat': self.get_timetable(saturday_schedule_ids),
					'sun': self.get_timetable(sun_schedule_ids),
				}
		values = {
			'student': student,
			'days': days or False,
			'time_slots': time_slots or False,
			'default_url': '/my/course',
			'timetable':rec or False,
		}
		return request.render("odoocms_student_portal.portal_student_timetable", values)
	