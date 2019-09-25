import pdb
import time
import datetime
from openerp import api, fields, models,_
from dateutil.relativedelta import relativedelta
from ..models import aarsol_unitime


class OdooCMSSyncUnitimeSession(models.TransientModel):
	_name ='odoocms.sync.unitime.session'
	_description = 'Sync Unitime Session'
	
	@api.multi
	def sync_session(self):
		data = aarsol_unitime.get_session_setup()
		self.env['odoocms.time.pattern'].sync_unitime_odoo(data['timePatterns'])
		self.env['odoocms.date.pattern'].sync_unitime_odoo(data['datePatterns'])
		self.env['odoocms.department'].sync_unitime_odoo(data['departments'])
		
		return {'type': 'ir.actions.act_window_close'}
	
	@api.multi
	def import_rooms(self):
		data = aarsol_unitime.import_rooms()
		self.env['odoocms.room'].sync_unitime_odoo(data)
	
	@api.multi
	def import_instructors(self):
		data = aarsol_unitime.import_instructors()
		self.env['odoocms.faculty.staff'].sync_unitime_odoo(data)
	