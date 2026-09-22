import json
import frappe
from frappe.utils import now_datetime, format_datetime
from frappe.utils.pdf import get_pdf
from coding_lms.api.evaluator import evaluate_code

@frappe.whitelist()
def unlock_section_in_lab(experiment_id: str, section: str, password: str) -> dict:
    """
    Instructor unlocks In-Lab step for a specific section and sets the access password.
    """
    access_doc = frappe.db.get_value(
        "Lab Section Access",
        {"experiment": experiment_id, "section": section},
        "name"
    )

    if access_doc:
        doc = frappe.get_doc("Lab Section Access", access_doc)
        doc.is_unlocked = 1
        doc.access_password = password
        doc.instructor = frappe.session.user
        doc.unlocked_at = now_datetime()
        doc.save(ignore_permissions=True)
    else:
        doc = frappe.get_doc({
            "doctype": "Lab Section Access",
            "experiment": experiment_id,
            "section": section,
            "is_unlocked": 1,
            "access_password": password,
            "instructor": frappe.session.user,
            "unlocked_at": now_datetime()
        })
        doc.insert(ignore_permissions=True)

    return {"success": True, "message": f"In-Lab unlocked successfully for {section}."}

@frappe.whitelist()
def verify_in_lab_access(experiment_id: str, section: str, password: str) -> dict:
    """
    Checks if In-Lab is unlocked for this section and validates the entered password.
    """
    access = frappe.db.get_value(
        "Lab Section Access",
        {"experiment": experiment_id, "section": section},
        ["is_unlocked", "access_password"],
        as_dict=True
    )

    if not access or not access.is_unlocked:
        return {"authorized": False, "error": "In-Lab is locked by your instructor. Please wait for it to be unlocked."}

    if access.access_password and access.access_password.strip() != password.strip():
        return {"authorized": False, "error": "Incorrect In-Lab password. Please check with your instructor."}

    return {"authorized": True}

@frappe.whitelist()
def submit_in_lab(
    experiment_id: str,
    section: str,
    roll_number: str,
    year: str,
    department: str,
    aim: str,
    algorithm: str,
    conclusion: str,
    source_code: str,
    language: str,
    pre_lab_submission_id: str = None
) -> dict:
    """
    Submits In-Lab work: evaluates coding challenge, auto-generates downloadable PDF record,
    and creates the Lab Submission record.
    """
    student = frappe.session.user
    experiment = frappe.get_doc("Lab Experiment", experiment_id)

    # 1. Evaluate In-Lab Coding Challenge
    eval_result = evaluate_code(
        problem_id=experiment.in_lab_problem,
        source_code=source_code,
        language=language,
        mode="exam",
        user=student
    )

    in_lab_submission_id = eval_result.get("submission_id")
    in_lab_auto_score = float(eval_result.get("score") or 0.0)

    # 2. Retrieve Pre-Lab Auto Score if available
    pre_lab_auto_score = 0.0
    if pre_lab_submission_id:
        pre_lab_auto_score = float(frappe.db.get_value("Coding Submission", pre_lab_submission_id, "score") or 0.0)

    # 3. Generate Automated PDF Lab Record
    template_data = {
        "experiment": experiment,
        "student_name": frappe.utils.get_fullname(student),
        "roll_number": roll_number,
        "department": department,
        "section": section,
        "year": year,
        "submission_date": format_datetime(now_datetime(), "dd-MM-yyyy HH:mm"),
        "aim": aim,
        "algorithm": algorithm,
        "conclusion": conclusion,
        "source_code": source_code,
        "testcase_results": eval_result.get("testcases", [])
    }

    html_content = frappe.render_template("coding_lms/templates/lab_record.html", template_data)
    pdf_data = get_pdf(html_content)

    clean_roll = (roll_number or "STUDENT").replace(" ", "_")
    clean_id = experiment.name.replace(" ", "_")
    filename = f"Experiment_{clean_roll}_{clean_id}.pdf"

    # Save to Frappe File Manager
    saved_file = frappe.get_doc({
        "doctype": "File",
        "file_name": filename,
        "content": pdf_data,
        "is_private": 0
    })
    saved_file.insert(ignore_permissions=True)

    # 4. Create Lab Submission Record
    lab_sub = frappe.get_doc({
        "doctype": "Lab Submission",
        "student": student,
        "roll_number": roll_number,
        "year": year,
        "department": department,
        "section": section,
        "experiment": experiment_id,
        "status": "In-Lab Submitted",
        "aim": aim,
        "algorithm": algorithm,
        "conclusion": conclusion,
        "pre_lab_submission": pre_lab_submission_id,
        "pre_lab_auto_score": pre_lab_auto_score,
        "pre_lab_final_score": pre_lab_auto_score,
        "in_lab_submission": in_lab_submission_id,
        "in_lab_auto_score": in_lab_auto_score,
        "in_lab_final_score": in_lab_auto_score,
        "generated_pdf": saved_file.file_url,
        "viva_score": 0.0,
        "final_total_score": pre_lab_auto_score + in_lab_auto_score
    })
    lab_sub.insert(ignore_permissions=True)

    return {
        "success": True,
        "lab_submission_id": lab_sub.name,
        "pdf_url": saved_file.file_url,
        "eval_result": eval_result
    }

@frappe.whitelist()
def evaluate_post_lab(
    lab_submission_id: str,
    viva_score: float,
    pre_lab_override: float = None,
    in_lab_override: float = None,
    teacher_feedback: str = ""
) -> dict:
    """
    Teacher post-lab review: records viva marks, optional score overrides, and computes final total.
    """
    doc = frappe.get_doc("Lab Submission", lab_submission_id)

    if pre_lab_override is not None and pre_lab_override != "":
        doc.pre_lab_final_score = float(pre_lab_override)

    if in_lab_override is not None and in_lab_override != "":
        doc.in_lab_final_score = float(in_lab_override)

    doc.viva_score = float(viva_score or 0.0)
    doc.teacher_feedback = teacher_feedback
    doc.evaluated_by = frappe.session.user
    doc.evaluated_at = now_datetime()
    doc.status = "Evaluated"
    doc.save(ignore_permissions=True)

    return {
        "success": True,
        "final_total_score": doc.final_total_score,
        "status": doc.status
    }
