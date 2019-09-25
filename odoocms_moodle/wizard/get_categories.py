import pdb
import time
import datetime
from openerp import api, fields, models,_
from dateutil.relativedelta import relativedelta


class OdooCMSGetMoodleCategories(models.TransientModel):
	_name ='odoocms.get.moodle.categories'
	_description = 'Get Moodle Categories'
	
	@api.multi
	def get_categories(self):
		invoices = self.env['odoocms.moodle.category'].get_categories()
		
		return {'type': 'ir.actions.act_window_close'}

