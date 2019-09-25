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
	@http.route('/my/class/student', csrf=False, type='http', auth="user", method=['GET'], website=True)
	def get_my_students(self, **get):

		partner = request.env.user.partner_id
		faculty_staff = http.request.env['odoocms.faculty.staff'].sudo().search([('partner_id', '=', partner.id)])
		student_class = http.request.env['odoocms.class'].sudo().search([('faculty_staff_id', '=', faculty_staff.id)])
		values = {
			'faculty_staff': faculty_staff,
			'student_classes': student_class,

		}
		return http.request.render('odoocms_faculty_portal.portal_faculty_class_students', values)

	@http.route(['/my/class/student/profile/id/<int:id>'], type='http', auth="user", website=True)
	def student_profile(self, id=0, date_begin=None, date_end=None, sortby=None, **kw):

		if id != 0:
			domain = [
				('id', '=', id)
			]
			student = request.env['odoocms.student'].sudo().search(domain)
			# request.session['my_orders_history'] = orders.ids[:100]
			values = {
				'student': student,
				# 'page_name': 'order',
				# 'pager': pager,
			}
			return request.render("odoocms_faculty_portal.faculty_portal_student_profile", values)
		else:
			return "Nothing Found"


	
