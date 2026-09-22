import frappe

def get_lab_submission_conditions(user=None):
    """
    Enforces multi-section scoping:
    - System Managers & Admins see all submissions.
    - Instructors see only submissions for sections they are assigned to.
    - Students see only their own submissions.
    """
    if not user:
        user = frappe.session.user

    roles = frappe.get_roles(user)
    if "System Manager" in roles or "Administrator" in roles:
        return ""

    if "Instructor" in roles:
        assigned_sections = frappe.db.get_all(
            "Lab Section Access",
            filters={"instructor": user},
            pluck="section"
        )
        if assigned_sections:
            formatted = ", ".join(f"'{frappe.db.escape(s)}'" for s in set(assigned_sections))
            return f"`tabLab Submission`.section IN ({formatted})"
        return "1=0"  # No assigned sections -> hide all

    # Student default
    return f"`tabLab Submission`.student = '{frappe.db.escape(user)}'"

def get_section_access_conditions(user=None):
    """
    Restricts Lab Section Access doc view based on instructor assignment.
    """
    if not user:
        user = frappe.session.user

    roles = frappe.get_roles(user)
    if "System Manager" in roles or "Administrator" in roles:
        return ""

    if "Instructor" in roles:
        return f"`tabLab Section Access`.instructor = '{frappe.db.escape(user)}'"

    return ""
