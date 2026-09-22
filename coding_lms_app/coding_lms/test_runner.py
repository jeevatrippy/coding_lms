import frappe
from coding_lms.api.evaluator import evaluate_code, generate_output_from_solution
from coding_lms.api.lab import unlock_section_in_lab, verify_in_lab_access, submit_in_lab, evaluate_post_lab

def run_test():
    print("\n=== STARTING END-TO-END CODING LMS SYSTEM VALIDATION ===\n")
    frappe.set_user("Administrator")

    # 1. Question Bank
    bank_title = "Test DSA Question Bank"
    existing_qb = frappe.db.get_value("Coding Question Bank", {"bank_title": bank_title}, "name")
    if not existing_qb:
        bank = frappe.get_doc({
            "doctype": "Coding Question Bank",
            "bank_title": bank_title,
            "category": "DSA",
            "description": "Standard DSA Question Bank"
        }).insert(ignore_permissions=True)
        print("[PASS] 1. Created Question Bank:", bank.name)
    else:
        bank = frappe.get_doc("Coding Question Bank", existing_qb)
        print("[INFO] 1. Using existing Question Bank:", bank.name)

    # 2. Coding Problem
    prob_title = "Sum of First N Numbers"
    existing_prob = frappe.db.get_value("Coding Problem", {"title": prob_title}, "name")
    if existing_prob:
        frappe.delete_doc("Coding Problem", existing_prob, force=1)

    solution = "n = int(input())\ns = 0\ni = 1\nwhile i <= n:\n    s += i\n    i += 1\nprint(s)\n"
    prob = frappe.get_doc({
        "doctype": "Coding Problem",
        "title": prob_title,
        "question_bank": bank.name,
        "difficulty": "Easy",
        "language": "python",
        "content": "Write a program to compute sum from 1 to N using a while loop.",
        "starter_code": "# Write python code here\n",
        "solution_code": solution,
        "whitelist_keywords": "while",
        "blacklist_keywords": "eval, exec",
        "testcases": [
            {
                "doctype": "Coding Testcase",
                "description": "Sample Test 1",
                "is_public": 1,
                "input": "5",
                "expected_output": "15",
                "weightage": 50.0
            },
            {
                "doctype": "Coding Testcase",
                "description": "Hidden Test 1",
                "is_public": 0,
                "input": "10",
                "expected_output": "55",
                "weightage": 50.0
            }
        ]
    }).insert(ignore_permissions=True)
    print("[PASS] 2. Created Coding Problem:", prob.name)

    # 3. Test Auto-Generation from Solution Code
    out_res = generate_output_from_solution(prob.name, "7")
    assert out_res.get("success") is True, f"Auto-gen failed: {out_res}"
    assert out_res.get("output").strip() == "28", f"Expected 28, got {out_res.get('output')}"
    print("[PASS] 3. Solution Code Output Auto-Generation: input 7 -> output 28")

    # 4. Blacklist Check
    bad_code = 'eval("print(15)")'
    b_res = evaluate_code(prob.name, bad_code, "python")
    assert b_res.get("success") is False
    assert "Forbidden keyword" in b_res.get("error_message")
    print("[PASS] 4. Blacklist Protection: Blocked forbidden keyword 'eval'")

    # 5. Whitelist Check
    no_while_code = "n = int(input())\nprint(n * (n + 1) // 2)"
    w_res = evaluate_code(prob.name, no_while_code, "python")
    assert w_res.get("success") is False
    assert "Mandatory construct" in w_res.get("error_message")
    print("[PASS] 5. Whitelist Enforcement: Blocked missing mandatory construct 'while'")

    # 6. Evaluation with Valid Code
    v_res = evaluate_code(prob.name, solution, "python", mode="exam")
    assert v_res.get("success") is True, f"Evaluation failed: {v_res}"
    assert v_res.get("score") == 100.0, f"Expected 100.0 score, got {v_res.get('score')}"
    assert v_res.get("passed_count") == 2
    print("[PASS] 6. Code Evaluation Engine: Passed all 2 testcases (1 public, 1 hidden) with score 100.0")

    # 7. Lab Experiment
    lab_title = "Lab 1 - Loops and Accumulators"
    existing_lab = frappe.db.get_value("Lab Experiment", {"title": lab_title}, "name")
    if existing_lab:
        frappe.delete_doc("Lab Experiment", existing_lab, force=1)

    lab_exp = frappe.get_doc({
        "doctype": "Lab Experiment",
        "course": "CS101 Python Programming",
        "experiment_number": 1,
        "title": lab_title,
        "pre_lab_problem": prob.name,
        "in_lab_problem": prob.name,
        "pre_lab_max_marks": 20.0,
        "in_lab_max_marks": 50.0,
        "viva_max_marks": 30.0
    }).insert(ignore_permissions=True)
    print("[PASS] 7. Created Lab Experiment:", lab_exp.name)

    # 8. Section Unlock & Password Check
    unlock_res = unlock_section_in_lab(lab_exp.name, "Section A", "labpass123")
    assert unlock_res.get("success") is True
    print("[PASS] 8. Section Unlock API: In-Lab unlocked for Section A")

    auth_fail = verify_in_lab_access(lab_exp.name, "Section A", "wrongpass")
    assert auth_fail.get("authorized") is False
    print("[PASS] 8b. Security: Rejected incorrect In-Lab password")

    auth_ok = verify_in_lab_access(lab_exp.name, "Section A", "labpass123")
    assert auth_ok.get("authorized") is True
    print("[PASS] 8c. Security: Authorized correct In-Lab password")

    # 9. In-Lab Submission & PDF Generation
    in_sub = submit_in_lab(
        experiment_id=lab_exp.name,
        section="Section A",
        roll_number="23CS042",
        year="1st Year",
        department="Computer Science",
        aim="To calculate the sum of first N natural numbers using while loop in Python.",
        algorithm="Step 1: Read integer N\nStep 2: Initialize sum=0 and i=1\nStep 3: Loop while i <= N and add i to sum\nStep 4: Print sum",
        conclusion="The program successfully computed the sum meeting all limits.",
        source_code=solution,
        language="python",
        pre_lab_submission_id=v_res.get("submission_id")
    )
    assert in_sub.get("success") is True
    assert in_sub.get("pdf_url") is not None
    print("[PASS] 9. In-Lab Submission: Record and PDF Generated at:", in_sub.get("pdf_url"))

    # 10. Post-Lab Faculty Viva Grading
    post_res = evaluate_post_lab(
        lab_submission_id=in_sub.get("lab_submission_id"),
        viva_score=28.5,
        pre_lab_override=20.0,
        in_lab_override=50.0,
        teacher_feedback="Excellent logic and clean coding style."
    )
    assert post_res.get("success") is True
    print("[PASS] 10. Post-Lab Evaluation: Final score calculated successfully! Status:", post_res.get("status"))

    print("\n=======================================================")
    print(" ALL 10 END-TO-END TESTS PASSED WITH 100% ACCURACY! ")
    print("=======================================================\n")

if __name__ == "__main__":
    run_test()
