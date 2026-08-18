from odoo import api, fields, models


class WorkoutMembershipPlan(models.Model):
    _name = 'workout.membership.plan'
    _description = 'Membership Plan'
    _order = 'sequence, name'
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    duration_days = fields.Integer(required=True, default=30)
    price = fields.Monetary(required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id, required=True)
    trainer_sessions = fields.Integer()
    workout_access = fields.Boolean(default=True)
    nutrition_access = fields.Boolean()
    active = fields.Boolean(default=True)


class WorkoutMembership(models.Model):
    _name = 'workout.membership'
    _description = 'Member Membership'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'end_date desc, id desc'
    name = fields.Char(compute='_compute_name', store=True)
    member_id = fields.Many2one('res.partner', required=True, domain=[('is_workout_member', '=', True)], ondelete='cascade')
    plan_id = fields.Many2one('workout.membership.plan', required=True)
    start_date = fields.Date(default=fields.Date.today, required=True)
    end_date = fields.Date(required=True)
    status = fields.Selection([('draft', 'Draft'), ('active', 'Active'), ('paused', 'Paused'), ('expired', 'Expired'), ('cancelled', 'Cancelled')], default='draft', tracking=True)
    trainer_sessions_remaining = fields.Integer(related='plan_id.trainer_sessions', readonly=False)
    notes = fields.Text()

    @api.depends('member_id.name', 'plan_id.name')
    def _compute_name(self):
        for record in self: record.name = '%s — %s' % (record.member_id.name or '', record.plan_id.name or '')

    @api.onchange('plan_id', 'start_date')
    def _onchange_plan_dates(self):
        if self.plan_id and self.start_date: self.end_date = fields.Date.add(self.start_date, days=self.plan_id.duration_days - 1)

    def action_activate(self): self.write({'status': 'active'})
    def action_pause(self): self.write({'status': 'paused'})
