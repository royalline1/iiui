
from odoo import api, models, fields, modules, SUPERUSER_ID
from odoo.tools.safe_eval import safe_eval
import pdb


class MailActivityType(models.Model):
	_inherit = "mail.activity.type"
	
	pre_fnc = fields.Char('Pre Function')
	post_fnc = fields.Char('Post Function')
	user_id = fields.Many2one('res.users', 'Assigned To')


class MailActivityMixin(models.AbstractModel):
	_inherit = 'mail.activity.mixin'
	activity_ids = fields.One2many(domain=lambda self: [('res_model', '=', self._name), ('active', '=', True)])
	
	# mail_activity_board
	def redirect_to_activities(self, **kwargs):
		"""Redirects to the list of activities of the object shown.

		Redirects to the activity board and configures the domain so that
		only those activities that are related to the object shown are
		displayed.

		Add to the title of the view the name the class of the object from
		which the activities will be displayed.

		:param kwargs: contains the id of the object and the model it's about.
		:return: action.
		"""
		_id = kwargs.get("id")
		action = self.env['mail.activity'].action_activities_board()
		views = []
		for v in action['views']:
			if v[1] == 'tree':
				v = (v[0], 'list')
			views.append(v)
		action['views'] = views
		action['domain'] = [('res_id', '=', _id)]
		return action
 
class MailActivity(models.Model):
	_inherit = "mail.activity"
	
	pre_fnc = fields.Char('Pre Function')
	post_fnc = fields.Char('Post Function')
	user_id = fields.Many2one('res.users', 'Assigned To')
	
	# mail_activity_done
	active = fields.Boolean(default=True)
	done = fields.Boolean(default=False)
	state = fields.Selection(selection_add=[('done', 'Done')], compute='_compute_state')
	date_done = fields.Date('Completed Date', index=True, readonly=True,)
	
	
	
	# # mail_activity_board
	res_model_id_name = fields.Char(related='res_model_id.name', string="Origin", readonly=True)
	duration = fields.Float(related='calendar_event_id.duration', readonly=True)
	calendar_event_id_start = fields.Datetime(related='calendar_event_id.start', readonly=True)
	calendar_event_id_partner_ids = fields.Many2many(related='calendar_event_id.partner_ids',readonly=True)
	
	@api.depends('date_deadline', 'done')
	def _compute_state(self):
		super(MailActivity, self)._compute_state()
		for record in self.filtered(lambda activity: activity.done):
			record.state = 'done'
	
	@api.multi
	@api.onchange('previous_activity_type_id')
	def _onchange_previous_activity_type_id(self):
		for record in self:
			if record.previous_activity_type_id.default_next_type_id:
				record.activity_type_id = record.previous_activity_type_id.default_next_type_id
				record.user_id = record.previous_activity_type_id.default_next_type_id.user_id or self.env.user.id
				
	@api.multi
	def unlink(self):
		self._check_access('unlink')
		for activity in self:
			if activity.date_deadline <= fields.Date.today():
				self.env['bus.bus'].sendone(
					(self._cr.dbname, 'res.partner', activity.user_id.partner_id.id),
					{'type': 'activity_updated', 'activity_deleted': True})
		self.action_feedback('Cancelled/ Rejected')
		return True
		#return super(MailActivity, self.sudo()).unlink()
	
	def action_feedback(self, feedback=False):
		
		#res = super(MailActivity,self).action_feedback(feedback=feedback)
		# Changed original to avoid unlink
		message = self.env['mail.message']
		if feedback:
			self.write(dict(feedback=feedback))
		for activity in self:
			record = self.env[activity.res_model].browse(activity.res_id)
			activity.done = True
			activity.active = False
			activity.date_done = fields.Date.today()
			record.message_post_with_view(
				'mail.message_activity_done',
				values={'activity': activity},
				subtype_id=self.env.ref('mail.mt_activities').id,
				mail_activity_type_id=activity.activity_type_id.id,
			)
			message |= record.message_ids[0]
			
			localdict = {'record': record}
			pre_fnc = activity.pre_fnc or activity.activity_type_id.pre_fnc or False
			post_fnc = activity.post_fnc or activity.activity_type_id.post_fnc or False
			
			if post_fnc:
				safe_eval(post_fnc, localdict, mode="exec", nocopy=True)
			
		return message.ids and message.ids[0] or False
		
	@api.multi
	def open_origin(self):   # mail_activity_board
		self.ensure_one()
		vid = self.env[self.res_model].browse(self.res_id).get_formview_id()
		response = {
			'type': 'ir.actions.act_window',
			'res_model': self.res_model,
			'view_mode': 'form',
			'res_id': self.res_id,
			'target': 'current',
			'flags': {
				'form': {
					'action_buttons': False
				}
			},
			'views': [
				(vid, "form")
			]
		}
		return response
	
	@api.model   # mail_activity_board
	def action_activities_board(self):
		action = self.env.ref('aarsol_activity.open_boards_activities').read()[0]
		return action
	
	@api.model  # mail_activity_board
	def _find_allowed_model_wise(self, doc_model, doc_dict):
		doc_ids = list(doc_dict)
		allowed_doc_ids = self.env[doc_model].with_context(active_test=False).search([('id', 'in', doc_ids)]).ids
		return set([message_id for allowed_doc_id in allowed_doc_ids
		    for message_id in doc_dict[allowed_doc_id]])
	
	@api.model  # mail_activity_board
	def _find_allowed_doc_ids(self, model_ids):
		ir_model_access_model = self.env['ir.model.access']
		allowed_ids = set()
		for doc_model, doc_dict in model_ids.items():
			if not ir_model_access_model.check(doc_model, 'read', False):
				continue
			allowed_ids |= self._find_allowed_model_wise(doc_model, doc_dict)
		return allowed_ids
	
	@api.model       # mail_activity_board
	def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
		# Rules do not apply to administrator
		if self._uid == SUPERUSER_ID:
			return super(MailActivity, self)._search(
				args, offset=offset, limit=limit, order=order,
				count=count, access_rights_uid=access_rights_uid)
		
		ids = super(MailActivity, self)._search(
			args, offset=offset, limit=limit, order=order,
			count=False, access_rights_uid=access_rights_uid)
		if not ids and count:
			return 0
		elif not ids:
			return ids
		
		# check read access rights before checking the actual rules
		super(MailActivity, self.sudo(access_rights_uid or self._uid)).check_access_rights('read')
		
		model_ids = {}
		
		self._cr.execute("""
			SELECT DISTINCT a.id, im.id, im.model, a.res_id
			FROM "%s" a
			LEFT JOIN ir_model im ON im.id = a.res_model_id
			WHERE a.id = ANY (%%(ids)s)""" % self._table, dict(ids=ids))
		for a_id, ir_model_id, model, model_id in self._cr.fetchall():
			model_ids.setdefault(model, {}).setdefault(model_id, set()).add(a_id)
		
		allowed_ids = self._find_allowed_doc_ids(model_ids)
		
		final_ids = allowed_ids
		
		if count:
			return len(final_ids)
		else:
			# re-construct a list based on ids, because set didn't keep order
			id_list = [a_id for a_id in ids if a_id in final_ids]
			return id_list


# mail_activity_done
class ResUsers(models.Model):
	_inherit = 'res.users'

	@api.model
	def systray_get_activities(self):
		# Here we totally override the method. Not very nice, but
		# we should perhaps ask Odoo to add a hook here.
		query = """SELECT m.id, count(*), act.res_model as model,
		                CASE
		                    WHEN %(today)s::date -
		                    act.date_deadline::date = 0 Then 'today'
		                    WHEN %(today)s::date -
		                    act.date_deadline::date > 0 Then 'overdue'
		                    WHEN %(today)s::date -
		                    act.date_deadline::date < 0 Then 'planned'
		                END AS states
		            FROM mail_activity AS act
		            JOIN ir_model AS m ON act.res_model_id = m.id
		            WHERE user_id = %(user_id)s
		            AND act.done = False
		            GROUP BY m.id, states, act.res_model;
		            """
		self.env.cr.execute(query, {
		    'today': fields.Date.context_today(self),
		    'user_id': self.env.uid,
		})
		activity_data = self.env.cr.dictfetchall()
		model_ids = [a['id'] for a in activity_data]
		model_names = {n[0]: n[1] for n in self.env['ir.model'].browse(model_ids).name_get()}
		
		user_activities = {}
		for activity in activity_data:
			if not user_activities.get(activity['model']):
				user_activities[activity['model']] = {
				    'name': model_names[activity['id']],
				    'model': activity['model'],
				    'icon': modules.module.get_module_icon(
				        self.env[activity['model']]._original_module),
				    'total_count': 0, 'today_count': 0,
				    'overdue_count': 0, 'planned_count': 0,
				    'type': 'activity',
				}
			user_activities[activity['model']]['%s_count' % activity['states']] += activity['count']
			if activity['states'] in ('today', 'overdue'):
				user_activities[activity['model']]['total_count'] += activity['count']
		
		return list(user_activities.values())
