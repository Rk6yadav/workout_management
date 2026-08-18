# Workout Management for Odoo 19

A V1 foundation for a connected gym and personal-training platform. The module is deliberately built around the fitness lifecycle rather than separate, disconnected trackers:

`Member → program prescription → session execution → completed sets → progress event / PR`

## Included V1 capabilities

- **Member profile on `res.partner`** — members are not duplicated. Fitness level, trainer, workout preference, emergency contact, safety/diet preference notes, goals, measurements, and membership status live with the existing Odoo contact.
- **Trainer flags and assignment** — any partner can be marked as a personal trainer and assigned to a member.
- **Exercise library** — categories, primary/secondary muscles, equipment, instructions, safety notes, video URL, and alternatives.
- **Program builder** — program, weekly day schedule, and exercise prescription support strength, cardio, time-based, AMRAP, and EMOM programming. Strength prescriptions include sets, reps, load, rest, tempo, RPE, and RIR.
- **Prescription vs. performance** — planned program lines are never overwritten. Starting a session copies them into execution lines; completed sets capture the actual reps, weight, duration, distance, and RPE.
- **Progressive-overload data** — completed session volume is calculated as `reps × weight`; completion automatically creates a progress event and updates best weight, reps, and exercise-volume personal records.
- **Measurement history** — chronological weight, body fat, BMI, chest, waist, and hip data. The member profile displays the newest values without duplicating data.
- **Membership and attendance** — membership plans, active/pause lifecycle, and check-in/out records with manual, QR, RFID, kiosk, and website methods.
- **Security roles** — Workout User for operating data and Workout Manager for configuration and full management.

## Installation

1. Place this repository directory in your Odoo 19 addons path.
2. Update the Apps List.
3. Install **Workout Management**.
4. Give staff the **Workout User** or **Workout Manager** access group.

## Important design boundaries

This V1 is an ERP/backend foundation. It intentionally does not expose ordinary members to the Odoo backend, nor does it claim to provide medical diagnosis. A member PWA/portal, nutrition, sales/accounting subscriptions, notifications, QR kiosk, equipment maintenance, and AI recommendations are suitable independent V2/V3 modules on top of this core.

## Suggested next modules

- `workout_portal`: mobile-first member and trainer portal/PWA
- `workout_nutrition`: food, recipes, plans, daily logs, and grocery planning
- `workout_membership_sale`: Sales, subscriptions, invoicing, payments, PT packages, and commissions
- `workout_equipment_maintenance`: Maintenance tickets, QR equipment interactions, and fault reporting
- `workout_advanced`: periodization, supersets/circuits, recovery, challenges, and achievements
- `workout_ai`: human-approved recommendations over authorized fitness data
