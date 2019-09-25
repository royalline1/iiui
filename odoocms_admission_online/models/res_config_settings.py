# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auth_signup_way_entry = fields.Boolean(string='Enable SignUp With Entry ID', config_parameter='auth_signup.way_entryID')
    auth_signup_cnic_phone = fields.Boolean(string='Enable SignUp With CNIC And Phone',
                                           config_parameter='auth_signup.way_CNICPhone')
    
