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
	

	@http.route(['/my/profile', '/my/profile/page/<int:page>'], type='http', auth="user", website=True)
	def portal_student_profile(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
		# values = self._prepare_portal_layout_values()
		partner = request.env.user.partner_id
		Student= request.env['odoocms.student']
		domain = [
			('partner_id','=',partner.id)
		]
		archive_groups = self._get_archive_groups('odoocms.student')
		student = Student.search(domain)
		# request.session['my_orders_history'] = orders.ids[:100]
		values = {
			'student': student.sudo(),
			# 'page_name': 'order',
			# 'pager': pager,
			'archive_groups': archive_groups,
			'default_url': '/my/profile',
		}
		return request.render("odoocms_student_portal.portal_student_profile", values)
	
	@http.route(['/my/request/forms'], type='http', auth="user", website=True)
	def portal_student_profilechange(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
		values = self._prepare_portal_layout_values()
		partner = request.env.user.partner_id
		student_search = request.env['odoocms.student']
		domain = [
			('partner_id', '=', partner.id)
		]
		archive_groups = self._get_archive_groups('odoocms.student')
		student = student_search.search(domain)

		values.update({
			'student': student.sudo(),
			# 'page_name': 'order',
			# 'pager': pager,
			'archive_groups': archive_groups,
			'default_url': '/my/student',
		})
		return request.render("odoocms_student_portal.portal_student_profilechange")
	
	@http.route(['/my/request/forms/open'], type='http', auth="user", website=True)
	def portal_student_profilechange_save(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
		return request.render("odoocms_student_portal.portal_student_profilechange_save")

	@http.route(['/my/request/course/enrollment'], type='http', auth="user", website=True)
	def portal_student_course_reenrollment(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
		student = request.env['odoocms.student'].sudo().search([('partner_id', '=', request.env.user.partner_id.id)])
		config_academic_semester = http.request.env['ir.config_parameter'].sudo().get_param('odoocms.current_academic_semester')
		if config_academic_semester:
			new_semester = request.env['odoocms.academic.semester'].sudo().browse(int(config_academic_semester))
		else:
			new_semester = request.env['odoocms.academic.semester'].sudo().search([])[0]

		classes = student.get_possible_classes(new_semester)[0]
		
		# credit hours allowed
		batch = request.env['odoocms.batch'].sudo().search([('id', '=', student.batch_id.id)])
		if student.reregister_credit_hours:
			credit_hours = student.reregister_credit_hours
		elif batch.reregister_credit_hours:
			credit_hours = batch.reregister_credit_hours
		else:
			credit_hours = http.request.env['ir.config_parameter'].sudo().get_param('odoocms.reregister_credit_hours')
		
		values = {
			'compulsory_subject_ids': classes['comp_class_ids'].sudo(),
			'elective_subject_ids': classes['elec_class_ids'].sudo(),
			'failed_subject_ids': classes['offered_f'].sudo(),
			'to_improve_subject_ids': classes['offered_r'].sudo(),
			'max_credit_hours': credit_hours,
		}
		return request.render("odoocms_student_portal.portal_student_course_enrollment",values)

	@http.route('/my/request/course/enrollment/save', csrf=False, type='http', auth="user", method=['GET'], website=True)
	def portal_student_course_reenrollment_save(self, **kw):
		compulsory_subject_ids = kw.get('com_subject_list')
		elective_subject_ids = kw.get('elected_subject_list')
		failed_subject_ids = kw.get('repeat_subject_list')
		to_improve_subject_ids = kw.get('improve_subject_list')
		subject_credit_hour = int(kw.get('subject_credit_hour'))

		student = request.env['odoocms.student'].sudo().search([('partner_id', '=', request.env.user.partner_id.id)])
		config_academic_semester = http.request.env['ir.config_parameter'].sudo().get_param('odoocms.current_academic_semester')
		if config_academic_semester:
			new_semester = request.env['odoocms.academic.semester'].sudo().browse(int(config_academic_semester))
		else:
			new_semester = request.env['odoocms.academic.semester'].sudo().search([])[0]
	
		values = {
			'student_id': student.id,
			'academic_semester_id': new_semester.id,
			'state': 'draft',
		}

		if len(compulsory_subject_ids) > 0:
			values['compulsory_subject_ids']= [(6, 0, list(map(int, compulsory_subject_ids.split(','))) )]
		if len(failed_subject_ids) > 0:
			values['failed_subject_ids']= [(6, 0, list(map(int, failed_subject_ids.split(','))) )]
		if len(elective_subject_ids) > 0:
			values['elective_subject_ids']= [(6, 0, list(map(int, elective_subject_ids.split(','))) )]
		if len(to_improve_subject_ids) > 0:
			values['to_improve_subject_ids']= [(6, 0, list(map(int, to_improve_subject_ids.split(','))) )]

		draf_reg = request.env['odoocms.subject.registration'].sudo().search([
			('student_id', '=', student.id),
			('state', '=', 'draft'),
			('academic_semester_id', '=', new_semester.id)
		])
		not_draf_reg = request.env['odoocms.subject.registration'].sudo().search([
			('student_id', '=', student.id),
			('state', '!=', 'draft'),
			('academic_semester_id', '=', new_semester.id)
		])

		Data = {"state": "error"}
		if draf_reg:
			new_request = draf_reg[0].update(values)
			Data = {"state": "submit"}
		elif not_draf_reg:
			Data = {"state": "nosubmit"}
		else:
			new_request = request.env['odoocms.subject.registration'].sudo().create(values)
			Data = {"state": "submit"}

		return json.dumps(Data)

	@http.route(['/my/request/forms/search'], csrf=False, type='http', auth="user", website=True)
	def portal_student_profilechange_search(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
		partner = request.env.user.partner_id
		current_user = http.request.env.user
		change_apply_for = kw.get('change_apply_for')
		try:
			student = http.request.env['odoocms.student'].sudo().search([('partner_id', '=', partner.id)])
			if (change_apply_for == 'name'):
				record = {'get_value': student.name}
			elif (change_apply_for == 'last_name'):
				record = {'get_value': student.last_name}
			elif (change_apply_for == 'cnic'):
				record = {'get_value': student.cnic}
			elif (change_apply_for == 'date_of_birth'):
				record = {'get_value': str(student.date_of_birth)}
			else:
				record = {'get_value': student.id}
		
		except:
			record = {'get_value': "error"}
		return json.dumps(record)
	
	@http.route(['/request/save'], csrf=False, type='http', auth="user", website=True)
	def portal_student_request_save(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
		partner = request.env.user.partner_id
		selected_field = kw.get('selected_field')
		old_info = kw.get('old_info')
		new_info = kw.get('new_info')
		student = http.request.env['odoocms.student'].sudo().search([('partner_id', '=', partner.id)])
		data = {
			'student_id': student.id,
			'change_in': selected_field,
			'old_info': old_info,
			'new_info': new_info
		}
		change_request = http.request.env['odoocms.request.student.profile'].sudo().create(data)
		return request.render("odoocms_student_portal.portal_student_profilechange")
	

class OdooCMSrequestStProfile(models.Model):
	_name = "odoocms.request.student.profile"
	_description = "Student Profile Change Request"

	student_id = fields.Many2one('odoocms.student', string="Student")
	change_in = fields.Char(string='Change In')
	old_info = fields.Char(string='Old Information')
	new_info = fields.Char(string='New Information')
