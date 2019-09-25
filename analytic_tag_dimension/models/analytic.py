from lxml import etree
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
import pdb
import json


class AccountAnalyticDimension(models.Model):
    _name = 'account.analytic.dimension'
    _description = 'Analytic Dimension'

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    analytic_tag_ids = fields.One2many('account.analytic.tag','analytic_dimension_id', string='Analytic Tags')
    account_ids = fields.Many2many('account.account','analytic_dimension_account_rel','nd_id','account_id',"Related Accounts")

    @api.model
    def create(self, values):
        if ' ' in values.get('code'):
            raise ValidationError(_("Code can't contain spaces!"))
        model_names = (
            'account.move.line',
            'account.analytic.line',
            'account.invoice.line',
            'account.invoice.report',
        )
        _models = self.env['ir.model'].search([
            ('model', 'in', model_names),
        ])
        _models.write({
            'field_id': [(0, 0, {
                'name': 'x_dimension_{}'.format(values.get('code')),
                'field_description': values.get('name'),
                'ttype': 'many2one',
                'relation': 'account.analytic.tag',
            })],
        })
        return super().create(values)


class AccountAnalyticTag(models.Model):
    _inherit = 'account.analytic.tag'

    analytic_dimension_id = fields.Many2one('account.analytic.dimension', string='Dimension')

    @api.multi
    @api.depends('name','analytic_dimension_id')	
    def name_get(self):
        result = []
        for tag in self:
            name = tag.name
            if tag.analytic_dimension_id:
                name = tag.analytic_dimension_id.name + '-' + name
            result.append((tag.id, name))
        return result 

    @api.multi
    def get_dimension_values(self):
        values = {}
        for tag in self.filtered('analytic_dimension_id'):
            code = tag.analytic_dimension_id.code
            values.update({
                'x_dimension_%s' % code: tag.id,
            })
        return values

    def _check_analytic_dimension(self):
        tags_with_dimension = self.filtered('analytic_dimension_id')
        dimensions = tags_with_dimension.mapped('analytic_dimension_id')
        if len(tags_with_dimension) != len(dimensions):
            raise ValidationError(_("You can not set two tags from same dimension."))


class AnalyticDimensionLine(models.AbstractModel):
    _name = 'analytic.dimension.line'
    _description = 'Dimension Line'
    _analytic_tag_field_name = 'analytic_tag_ids'

    @api.multi
    def _handle_analytic_dimension(self):
        for adl in self:
            tag_ids = adl[self._analytic_tag_field_name]
            tag_ids._check_analytic_dimension()
            dimension_values = tag_ids.get_dimension_values()
            super(AnalyticDimensionLine, adl).write(dimension_values)

    @api.model
    def create(self, values):
        result = super(AnalyticDimensionLine, self).create(values)
        if values.get(result._analytic_tag_field_name):
            result._handle_analytic_dimension()
        return result

    @api.multi
    def write(self, values):
        result = super(AnalyticDimensionLine, self).write(values)
        if values.get(self._analytic_tag_field_name):
            self._handle_analytic_dimension()
        return result


class AccountAccount(models.Model):
    _inherit = 'account.account'

    nd_ids = fields.Many2many('account.analytic.dimension','analytic_dimension_account_rel','account_id','nd_id','Related Dimension')


class AccountAnalyticLine(models.Model):
    _name = 'account.analytic.line'
    _inherit = ['analytic.dimension.line', 'account.analytic.line']
    _analytic_tag_field_name = 'tag_ids'


class AccountMoveLine(models.Model):
    _name = 'account.move.line'
    _inherit = ['analytic.dimension.line', 'account.move.line']
    _analytic_tag_field_name = 'analytic_tag_ids'
    
    def _get_tag_domain(self):
        domain = [('id','=',1)]
        if self.account_id:
            nd_ids = self.analytic_tag_ids.mapped('analytic_dimension_id')
            if self.account_id.nd_ids:
                rem_nd_ids = self.account_id.nd_ids - nd_ids
                domain = [
                    ('analytic_dimension_id', 'in', rem_nd_ids.ids),
                ]
            else:
                domain = [
                    ('analytic_dimension_id', '=', False),
                ]
        else:
            domain = [
                ('analytic_dimension_id', '=', False),
            ]
        return domain
    
    @api.onchange('account_id','analytic_tag_ids')
    def onchange_account_id_tag_id(self):
        for line in self:
            if line.account_id:
                nd_ids = line.analytic_tag_ids.mapped('analytic_dimension_id')
                if line.account_id.nd_ids:
                    rem_nd_ids = line.account_id.nd_ids - nd_ids
                    return {
                        'domain': {'analytic_tag_ids': [
                            ('analytic_dimension_id', 'in', rem_nd_ids.ids),
                        ]}
                    }
                else:
                    return {
                        'domain': {'analytic_tag_ids': [
                            ('analytic_dimension_id', '=', False),
                        ]}
                    }

    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags',
        domain=lambda self: self._get_tag_domain())


class AccountInvoiceLine(models.Model):
    _name = 'account.invoice.line'
    _inherit = ['analytic.dimension.line', 'account.invoice.line']
    _analytic_tag_field_name = 'analytic_tag_ids'

