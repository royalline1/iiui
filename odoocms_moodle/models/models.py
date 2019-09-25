# -*- coding: utf-8 -*-
import requests

from odoo import models, fields, api
import pdb
from . import aarsol_moodle
from datetime import date, datetime
from odoo.exceptions import ValidationError, UserError

#params = models.env['ir.config.parameter'].search([])
# aarsol_moodle.URL = "https://my.moodle.site"
# aarsol_moodle.KEY = "xxxxx (moodle secret token)"


class OdooCMSMoodleCategory(models.Model):
	_name = 'odoocms.moodle.category'
	_description = 'Moodle Category Table'
	
	category_id = fields.Integer('Moodle ID')
	category_parent = fields.Many2one('odoocms.moodle.category','Parent Category', ondelete="set null")
	name = fields.Char('Name')
	description = fields.Html('Description')
	
	@api.model
	def create(self, vals):
		if not vals.get('moodle_sync', False):
			try:
				vals['category_id'] = self.create_category(vals) # To avoid creating already existing categories
			except Exception:
				pass
		else:
			del vals['moodle_sync']
		return super(OdooCMSMoodleCategory, self).create(vals)
	
	@api.multi
	def write(self, vals):
		category = super(OdooCMSMoodleCategory, self).write(vals)
		if not vals.get('moodle_sync',False):
			try:
				self.update_category()
			except Exception:
				pass
		return category
	
	@api.multi
	def unlink(self):
		try:
			self.delete_category()
		except Exception:
			pass
		super(OdooCMSMoodleCategory, self).unlink()
	
	@api.model
	def create_category(self, vals):
		category_parent = self.search([('id', '=', vals['category_parent'])]).category_id
		print(category_parent)
		category = aarsol_moodle.MoodleCategory(
			name=vals['name'],
			parent= category_parent,
			description = vals['description'],
			descriptionformat = 1,
		)
		category.create()
		return category.id
	
	@api.model
	def update_category(self):
		category = aarsol_moodle.MoodleCategory(
			id = self.category_id,
			name= self.name,
			parent= self.category_parent.category_id,
			description= self.description,
			descriptionformat= 1,
			idnumber = self.id,
		)
		category.update()
	
	@api.model
	def delete_category(self):
		category = aarsol_moodle.MoodleCategory(
			id = self.category_id,
			newparent = 1,
		)
		category.delete()

	@api.model
	def get_categories(self):
		categories = aarsol_moodle.MoodleCategoryList()
		for req in categories:
			data = {
				'name': req.name,
				'description': req.description,
				'category_parent': False,
				'moodle_sync': 1,
			}
			if req.parent > 0:
				category_parent = self.search([('category_id', '=', req.parent)]).id
				data.update({'category_parent': category_parent})
				
			category = self.env['odoocms.moodle.category'].search([('category_id','=',req.id)])
			if category:
				try:
					category.write(data)
				except Exception:
					print('Category not updated')
			
			else:
				data.update({'category_id': req.id})
				try:
					self.create(data)
				except Exception:
					print('Category not created')


class OdooCMSMoodleCourse(models.Model):
	_name = 'odoocms.moodle.course'
	_description = 'Moodle Course Table'
	
	course_id = fields.Integer()
	category_id = fields.Many2one('odoocms.moodle.category','Category')
	fullname = fields.Char('Full Name')
	shortname = fields.Char('Short Name')
	date_start = fields.Datetime('Start Date')
	date_end = fields.Datetime('End Date')
	summary = fields.Html('Summary')
	
	@api.multi
	def _reopen_form(self):
		window = {
			'type': 'ir.actions.act_window',
			'res_model': self._name,
			'res_id': self.id,
			'view_type': 'form',
			'view_mode': 'form',
		}
		return window
	
	@api.model
	def create(self, vals):
		if not vals.get('moodle_sync', False):
			try:
				vals['course_id'] = self.create_moodle_course(vals)
			except Exception:
				pass
		else:
			del vals['moodle_sync']
		return super(OdooCMSMoodleCourse, self).create(vals)
	
	@api.multi
	def write(self, vals):
		course = super(OdooCMSMoodleCourse, self).write(vals)
		if not vals.get('moodle_sync', False):
			try:
				self.update_moodle_course()
			except Exception:
				pass
		return course
	
	@api.multi
	def unlink(self):
		try:
			self.delete_moodle_course()
		except Exception:
			pass
		super(OdooCMSMoodleCourse, self).unlink()
		
	@api.model
	def create_moodle_course(self, vals):
		category = self.env['odoocms.moodle.category'].search([('id', '=', vals['category_id'])]).category_id
	
		d0 = date(1970, 1, 1)
		d1 = datetime.strptime(vals['date_start'][:10], '%Y-%m-%d').date()
		delta = d1 - d0
		startdate = (delta.days + 1) * 86400
		
		d2 = datetime.strptime(vals['date_end'][:10], '%Y-%m-%d').date()
		delta = d2 - d0
		enddate = (delta.days + 1) * 86400
		
		course = aarsol_moodle.MoodleCourse(
			fullname = vals['fullname'],
			shortname = vals['shortname'],
			categoryid = category,
			summary = vals['summary'],
			format = 'weeks',
			startdate = startdate,
			enddate = enddate,
		)
		course.create()
		return course.id
	
	@api.model
	def update_moodle_course(self):
		category = self.env['odoocms.moodle.category'].search([('id', '=', self.category_id.id)]).category_id
		d0 = date(1970, 1, 1)
		d1 = self.date_start.date()
		delta = d1 - d0
		startdate = (delta.days + 1) * 86400
		
		d2 = self.date_end.date()
		delta = d2 - d0
		enddate = (delta.days + 1) * 86400
		
		course = aarsol_moodle.MoodleCourse(
			id = self.course_id,
			fullname = self.fullname,
			shortname = self.shortname,
			categoryid = category,
			summary = self.summary,
			startdate = startdate,
			enddate = enddate,
			idnumber=self.id,
		)
		course.update()
	
	@api.model
	def delete_moodle_course(self):
		course = aarsol_moodle.MoodleCourse(
			id=self.course_id,
		)
		course.delete()
	
	def get_moodle_contents(self):
		course = aarsol_moodle.MoodleCourse(
			id=self.course_id,
		)
		course.get_contents()
		
	def get_moodle_grades(self):
		course = aarsol_moodle.MoodleCourse(
			id=self.course_id,
		)
		course.get_grades2()

		
	@api.model
	def get_courses(self):
		courses = aarsol_moodle.MoodleCourseList()
		
		for req in courses:
			category = self.env['odoocms.moodle.category'].search([('category_id', '=', req.categoryid)]).id
			data = {
				'fullname': req.fullname,
				'shortname': req.shortname,
				'summary': req.summary,
				'category_id': category,
				'moodle_sync': 1,
			}
			
			course = self.env['odoocms.moodle.course'].search([('course_id', '=', req.id)])
			if course:
				try:
					course.write(data)
				except Exception:
					print('Course not updated')
			
			else:
				data.update({'course_id': req.id})
				try:
					self.create(data)
				except Exception:
					print('Course not created')

	
class OdooCMSStudent(models.Model):
	_inherit = 'odoocms.student'
	
	moodle_user_id = fields.Integer('Moodle ID', track_visibility='onchange')
	
	@api.multi
	def create_student_user(self):
		super(OdooCMSStudent, self).create_student_user()

		user = aarsol_moodle.MoodleUser(
			firstname=self.first_name,
			lastname=self.last_name,
			username=self.id_number.lower() or self.entryID.lower() or self.email.lower(),
			password='Pakistan@655',
			email=self.email or (self.id_number + '@gmail.com'),
			city=self.city,
			country='pk',
			idnumber=self.id,
			auth='manual',
			#lang='en',
			#theme='standard',
			#mailformat=0,
			description='Hello World!',
		)
		user.create()
		self.moodle_user_id = user.id
	
	def update_moodle_user(self):
		if self.moodle_user_id > 0:
			user = aarsol_moodle.MoodleUser(
				id=self.moodle_user_id,
				firstname=self.first_name,
				lastname=self.last_name,
				username=self.id_number.lower() or self.entryID.lower() or self.email.lower(),
				password='Pakistan@655',
				email=self.email or (self.id_number + '@gmail.com'),
				city=self.city,
				country='pk',
				idnumber=self.id,
				auth='manual',
				description='Hello World!',
				lang='en',
			    mailformat = 1,
			)
			user.update()
		else:
			raise UserError("Moodle User did not Mapped!")
	
	def get_moodle_user(self):
		user = aarsol_moodle.MoodleUser(
			username=self.id_number.lower() or self.entryID.lower() or self.email.lower(),
		)
		user_info = user.get_by_field()
		if user_info:
			data = {
				'moodle_sync': 1,
				'first_name': user_info.firstname,
				'last_name': user_info.lastname,
				'email': user_info.email,
				'city': user_info.city,
			}
			self.write(data)
			
	def enroll_courses(self):
		courseList = aarsol_moodle.MoodleCourseList()
		user = aarsol_moodle.MoodleUser(
			id=self.moodle_user_id,
			courses=courseList.courses,
		)
		user.enroll()

