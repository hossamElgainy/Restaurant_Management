from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RestaurantOrder(models.Model):
    _name = 'restaurant.order'
    _description = 'Restaurant Order'

    order_no = fields.Char(string='Order No', readonly=True, default='NEW', required=True, copy=False)
    customer_id = fields.Many2one('res.partner', string='Customer', domain=[('is_restaurant_customer', '=', True)])
    waiter_id = fields.Many2one('res.users', string='Waiter')
    table_id = fields.Many2one('restaurant.table', string='Table')
    order_date = fields.Datetime(string='Order Date', default=fields.Datetime.now, readonly=True, copy=False)
    order_line_ids = fields.One2many('restaurant.order.line', 'order_id', string='Lines')
    payment_ids = fields.One2many('restaurant.payment', 'order_id', string='Payments')

    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id)
    subtotal = fields.Monetary(string='Subtotal', currency_field='currency_id', readonly=True, compute='_compute_subtotal', store=True)
    discount = fields.Monetary(string='Discount', currency_field='currency_id', default=0.0)
    net_amount = fields.Monetary(string='Net Amount',readonly=True, currency_field='currency_id',compute='_compute_net_amount',store=True)
    tax = fields.Float(string='Tax (%)', default=14.0)
    service = fields.Float(string='Service (%)', default=12.0)
    total_amount = fields.Monetary(string='Total Amount', currency_field='currency_id', readonly=True, compute='_compute_total_amount', store=True)
    paid = fields.Monetary(string='Paid', currency_field='currency_id', readonly=True, compute='_compute_paid', store=True)
    remaining = fields.Monetary(string='Remaining', currency_field='currency_id', readonly=True, compute='_compute_remaining', store=True)


    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('served', 'Served'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, copy=False)


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('order_no', 'NEW') == 'NEW':
                vals['order_no'] = self.env['ir.sequence'].next_by_code('restaurant.order') or 'NEW'
        return super().create(vals_list)


    @api.depends('order_line_ids.subtotal')
    def _compute_subtotal(self):
        for order in self:
            order.subtotal = sum(order.order_line_ids.mapped('subtotal'))

    @api.depends('subtotal', 'discount')
    def _compute_net_amount(self):
        for item in self:
            item.net_amount = item.subtotal - item.discount

    @api.depends('net_amount', 'tax', 'service')
    def _compute_total_amount(self):
        for order in self:
            tax_amount = order.net_amount * order.tax / 100
            service_amount = order.net_amount * order.service / 100
            order.total_amount = order.net_amount + tax_amount + service_amount


    @api.depends('payment_ids.amount')
    def _compute_paid(self):
        for order in self:
            order.paid = sum(order.payment_ids.mapped('amount'))

    @api.depends('total_amount', 'paid')
    def _compute_remaining(self):
        for order in self:
            order.remaining = order.total_amount - order.paid


    @api.constrains('discount', 'subtotal')
    def _check_discount(self):
        for order in self:
            if order.discount < 0:
                raise ValidationError('Discount cannot be negative.')
            if order.discount > order.subtotal:
                raise ValidationError('Discount cannot be greater than the subtotal.')


    @api.constrains('tax')
    def _check_tax(self):
        for order in self:
            if order.tax < 0:
                raise ValidationError('Tax percentage cannot be negative.')


    @api.constrains('service')
    def _check_service(self):
        for order in self:
            if order.service < 0:
                raise ValidationError('Service percentage cannot be negative.')

    @api.constrains('payment_ids')
    def _check_payments(self):
        for order in self:
            if order.paid > order.total_amount:
                raise ValidationError('Total payments cannot be greater than the order total.')


    def action_confirm(self):
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError('Only draft orders can be confirmed.')
        if not self.order_line_ids:
            raise ValidationError("Can't confirm an empty order.")
        self.state = 'confirmed'


    def action_start_preparing(self):
        self.ensure_one()
        if self.state != 'confirmed':
            raise ValidationError('You can not prepare an order before being confirmed.')
        self.state = 'preparing'


    def action_mark_ready(self):
        self.ensure_one()
        if self.state != 'preparing':
            raise ValidationError('You can not mark an order as ready before being prepared.')
        self.state = 'ready'


    def action_serve(self):
        self.ensure_one()
        if self.state != 'ready':
            raise ValidationError('You can not serve an order before it is ready.')
        self.state = 'served'


    def action_pay(self):
        self.ensure_one()
        if self.state != 'served':
            raise ValidationError('You can only pay an order that has been served.')
        if self.paid <= 0:
            raise ValidationError('You cannot mark the order as paid without a payment.')
        if self.paid < self.total_amount:
            raise ValidationError('The order has not been fully paid.')
        self.state = 'paid'

    def action_cancel(self):
        self.ensure_one()
        if self.state == 'paid':
            raise ValidationError('You can not cancel an order that has been paid.')
        self.state = 'cancelled'

    def unlink(self):
        for order in self:
            if order.state != 'draft':
                raise ValidationError('Only draft orders can be deleted.')
        return super().unlink()

    @api.model
    def get_kitchen_orders(self):
        orders = self.search([('state', 'in', ['confirmed', 'preparing', 'ready'])], order='order_date asc')
        return [{
            'id': order.id,
            'order_no': order.order_no,
            'order_date': order.order_date,
            'customer': order.customer_id.name if order.customer_id else 'Walk-in Customer',
            'table': order.table_id.name if order.table_id else 'No Table',
            'state': order.state,
            'lines': [{
                'id': line.id,
                'item': line.item_id.name if line.item_id else 'Unknown Item',
                'quantity': line.quantity,
                'modifiers': [modifier.name for modifier in line.modifier_ids]
            } for line in order.order_line_ids]
        } for order in orders]