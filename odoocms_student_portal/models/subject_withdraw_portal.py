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


	@http.route(['/my/subject/withdraw/request'], type='http', auth="user", website=True)
	def portal_student_subjectwithdraw(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
		values = self._prepare_portal_layout_values()
		partner = request.env.user.partner_id
		student = http.request.env['odoocms.student'].sudo().search([ ('partner_id','=',partner.id)])
		subject =request.env['odoocms.student.subject'].search([('student_id','=',student.id),('state','=','current')])
		# current_subject = request.env['odoocms.subject'].search([('id','=',subject.subject_id.id)])

		return request.render("odoocms_student_portal.portal_student_subjectwithdraw", {'student': student,
			'subject': subject,
			})



	@http.route(['/my/requests/subjectwithdraw/save'], csrf=False, type='http', auth="user", website=True)
	def portal_my_student_subjectwithdraw_save(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
		partner = request.env.user.partner_id

		reason=kw.get('reason')
		subject_id=kw.get('subject_id')
		student = http.request.env['odoocms.student'].sudo().search([ ('partner_id','=',partner.id)])
		save_request = http.request.env['odoocms.request.subject.withdraw'].sudo().create({
			'student_id':student.id,'subject_id':subject_id,'reason': reason })
		return request.render("odoocms_student_portal.portal_thankyou")
