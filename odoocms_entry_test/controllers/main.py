# -*- coding: utf-8 -*-

from odoo import http
import requests
import json
import os
import pdb
import sys
import base64
import random

class EntryTest(http.Controller):


	@http.route('/entry/application/data', csrf=False, type='http', auth="public", method=['GET'], website=True)
	def get_entry_application_data(self, **get):
		mobile = get.get('mobile')
		test_center_select = get.get('test_center_select')
		application = http.request.env['odoocms.entrytest.application'].sudo().search([('mobile', '=', mobile)])
		application.sudo().update({'center_id':test_center_select})
		if(application.name and application.father_name and application.date_of_birth and application.guardian_name and application.guardian_cnic and application.image
			and application.cnic and application.guardian_number and application.email and application.street and application.per_street
			and application.ssc_total_marks and application.ssc_obtained_marks and application.ssc_passing_year and application.ssc_board
			and application.hssc_total_marks and application.hssc_passing_year and application.hssc_board
			and application.center_id
			):
			application.update({'state':'confirm'})
			Data = {"state":"submit"}
		else:
			Data = {"state":"draft"}
		return json.dumps(Data)
		
		
	@http.route('/entry/profileimage/save', csrf=False, type="http", methods=['POST', 'GET'], auth="public", website=True)
	def entry_test_registration(self, **kw):
		file = kw.get('applicantImage')
		mobile = kw.get('mobile')
		try:
			application = http.request.env['odoocms.entrytest.application'].sudo().search([('mobile', '=', mobile)])
			attachment_value = {
                'image': base64.encodestring(file.read())
            }
			application.sudo().update(attachment_value)
			record = {'status_is': "noerror"}
		except:
			record = {'status_is': "error"}
		return json.dumps(record)
	
	@http.route('/entrytest/registration', csrf=False, type="http", methods=['POST', 'GET'], auth="public", website=True)
	def entry_profile_image_save(self, **kw):
		return http.request.render('odoocms_entry_test.entry_bank_fee')
		
	@http.route('/entrytest/fee/verification', csrf=False, type="http", methods=['POST', 'GET'], auth="public", website=True)
	def entry_test_fee_verification(self, **kw):
		sequence_no = kw.get('sequence_no')
		branch_code = kw.get('branch_code')
		submission_date = kw.get('submission_date')
		mobile = kw.get('mobile')
		
		test_center = http.request.env['odoocms.entrytest.center'].sudo()
		test_centers = http.request.env['odoocms.entrytest.center'].sudo().search([])
		for rec in test_centers:
			if len(rec.application_ids) < rec.capacity:
				test_center+=rec
				
		applicant_fee = http.request.env['odoocms.entrytest.fee'].sudo().search([('sequence_no', '=', sequence_no),('branch_code', '=', branch_code),('submission_date', '=', submission_date),('mobile', '=', mobile)])
		if(applicant_fee):
			company = http.request.env['res.company'].sudo().search([])
			entrytest = http.request.env['odoocms.entrytest'].sudo().search([('active','=','True')])
			applicant = http.request.env['odoocms.entrytest.application'].sudo().search([('mobile', '=', mobile)])
			instructions = http.request.env['odoocms.entrytest.instruction'].sudo().search([('active','=','True')])
			if(applicant):
				values = {
					"applicant":applicant,
					'test_centers':test_center,
					'company':company,
					'entrytest':entrytest,
					'instructions':instructions,
					}
				if(applicant.state=='draft'):
					return http.request.render('odoocms_entry_test.entry_registration',values)
				elif(applicant.state=='confirm'):
					return http.request.render('odoocms_entry_test.entry_registration_confirm',values)
				else:
					return http.request.render('odoocms_entry_test.admit_card',values)
			else:
				if (applicant_fee.is_used == False):
					applicant = http.request.env['odoocms.entrytest.application'].sudo().create({'mobile':mobile})
					if applicant:
						applicant_fee.sudo().update({'is_used':True})
					values = {
						"applicant":applicant,
						'test_centers':test_center,
						'company':company,
						'entrytest':entrytest,
						'instructions':instructions,
						}
					return http.request.render('odoocms_entry_test.entry_registration',values)
				else:
					return http.request.render('odoocms_entry_test.entry_bank_fee')
		else:
			return http.request.render('odoocms_entry_test.entry_bank_fee')
			
	
	# This is called from ajax to save applicant data
	@http.route('/entry/application/save', csrf=False, type="http", methods=['POST', 'GET'], auth="public", website=True)
	def save_entry_application_contents(self, **kw):
		
		mobile = kw.get('mobile')
		
		first_name = kw.get('first_name')
		father_name = kw.get('father_name')
		guardian_name = kw.get('guardian_name')
		guardian_cnic = kw.get('guardian_cnic')
		dob = kw.get('dob')
		gender = kw.get('gender')
		cnic = kw.get('cnic')
		mobile = kw.get('mobile')
		email = kw.get('email')
		guardian_number = kw.get('guardian_number')
		
		ssc_total_marks = kw.get('ssc_total_marks')
		ssc_obtained_marks = kw.get('ssc_obtained_marks')
		ssc_passing_year = kw.get('ssc_passing_year')
		ssc_board = kw.get('ssc_board')
		
		hssc_total_marks = kw.get('hssc_total_marks')
		hssc_obtained_marks = kw.get('hssc_obtained_marks')
		hssc_passing_year = kw.get('hssc_passing_year')
		hssc_board = kw.get('hssc_board')
		hssc_group = kw.get('hssc_group')
		
		per_street = kw.get('per_street')
		per_street2 = kw.get('per_street2')
		
		street = kw.get('street')
		street2 = kw.get('street2')
		
		is_same_address = bool(kw.get('is_same_address'))
		
		application = http.request.env['odoocms.entrytest.application'].sudo().search([('mobile', '=', mobile)])
		
		try:
			if (application):
				application.sudo().update({
					'name': first_name,'father_name': father_name, 'guardian_name': guardian_name, 'guardian_cnic':guardian_cnic, 'date_of_birth': dob,
					'gender': gender, 'cnic':cnic, 'email':email, 'guardian_number':guardian_number, 
					'per_street': per_street, 'per_street2': per_street2,'street': street, 'street2': street2,'is_same_address': is_same_address,
					'ssc_total_marks':ssc_total_marks, 'ssc_obtained_marks':ssc_obtained_marks, 'ssc_passing_year':ssc_passing_year, 'ssc_board':ssc_board,
					'hssc_total_marks':hssc_total_marks, 'hssc_obtained_marks':hssc_obtained_marks, 'hssc_passing_year':hssc_passing_year, 'hssc_board':hssc_board, 'hssc_group':hssc_group,
				})
				record = {'status_is': "update"}
					
			else:
				record = {'status_is': "create"}
				return http.request.render('odoocms_entry_test.entry_bank_fee')
		except:
			record = {'status_is': "error"}
		return json.dumps(record)
		
	@http.route('/entry/application/change/state', csrf=False, type='http', auth="public", method=['GET'], website=True)
	def entry_application_change_state(self, **get):
		
		mobile = get.get('mobile')
		applicant = http.request.env['odoocms.entrytest.application'].sudo().search([('mobile', '=', mobile)])
		if(applicant):
			entry_sequence = http.request.env['odoocms.entrytest.center.sequence'].sudo().search([('hssc_group', '=', applicant.hssc_group),('active', '=', True)])
			if (entry_sequence):
				expect_element = http.request.env['odoocms.entrytest.application'].sudo().search([]).entryID
				if expect_element:
					sql = "select generate_series("+ entry_sequence.entryID_from +","+ entry_sequence.entryID_to +") Except (select entryID from odoocms_entrytest_application)"
				else:
					sql = "select generate_series("+ entry_sequence.entryID_from +","+ entry_sequence.entryID_to +")"
				http.request.env.cr.execute(sql)
				list = http.request.env.cr.dictfetchall()
				entryID = random.choice(list)
				#here we will give unique entryID to each student
				applicant.sudo().update({'entryID': entryID["generate_series"] ,'state':'submit'})
				Data ={"state":"submit"}
			else:
				Data ={"state":"draft"}
		else:
			Data ={"state":"draft"}
		return json.dumps(Data)