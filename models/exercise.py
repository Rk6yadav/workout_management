from odoo import fields, models


class WorkoutMuscle(models.Model):
    _name = 'workout.muscle'
    _description = 'Muscle Group'
    _order = 'name'
    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    _sql_constraints = [('workout_muscle_name_unique', 'unique(name)', 'Muscle group names must be unique.')]


class WorkoutEquipment(models.Model):
    _name = 'workout.equipment'
    _description = 'Gym Equipment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    name = fields.Char(required=True, tracking=True)
    reference = fields.Char(copy=False, readonly=True)
    category = fields.Selection([('free_weight', 'Free Weight'), ('machine', 'Machine'), ('cardio', 'Cardio'), ('functional', 'Functional'), ('other', 'Other')], default='other')
    status = fields.Selection([('available', 'Available'), ('maintenance', 'Maintenance Required'), ('unavailable', 'Unavailable')], default='available', tracking=True)
    location = fields.Char()
    manufacturer = fields.Char()
    notes = fields.Text()


class WorkoutExercise(models.Model):
    _name = 'workout.exercise'
    _description = 'Exercise'
    _order = 'name'
    _rec_name = 'name'
    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    category = fields.Selection([('strength', 'Strength'), ('cardio', 'Cardio'), ('mobility', 'Mobility'), ('stretching', 'Stretching'), ('other', 'Other')], default='strength', required=True)
    difficulty = fields.Selection([('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')], default='beginner')
    primary_muscle_id = fields.Many2one('workout.muscle')
    secondary_muscle_ids = fields.Many2many('workout.muscle', 'workout_exercise_secondary_muscle_rel', 'exercise_id', 'muscle_id')
    equipment_ids = fields.Many2many('workout.equipment', 'workout_exercise_equipment_rel', 'exercise_id', 'equipment_id')
    alternative_ids = fields.Many2many('workout.exercise', 'workout_exercise_alternative_rel', 'exercise_id', 'alternative_id', string='Alternative Exercises')
    instructions = fields.Html()
    safety_instructions = fields.Html()
    video_url = fields.Char(string='Instruction Video URL')
    image = fields.Image()
    calories_per_minute = fields.Float(digits=(6, 2))
    notes = fields.Text()
