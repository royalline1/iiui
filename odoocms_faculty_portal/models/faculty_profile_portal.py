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
	@http.route(['/my/faculty/profile', '/my/faculty/profile/page/<int:page>'], type='http', auth="user", website=True)
	def portal_faculty_profile(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
		partner = request.env.user.partner_id
		faculty_search= request.env['odoocms.faculty.staff']
		domain = [
			('partner_id','=',partner.id)
		]
		faculty = faculty_search.search(domain)

		return request.render("odoocms_faculty_portal.portal_faculty_profile",{
			'faculty':faculty,

			})