import base64
import requests
import frappe

# Judge0 Comprehensive Language ID Map (Supports 47+ standard languages in Judge0 v1.13+)
JUDGE0_LANGUAGES = {
    # Python
    "python": 71,          # Python (3.8.1)
    "python3": 71,         # Python (3.8.1)
    "python2": 70,         # Python (2.7.17)
    
    # C & C++
    "c": 50,               # C (GCC 9.2.0)
    "c_gcc7": 48,          # C (GCC 7.4.0)
    "c_gcc8": 49,          # C (GCC 8.3.0)
    "c_clang": 75,         # C (Clang 7.0.1)
    "cpp": 54,             # C++ (GCC 9.2.0)
    "c++": 54,
    "cpp_gcc7": 52,        # C++ (GCC 7.4.0)
    "cpp_gcc8": 53,        # C++ (GCC 8.3.0)
    "cpp_clang": 76,       # C++ (Clang 7.0.1)
    
    # Java
    "java": 62,            # Java (OpenJDK 13.0.1)
    
    # JavaScript & TypeScript
    "javascript": 63,      # JavaScript (Node.js 12.14.0)
    "js": 63,
    "nodejs": 63,
    "typescript": 74,      # TypeScript (3.7.4)
    "ts": 74,
    
    # Modern Systems & Backend
    "csharp": 51,          # C# (Mono 6.6.0.161)
    "c#": 51,
    "go": 60,              # Go (1.13.5)
    "golang": 60,
    "rust": 73,            # Rust (1.40.0)
    "php": 68,             # PHP (7.4.1)
    "ruby": 72,            # Ruby (2.7.0)
    "kotlin": 78,          # Kotlin (1.3.70)
    "swift": 83,           # Swift (5.2.3)
    
    # Data & Scripting
    "sql": 82,             # SQL (SQLite 3.27.2)
    "sqlite": 82,
    "bash": 46,            # Bash (5.0.0)
    "sh": 46,
    "shell": 46,
    "r": 80,               # R (4.0.0)
    "scala": 81,            # Scala (2.13.2)
    "perl": 85,             # Perl (5.28.1)
    "haskell": 61,          # Haskell (GHC 8.8.1)
    "lua": 64,             # Lua (5.3.5)
    "elixir": 57,          # Elixir (1.9.4)
    "erlang": 58,          # Erlang (OTP 22.2)
    "clojure": 86,         # Clojure (1.10.1)
    "assembly": 45,        # Assembly (NASM 2.14.02)
    "nasm": 45,
    "d": 56,               # D (DMD 2.089.1)
    "fortran": 59,          # Fortran (GFortran 9.2.0)
    "pascal": 67,          # Pascal (FPC 3.0.4)
    "prolog": 69,          # Prolog (GNU Prolog 1.4.5)
    "groovy": 88           # Groovy (3.0.3)
}

def get_judge0_url() -> str:
    """Resolves Judge0 base URL. Defaults to internal docker service or localhost."""
    return frappe.conf.get("judge0_url") or "http://host.docker.internal:2358"

def get_language_id(language: str) -> int:
    """Resolves Judge0 language ID from language string name or alias."""
    if not language:
        return 71
    normalized = str(language).strip().lower()
    return JUDGE0_LANGUAGES.get(normalized, 71)

@frappe.whitelist()
def get_supported_languages() -> list:
    """Returns list of all supported languages with IDs and display labels."""
    url = get_judge0_url() + "/languages"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass

    return [{"id": v, "name": k.capitalize()} for k, v in JUDGE0_LANGUAGES.items()]

def _b64_encode(val) -> str:
    if val is None:
        return ""
    if isinstance(val, str):
        return base64.b64encode(val.encode("utf-8")).decode("ascii")
    if isinstance(val, (bytes, bytearray)):
        return base64.b64encode(val).decode("ascii")
    return base64.b64encode(str(val).encode("utf-8")).decode("ascii")

def _b64_decode(val) -> str:
    if not val:
        return ""
    try:
        if isinstance(val, str):
            return base64.b64decode(val.encode("ascii")).decode("utf-8", errors="replace")
        return base64.b64decode(val).decode("utf-8", errors="replace")
    except Exception:
        return str(val)

def submit_to_judge0(
    source_code: str,
    language: str,
    stdin: str = "",
    cpu_time_limit: float = 2.0,
    memory_limit_kb: int = 256000
) -> dict:
    """
    Submits source code to the sandboxed Judge0 compiler microservice with base64 encoding
    to reliably support compiler diagnostics, warnings, and non-ASCII character outputs.
    Returns dictionary with stdout, stderr, compile_output, message, status, time, and memory.
    """
    url = get_judge0_url() + "/submissions?wait=true&base64_encoded=true"
    lang_id = get_language_id(language)

    payload = {
        "source_code": _b64_encode(source_code),
        "language_id": lang_id,
        "stdin": _b64_encode(stdin or ""),
        "cpu_time_limit": float(cpu_time_limit or 2.0),
        "memory_limit": int(memory_limit_kb or 256000)
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        raw = response.json()
        decoded = dict(raw)
        for key in ("stdout", "stderr", "compile_output", "message"):
            if raw.get(key):
                decoded[key] = _b64_decode(raw[key])
            else:
                decoded[key] = ""
        return decoded
    except requests.exceptions.Timeout:
        return {
            "stdout": "",
            "stderr": "Execution timed out contacting compiler sandbox.",
            "compile_output": "",
            "message": "Timeout Error",
            "status": {"id": 13, "description": "Timeout Error"},
            "time": None,
            "memory": None
        }
    except Exception as e:
        frappe.log_error("Judge0 Submission Error: " + str(e), "coding_lms.judge0")
        return {
            "stdout": "",
            "stderr": "Compiler Service Error: " + str(e),
            "compile_output": "",
            "message": str(e),
            "status": {"id": 13, "description": "Internal Error"},
            "time": None,
            "memory": None
        }
