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
from datetime import date

import json
import pdb


class CustomerPortal(CustomerPortal):
	@http.route('/my/classes', csrf=False, type='http', auth="user", method=['GET'], website=True)
	def get_my_classes(self, **get):
		partner = request.env.user.partner_id
		faculty_staff = http.request.env['odoocms.faculty.staff'].sudo().search([('partner_id', '=', partner.id)])
		student_class = http.request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id)])
		values = {
			'faculty_staff': faculty_staff,
			'student_classes': student_class,

		}
		return http.request.render('odoocms_faculty_portal.portal_faculty_attendance_classes', values)



	@http.route(['/my/class/id/<int:id>'], type='http', auth="user", website=True)
	def student_profile(self, id=0, date_begin=None, date_end=None, sortby=None, **kw):
		partner = request.env.user.partner_id
		faculty_staff = http.request.env['odoocms.faculty.staff'].sudo().search([('partner_id', '=', partner.id)])
		if id != 0:
			domain = [
				('id', '=', id),
				('faculty_staff_id','=', faculty_staff.id)
			]
			attendance_class = request.env['odoocms.class'].sudo().search(domain)
			today = date.today()
			values = {
				'attendance_class': attendance_class,
				'faculty_staff':faculty_staff,
				'attendance_day':today,
				# 'page_name': 'order',
				# 'pager': pager,
			}
			return request.render("odoocms_faculty_portal.portal_faculty_attendance_class", values)
		else:
			return "Nothing Found"


	# This is to save attendance
	@http.route('/my/class/attendance/save', csrf=False, type="http", methods=['POST', 'GET'], auth="public", website=True)
	def save_my_class_attendance(self, **kw):
		# The is to get teacher id
		partner = request.env.user.partner_id
		faculty_staff = http.request.env['odoocms.faculty.staff'].sudo().search([('partner_id', '=', partner.id)])

		# Get all data from AJAX
		class_id = int(kw.get('class_id'))
		today = date.today()

		record = {'status_is': "norecord"}
		class_attendance = http.request.env['odoocms.class.attendance'].sudo().search([('class_id', '=', class_id),('date', '=', today),('faculty_id', '=', faculty_staff.id)])
		if(not class_attendance):
			record = {'status_is': "attendance"}
			values = {
				'class_id': class_id,
				'faculty_id': faculty_staff.id,
				'date': today,
			}
			class_attendance = class_attendance.sudo().create(values)

		student_ids =  kw.get('student_ids')
		students_list = student_ids.split(',')

		students_list = [6,8]
		for i in students_list:
			values = {
				'class_id': class_id,
				'student_id': int(i),
				'present':True,
				'date':today,
				'attendance_id': class_attendance.id,
			}
			student_attendance_line = http.request.env['odoocms.class.attendance.line'].sudo().search([('class_id', '=', class_id),('date', '=', today),('student_id', '=',int(i) ),('attendance_id','=',class_attendance.id)])
			if student_attendance_line:
				student_attendance_line.sudo().update(values)
				record = {'status_is': "line update"}
			else:
				student = student_attendance_line.sudo().create(values)
				if student:
					record = {'status_is': "line create"}
				else:
					record = {'status_is': "line create error"}

		return json.dumps(record)

	
