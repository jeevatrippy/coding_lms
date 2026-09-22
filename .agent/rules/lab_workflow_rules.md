# Lab Workflow Rules (3-Step Lifecycle)

1. Pre-Lab Gating:
   - Auto-graded basic coding challenge. Must be marked completed before student can proceed.
2. In-Lab Security & Execution:
   - Locked by default. Unlocked only by the assigned section instructor using a section password.
   - Enforce 3 mandatory text areas: Aim, Algorithm / Procedure, Conclusion.
   - On submission: Automatically trigger PDF generation (`Experiment_<RollNo>_<ID>.pdf`) via Frappe Jinja HTML template. Store generated PDF in Frappe File Manager.
3. Post-Lab & Viva Evaluation:
   - Teacher evaluation screen with PDF preview, auto-calculated Pre-Lab & In-Lab scores.
   - Form for Viva marks + Teacher Feedback comments.
   - Score Override: If teacher overrides Pre-Lab or In-Lab scores, preserve both `original_score` and `override_score` in the database for auditing.
   - Final score = `Pre-Lab + In-Lab + Viva`.
