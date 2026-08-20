from odoo import fields, models, api
from odoo.exceptions import ValidationError


class RestaurantPromotion(models.Model):
    _name = 'restaurant.promotion'
    _description = 'Restaurant Promotion'

    name = fields.Char(
        string='Name',
        required=True,
    )

    type = fields.Selection([
        ('percentage', 'Percentage'),
        ('buy_x_get_y', 'Buy X Get Y'),
    ], string='Discount Type', required=True)

    target_type = fields.Selection([
        ('order', 'Entire Order'),
        ('category', 'Category'),
        ('items', 'Specific Items'),
    ], string='Target', required=True)

    category_id = fields.Many2one(
        'restaurant.menu.category',
        string='Category',
    )

    item_ids = fields.Many2many(
        'restaurant.menu.item',
        string='Items',
    )

    discount = fields.Float(
        string='Discount (%)',
    )

    pay = fields.Integer(
        string='Buy Quantity',
    )

    get = fields.Integer(
        string='Get Quantity',
    )

    start_date = fields.Datetime(
        string='Start Date',
    )

    end_date = fields.Datetime(
        string='End Date',
    )
    day_ids = fields.Many2many(
        'restaurant.promotion.day',
        string='Days',
    )

    priority = fields.Integer(
        string='Priority',
        default=10,
    )

    @api.constrains('type', 'discount')
    def _check_percentage_discount(self):
        for promotion in self:
            if promotion.type == 'percentage':
                if promotion.discount <= 0 or promotion.discount > 100:
                    raise ValidationError(
                        'Discount value must be greater than 0 and less than or equal to 100.'
                    )

    @api.constrains('type', 'pay', 'get')
    def _check_buy_x_get_y(self):
        for promotion in self:
            if promotion.type == 'buy_x_get_y':
                if promotion.pay <= 0:
                    raise ValidationError(
                        'Buy quantity must be greater than 0.'
                    )

                if promotion.get <= 0:
                    raise ValidationError(
                        'Get quantity must be greater than 0.'
                    )

    @api.constrains('target_type', 'category_id', 'item_ids')
    def _check_target_type(self):
        for promotion in self:

            if promotion.target_type == 'order':
                if promotion.category_id or promotion.item_ids:
                    raise ValidationError(
                        'An entire order promotion cannot have a category or specific items.'
                    )

            elif promotion.target_type == 'category':
                if not promotion.category_id:
                    raise ValidationError(
                        'Please select a category.'
                    )

                if promotion.item_ids:
                    raise ValidationError(
                        'A category promotion cannot have specific items.'
                    )

            elif promotion.target_type == 'items':
                if not promotion.item_ids:
                    raise ValidationError(
                        'Please select at least one item.'
                    )

                if promotion.category_id:
                    raise ValidationError(
                        'An items promotion cannot have a category.'
                    )

    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        for promotion in self:
            if promotion.start_date and promotion.end_date:
                if promotion.start_date >= promotion.end_date:
                    raise ValidationError(
                        'Start date must be before end date.'
                    )

    @api.constrains('priority')
    def _check_priority(self):
        for promotion in self:
            if promotion.priority < 0:
                raise ValidationError(
                    'Priority must be greater than or equal to 0.'
                )