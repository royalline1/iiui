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


	@http.route(['/my/course'], type='http', auth="user", website=True)
	def portal_student_course(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
		# values = self._prepare_portal_layout_values()
		partner = request.env.user.partner_id
		
		student_search= request.env['odoocms.student']
		domain_student = [
			('partner_id','=',partner.id)
		]
		student = student_search.sudo().search(domain_student)
		# archive_groups = self._get_archive_groups('odoocms.subject.registration')
		
		# student_course= student.current_semester_ids[0].student_subject_ids

		values = {
			# 'student_course': student_course,
			'student': student,
			# 'page_name': 'order',
			# 'pager': pager,
			# 'archive_groups': archive_groups,
			'default_url': '/my/course',
		}
		return request.render("odoocms_student_portal.portal_student_course", values)
	