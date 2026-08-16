from odoo import fields, models
class RestaurantMenuCategory(models.Model):
    _name = 'restaurant.menu.category'
    _description = 'Restaurant Menu Category'
    name = fields.Char(required=True)
    item_ids = fields.One2many('restaurant.menu.item', 'category_id',string="Items")