
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RestaurantTable(models.Model):
    _name = 'restaurant.table'
    _description = 'Restaurant Table'

    name = fields.Char(required=True)
    capacity = fields.Integer(required=True)
    location = fields.Char(required=True)

    @api.constrains('capacity')
    def _check_capacity(self):
        for table in self:
            if table.capacity <= 0:
                raise ValidationError('Capacity must be greater than 0')
