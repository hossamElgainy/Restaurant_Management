from odoo import api,models,fields
class RestaurantPromotionDay(models.Model):
    _name = 'restaurant.promotion.day'
    _description = 'Promotion Day'

    name = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ], required=True)