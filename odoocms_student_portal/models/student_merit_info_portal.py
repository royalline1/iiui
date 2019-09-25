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
		current_user = http.request.env.user
		student = http.request.env['odoocms.application'].sudo().search([('email', '=', current_user.email)])
		if student:
			values.update({
				'student_application': student,
			})
		return values


	@http.route(['/my/merit'], type='http', auth="user", website=True)
	def portal_applicant_merit_info(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):

		current_user = http.request.env.user

		application = http.request.env['odoocms.application'].sudo().search([('email', '=', current_user.email)])
		admission_reg = http.request.env['odoocms.admission.register'].sudo().search([('id','=',application.register_id.id)])

		applicant_merit = http.request.env['odoocms.application.merit'].sudo().search([
			('application_id', '=', application.id),
			('merit_register_id','=',admission_reg.merit_register_id.id)
		])

		locked_application = http.request.env['odoocms.application.merit'].sudo().search([
			('application_id', '=', application.id),
			('locked', '=', True)
		])

		cancelled_application = http.request.env['odoocms.application.merit'].sudo().search([
			('application_id', '=', application.id),
			('state', 'in', ('cancel','reject','absent'))
		])

		values = {
			'applicant_merit': applicant_merit,
			'applicant':application,
			'default_url': '/my/merit',
			'locked_application':locked_application,
			'cancelled_application':cancelled_application,
		}
		return request.render("odoocms_student_portal.portal_applicant_merit", values)
	