from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import pdb


class OdooCMSAdmissionRegister(models.Model):
    _name = "odoocms.admission.register"
    _description = "Admission Register"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', required=True, readonly=True, states={'draft': [('readonly', False)]})
    academic_session_id = fields.Many2one('odoocms.academic.session','Academic Session', required=True)
    academic_semester_id = fields.Many2one('odoocms.academic.semester','Academic Term', required=True)
    career_id = fields.Many2one('odoocms.career', 'Career',required=True)
    date_start = fields.Date('Start Date', readonly=True, default=fields.Date.today(), states={'draft': [('readonly', False)]})
    date_end = fields.Date('End Date', readonly=True, default=(fields.Date.today() + relativedelta(days=30)),
        states={'draft': [('readonly', False)]})
    
    application_ids = fields.One2many('odoocms.application', 'register_id', 'Admissions')
    program_ids = fields.Many2many('odoocms.program','register_program_rel','register_id','program_id','Offered Programs')
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirmed'),
         ('cancel', 'Cancelled'), ('application', 'Application Gathering'), ('sort','Sort List'),
         ('admission', 'Admission Process'), ('merit','Merit'),('done', 'Done')],
        'Status', default='draft', track_visibility='onchange')

    allocation_id = fields.Many2one('odoocms.admission.allocation','Quota Allocation')
    merit_register_id = fields.Many2one('odoocms.merit.register','Merit Register')
    first_merit_register_id = fields.Many2one('odoocms.merit.register','First Merit Register')
    merit_register_ids = fields.One2many('odoocms.merit.register','register_id','Merit Registers')
    
    def sort_applications(self):
        i = 1
        for application in self.application_ids.sorted(key=lambda r: r.merit_score, reverse=True):
            application.merit_number = i
            i += 1
        
    def merit_list(self, merit_register, schedule_lines):
        allocation_id = self.env['odoocms.admission.allocation'].search([('academic_session_id','=',self.academic_session_id.id),('career_id','=',self.career_id.id)])
        cnt = 1
        for application in self.application_ids.filtered(lambda l: l.state in ('approve','open')).sorted(key=lambda r: r.merit_number):
            if application.locked:
                quota_line = allocation_id.seat_ids.filtered(lambda k: k.program_id.id == application.program_id.id)
                prg_merit_cnt = self.env['odoocms.application.merit.line'].search_count([
                    ('merit_register_id', '=', merit_register.id), ('program_id', '=', application.program_id.id)
                ])
                merit_lines = []
                merit_line = {
                    'program_id': application.program_id.id,
                    'preference': application.preference,
                    'program_merit_number': prg_merit_cnt + 1,
                    'seats': quota_line.seats,
                    'selected': True,
                }
                merit_lines.append([0, 0, merit_line])
                merit_ids = application.merit_ids
                data = {
                    'register_id': self.id,
                    'application_id': application.id,
                    'program_id': application.program_id.id,
                    'preference': application.preference,
                    'merit_register_id': merit_register.id,
                    'merit_number': application.merit_number,
                    'program_merit_number': prg_merit_cnt + 1,
                    'date_interview': False,
                    'state': 'done',
                    'locked': True,
                    'line_ids': merit_lines,
                }
                app_merit = self.env['odoocms.application.merit'].create(data)
                if merit_ids:
                    merit_ids[0].next_merit_app_id = app_merit.id
                    app_merit.prev_merit_app_id = merit_ids[0].id
                    
            else:
                schedule = schedule_lines.filtered(lambda l: l.serial_start <= cnt and l.serial_end >= cnt)
                
                merit_lines = []
                for preference in application.preference_ids.sorted(key=lambda r: r.preference):
                    quota_line = allocation_id.seat_ids.filtered(lambda k: k.program_id.id == preference.program_id.id)
                    if not quota_line:
                        raise ValidationError(_("Seats not defined for %s-%s-%s" % (preference.program_id.name,application.name,application.id)))
                    
                    prg_merit_cnt = self.env['odoocms.application.merit.line'].search_count([
                        ('merit_register_id','=',merit_register.id),('program_id','=',preference.program_id.id)
                    ])
                    merit_line = {
                        # 'application_merit_id':
                        'program_id': preference.program_id.id,
                        'preference': preference.preference,
                        'program_merit_number': prg_merit_cnt + 1,
                        'seats': quota_line.seats,
                        'selected': prg_merit_cnt < quota_line.seats,
                    }
                    merit_lines.append([0,0,merit_line])
                    if prg_merit_cnt < quota_line.seats:
                        merit_ids = application.merit_ids
                        data = {
                            'register_id': self.id,
                            'application_id': application.id,
                            'program_id': preference.program_id.id,
                            'preference': preference.preference,
                            'merit_register_id': merit_register.id,
                            'merit_number': application.merit_number,
                            'program_merit_number': prg_merit_cnt + 1,
                            'date_interview': schedule and schedule.date_interview or False,
                            'line_ids': merit_lines,
                        }
                        app_merit = self.env['odoocms.application.merit'].create(data)
                        if merit_ids:
                            merit_ids[0].next_merit_app_id = app_merit.id
                            app_merit.prev_merit_app_id = merit_ids[0].id
                        
                        application.program_id = preference.program_id.id
                        application.preference = preference.preference
                        app_merit.amount = application._get_fee_amount()
                        cnt += 1
                        break
                    
        self.state = 'merit'

    @api.multi
    @api.constrains('date_start', 'date_end')
    def check_dates(self):
        for record in self:
            start_date = fields.Date.from_string(record.date_start)
            end_date = fields.Date.from_string(record.date_end)
            if start_date > end_date:
                raise ValidationError(
                    _("End Date cannot be set before Start Date."))

    @api.multi
    def confirm_register(self):
        self.state = 'confirm'

    @api.multi
    def set_to_draft(self):
        self.state = 'draft'

    @api.multi
    def cancel_register(self):
        self.state = 'cancel'

    @api.multi
    def start_application(self):
        self.state = 'application'

    @api.multi
    def stop_application(self):
        self.state = 'sort'

    @api.multi
    def start_admission(self):
        self.sort_applications()
        self.state = 'admission'

    
