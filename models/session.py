from odoo import api, fields, models
from odoo.exceptions import UserError


class WorkoutSession(models.Model):
    _name = 'workout.session'
    _description = 'Workout Session'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_datetime desc, id desc'
    name = fields.Char(compute='_compute_name', store=True)
    reference = fields.Char(copy=False, readonly=True, default='New')
    member_id = fields.Many2one('res.partner', required=True, domain=[('is_workout_member', '=', True)], index=True, tracking=True)
    trainer_id = fields.Many2one(related='member_id.trainer_id', store=True)
    program_day_id = fields.Many2one('workout.program.day', string='Prescription Day')
    start_datetime = fields.Datetime(default=fields.Datetime.now, required=True)
    end_datetime = fields.Datetime()
    state = fields.Selection([('planned', 'Planned'), ('in_progress', 'In Progress'), ('done', 'Completed'), ('cancelled', 'Cancelled')], default='planned', tracking=True)
    session_exercise_ids = fields.One2many('workout.session.exercise', 'session_id', copy=False)
    duration_minutes = fields.Float(compute='_compute_metrics', store=True)
    total_volume_kg = fields.Float(compute='_compute_metrics', store=True)
    notes = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', 'New') == 'New': vals['reference'] = self.env['ir.sequence'].next_by_code('workout.session') or 'New'
        return super().create(vals_list)

    @api.depends('reference', 'member_id.name', 'start_datetime')
    def _compute_name(self):
        for record in self: record.name = '%s — %s' % (record.reference or '', record.member_id.name or '')

    @api.depends('start_datetime', 'end_datetime', 'session_exercise_ids.set_ids.volume_kg')
    def _compute_metrics(self):
        for session in self:
            session.duration_minutes = (session.end_datetime - session.start_datetime).total_seconds() / 60 if session.end_datetime and session.start_datetime else 0
            session.total_volume_kg = sum(session.session_exercise_ids.mapped('set_ids.volume_kg'))

    def action_start(self):
        for record in self:
            if record.state != 'planned': continue
            record.write({'state': 'in_progress', 'start_datetime': fields.Datetime.now()})
            if record.program_day_id and not record.session_exercise_ids:
                record._copy_prescriptions()

    def _copy_prescriptions(self):
        self.ensure_one()
        for prescription in self.program_day_id.prescription_ids:
            self.env['workout.session.exercise'].create({
                'session_id': self.id, 'prescription_id': prescription.id, 'exercise_id': prescription.exercise_id.id,
                'sequence': prescription.sequence, 'target_sets': prescription.set_count, 'target_reps': prescription.target_reps,
                'target_weight_kg': prescription.target_weight_kg, 'rest_seconds': prescription.rest_seconds,
                'target_rpe': prescription.target_rpe,
            })

    def action_complete(self):
        for record in self:
            if record.state != 'in_progress': raise UserError('Only an in-progress session can be completed.')
            record.write({'state': 'done', 'end_datetime': fields.Datetime.now()})
            record._update_progress()

    def _update_progress(self):
        self.ensure_one()
        self.env['workout.progress.event'].create_from_session(self)


class WorkoutSessionExercise(models.Model):
    _name = 'workout.session.exercise'
    _description = 'Executed Exercise'
    _order = 'sequence, id'
    session_id = fields.Many2one('workout.session', required=True, ondelete='cascade')
    prescription_id = fields.Many2one('workout.prescription', string='Source Prescription', ondelete='set null')
    sequence = fields.Integer(default=10)
    exercise_id = fields.Many2one('workout.exercise', required=True)
    target_sets = fields.Integer()
    target_reps = fields.Integer()
    target_weight_kg = fields.Float(digits=(8, 2))
    rest_seconds = fields.Integer()
    target_rpe = fields.Float(digits=(3, 1))
    set_ids = fields.One2many('workout.session.set', 'session_exercise_id', copy=False)
    completed_sets = fields.Integer(compute='_compute_completed_sets')

    def _compute_completed_sets(self):
        for record in self: record.completed_sets = len(record.set_ids.filtered('completed'))


class WorkoutSessionSet(models.Model):
    _name = 'workout.session.set'
    _description = 'Executed Set'
    _order = 'sequence, id'
    session_exercise_id = fields.Many2one('workout.session.exercise', required=True, ondelete='cascade')
    sequence = fields.Integer(default=1)
    reps = fields.Integer()
    weight_kg = fields.Float(digits=(8, 2))
    duration_seconds = fields.Integer()
    distance_km = fields.Float(digits=(8, 2))
    rpe = fields.Float(digits=(3, 1))
    completed = fields.Boolean(default=False)
    completed_at = fields.Datetime()
    volume_kg = fields.Float(compute='_compute_volume', store=True)

    @api.depends('reps', 'weight_kg', 'completed')
    def _compute_volume(self):
        for record in self: record.volume_kg = record.reps * record.weight_kg if record.completed else 0

    def action_complete(self):
        self.write({'completed': True, 'completed_at': fields.Datetime.now()})
