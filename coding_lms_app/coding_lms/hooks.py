app_name = "coding_lms"
app_title = "Coding LMS Extension"
app_publisher = "Coding LMS"
app_description = "Standalone Frappe LMS Extension for CodeRunner, Judge0 Execution, Client-Side Proctored Exams & 3-Step Lab Workflow"
app_email = "dev@codinglms.local"
app_license = "mit"

# Section Scoping Permissions
permission_query_conditions = {
    "Lab Submission": "coding_lms.api.permissions.get_lab_submission_conditions",
    "Lab Section Access": "coding_lms.api.permissions.get_section_access_conditions"
}
