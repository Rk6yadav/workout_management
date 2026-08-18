from odoo import api, fields, models
from odoo.exceptions import ValidationError


class WorkoutProgram(models.Model):
    _name = 'workout.program'
    _description = 'Workout Program'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True)
    trainer_id = fields.Many2one('res.partner', domain=[('is_workout_trainer', '=', True)])
    member_ids = fields.Many2many('res.partner', 'workout_program_member_rel', 'program_id', 'member_id', domain=[('is_workout_member', '=', True)])
    goal = fields.Selection([('weight_loss', 'Weight Loss'), ('muscle_gain', 'Muscle Gain'), ('strength', 'Strength'), ('endurance', 'Endurance'), ('general_fitness', 'General Fitness'), ('flexibility', 'Flexibility')])
    level = fields.Selection([('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')], default='beginner')
    duration_weeks = fields.Integer(default=4, required=True)
    day_ids = fields.One2many('workout.program.day', 'program_id', copy=True)
    notes = fields.Html()
    state = fields.Selection([('draft', 'Draft'), ('published', 'Published'), ('archived', 'Archived')], default='draft', tracking=True)

    def action_publish(self): self.write({'state': 'published'})
    def action_archive(self): self.write({'state': 'archived'})


class WorkoutProgramDay(models.Model):
    _name = 'workout.program.day'
    _description = 'Workout Program Day'
    _order = 'week_number, sequence, id'
    program_id = fields.Many2one('workout.program', required=True, ondelete='cascade')
    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    week_number = fields.Integer(default=1, required=True)
    weekday = fields.Selection([('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'), ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')])
    estimated_minutes = fields.Integer()
    prescription_ids = fields.One2many('workout.prescription', 'program_day_id', copy=True)
    notes = fields.Text()

    @api.constrains('week_number')
    def _check_week_number(self):
        if any(day.week_number < 1 for day in self): raise ValidationError('Week number must be positive.')


class WorkoutPrescription(models.Model):
    _name = 'workout.prescription'
    _description = 'Workout Exercise Prescription'
    _order = 'sequence, id'
    program_day_id = fields.Many2one('workout.program.day', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    exercise_id = fields.Many2one('workout.exercise', required=True)
    prescription_type = fields.Selection([('strength', 'Strength'), ('cardio', 'Cardio'), ('time', 'Time Based'), ('amrap', 'AMRAP'), ('emom', 'EMOM')], default='strength', required=True)
    set_count = fields.Integer(string='Target Sets', default=3)
    target_reps = fields.Integer()
    target_weight_kg = fields.Float(string='Target Weight (kg)', digits=(8, 2))
    target_duration_seconds = fields.Integer(string='Duration (seconds)')
    target_distance_km = fields.Float(string='Distance (km)', digits=(8, 2))
    rest_seconds = fields.Integer(string='Rest (seconds)', default=90)
    tempo = fields.Char(help='Example: 3-1-1-0')
    target_rpe = fields.Float(string='Target RPE', digits=(3, 1))
    target_rir = fields.Integer(string='Target RIR')
    rounds = fields.Integer()
    notes = fields.Text()
