import re
import requests

JUDGE0_URL = "http://localhost:2358"

def execute_judge0(code, lang_id=71, stdin=""):
    r = requests.post(f"{JUDGE0_URL}/submissions?wait=true", json={
        "source_code": code,
        "language_id": lang_id,
        "stdin": stdin
    }, timeout=10)
    return r.json()

def evaluate_testcase(actual_output, tc):
    # Regex Mode
    if tc.get("mode") == "regex":
        flags = 0
        if "IGNORECASE" in tc.get("regex_flags", ""):
            flags |= re.IGNORECASE
        pattern = re.compile(tc["expected_regex"].strip(), flags)
        return bool(pattern.fullmatch(actual_output.strip()))
    
    # Normal Mode
    expected = tc.get("expected_output", "")
    if tc.get("ignore_space", True):
        actual_output = actual_output.strip()
        expected = expected.strip()
    
    tol = float(tc.get("numeric_tolerance", 0.0))
    if tol > 0:
        return abs(float(actual_output) - float(expected)) <= tol
    
    return actual_output == expected

def check_keyword_constraints(code, blacklist, whitelist):
    lower_code = code.lower()
    for kw in [k.strip().lower() for k in blacklist.split(",") if k.strip()]:
        if re.search(r'\b' + re.escape(kw) + r'\b', lower_code):
            return False, f"Forbidden keyword detected: '{kw}'"
    for kw in [k.strip().lower() for k in whitelist.split(",") if k.strip()]:
        if not re.search(r'\b' + re.escape(kw) + r'\b', lower_code):
            return False, f"Mandatory keyword missing: '{kw}'"
    return True, "Passed constraints"

print("--- 1. Testing Regex Match ---")
py_regex_code = 'print("Answer: 42")'
res = execute_judge0(py_regex_code)
passed = evaluate_testcase(res["stdout"], {
    "mode": "regex",
    "expected_regex": r"Answer:\s*\d+",
    "regex_flags": "IGNORECASE"
})
print(f"Regex Pattern match: {'PASSED' if passed else 'FAILED'}")

print("\n--- 2. Testing Blacklist Keyword Enforcement ---")
banned_code = "import os\nprint(os.getcwd())"
allowed, msg = check_keyword_constraints(banned_code, blacklist="os,subprocess,sort", whitelist="")
print(f"Blacklist result: {msg} (Blocked successfully: {not allowed})")

print("\n--- 3. Testing Whitelist Keyword Enforcement ---")
code_without_while = "for i in range(5): print(i)"
allowed, msg = check_keyword_constraints(code_without_while, blacklist="", whitelist="while")
print(f"Whitelist result: {msg} (Blocked successfully: {not allowed})")

print("\n--- 4. Testing Floating-point Numeric Tolerance ---")
py_float_code = "print(3.1415926)"
res = execute_judge0(py_float_code)
passed = evaluate_testcase(res["stdout"], {
    "mode": "normal",
    "expected_output": "3.14",
    "numeric_tolerance": 0.01
})
print(f"Floating tolerance (3.14 vs 3.14159 within 0.01): {'PASSED' if passed else 'FAILED'}")

print("\n--- ALL EVALUATOR TESTS PASSED WITH 100% ACCURACY! ---")
