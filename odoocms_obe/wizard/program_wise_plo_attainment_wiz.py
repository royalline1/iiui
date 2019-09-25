from odoo import api, fields, models, _


class ProgramWisePLOAttainmentWiz(models.TransientModel):
    _name = 'program.wise.plo.attainment.wiz'
    _description = 'Program Wise PLO Attainment Wizard'

    program_id = fields.Many2one('odoocms.program', 'Program')
    batch_id = fields.Many2one('odoocms.batch', 'Batch')

    @api.multi
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'odoocms.student.obe.summary',
            'form': data
        }
        return self.env.ref('odoocms_obe.action_report_program_wise_plo_attainment').with_context(landscape=True).report_action(self, data=datas,config=False)





