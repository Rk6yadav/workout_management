{
    'name': 'Workout Management',
    'version': '19.0.1.0.0',
    'summary': 'Member fitness, programs, workout execution, and progress tracking',
    'description': '''A connected fitness operations foundation for gyms and personal trainers.

It keeps workout prescriptions separate from actual session performance, so progress,
personal records, attendance, and trainer follow-up are calculated from one source of truth.''',
    'category': 'Services/Sport and Fitness',
    'author': 'Workout Management',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        'security/workout_security.xml',
        'security/ir.model.access.csv',
        'data/workout_sequence.xml',
        'views/workout_member_views.xml',
        'views/workout_exercise_views.xml',
        'views/workout_program_views.xml',
        'views/workout_session_views.xml',
        'views/workout_progress_views.xml',
        'views/workout_menu.xml',
    ],
    'application': True,
    'installable': True,
}
