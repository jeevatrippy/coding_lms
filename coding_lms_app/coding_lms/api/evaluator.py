import re
import json
import frappe
from coding_lms.api.judge0_client import submit_to_judge0

def verify_testcase_match(tc, stdout: str) -> bool:
    """Helper to verify testcase output matching (exact, tolerance, or regex)."""
    mode = getattr(tc, "mode", None) or (tc.get("mode") if isinstance(tc, dict) else "normal")
    
    if mode == "regex":
        exp_regex = getattr(tc, "expected_regex", None) or (tc.get("expected_regex") if isinstance(tc, dict) else "")
        if not exp_regex:
            return True
        flags = 0
        f_str = (getattr(tc, "regex_flags", None) or (tc.get("regex_flags") if isinstance(tc, dict) else "") or "").upper()
        if "IGNORECASE" in f_str:
            flags |= re.IGNORECASE
        if "MULTILINE" in f_str:
            flags |= re.MULTILINE
        
        match_mode = getattr(tc, "match_mode", None) or (tc.get("match_mode") if isinstance(tc, dict) else "fullmatch")
        try:
            pattern = re.compile(exp_regex.strip(), flags)
            if match_mode == "search":
                return bool(pattern.search(stdout))
            return bool(pattern.fullmatch(stdout))
        except re.error:
            return False
    else:
        expected = getattr(tc, "expected_output", None) or (tc.get("expected_output") if isinstance(tc, dict) else "") or ""
        actual_comp = stdout.rstrip("\n")
        exp_comp = expected.rstrip("\n")

        ignore_space = getattr(tc, "ignore_space", True) if not isinstance(tc, dict) else tc.get("ignore_space", True)
        if ignore_space:
            actual_comp = "\n".join(line.rstrip() for line in actual_comp.strip().splitlines())
            exp_comp = "\n".join(line.rstrip() for line in exp_comp.strip().splitlines())

        ignore_case = getattr(tc, "ignore_case", False) if not isinstance(tc, dict) else tc.get("ignore_case", False)
        if ignore_case:
            actual_comp = actual_comp.lower()
            exp_comp = exp_comp.lower()

        tolerance = getattr(tc, "numeric_tolerance", 0.0) if not isinstance(tc, dict) else tc.get("numeric_tolerance", 0.0)
        try:
            tol = float(tolerance or 0.0)
        except (ValueError, TypeError):
            tol = 0.0

        if tol > 0.0:
            try:
                return abs(float(actual_comp) - float(exp_comp)) <= tol
            except ValueError:
                return actual_comp == exp_comp
        
        return actual_comp == exp_comp

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
        stderr = (judge_res.get("stderr") or "").strip()
        compile_output = (judge_res.get("compile_output") or "").strip()
        message = (judge_res.get("message") or "").strip()
        status_info = judge_res.get("status") or {}
        status_id = status_info.get("id", 0)
        judge_status = status_info.get("description", "Unknown")

        passed = False
        actual_output = stdout
        tc_error = ""

        # Compilation Error Check
        if status_id == 6 or compile_output or "compil" in judge_status.lower():
            overall_status = "Compilation Error"
            tc_error = compile_output or stderr or message or "Compilation failed"
            if not first_error:
                first_error = tc_error
        # Runtime Error Check
        elif status_id in (7, 8, 9, 10, 11, 12) or "runtime error" in judge_status.lower():
            if overall_status == "Accepted":
                overall_status = "Runtime Error"
            tc_error = stderr or message or judge_status
            if not first_error:
                first_error = tc_error
        # Time Limit Exceeded
        elif status_id == 5 or judge_status == "Time Limit Exceeded":
            if overall_status == "Accepted":
                overall_status = "Time Limit Exceeded"
            tc_error = "Time Limit Exceeded"
            if not first_error:
                first_error = "Time Limit Exceeded"
        # Memory Limit Exceeded
        elif status_id == 4 or judge_status == "Memory Limit Exceeded":
            if overall_status == "Accepted":
                overall_status = "Memory Limit Exceeded"
            tc_error = "Memory Limit Exceeded"
            if not first_error:
                first_error = "Memory Limit Exceeded"
        else:
            passed = verify_testcase_match(tc, stdout)
            if not passed and overall_status == "Accepted":
                overall_status = "Wrong Answer"
            if stderr:
                tc_error = stderr

        if passed:
            passed_count += 1
            total_score += float(tc.weightage or 0)

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
            "error": tc_error if (is_pub or overall_status == "Compilation Error") else "",
            "execution_time": judge_res.get("time"),
            "memory": judge_res.get("memory")
        })

        # If code failed to compile, remaining test cases will fail identically with Compilation Error
        if overall_status == "Compilation Error":
            for rem_idx in range(idx + 1, len(eval_tcs)):
                rem_tc = eval_tcs[rem_idx]
                rem_pub = bool(rem_tc.is_public)
                results.append({
                    "testcase_index": rem_idx + 1,
                    "description": rem_tc.description or f"Test Case {rem_idx + 1}",
                    "is_public": rem_pub,
                    "status": "failed",
                    "weightage": float(rem_tc.weightage or 0),
                    "input": (rem_tc.input or "") if rem_pub else "[Hidden]",
                    "expected_output": (rem_tc.expected_output or "") if rem_pub else "[Hidden]",
                    "actual_output": "[Hidden Actual Output]",
                    "error": first_error if rem_pub else "",
                    "execution_time": "-",
                    "memory": "-"
                })
            break

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
def test_problem_draft(
    solution_code: str,
    language: str,
    testcases,
    time_limit: float = 2.0,
    memory_limit: int = 256,
    whitelist_keywords: str = "",
    blacklist_keywords: str = ""
) -> dict:
    """
    Interactive test runner for Desk. Executes author's solution code against draft testcases
    via Judge0 and returns detailed status, time, memory, stdout, compilation diagnostics,
    runtime errors, and match diffs.
    """
    if isinstance(testcases, str):
        try:
            testcases = json.loads(testcases)
        except Exception:
            testcases = []

    if not solution_code:
        return {"success": False, "error": "Solution code is required to test problem."}

    if not testcases:
        return {"success": False, "error": "Please add at least one test case."}

    # Keyword check
    lower_code = solution_code.lower()
    if blacklist_keywords:
        b_list = [k.strip().lower() for k in str(blacklist_keywords).split(",") if k.strip()]
        for kw in b_list:
            if re.search(r'\b' + re.escape(kw) + r'\b', lower_code):
                return {
                    "success": False,
                    "status": "Forbidden Keyword",
                    "error": f"Reference solution violates blacklist: '{kw}' is present.",
                    "results": []
                }

    if whitelist_keywords:
        w_list = [k.strip().lower() for k in str(whitelist_keywords).split(",") if k.strip()]
        for kw in w_list:
            if not re.search(r'\b' + re.escape(kw) + r'\b', lower_code):
                return {
                    "success": False,
                    "status": "Mandatory Construct Missing",
                    "error": f"Reference solution misses whitelist construct: '{kw}'.",
                    "results": []
                }

    results = []
    passed_count = 0
    global_compilation_error = None
    global_runtime_error = None

    for idx, tc in enumerate(testcases):
        stdin = tc.get("input") or ""
        if tc.get("allow_empty_input"):
            stdin = ""

        try:
            t_limit = float(time_limit or 2.0)
        except (ValueError, TypeError):
            t_limit = 2.0

        try:
            m_limit = int(memory_limit or 256) * 1024
        except (ValueError, TypeError):
            m_limit = 256 * 1024

        judge_res = submit_to_judge0(
            source_code=solution_code,
            language=language,
            stdin=stdin,
            cpu_time_limit=t_limit,
            memory_limit_kb=m_limit
        )

        stdout = (judge_res.get("stdout") or "").rstrip("\n")
        stderr = (judge_res.get("stderr") or "").strip()
        compile_output = (judge_res.get("compile_output") or "").strip()
        message = (judge_res.get("message") or "").strip()
        status_info = judge_res.get("status") or {}
        status_id = status_info.get("id", 0)
        judge_status = status_info.get("description", "Unknown")
        exec_time = judge_res.get("time")
        exec_memory = judge_res.get("memory")

        mode = tc.get("mode", "normal")
        exp_output = tc.get("expected_output", "")
        exp_regex = tc.get("expected_regex", "")

        is_blank_expected = (mode == "normal" and not exp_output) or (mode == "regex" and not exp_regex)

        passed = False
        status_label = ""
        error_detail = ""

        # Compilation Error Check
        if status_id == 6 or compile_output or "compil" in judge_status.lower():
            status_label = "Compilation Error"
            error_detail = compile_output or stderr or message or "Compilation failed"
            passed = False
            if not global_compilation_error:
                global_compilation_error = error_detail
        # Runtime Error Check (SIGSEGV, SIGFPE, SIGABRT, NZEC, etc.)
        elif status_id in (7, 8, 9, 10, 11, 12) or "runtime error" in judge_status.lower() or (stderr and not stdout and status_id != 3):
            status_label = judge_status if "runtime" in judge_status.lower() else f"Runtime Error ({judge_status})"
            error_detail = stderr or message or judge_status
            passed = False
            if not global_runtime_error:
                global_runtime_error = error_detail
        # Time Limit Exceeded
        elif status_id == 5 or judge_status == "Time Limit Exceeded":
            status_label = "Time Limit Exceeded"
            error_detail = "Time Limit Exceeded"
            passed = False
        # Memory Limit Exceeded
        elif status_id == 4 or judge_status == "Memory Limit Exceeded":
            status_label = "Memory Limit Exceeded"
            error_detail = "Memory Limit Exceeded"
            passed = False
        # Sandbox or Internal Error
        elif status_id == 13 or "internal" in judge_status.lower():
            status_label = judge_status
            error_detail = stderr or message or "Sandbox Error"
            passed = False
        else:
            if is_blank_expected:
                passed = True
                status_label = "Generated Output"
            else:
                passed = verify_testcase_match(tc, stdout)
                status_label = "Passed" if passed else "Wrong Answer"
            if stderr:
                error_detail = stderr

        if passed:
            passed_count += 1

        results.append({
            "index": idx + 1,
            "description": tc.get("description") or f"Case {idx + 1}",
            "input": stdin,
            "expected_output": exp_output,
            "expected_regex": exp_regex,
            "actual_output": stdout,
            "mode": mode,
            "passed": passed,
            "status": status_label,
            "time": f"{exec_time}s" if exec_time else "-",
            "memory": f"{exec_memory} KB" if exec_memory else "-",
            "error": error_detail,
            "compile_output": compile_output,
            "stderr": stderr,
            "is_blank_expected": is_blank_expected
        })

        # If compilation failed on this testcase, all subsequent testcases will fail with the exact same error
        if status_label == "Compilation Error":
            for rem_idx in range(idx + 1, len(testcases)):
                rem_tc = testcases[rem_idx]
                results.append({
                    "index": rem_idx + 1,
                    "description": rem_tc.get("description") or f"Case {rem_idx + 1}",
                    "input": rem_tc.get("input") or "",
                    "expected_output": rem_tc.get("expected_output", ""),
                    "expected_regex": rem_tc.get("expected_regex", ""),
                    "actual_output": "",
                    "mode": rem_tc.get("mode", "normal"),
                    "passed": False,
                    "status": "Compilation Error",
                    "time": "-",
                    "memory": "-",
                    "error": error_detail,
                    "compile_output": compile_output,
                    "stderr": stderr,
                    "is_blank_expected": False
                })
            break

    all_passed = (passed_count == len(results))
    return {
        "success": True,
        "all_passed": all_passed,
        "total_testcases": len(results),
        "passed_count": passed_count,
        "compilation_error": global_compilation_error,
        "runtime_error": global_runtime_error,
        "results": results
    }

@frappe.whitelist()
def generate_output_from_solution(problem_id: str, testcase_input: str) -> dict:
    """Auto-generates expected output by executing the author's Solution Code via Judge0."""
    problem = frappe.get_doc("Coding Problem", problem_id)
    if not problem.solution_code:
        return {"success": False, "error": "No solution code defined for this problem."}

    res = submit_to_judge0(
        source_code=problem.solution_code,
        language=problem.language or "python",
        stdin=testcase_input or ""
    )

    stdout = (res.get("stdout") or "").rstrip("\n")
    compile_output = (res.get("compile_output") or "").strip()
    stderr = (res.get("stderr") or "").strip()
    message = (res.get("message") or "").strip()

    err = compile_output or stderr or message
    if err:
        return {"success": False, "error": err}

    return {"success": True, "output": stdout}
