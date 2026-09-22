import requests
import frappe

# Judge0 Standard Language ID Map
JUDGE0_LANGUAGES = {
    "python": 71,
    "cpp": 54,
    "c": 50,
    "java": 62,
    "javascript": 63
}

def get_judge0_url():
    return frappe.conf.get("judge0_url") or "http://host.docker.internal:2358"

def submit_to_judge0(source_code: str, language: str, stdin: str = "", cpu_time_limit: float = 2.0, memory_limit_kb: int = 256000) -> dict:
    """
    Submits raw source code to the Judge0 execution microservice.
    Returns dict containing stdout, stderr, execution time, and status.
    """
    url = f"{get_judge0_url()}/submissions?wait=true"
    lang_id = JUDGE0_LANGUAGES.get(language.lower(), 71)
    
    payload = {
        "source_code": source_code,
        "language_id": lang_id,
        "stdin": stdin or "",
        "cpu_time_limit": cpu_time_limit,
        "memory_limit": memory_limit_kb
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        frappe.log_error(f"Judge0 Submission Error: {str(e)}", "coding_lms.judge0")
        return {
            "stdout": "",
            "stderr": f"Compiler Service Error: {str(e)}",
            "status": {"id": 13, "description": "Internal Error"}
        }
