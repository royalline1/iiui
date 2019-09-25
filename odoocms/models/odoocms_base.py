import pdb
import calendar
from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class OdooCMSBuilding(models.Model):
    _name = 'odoocms.building'
    _description = "Building"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence desc'

    name = fields.Char('Name')
    code = fields.Char('Code')  #abbreviation
    sequence = fields.Integer('Sequence')
    externalId = fields.Char('Ecternal ID')
    locationX = fields.Float('Location X')
    locationY = fields.Float('Location Y')
    unitime_id = fields.Integer()


class OdooCMSRoomType(models.Model):
    _name = 'odoocms.room.type'
    _description = "Room Type"

    name = fields.Char('Name')
    code = fields.Char('Code')
    type = fields.Selection([('Room','Room'),('Other','Other')],'Room Type',default='Room')
    unitime_id = fields.Integer()
    

class OdooCMSRoom(models.Model):
    _name = 'odoocms.room'
    _description = "Class Room"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence desc'
    
    name = fields.Char('Display Name')
    code = fields.Char('Room Number')  #roomNumber
    building_id = fields.Many2one('odoocms.building','Building')
    room_type = fields.Many2one('odoocms.room.type','Room Type')  #domain Room
    sequence = fields.Integer('Sequence')
    capacity = fields.Integer('Capacity')
    examCapacity = fields.Integer('Exam Capacity')
    externalId = fields.Char('Ecternal ID')
    locationX = fields.Float('Location X',help='X Coordinates')
    locationY = fields.Float('Location Y',help='Y Coordinates')
    area = fields.Float('Area',help='Square Feet')
    controlDepartment = fields.Many2one('odoocms.department','Control Department')
    eventDepartment = fields.Many2one('odoocms.department','Event Department')
    instructional = fields.Boolean('Instructional')
    roomClassification = fields.Char('Classification')
    scheduledRoomType = fields.Selection([('computingLab','computingLab'),('departmental','departmental'),('genClassroom','genClassroom')],'Room Type')
    eventNote = fields.Text('Event Note')
    roomSharingNote = fields.Text('Room Sharing Note')
    
    feature_ids = fields.One2many('odoocms.room.feature', 'class_room_id', string='Class Amenities')
    
    def sync_unitime_odoo(self, rooms):
        for room in rooms:
            extra = room['extra']
            del room['extra']
            
            if extra.get('building',False):
                building = extra.get('building',False)
                building_data = {
                    'unitime_id': building.get('id',False),
                    'code': building.get('abbreviation',False),
                    'name': building.get('Purdue Village Apts #113'),
                    'locationX': building.get('x',False),
                    'locationY': building.get('y',False),
                    'externalId': building.get('externalId',False),
                }
                building = self.env['odoocms.building'].search([('code', '=', building_data['code'])])
                if not building:
                    building = self.env['odoocms.building'].create(building_data)
                else:
                    building.write(building_data)
                room['building_id'] = building.id
                
            if extra.get('roomType',False):
                roomType = extra.get('roomType',False)
                roomType_data = {
                    'unitime_id': roomType.get('id',False),
                    'code': roomType.get('reference',False),
                    'name': roomType.get('label',False),
                }
                rtype = self.env['odoocms.room.type'].search([('unitime_id', '=', roomType_data['unitime_id'])])
                if not rtype:
                    rtype = self.env['odoocms.room.type'].create(roomType_data)
                else:
                    rtype.write(roomType_data)
                room['room_type'] = rtype.id
         
            if room.get('eventDepartment',False):
                room['eventDepartment'] = self.env['odoocms.department'].search([('code','=',room['eventDepartment']['code'])])
            pattern = self.env['odoocms.room'].search([('code', '=', room['code'])])
            if not pattern:
                pattern = self.env['odoocms.room'].search([('name', '=', room['name'])])
            if not pattern:
                pattern = self.env['odoocms.room'].create(room)
            else:
                pattern.write(room)
                
            if extra.get('features',False):
                features = extra.get('features',False)
                for feature in features:
                    feature_data = {
                        'unitime_id': feature.get('id',False),
                        'code': feature.get('abbv',False),
                        'name': feature.get('label',False),
                    }
                amenities = self.env['odoocms.amenities'].search([('unitime_id', '=', feature_data['unitime_id'])])
                if not amenities:
                    amenities = self.env['odoocms.amenities'].create(feature_data)
                else:
                    amenities.write(feature_data)
                
                feature_id = self.env['odoocms.room.feature'].search([('name','=',amenities.id),('class_room_id','=',pattern.id)])
                if not feature_id:
                    self.env['odoocms.room.feature'].create({
                        'name': amenities.id,
                        'class_romm_id': pattern.id
                    })
                


class OdooCMSRoomFeature(models.Model):
    _name = 'odoocms.room.feature'
    _description = "Amenities in Class"
    
    name = fields.Many2one('odoocms.amenities', string="Amenities", help="Select the amenities in Class Room")
    qty = fields.Float(string='Quantity', help="The quantity of the amenities", default=1.0)
    class_room_id = fields.Many2one('odoocms.room', string="Class Room")
    
    @api.constrains('qty')
    def check_qty(self):
        for rec in self:
            if rec.qty <= 0:
                raise ValidationError(_('Quantity must be Positive'))


class OdooCMSAmenities(models.Model):
    _name = 'odoocms.amenities'
    _description = 'Amenities in Institution'
    _order = 'name asc'
    _rec_name = 'name'
    
    name = fields.Char(string='Name', required=True, help='Name of Amenity')
    code = fields.Char(string='Code', help='Code of Amenity')
    unitime_id = fields.Integer()
    
    _sql_constraints = [
        ('code', 'unique(code)', "Another Amenity already exists with this code!"),
    ]

class OdooCMSInstitute(models.Model):
    _inherit = 'res.company'

    affiliation = fields.Char(string='Affiliation')
    register_num = fields.Char(string='Register')
    signature = fields.Binary('Signature')
    accreditation = fields.Text('Accreditation')
    approval_authority = fields.Text('Approval Authority')


class OdooCMSReligion(models.Model):
    _name = 'odoocms.religion'
    _description = 'Religion'

    name = fields.Char(string="Religion", required=True)
    code = fields.Char(string="Code", required=True)


class OdooCMSDomicile(models.Model):
    _name = 'odoocms.domicile'
    _description = 'Domicile'

    name = fields.Char(string="Domicile Region", required=True)
    code = fields.Char(string="Code", required=True)
    
    
class IrModelData(models.Model):
    _inherit = 'ir.model.data'

    @api.multi
    def name_get(self):
        #model_id_name = defaultdict(dict)  # {res_model: {res_id: name}}
        #for xid in self:
        #    model_id_name[xid.model][xid.res_id] = None
        #
        # fill in model_id_name with name_get() of corresponding records
        #for model, id_name in model_id_name.items():
        #    try:
        #        ng = self.env[model].browse(id_name).name_get()
        #        id_name.update(ng)
        #    except Exception:
        #        pass
    
        # return results, falling back on complete_name
        #return [(xid.id, model_id_name[xid.model][xid.res_id] or xid.complete_name)
        #        for xid in self]

        return [(xid.id, xid.complete_name) for xid in self]