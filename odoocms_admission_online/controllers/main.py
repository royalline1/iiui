

import logging
from odoo.http import request
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.exceptions import UserError
from odoo import _
import pdb

_logger = logging.getLogger(__name__)

class AuthSignupHome(Home):

	# def do_signup(self, qcontext):
	# 	""" Shared helper that creates a res.partner out of a token """
	# 	values = dict((key, qcontext.get(key)) for key in ('login', 'name', 'password', 'cnic'))
	# 	assert any([k for k in values.values()]), "The form was not properly filled in."
	# 	assert values.get('password') == qcontext.get('confirm_password'), "Passwords do not match; please retype them."
	# 	self._signup_with_values(qcontext.get('token'), values)
	# 	request.cr.commit()

	def do_signup(self, qcontext):
		""" Shared helper that creates a res.partner out of a token """
		values = { key: qcontext.get(key) for key in ('login', 'name', 'password', 'cnic','mobile') }
		if not values:
			raise UserError(_("The form was not properly filled in."))

#get all user and check if the email already exist or not
		user = request.env["res.users"].sudo().search([])
		count = 0
		for rec in user:
			if (rec.login).upper() == (qcontext.get("login")).upper():
				count += 1
		#this is to check entryID is valid or not
		valid_entryID = request.env['odoocms.entrytest.result'].sudo().search([('applicantID', '=', values.get('login')),('cnic', '=', values.get('cnic'))])
		if qcontext.get('signup_entryID_way_enabled'):
			if request.env["res.users"].sudo().search([("cnic", "=", qcontext.get("cnic"))]) or count>0:
				raise UserError(_("Another user is already registered with same CNIC or userID."))
			elif (not valid_entryID):
				raise UserError(_("Invalid ID or CNIC."))

		# this is to check CNIC And phone is valid or not
		valid_user = request.env['odoocms.condidate.verification'].sudo().search([('cnic', '=', values.get('cnic')), ('mobile', '=', values.get('mobile'))])
		if qcontext.get('signup_CNICPhone_way_enabled'):
			if count>0:
				raise UserError(_("Another user is already registered with same Email."))
			elif request.env["res.users"].sudo().search(['|',("cnic", "=", qcontext.get("cnic")),("mobile", "=", qcontext.get("mobile"))]):
				raise UserError(_("Another user is already registered with same Email, Phone or CNIC."))
			elif (not valid_user):
				raise UserError(_("Invalid Phone or CNIC."))
			
		if values.get('password') != qcontext.get('confirm_password'):
			raise UserError(_("Passwords do not match; please retype them."))
		supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
		if request.lang in supported_langs:
			values['lang'] = request.lang
		self._signup_with_values(qcontext.get('token'), values)
		request.env.cr.commit()
	

	# This is super call for sinup with entryID configuration
	def get_auth_signup_config(self):
		res = super(AuthSignupHome, self).get_auth_signup_config()
		get_param = request.env['ir.config_parameter'].sudo().get_param
		res['signup_entryID_way_enabled'] = get_param('auth_signup.way_entryID') == 'True'
		res['signup_CNICPhone_way_enabled'] = get_param('auth_signup.way_CNICPhone') == 'True'
		return res
	
	
