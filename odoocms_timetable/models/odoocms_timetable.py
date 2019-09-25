from odoo import models, fields, api, _
from . import aarsol_unitime
import pdb

class OdooCMSTimeTable(models.Model):
    _name = 'odoocms.timetable'
    _description = 'Timetable'

    program_id = fields.Many2one('odoocms.program', string='Program', required=True)
    batch_id = fields.Many2one('odoocms.batch','Batch',required=True)
    section_id = fields.Many2one('odoocms.batch.section','Section',required=True)
    academic_semester_id = fields.Many2one('odoocms.academic.semester', string='Academic Term', required=True)
    
    active = fields.Boolean('Active', default=True)
    name = fields.Char(compute='_get_name',store=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get())
    
    
    timetable_mon = fields.One2many('odoocms.timetable.schedule', 'timetable_id', domain=[('week_day', '=', '0')])
    timetable_tue = fields.One2many('odoocms.timetable.schedule', 'timetable_id', domain=[('week_day', '=', '1')])
    timetable_wed = fields.One2many('odoocms.timetable.schedule', 'timetable_id', domain=[('week_day', '=', '2')])
    timetable_thu = fields.One2many('odoocms.timetable.schedule', 'timetable_id', domain=[('week_day', '=', '3')])
    timetable_fri = fields.One2many('odoocms.timetable.schedule', 'timetable_id', domain=[('week_day', '=', '4')])
    timetable_sat = fields.One2many('odoocms.timetable.schedule', 'timetable_id', domain=[('week_day', '=', '5')])
    timetable_sun = fields.One2many('odoocms.timetable.schedule', 'timetable_id', domain=[('week_day', '=', '6')])
    
    @api.depends('batch_id','section_id','academic_semester_id')
    def _get_name(self):
        for rec in self:
             if rec.batch_id and rec.section_id and rec.academic_semester_id:
                rec.name = rec.batch_id.name + " (" + rec.section_id.name  + ")" + " /" + rec.academic_semester_id.name


class OdooCMSTimeTableSchedule(models.Model):
    _name = 'odoocms.timetable.schedule'
    _description = 'Timetable Schedule'
    _rec_name = 'period_id'

    period_id = fields.Many2one('odoocms.time.pattern', string="Period", required=True,)
    time_from = fields.Float(string='From', required=True, index=True, help="Start and End time of Period.")
    time_to = fields.Float(string='To', required=True)
    subject_id = fields.Many2one('odoocms.class', string='Subject', required=True)
    faculty_id = fields.Many2one('odoocms.faculty.staff', string='Faculty', related='subject_id.faculty_staff_id',store=True)
    week_day = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ], 'Week', required=True)
    building_id = fields.Many2one('odoocms.building', 'Building')
    room_id = fields.Many2one('odoocms.room','Room')
    timetable_id = fields.Many2one('odoocms.timetable', required=True,)
    active = fields.Boolean('Active', related='timetable_id.active',store=True)
    
    #@api.onchange('period_id')
    #def onchange_period_id(self):
    #    for i in self:
    #        i.time_from = i.period_id.time_from
    #        i.time_till = i.period_id.time_to


class OdooCMSTimePattern(models.Model):
    _name = 'odoocms.time.pattern'
    _description = 'Time Pattern'

    name = fields.Char(string="Name", required=True,)
    #uniId = fields.Integer('Unitime ID')
    nbrMeetings = fields.Integer("No. of Meetings")
    minsPerMeeting = fields.Integer("Minutes Per Meeting")
    type = fields.Selection([('Standard', 'Standard'), ('Morning', 'Morning'), ('Evening', 'Evening'), ('Extended','Extended'),
        ('Saturday', 'Saturday'), ('Exact Time', 'Exact Time')], 'Type', default='Standard')
    visible = fields.Boolean('Visible')
    nbrSlotsPerMeeting = fields.Integer('Slots per Meeting')
    breakTime = fields.Integer('Break Time')
    pattern_days = fields.One2many('odoocms.time.pattern.days','pattern_id','Pattern Days')
    pattern_times = fields.One2many('odoocms.time.pattern.time','pattern_id','Pattern Times')
    #session_id = constraint `fk_time_pattern_session` foreign key (`session_id`) references `sessions` (`uniqueid`) on delete cascade

    def sync_unitime_odoo(self,timePatterns):
        for timePattern in timePatterns:
            data = {
                'name': timePattern['name'],
                'nbrMeetings': timePattern['nbrMeetings'],
                'minsPerMeeting': timePattern['minsPerMeeting'],
                'type': timePattern['type'],
                'visible': timePattern['visible'],
                'nbrSlotsPerMeeting': timePattern['nbrSlotsPerMeeting'],
                'breakTime': timePattern['breakTime'],
            }
            pattern = self.env['odoocms.time.pattern'].search([('name','=',timePattern['name'])])
            if pattern:
                pattern.write(data)
            else:
                pattern = self.env['odoocms.time.pattern'].create(data)
                
            # Days
            for days in timePattern['days']:
                daydata = {
                    'code': days['code'],
                    'pattern_id': pattern.id,
                }
                patternDay = self.env['odoocms.time.pattern.days'].search([('pattern_id', '=', pattern.id),('code', '=', days['code'])])
                if patternDay:
                    patternDay.write(daydata)
                else:
                    patternDay = self.env['odoocms.time.pattern.days'].create(daydata)

            # Slots
            for slot in timePattern['time']:
                timedata = {
                    'start': slot['start'],
                    'pattern_id': pattern.id,
                }
                patternSlot = self.env['odoocms.time.pattern.time'].search([('pattern_id', '=', pattern.id),('start', '=', slot['start'])])
                if patternSlot:
                    patternSlot.write(timedata)
                else:
                    patternSlot = self.env['odoocms.time.pattern.time'].create(timedata)
                    

class OdooCMSTimePatternDays(models.Model):
    _name = 'odoocms.time.pattern.days'
    _description = 'Time Pattern Days'
    
    code = fields.Char('Day Code')
    pattern_id = fields.Many2one('odoocms.time.pattern', 'Pattern', ondelete='cascade')
    #uniId = fields.Integer('Unitime ID')
    #uni_pattern_id = fields.Integer('Unitime Pattern')


class OdooCMSTimePatternTime(models.Model):
    _name = 'odoocms.time.pattern.time'
    _description = 'Time Pattern Time'
    
    start = fields.Char('Slot Start')
    pattern_id = fields.Many2one('odoocms.time.pattern', 'Pattern', ondelete='cascade')
    #uniId = fields.Integer('Unitime ID')
    #uni_pattern_id = fields.Integer('Unitime Pattern')


class OdooCMSDatePattern(models.Model):
    _name = 'odoocms.date.pattern'
    _description = 'Date Pattern'

    name = fields.Char(string="Name", required=True,)
    type = fields.Selection([('Standard', 'Standard'), ('Non-standard', 'Non-standard'), ('Extended','Extended'), ('Alternate Weeks', 'Alternate Weeks'),
        ('Saturday', 'Saturday'), ('Exact Time', 'Exact Time')], 'Type', default='Standard')
    visible = fields.Boolean('Visible')
    default = fields.Boolean('Default')
    pattern_dates = fields.One2many('odoocms.date.pattern.dates','pattern_id','Pattern Dates')
    #pattern, offset

    def sync_unitime_odoo(self, datePatterns):
        for datePattern in datePatterns:
            data = {
                'name': datePattern['name'],
                'type': datePattern['type'],
                'visible': datePattern['visible'],
                'default': datePattern['default'],
            }
            pattern = self.env['odoocms.date.pattern'].search([('name', '=', datePattern['name'])])
            if pattern:
                pattern.write(data)
            else:
                pattern = self.env['odoocms.date.pattern'].create(data)
        
            # Dates
            for date in datePattern['dates']:
                datedata = {
                    'fromDate': date['fromDate'],
                    'toDate': date['toDate'],
                    'pattern_id': pattern.id,
                }
                patternDate = self.env['odoocms.date.pattern.dates'].search(
                    [('pattern_id', '=', pattern.id), ('fromDate', '=', date['fromDate']), ('toDate', '=', date['toDate'])])
                if patternDate:
                    patternDate.write(datedata)
                else:
                    patternDate = self.env['odoocms.date.pattern.dates'].create(datedata)


class OdooCMSDatePatternDates(models.Model):
    _name = 'odoocms.date.pattern.dates'
    _description = 'Date Pattern Dates'
    
    fromDate = fields.Date('From Date')
    toDate = fields.Date('To Date')
    pattern_id = fields.Many2one('odoocms.date.pattern', 'Pattern', ondelete='cascade')
    

class OdooCmsDepartment(models.Model):
    _inherit = 'odoocms.department'

    externalId = fields.Char('External ID')
    abbreviation = fields.Char('Abbreviation')
    event_mgmt = fields.Boolean('Event Management')
    external_manager = fields.Boolean('External Manager')
    external_manager_name = fields.Char('External Manager Name')
    external_manager_abbreviation = fields.Char('External Manager Abbreviation')

    def sync_unitime_odoo(self, departments):
        for department in departments:
            data = {
                'name': department['name'],
                'code': department['code'],
                'externalId': department['externalId'],
                'abbreviation': department['abbreviation'],
                'event_mgmt': department.get('event_mgmt',False),
                'external_manager': department.get('external_manager',False),
                'external_manager_name': department.get('external_manager_name',''),
                'external_manager_abbreviation': department.get('external_manager_abbreviation','')
            }
            pattern = self.env['odoocms.department'].search([('code', '=', department['code'])])
            if pattern:
                pattern.write(data)
            else:
                pattern = self.env['odoocms.department'].create(data)
