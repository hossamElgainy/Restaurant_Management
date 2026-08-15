from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RestaurantOrderLine(models.Model):
    _name = 'restaurant.order.line'
    _description = 'Restaurant Order Line'

    order_id = fields.Many2one('restaurant.order')
    item_id = fields.Many2one('restaurant.menu.item',required=True)
    quantity = fields.Float(string='Quantity')
    unit_price = fields.Float(string='Unit Price',readonly=True)
    subtotal = fields.Float(string='Subtotal',readonly=True,compute='_compute_subtotal',store=True)


    @api.depends('quantity','unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price

    @api.onchange('item_id')
    def _onchange_item_id(self):
        if self.item_id:
            self.unit_price = self.item_id.price
        else:
            self.unit_price = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            item_id = vals.get('item_id')

            if item_id:
                item = self.env['restaurant.menu.item'].browse(item_id)
                vals['unit_price'] = item.price

        return super().create(vals_list)

    def write(self, vals):
        if 'item_id' in vals:
            item = self.env['restaurant.menu.item'].browse(vals['item_id'])
            vals['unit_price'] = item.price

        return super().write(vals)

    @api.constrains('quantity')
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(f'Quantity of {line.item_id.name} must be greater than 0')