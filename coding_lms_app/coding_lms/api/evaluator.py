import re
import frappe
from coding_lms.api.judge0_client import submit_to_judge0

@frappe.whitelist()
def evaluate_code(problem_id: str, source_code: str, language: str, mode: str = "practice", user: str = None) -> dict:
    """
    Evaluates submitted code against testcases stored in the Coding Problem DocType.
    Validates keyword whitelist/blacklist, calls Judge0, and checks regex/fullmatch conditions.
    """
    if not user:
        user = frappe.session.user

    problem = frappe.get_doc("Coding Problem", problem_id)

    # 1. Pre-execution Keyword Constraints Check
    if problem.blacklist_keywords:
        b_list = [k.strip().lower() for k in problem.blacklist_keywords.split(",") if k.strip()]
        lower_code = source_code.lower()
        for kw in b_list:
            if re.search(r'\b' + re.escape(kw) + r'\b', lower_code):
                return {
                    "success": False,
                    "status": "Forbidden Keyword",
                    "error_message": f"Forbidden keyword detected: '{kw}' is not allowed in this problem.",
                    "testcases": []
                }

    if problem.whitelist_keywords:
        w_list = [k.strip().lower() for k in problem.whitelist_keywords.split(",") if k.strip()]
        lower_code = source_code.lower()
        for kw in w_list:
            if not re.search(r'\b' + re.escape(kw) + r'\b', lower_code):
                return {
                    "success": False,
                    "status": "Mandatory Construct Missing",
                    "error_message": f"Mandatory construct missing: Solution must use '{kw}'.",
                    "testcases": []
                }

    # 2. Select Test Cases based on Mode
    all_tcs = problem.testcases or []
    if mode == "practice_sample_only":
        eval_tcs = [tc for tc in all_tcs if tc.is_public]
    else:
        # In both Practice submit and Exam mode, evaluate against all testcases
        eval_tcs = all_tcs

    results = []
    total_score = 0.0
    max_score = sum(float(tc.weightage or 0) for tc in eval_tcs) or 100.0
    passed_count = 0
    overall_status = "Accepted"
    first_error = ""

    # 3. Execute Each Test Case
    for idx, tc in enumerate(eval_tcs):
        stdin = tc.input or ""
        if tc.allow_empty_input:
            stdin = ""

        time_limit = float(problem.time_limit or 2.0)
        memory_limit = int(problem.memory_limit or 256) * 1024

        judge_res = submit_to_judge0(
            source_code=source_code,
            language=language,
            stdin=stdin,
            cpu_time_limit=time_limit,
            memory_limit_kb=memory_limit
        )

        stdout = (judge_res.get("stdout") or "").rstrip("\n")
        stderr = judge_res.get("stderr") or judge_res.get("compile_output") or ""
        judge_status = judge_res.get("status", {}).get("description", "Unknown")

        passed = False
        actual_output = stdout

        if stderr:
            overall_status = "Compilation Error" if "compile" in judge_status.lower() else "Runtime Error"
            first_error = stderr
        elif judge_status == "Time Limit Exceeded":
            overall_status = "Time Limit Exceeded"
            first_error = "Time Limit Exceeded"
        else:
            # Evaluate Output
            if tc.mode == "regex" and tc.expected_regex:
                flags = 0
                f_str = (tc.regex_flags or "").upper()
                if "IGNORECASE" in f_str:
                    flags |= re.IGNORECASE
                if "MULTILINE" in f_str:
                    flags |= re.MULTILINE

                try:
                    pattern = re.compile(tc.expected_regex.strip(), flags)
                    if tc.match_mode == "fullmatch":
                        passed = bool(pattern.fullmatch(stdout))
                    else:
                        passed = bool(pattern.search(stdout))
                except re.error as e:
                    passed = False
                    first_error = f"Regex Evaluation Error: {str(e)}"
            else:
                expected = (tc.expected_output or "").rstrip("\n")
                actual_comp = stdout
                exp_comp = expected

                if tc.ignore_space:
                    actual_comp = "\n".join(line.rstrip() for line in actual_comp.strip().splitlines())
                    exp_comp = "\n".join(line.rstrip() for line in exp_comp.strip().splitlines())

                if tc.ignore_case:
                    actual_comp = actual_comp.lower()
                    exp_comp = exp_comp.lower()

                # Numeric Tolerance Check
                tol = float(tc.numeric_tolerance or 0.0)
                if tol > 0.0:
                    try:
                        passed = abs(float(actual_comp) - float(exp_comp)) <= tol
                    except ValueError:
                        passed = (actual_comp == exp_comp)
                else:
                    passed = (actual_comp == exp_comp)

        if passed:
            passed_count += 1
            total_score += float(tc.weightage or 0)
        elif overall_status == "Accepted":
            overall_status = "Wrong Answer"

        is_pub = bool(tc.is_public)
        results.append({
            "testcase_index": idx + 1,
            "description": tc.description or f"Test Case {idx + 1}",
            "is_public": is_pub,
            "status": "passed" if passed else "failed",
            "weightage": float(tc.weightage or 0),
            "input": stdin if is_pub else "[Hidden]",
            "expected_output": (tc.expected_output or "") if is_pub else "[Hidden]",
            "actual_output": actual_output if (is_pub or passed) else "[Hidden Actual Output]",
            "execution_time": judge_res.get("time"),
            "memory": judge_res.get("memory")
        })

    # 4. Save Submission Record in Database
    submission_doc = frappe.get_doc({
        "doctype": "Coding Submission",
        "user": user,
        "problem": problem_id,
        "language": language,
        "source_code": source_code,
        "mode": mode,
        "status": overall_status,
        "score": round(total_score, 2),
        "total_marks": round(max_score, 2),
        "passed_testcases": passed_count,
        "total_testcases": len(eval_tcs),
        "error_message": first_error,
        "testcase_results": frappe.as_json(results)
    })
    submission_doc.insert(ignore_permissions=True)

    return {
        "success": True,
        "submission_id": submission_doc.name,
        "status": overall_status,
        "score": round(total_score, 2),
        "total_marks": round(max_score, 2),
        "passed_count": passed_count,
        "total_testcases": len(eval_tcs),
        "error_message": first_error,
        "testcases": results
    }

@frappe.whitelist()
def generate_output_from_solution(problem_id: str, testcase_input: str) -> dict:
    """
    Auto-generates expected output by executing the author's Solution Code via Judge0.
    """
    problem = frappe.get_doc("Coding Problem", problem_id)
    if not problem.solution_code:
        return {"success": False, "error": "No solution code defined for this problem."}

    res = submit_to_judge0(
        source_code=problem.solution_code,
        language=problem.language or "python",
        stdin=testcase_input or ""
    )

    stdout = (res.get("stdout") or "").rstrip("\n")
    stderr = res.get("stderr") or res.get("compile_output") or ""

    if stderr:
        return {"success": False, "error": stderr}

    return {"success": True, "output": stdout}
