import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class ReceiptReceivedDetailReport(models.AbstractModel):
    _name = 'report.odoocms_fee.receipt_received_detail_report'
    _description = 'Receipt Received Detail Report'

    @api.model
    def _get_report_values(self, docsid, data=None):

        date_from = data['form']['date_from'] and data['form']['date_from'] or False
        date_to = data['form']['date_to'] and data['form']['date_to'] or False

        invoice = self.env['account.invoice'].search([])
        total_amount = 0

        if date_from and date_to:
            date_from = fields.Date.from_string(date_from)
            date_to = fields.Date.from_string(date_to)
            if date_from >= date_to:
                raise ValidationError(_('Start Date must be Anterior to End Date'))
            else:
                invoice = self.env['account.invoice'].search([('date_invoice','>=',date_from),('date_invoice','<=',date_to),('state','=','paid')])

        for inv in invoice:
            total_amount += inv.amount_total

        report = self.env['ir.actions.report']._get_report_from_name('odoocms_fee.receipt_received_detail_report')
        docargs = {
            'doc_ids': [],
            'doc_model': report.model,
            'data': data['form'],
            'invoice': invoice or False,
            'total_amount': total_amount or False,
            'date_from': date_from or False,
            'date_to': date_to or False,
        }
        return docargs
