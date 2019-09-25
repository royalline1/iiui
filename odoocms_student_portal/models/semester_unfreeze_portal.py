import base64
from collections import OrderedDict
import pdb


from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.tools import image_resize_image
from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
from odoo.addons.web.controllers.main import Binary
import json

class CustomerPortal(CustomerPortal):
	def _prepare_portal_layout_values(self):
		values = super(CustomerPortal, self)._prepare_portal_layout_values()
		partner = request.env.user.partner_id
		student_search = request.env['odoocms.student']
		student = student_search.search_count([('partner_id','=', partner.id)])
		values.update({
        	'student':student,
        	})
		return values


	@http.route(['/my/semester/unfreeze/request'], type='http', auth="user", website=True)
	def portal_student_semesterunfreeze(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
		values = self._prepare_portal_layout_values()
		partner = request.env.user.partner_id
		student = http.request.env['odoocms.student'].sudo().search([ ('partner_id','=',partner.id)])
		student_search_freeze = http.request.env['odoocms.student.semester.freeze'].sudo().search([ ('student_id','=',student.id)])

		return request.render("odoocms_student_portal.portal_student_semesterunfreeze",{'student': student,
			'student_search_freeze':student_search_freeze
			})



	@http.route(['/my/requests/semesterunfreeze/save'], csrf=False, type='http', auth="user", website=True)
	def portal_my_student_semesterunfreeze_save(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
		partner = request.env.user.partner_id

		reason=kw.get('reason')
		student = http.request.env['odoocms.student'].sudo().search([ ('partner_id','=',partner.id)])
		save_request = http.request.env['odoocms.student.semester.unfreeze'].sudo().create({
			'student_id':student.id })
		return request.render("odoocms_student_portal.portal_thankyou")
