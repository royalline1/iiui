
from odoo import fields, models, api


class OdooCmsProvince(models.Model):
    _name = 'odoocms.province'
    _description = 'Province'

    country_id = fields.Many2one('res.country', string="Country")
    name = fields.Char('Province Name',size=32, required=True)
    code = fields.Char('Code', size=8, required=True)
    district_ids = fields.One2many('odoocms.district', 'province_id', string="Districts")


class OdooCmsDistrict(models.Model):
    _name = 'odoocms.district'
    _description = 'District'

    province_id = fields.Many2one('odoocms.province', string="Province")
    name = fields.Char('District Name',size=32, required=True)
    code = fields.Char('Code', size=8, required=True)

