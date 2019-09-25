from odoo import api, models


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    @api.model
    def get_moodle_options(self):
        opts = ['moodle_options.token', 'moodle_options.server',]
        return self.sudo().search_read([['key', 'in', opts]], ["key", "value"])
