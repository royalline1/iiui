from odoo import api, fields, models, _

class SemesterWisePLOAttainmentWiz(models.TransientModel):
    _name = 'semester.wise.plo.attainment.wiz'
    _description = 'Semesters Wise PLO Attainment Wizard'

    program_id = fields.Many2one('odoocms.program', 'Program')
    batch_id = fields.Many2one('odoocms.batch', 'Batch')
    academic_semester_id = fields.Many2one('odoocms.academic.semester')

    @api.multi
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'odoocms.semester.obe.summary',
            'form': data
        }
        return self.env.ref('odoocms_obe.action_report_semester_wise_plo_attainment').with_context(landscape=True).report_action(self, data=datas,config=False)


