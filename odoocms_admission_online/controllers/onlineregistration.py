# -*- coding: utf-8 -*-

from odoo import http
import requests
import json
import os
import pdb
import sys
import base64
import webbrowser

class Todos(http.Controller):
	
	# This is for ajax checking all the info in added or not
	@http.route('/admission/application/data', csrf=False, type='http', auth="user", method=['GET'], website=True)
	def get_admission_application_data(self, **get):
		current_user = http.request.env.user
		student = http.request.env['odoocms.application'].sudo().search([('entryID', '=', current_user.email)])
		program_perferences = http.request.env['odoocms.application.preference'].sudo().search([('application_id', '=', student.id)])
		matric_education = http.request.env['odoocms.application.academic'].sudo().search([('application_id', '=', student.id),('degree_level', '=', 'matric')])
		inter_education = http.request.env['odoocms.application.academic'].sudo().search([('application_id', '=', student.id),('degree_level', '=', 'inter')])
		application_documents = http.request.env['odoocms.application.documents'].sudo().search([('application_id', '=', student.id)])

		entryId = student.entryID
		entryScore = student.entry_score
		register = student.register_id

		# *************************************this is for when signup with CNIC and Phone is Enabled***********************************************
		auth_signup_cnic_phone = http.request.env['ir.config_parameter'].sudo().get_param('auth_signup.way_CNICPhone')
		if auth_signup_cnic_phone:
			entryId = True
			entryScore = True
			program_perferences = [1,2,3,4,5]
			register = True
		# *************************************this is for when signup with CNIC and Phone is Enabled***********************************************

		if(len(matric_education)>0 and len(inter_education)>0):
			if(student.name and student.father_name and register and student.date_of_birth and student.image
				and student.cnic and student.mobile and student.street and student.city and student.per_city and entryId and entryScore
				and student.per_street
				and matric_education.total_marks and matric_education.obtained_marks
				and inter_education.total_marks and inter_education.obtained_marks
				and len(program_perferences)>0 and len(application_documents)>0
				):
				student.update({"state":"confirm"})
				Data = {"state":"submit"}
			else:
				Data = {"state":"draft"}
		else:
			Data = {"state":"draft"}
		return json.dumps(Data)	



	# This is for registration template to load and show data if already added in database
	@http.route('/admission/registration', type='http', auth="user", method=['GET'], website=True)
	def admission_registration(self, **get):
		programs_apply_for = http.request.env['odoocms.admission.register'].sudo().search([('state', '=', 'application')])
		countries = http.request.env['res.country'].sudo().search([])
		religion_id = http.request.env['odoocms.religion'].sudo().search([])
		
		current_user = http.request.env.user
		auth_signup_cnic_phone = http.request.env['ir.config_parameter'].sudo().get_param('auth_signup.way_CNICPhone')

		student = http.request.env['odoocms.application'].sudo().search([('entryID', '=', current_user.email)])
		programs_apply = http.request.env['odoocms.admission.register'].sudo().search([('state', '=', 'application'),('id', '=', student.register_id.id)])
		programs = programs_apply.program_ids
		
		program_perferences = http.request.env['odoocms.application.preference'].sudo().search([('application_id', '=', student.id)])
		program_perferences_ordered = http.request.env['odoocms.application.preference'].sudo().search([('application_id', '=', student.id)], order = 'preference asc' )

		matric_education = http.request.env['odoocms.application.academic'].sudo().search([('application_id', '=', student.id),('degree_level', '=', 'matric')])
		inter_education = http.request.env['odoocms.application.academic'].sudo().search([('application_id', '=', student.id),('degree_level', '=', 'inter')])
		
		application_documents = http.request.env['odoocms.application.documents'].sudo().search([('application_id', '=', student.id)])
		boards = http.request.env['odoocms.application.board'].sudo().search([])
		sessions = http.request.env['odoocms.application.passing.year'].sudo().search([])


		if (student):
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
				    "auth_signup_cnic_phone":auth_signup_cnic_phone,
				   "boards":boards,
				   "sessions":sessions,
				   "religion_id":religion_id,
					}
			if(student.state=='draft'):
				return http.request.render('odoocms_admission_online.addmission_registration', Data)
			elif (student.state=='confirm'):
				return http.request.render('odoocms_admission_online.addmission_registration_submit', Data)

			#*********************************************************************************************888
			elif auth_signup_cnic_phone:
				return http.request.render('odoocms_admission_online.addmission_registration', Data)
			#************************************************************************************************

			else:
				return http.request.render('odoocms_admission_online.application_final_report', Data)
		else:
			# *************************************this is for when signup with CNIC and Phone is Enabled***********************************************
			if auth_signup_cnic_phone:
				programs_apply_for = http.request.env['odoocms.admission.register'].sudo().search(
					[('state', '=', 'application')])
				student = http.request.env['odoocms.application'].sudo().create({
					'cnic': current_user.cnic,
					'entryID': current_user.email,
					'name': current_user.name,
					'mobile': current_user.mobile,
					'register_id':programs_apply_for[0].id,
				})
				if (student):
					programs_apply = http.request.env['odoocms.admission.register'].sudo().search(
						[('state', '=', 'application'),('id','=',student.register_id.id)])
					countries = http.request.env['res.country'].sudo().search([])

					current_user = http.request.env.user
					programs = programs_apply.program_ids

					program_perferences = http.request.env['odoocms.application.preference'].sudo().search(
						[('application_id', '=', student.id)])
					program_perferences_ordered = http.request.env['odoocms.application.preference'].sudo().search(
						[('application_id', '=', student.id)], order='preference asc')
					matric_education = http.request.env['odoocms.application.academic'].sudo().search(
						[('application_id', '=', student.id), ('degree_level', '=', 'matric')])
					inter_education = http.request.env['odoocms.application.academic'].sudo().search(
						[('application_id', '=', student.id), ('degree_level', '=', 'inter')])
					application_documents = http.request.env['odoocms.application.documents'].sudo().search(
						[('application_id', '=', student.id)])

					boards = http.request.env['odoocms.application.board'].sudo().search([])
					sessions = http.request.env['odoocms.application.passing.year'].sudo().search([])

					Data = {"students": student,
							"programs": programs,
							"countries": countries,
							"current_user": current_user,
							"programs_apply_for": programs_apply_for,
							"program_perferences": program_perferences,
							"matric_education": matric_education,
							"inter_education": inter_education,
							"program_perferences_ordered": program_perferences_ordered,
							"application_documents": application_documents,
							"auth_signup_cnic_phone": auth_signup_cnic_phone,
							"boards": boards,
							"sessions": sessions,
							"religion_id":religion_id,
							}
					return http.request.render('odoocms_admission_online.addmission_registration', Data)
			# *************************************this is for when signup with CNIC and Phone is Enabled***********************************************
			return http.request.render('odoocms_admission_online.admission_bank_fee')
	
	
	

	# This is to save program apply for because after selection of program register you need to reload the programs
	@http.route('/admissiononline/programregister/save', csrf=False, type="http", methods=['POST', 'GET'], auth="public", website=True)
	def save_program_register(self, **kw):
		current_user = http.request.env.user
		program_apply_for = kw.get('program_apply_for')
		try:
			application = http.request.env['odoocms.application'].sudo().search([('entryID', '=', current_user.email)])
			application.sudo().update({'register_id':program_apply_for
			})
			record = {'status_is': "noerror"}
		except:
			record = {'status_is': "error"}
		return json.dumps(record)
		
	
	# This is called from ajax to save applicant data
	@http.route('/admission/save', csrf=False, type="http", methods=['POST', 'GET'], auth="public", website=True)
	def save_admission_application_contents(self, **kw):
		# image = kw.get('image')
		# imageData = image.read()
		# image_base64 = base64.encodestring(imageData)
		current_user = http.request.env.user
		first_name = kw.get('first_name')
		father_name = kw.get('father_name')
		last_name = kw.get('last_name')
		blood_group = kw.get('bloodgroup')
		religion_id = int(kw.get('religion_id'))
		dob = kw.get('dob')
		cnic = kw.get('cnic')
		mobile = kw.get('mobile')
		gender = kw.get('gender')
		domicile = kw.get('domicile')
		nationality = int(kw.get('nationality'))
		
		per_street = kw.get('per_street')
		per_street2 = kw.get('per_street2')
		per_city = kw.get('per_city')
		per_country = int(kw.get('per_country'))
		
		street = kw.get('street')
		street2 = kw.get('street2')
		country = int(kw.get('country'))
		city = kw.get('city')
		is_same_address = bool(kw.get('is_same_address'))
		is_hafiz = bool(kw.get('is_hafiz'))
		
		program_apply_for = kw.get('program_apply_for')
		choice1 = kw.get("choice1")
		choice2 = kw.get("choice2")
		choice3 = kw.get("choice3")
		choice4 = kw.get("choice4")
		choice5 = kw.get("choice5")
		choice6 = kw.get("choice6")
		choice7 = kw.get("choice7")
		choice8 = kw.get("choice8")
		choice9 = kw.get("choice9")
		choice10 = kw.get("choice10")
		choice11 = kw.get("choice11")
		choice12 = kw.get("choice12")
		choice13 = kw.get("choice13")
		choice14 = kw.get("choice14")
		choice15 = kw.get("choice15")
		choice16 = kw.get("choice16")
		choice17 = kw.get("choice17")
		choice18 = kw.get("choice18")
		
		application = http.request.env['odoocms.application'].sudo().search([('entryID', '=', current_user.email)])
		programs_apply = http.request.env['odoocms.admission.register'].sudo().search([('state', '=', 'application'),('id', '=', application.register_id.id)])
		programs = programs_apply.program_ids
		
		choices = []
		selected_programs = []

		auth_signup_cnic_phone = http.request.env['ir.config_parameter'].sudo().get_param('auth_signup.way_CNICPhone')
		if not auth_signup_cnic_phone:
			if (choice1!= "0"  and choice1!= None):
				choices.append(choice1)
				selected_programs.append(programs[0].id)
			if (choice2!= "0"  and choice2!= None):
				choices.append(choice2)
				selected_programs.append(programs[1].id)
			if (choice3!= "0" and choice3!= None):
				choices.append(choice3)
				selected_programs.append(programs[2].id)
			if (choice4!= "0" and choice4!= None):
				choices.append(choice4)
				selected_programs.append(programs[3].id)
			if (choice5!= "0" and choice5!= None):
				choices.append(choice5)
				selected_programs.append(programs[4].id)
			if (choice6!="0" and choice6!= None):
				choices.append(choice6)
				selected_programs.append(programs[5].id)
			if (choice7!="0" and choice7!= None):
				choices.append(choice7)
				selected_programs.append(programs[6].id)
			if (choice8!="0" and choice8!= None):
				choices.append(choice8)
				selected_programs.append(programs[7].id)
			if (choice9!="0" and choice9!= None):
				choices.append(choice9)
				selected_programs.append(programs[8].id)
			if (choice10!="0" and choice10!= None):
				choices.append(choice10)
				selected_programs.append(programs[9].id)
			if (choice11!="0" and choice11!= None):
				choices.append(choice11)
				selected_programs.append(programs[10].id)
			if (choice12!="0" and choice12!= None):
				choices.append(choice12)
				selected_programs.append(programs[11].id)
			if (choice13!="0" and choice13!= None):
				choices.append(choice13)
				selected_programs.append(programs[12].id)
			if (choice14!="0" and choice14!= None):
				choices.append(choice14)
				selected_programs.append(programs[13].id)
			if (choice15!="0" and choice15!= None):
				choices.append(choice15)
				selected_programs.append(programs[14].id)
			if (choice16!="0" and choice16!= None):
				choices.append(choice16)
				selected_programs.append(programs[15].id)
			if (choice17!="0" and choice17!= None):
				choices.append(choice17)
				selected_programs.append(programs[16].id)
			if (choice18!="0" and choice18!= None):
				choices.append(choice18)
				selected_programs.append(programs[17].id)

		try:
			current_user = http.request.env.user
			if (application):
				application.sudo().update({
					'first_name': first_name, 'last_name': last_name,'blood_group':blood_group, 'email':current_user.email, 'father_name': father_name, 'mobile': mobile, 'gender': gender, 'domicile': domicile, 'nationality': nationality, 'date_of_birth': dob,
					'per_street': per_street, 'per_street2': per_street2,'per_country_id': per_country, 'per_city': per_city, 'street': street, 'street2': street2, 'city': city, 'country_id': country, 'is_same_address': is_same_address, 'religion_id':religion_id,
					# 'register_id':program_apply_for,
					'is_hafiz':is_hafiz
				})
				http.request.env['odoocms.application.preference'].sudo().search([('application_id', '=', application.id)]).sudo().unlink()

				if auth_signup_cnic_phone:
					http.request.env['odoocms.application.preference'].sudo().create({
						'preference': 1,
						'application_id': application.id,
						'program_id': int(choice1)
					})
				else:
					for choice in range (0,len(choices)):
						http.request.env['odoocms.application.preference'].sudo().create({
						'preference': choices[choice],
						'application_id': application.id,
						'program_id': int(selected_programs[choice])
						})
					choices = []
					selected_programs = []
				record = {'status_is': "update"}
					
			else:
				record = {'status_is': "create"}
				# application.sudo().create({
					# 'cnic': cnic, 
					# 'name': student_name, 'last_name': last_name, 'email':current_user.email, 'father_name': father_name, 'mobile': mobile, 'gender': gender, 'domicile': domicile, 'nationality': nationality, 'date_of_birth': dob,
					# 'per_street': per_street, 'per_street2': per_street2,'per_country_id': per_country, 'per_city': per_city, 'street': street, 'street2': street2, 'city': city, 'country_id': country, 'is_same_address': is_same_address,
					# 'register_id':program_apply_for,
				# })
				# http.request.env['odoocms.application.preference'].sudo().search([('application_id', '=', application.id)]).sudo().unlink()
				# for choice in range (0,len(choices)):
					# http.request.env['odoocms.application.preference'].sudo().create({
					# 'preference': choices[choice], 
					# 'application_id': application.id, 
					# 'program_ids': programs[choice].id
					# })
				# choices = []
		except:
			record = {'status_is': "error"}
		return json.dumps(record)
		
	@http.route('/admission/education/inter/save', csrf=False, type="http", methods=['POST', 'GET'], auth="public", website=True)
	def save_admission_inter_education(self, **kw):
		application_id = int(kw.get('application_id'))
		total_marks = kw.get('intertotalmarks')
		obtained_marks = kw.get('interbtainedmarks')
		
		degree = kw.get('inter_degree')
		year = kw.get('inter_pass_year')
		board = kw.get('inter_board')
		subjects = kw.get('inter_subject')
		
		repeat_times = kw.get('repeat_times')
		is_additional = bool(kw.get('is_additional'))
		
		try:
			student_inter = http.request.env['odoocms.application.academic'].sudo().search([('application_id', '=', application_id),('degree_level', '=', 'inter')])
			if (student_inter):
				record = {'status_is': "update"}
				student_inter.sudo().update({
					'obtained_marks': obtained_marks, 'total_marks': total_marks, 
					'degree': degree, 'year': year,
					'board': board, 'subjects': subjects, 
				})
			else:
				record = {'status_is': "create_inter_record"}
				http.request.env['odoocms.application.academic'].sudo().create({
					'application_id':application_id, 'degree_level': "inter",
					'obtained_marks': obtained_marks, 'total_marks': total_marks, 
					'degree': degree, 'year': year,
					'board': board, 'subjects': subjects,
				})
			student = http.request.env['odoocms.application'].sudo().search([('id', '=', application_id)])
			values = {'repeat_times': repeat_times, 
					'is_additional':is_additional,
					'inter_marks':obtained_marks
					}
			student.sudo().update(values)
		except:
			record = {'status_is': "error"}
		return json.dumps(record)
		
	@http.route('/admission/education/matric/save', csrf=False, type="http", methods=['POST', 'GET'], auth="public", website=True)
	def save_admission_matric_education(self, **kw):
		application_id = int(kw.get('application_id'))
		total_marks = kw.get('matrictotalmarks')
		obtained_marks = kw.get('matricobtainedmarks')
		
		degree = kw.get('matric_degree')
		year = kw.get('matric_pass_year')
		board = kw.get('matric_board')
		subjects = kw.get('matric_subject')
		
		try:
			student_matric = http.request.env['odoocms.application.academic'].sudo().search([('application_id', '=', application_id),('degree_level', '=', 'matric')])
			if (student_matric):
				record = {'status_is': "update matric"}
				student_matric.sudo().update({
					'obtained_marks': obtained_marks, 'total_marks': total_marks, 
					'degree': degree, 'year': year,
					'board': board, 'subjects': subjects
				})
				
			else:
				record = {'status_is': application_id}
				http.request.env['odoocms.application.academic'].sudo().create({
					'application_id':application_id, 'degree_level': "matric",
					'obtained_marks': obtained_marks, 'total_marks': total_marks, 
					'degree': degree, 'year': year,
					'board': board, 'subjects': subjects
				})
			student = http.request.env['odoocms.application'].sudo().search([('id', '=', application_id)])
			student.sudo().update({'ssc_marks':obtained_marks})
		except:
			record = {'status_is': "error"}
		return json.dumps(record)
		
		
	@http.route('/entrytest/verfication', csrf=False, type='http', auth="user", method=['GET'], website=True)
	def verify_entrytest_data(self, **get):
	
		Data ={"status_is":"not_verified"}
		applicantID = get.get('applicantID')
		test_score = get.get('test_score')
		test_date = get.get('test_date')
		applicant_name = get.get('applicant_name')
		current_user = http.request.env.user
		applicant = http.request.env['odoocms.entrytest.result'].sudo().search([('applicantID', '=', current_user.email),('test_score', '=', test_score),('test_date', '=', test_date)])
		if (applicant):
			application = http.request.env['odoocms.application'].sudo().search([('entryID', '=', current_user.email)])
			values = {
                'entry_score': test_score, 'entryID': applicantID
            }
			application.sudo().update(values)
			Data ={"status_is":"verified"}
		else:
			Data = {"status_is":"not_verified"}
		return json.dumps(Data)
	
	@http.route('/application/change/state', csrf=False, type='http', auth="user", method=['GET'], website=True)
	def application_change_state(self, **get):
		current_user = http.request.env.user
		applicant = http.request.env['odoocms.application'].sudo().search([('entryID', '=', current_user.email)])
		if(applicant):
			applicant.update({'state':'submit'})
			Data ={"state":"submit"}
		else:
			Data ={"state":"draft"}
		return json.dumps(Data)
	
	# This is to save profile image
	@http.route('/admissiononline/profileimage/save', csrf=False, type="http", methods=['POST', 'GET'], auth="public", website=True)
	def save_profile_image(self, **kw):
		current_user = http.request.env.user
		file = kw.get('userImage')
		try:
			application = http.request.env['odoocms.application'].sudo().search([('entryID', '=', current_user.email)])
			attachment_value = {
                'image': base64.encodestring(file.read())
            }
			application.sudo().update(attachment_value)
			record = {'status_is': "noerror"}
		except:
			record = {'status_is': "error"}
		return json.dumps(record)
	

	# This is to save documents
	@http.route('/save/application/documents', csrf=False, type="http", methods=['POST', 'GET'], auth="public", website=True)
	def save_application_documents(self, **kw):
		current_user = http.request.env.user
		application = http.request.env['odoocms.application'].sudo().search([('entryID', '=', current_user.email)])
		matric_scaned_copy = kw.get('matric')
		inter_scaned_copy = kw.get('inter')
		domicile_scaned_copy = kw.get('domicile')
		prc_scaned_copy = kw.get('prc')
		matric_scaned_copy_size = matric_scaned_copy.tell()
		hafiz_scaned_copy = kw.get('hafiz')
		try:
			attachment_value = {
				'application_id':application.id,
                'matric_scaned_copy': base64.encodestring(matric_scaned_copy.read()),
				'matric_scaned_copy_name': matric_scaned_copy.filename,
				'matric_scaned_copy_size': matric_scaned_copy_size,
				
				'inter_scaned_copy': base64.encodestring(inter_scaned_copy.read()),
				'inter_scaned_copy_name': inter_scaned_copy.filename,
				# 'inter_scaned_copy_size': os.stat(inter_scaned_copy).st_size,

            }
			if domicile_scaned_copy:
				attachment_value['domicile_scaned_copy'] = base64.encodestring(domicile_scaned_copy.read())
				attachment_value['domicile_scaned_copy_name'] = domicile_scaned_copy.filename
				# 'domicile_scaned_copy_size': os.stat(domicile_scaned_copy).st_size,

			if prc_scaned_copy:
				attachment_value['prc_scaned_copy']= base64.encodestring(prc_scaned_copy.read())
				attachment_value['prc_scaned_copy_name'] = prc_scaned_copy.filename
				# 'prc_scaned_copy_size': os.stat(prc_scaned_copy).st_size,

			if hafiz_scaned_copy:
				attachment_value['hafiz_scaned_copy'] = base64.encodestring(hafiz_scaned_copy.read())
				attachment_value['hafiz_scaned_copy_name'] = prc_scaned_copy.filename

			application_documents = http.request.env['odoocms.application.documents'].sudo().search([('application_id', '=', application.id)])
			if(application_documents):
				application_documents.sudo().update(attachment_value)
				record = {'status_is': "update"}
			else:
				application_documents.sudo().create(attachment_value)
				record = {'status_is': "create"}
		except:
			record = {'status_is': "error"}
		return json.dumps(record)
	
