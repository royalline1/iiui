# -*- coding: utf-8 -*-
from odoo import http

# class Moodle(http.Controller):
#     @http.route('/moodle/moodle/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/moodle/moodle/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('moodle.listing', {
#             'root': '/moodle/moodle',
#             'objects': http.request.env['moodle.moodle'].search([]),
#         })

#     @http.route('/moodle/moodle/objects/<model("moodle.moodle"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('moodle.object', {
#             'object': obj
#         })