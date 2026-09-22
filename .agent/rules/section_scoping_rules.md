# Section Scoping & Security Rules

1. Single Course, Multi-Section:
   - A single Lab Course can be assigned across multiple departments / sections (e.g. CS-A, CS-B).
2. Permission Isolation:
   - Implement `permission_query_conditions` in Frappe `hooks.py` for all Lab and Submission DocTypes.
   - Instructor assigned to Section A must NEVER see Section B students, unlock Section B, or view Section B PDF reports.
   - System Managers / Administrators bypass section filters and see all data.
