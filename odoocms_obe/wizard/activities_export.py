import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date , datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time

import logging
_logger = logging.getLogger(__name__)

from io import StringIO
import io

try:
	import xlwt
except ImportError:
	_logger.debug('Cannot `import xlwt`.')

try:
	import cStringIO
except ImportError:
	_logger.debug('Cannot `import cStringIO`.')

try:
	import base64
except ImportError:
	_logger.debug('Cannot `import base64`.')
	

def str_to_datetime(strdate):
	return datetime.datetime.strptime(strdate, tools.DEFAULT_SERVER_DATE_FORMAT)


class ActivitiesExport(models.TransientModel):
	_name = 'odoocms.activies.export.wizard'
	_description = 'Activities Export Wizard'

	@api.multi
	def make_excel(self):
		workbook = xlwt.Workbook(encoding="utf-8")
		worksheet = workbook.add_sheet("Assessment Report")

		style_title = xlwt.easyxf("font:height 300; font: name Liberation Sans, bold on,color black; align: horiz center;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour cyan_ega;")
		style_table_header = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour cyan_ega;")
		style_table_header2 = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour silver_ega;alignment: wrap True;")
		style_table_totals = xlwt.easyxf("font:height 150; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour cyan_ega;")
		style_date_col = xlwt.easyxf("font:height 180; font: name Liberation Sans,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")
		style_product_header = xlwt.easyxf("font:height 200; font: name Liberation Sans,bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;pattern: pattern solid, fore_colour silver_ega;")
		style_table_totals2 = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz left;borders: left thin, right thin, top thin, bottom thin;")
		style_clo_col1 = xlwt.easyxf("font:height 180; font: name Liberation Sans,color black; align:horiz center;borders: left thin, right thin, top thin, bottom thin;")
		style_clo_col2 = xlwt.easyxf("font:height 150; font: name Liberation Sans,color black; align:horiz center;borders: left thin, right thin, top thin, bottom thin;")
		style_clo_col_rotation = xlwt.easyxf("font:height 160; font: name Liberation Sans,bold on,color black; align:rotation 90,horiz center,vertical center;borders: left thin, right thin, top thin, bottom thin;")
		style_clo_col_rotation1 = xlwt.easyxf("font:height 150; font: name Liberation Sans,bold on,color black; align:rotation 90,horiz center;borders: left thin, right thin, top thin, bottom thin;")
		
		search_class = self.env['odoocms.class'].search([('id', '=', self.env.context['active_id'])])
		
		worksheet.write_merge(0, 1, 0, 0, search_class.name, style=style_table_header2)
		worksheet.write(2, 0, search_class.code, style=style_table_header2)
		
		worksheet.write(0, 1,"Assessment Type", style= style_table_header)
		worksheet.write(1, 1,"Assessment Name", style= style_table_header)
		worksheet.write(2, 1,"Assessment Code", style= style_table_header)
		worksheet.write(3, 1,"Max Marks", style= style_table_header)
		worksheet.write(4, 1,"Value (OBE)", style= style_table_header)
		worksheet.write(5, 1,"CLOs", style= style_table_header)
		worksheet.write(6, 1, "Date", style=style_table_header)
		worksheet.write(7, 0,"Reg No", style= style_table_header)
		worksheet.write(7, 1,"Name", style= style_table_header)

		row = 0
		col = 2
		worksheet.col(0).width = 256 * 25
		worksheet.col(1).width = 256 * 30


		search_activities =self.env['odoocms.exam.activity'].search([('class_id','=',self.env.context['active_id'])])
		if search_activities:
			for ac in search_activities:
				worksheet.write(0, col,ac.activity_class_id.activity_type_id.name,style=style_date_col)
				worksheet.write(1, col,ac.name,style=style_date_col)
				worksheet.write(2, col,ac.code,style=style_date_col)
				worksheet.write(3, col,ac.max_marks,style=style_date_col)
				worksheet.write(4, col,ac.obe_weightage,style=style_date_col)
				worksheet.write(5, col,ac.clo_id.code.name,style=style_date_col)
				col +=1
		else:
			search_activities = self.env['odoocms.exam.activity.class'].search([('class_id', '=', self.env.context['active_id'])])
			for ac in search_activities:
				worksheet.write(0, col, ac.activity_type_id.name, style=style_date_col)
				col += 1


		row_st = 8
		col_st = 0
		search_students =self.env['odoocms.student.subject'].search([('class_id','=',self.env.context['active_id'])])
		for st in search_students:
			worksheet.write(row_st, 0,st.student_id.id_number,style=style_date_col)
			worksheet.write(row_st, 1,st.student_id.name,style=style_date_col)
			row_st +=1


		file_data = io.BytesIO()
		workbook.save(file_data)
		wiz_id = self.env['assessment.report.save.wizard'].create({
			'data': base64.encodestring(file_data.getvalue()),
			'name': 'Assessment.xls'
		})

		return {
			'type': 'ir.actions.act_window',
			'name': 'Assessment Sheet',
			'res_model': 'assessment.report.save.wizard',
			'view_mode': 'form',
			'view_type': 'form',
			'res_id': wiz_id.id,
			'target': 'new'
		}

	
class assessment_report_save_wizard(models.TransientModel):
	_name = "assessment.report.save.wizard"
	_description = 'Assessment Report Wizard'
	
	name = fields.Char('filename', readonly=True)
	data = fields.Binary('file', readonly=True)


		








