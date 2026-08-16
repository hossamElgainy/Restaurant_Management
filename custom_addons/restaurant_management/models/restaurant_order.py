from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RestaurantOrder(models.Model):
    _name = 'restaurant.order'

    order_no  = fields.Char(string='Order No',readonly=True,default='NEW',required=True,copy=False)
    customer_id = fields.Many2one('res.partner', string='Customer', domain=[('is_restaurant_customer', '=', True)])
    waiter_id = fields.Many2one('res.users', string='Waiter')
    table_id = fields.Many2one('restaurant.table',string='Table')
    order_date = fields.Datetime(string='Order Date',default=fields.Datetime.now,readonly=True,copy=False)
    order_line_ids = fields.One2many('restaurant.order.line', 'order_id', string='Lines')
    total_amount = fields.Float(string='Total Amount',readonly=True, compute='_compute_total_amount',store=True)
    state = fields.Selection([
        ('draft','Draft'),
        ('confirmed','Confirmed'),
        ('preparing','Preparing'),
        ('ready','Ready'),
        ('served','Served'),
        ('paid','Paid'),
        ('cancelled','Cancelled'),
    ],default='draft',required=True,copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            if val.get('order_no','NEW') =='NEW':
                val['order_no'] = self.env['ir.sequence'].next_by_code('restaurant.order') or 'NEW'
        return super().create(vals_list)

    @api.depends('order_line_ids.subtotal')
    def _compute_total_amount(self):
        for order in self:
            order.total_amount =sum(order.order_line_ids.mapped('subtotal'))

    def action_confirm(self):
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError("Only draft orders can be confirmed.")
        if not self.order_line_ids:
            raise ValidationError("Can't Confirm An Empty Order")
        self.state = 'confirmed'

    def action_start_preparing(self):
        self.ensure_one()
        if self.state != 'confirmed':
            raise ValidationError(
                "you can not prepare an order before being confirmed"
            )
        self.state = 'preparing'

    def action_mark_ready(self):
        self.ensure_one()
        if self.state != 'preparing':
            raise ValidationError(
                "you can not mark an order as ready before being prepared."
            )
        self.state = 'ready'

    def action_serve(self):
        self.ensure_one()
        if self.state != 'ready':
            raise ValidationError(
                "you can not serve an order before it has been ready"
            )
        self.state = 'served'

    def action_pay(self):
        self.ensure_one()
        if self.state != 'served':
            raise ValidationError(
                "You can only pay an order that has been served."
            )
        self.state = 'paid'

    def action_cancel(self):
        self.ensure_one()
        if self.state == 'paid':
            raise ValidationError(
                "you can not cancel an order that has been paid."
            )
        self.state = 'cancelled'

    def unlink(self):
        for order in self:
            if order.state != 'draft':
                raise ValidationError(
                    "Only draft orders can be deleted."
                )

        return super().unlink()