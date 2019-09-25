# -*- coding: utf-8 -*-

from odoo import http
import requests
import json
import os
import pdb
import sys
import base64
import webbrowser

class RegistrationFee(http.Controller):
	
	@http.route('/onlineadmission/registration/fee', type='http', auth="user", method=['GET'], website=True)
	def registration_fee_vari_template(self, **kwargs):
	
		current_user = http.request.env.user
		auth_signup_cnic_phone = http.request.env['ir.config_parameter'].sudo().get_param('auth_signup.way_CNICPhone')

		amount = 2500
		branch_code = kwargs.get('branch_code')
		voucher_no = kwargs.get('voucher_no')
		applicant_name = kwargs.get('applicant_name')
		
		student = http.request.env['odoocms.application'].sudo().search([('entryID', '=', current_user.email)])
		if(student):
			webbrowser.open('/admission/registration')
		else:
			fee = http.request.env['odoocms.admission.fee'].sudo().search([
				('amount', '=', 2500),('branch_code', '=', branch_code),('voucher_no', '=', voucher_no),
				('applicant_name', '=', applicant_name),('is_used', '=', False)])
			if(fee):
				student = http.request.env['odoocms.application'].sudo().create({
						'cnic': current_user.cnic,
						'entryID': current_user.email,
						'name': current_user.name,
						'branch_code': branch_code,
						'voucher_no':voucher_no,
						'amount': amount,
						'submission_date': fee.submission_date
					})
				if(student):
					fee.sudo().update({'is_used':True})
					programs_apply_for = http.request.env['odoocms.admission.register'].sudo().search([('state', '=', 'application')])
					countries = http.request.env['res.country'].sudo().search([])
					religion_id = http.request.env['odoocms.religion'].sudo().search([])
		
					current_user = http.request.env.user
					programs_apply = http.request.env['odoocms.admission.register'].sudo().search([('state', '=', 'application'),('id', '=', student.register_id.id)])
					programs = programs_apply.program_ids
		
					program_perferences = http.request.env['odoocms.application.preference'].sudo().search([('application_id', '=', student.id)])
					program_perferences_ordered = http.request.env['odoocms.application.preference'].sudo().search([('application_id', '=', student.id)], order = 'preference asc' )
					matric_education = http.request.env['odoocms.application.academic'].sudo().search([('application_id', '=', student.id),('degree_level', '=', 'matric')])
					inter_education = http.request.env['odoocms.application.academic'].sudo().search([('application_id', '=', student.id),('degree_level', '=', 'inter')])
					application_documents = http.request.env['odoocms.application.documents'].sudo().search([('application_id', '=', student.id)])

					boards = http.request.env['odoocms.application.board'].sudo().search([])
					sessions = http.request.env['odoocms.application.passing.year'].sudo().search([])

					Data ={"students":student,
					"programs":programs,
					"countries":countries,
					"current_user":current_user,
					"programs_apply_for":programs_apply_for,
					"program_perferences":program_perferences,
					"matric_education":matric_education,
					"inter_education":inter_education,
					"program_perferences_ordered": program_perferences_ordered,
					"application_documents":application_documents,
					'auth_signup_cnic_phone':auth_signup_cnic_phone,
				  	 "boards": boards,
				   	"sessions": sessions,
					'religion_id':religion_id,
					}
					return http.request.render('odoocms_admission_online.addmission_registration', Data)
				else:
					return http.request.render('odoocms_admission_online.admission_bank_fee')
			else:
				return http.request.render('odoocms_admission_online.admission_bank_fee')
		
	