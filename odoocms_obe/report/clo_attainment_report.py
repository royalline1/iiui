import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time
import logging
_logger = logging.getLogger(__name__)


class CLOAttainmentReport(models.AbstractModel):
    _name = 'report.odoocms_obe.clo_attainment_report'
    _description = 'CLO Attainment Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        class_rec = self.env['odoocms.class'].browse(docsid[0])
        line_ids = []
        if class_rec:
            
            for rec in class_rec.student_ids:
                line = {
                    'student_id' : rec.student_id.id_number,
                    'student_name' : rec.student_id.first_name + " " + rec.student_id.last_name,
                }
                if class_rec.clo_ids:
                    for clo_id in class_rec.clo_ids:
                        obe_summary_rec = self.env['odoocms.activity.obe.summary'].search([('clo_id','=',clo_id.id),('student_id','=',rec.student_id.id),('academic_semester_id','=',class_rec.academic_semester_id.id)])

                        line[clo_id.code.name] =round(obe_summary_rec.percentage,2)
                        if obe_summary_rec.percentage > class_rec.batch_id.clo_kpi:
                            line[clo_id.code.name + "-acheived"] = "Y"

                        else:
                            line[clo_id.code.name + "-acheived"] = "N"

                line_ids.append(line)
        res = {
            'lines': line_ids,
        }
       
        docargs = {
            'date': str(fields.Datetime.now()),
            'class_rec' : class_rec or False,
            'rep_data': res or False,
            'clo_kpi': class_rec.batch_id.clo_kpi or False
        }
        return docargs
