from odoo.http import request
from odoo.addons.portal.controllers.portal import pager as portal_pager, CustomerPortal
import pdb


class CustomerPortal(CustomerPortal):
    # This function to check where this portal user is in faculty model or not. If yes: show links of faculty portal
    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        faculty = request.env['odoocms.faculty.staff']

        faculty_count = faculty.search_count([('partner_id','=', partner.id)])
        values.update({
            'faculty_count': faculty_count,
        })
        return values