# Coding LMS 🚀

> **Marketplace-Ready Standalone Frappe LMS Extension for CodeRunner, Judge0 Execution, Client-Side Proctoring & 3-Step Lab Workflow**

---

## 🌟 Overview

**Coding LMS** is an enterprise-grade extension app for [Frappe LMS](https://github.com/frappe/lms). It adds native interactive coding challenges, isolated sandbox execution, automated testcase evaluation, and an academic **3-Step Lab Workflow** (Pre-Lab $\rightarrow$ In-Lab $\rightarrow$ Post-Lab) with automated PDF record generation.

Designed strictly adhering to Frappe conventions with **zero monkey-patching**, ensuring 100% upgrade-safety and marketplace readiness.

---

## ⚡ Key Features

### 1. Unified CodeRunner & Execution Sandbox
- **Powered by Judge0**: Isolated Linux `isolate` sandboxes supporting **Python 3, C++, C, Java, and JavaScript**.
- **Execution Modes**:
  - **Practice Mode**: Students test against sample/public testcases with instant console feedback.
  - **Exam / Lab Mode**: Full evaluation against all testcases (public + hidden) with dynamic scoring.
- **Auto-Generate Expected Outputs**: Reference solution code can be executed against testcase inputs to automatically generate expected outputs.

### 2. Independent Question Bank & Advanced Testcase Matching
- **Snippets Architecture**: Starter code, skeleton signature, and reference solution code.
- **Keyword Constraints**:
  - **Whitelist**: Enforces mandatory constructs (e.g., must use `while` or recursion).
  - **Blacklist**: Blocks disallowed functions/libraries (e.g., `eval`, `os`, `exec`).
- **Precision Matching**:
  - Regex matching (`fullmatch` or `search`) with `IGNORECASE` and `MULTILINE` flags.
  - Floating-point `numeric_tolerance` (e.g. `3.14` vs `3.14159`).
  - Text normalizers (stripping trailing spaces, case-insensitivity).
  - Empty `stdin` support (`stdin: ""`).

### 3. 3-Step Academic Lab Course Workflow
```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   Step 1:       │       │   Step 2:       │       │   Step 3:       │
│   PRE-LAB       │ ────► │   IN-LAB        │ ────► │   POST-LAB      │
│ Self-paced code │       │ Locked by Sec.  │       │ Faculty Review  │
│ gating criteria │       │ Aim/Algo + Code │       │ Viva + Override │
└─────────────────┘       └────────┬────────┘       └─────────────────┘
                                   │
                                   ▼
                      Immutable PDF Lab Record
                   (Experiment_<RollNo>_<ID>.pdf)
```
- **Pre-Lab**: Self-paced prerequisite challenge.
- **In-Lab**: Locked by default. Instructor unlocks per section with a session password. Students complete Aim, Algorithm, Conclusion write-ups and submit code $\rightarrow$ auto-generates an immutable PDF Lab Record.
- **Post-Lab**: Faculty review screen with PDF preview, Viva marks entry, and score override preservation.

### 4. Multi-Section Scoping & Security
- Single course shared across sections/departments without data leakage.
- Enforced via Frappe `permission_query_conditions` hooks (`coding_lms.api.permissions`).

### 5. Client-Side Proctoring
- Tab-switch count monitoring and threshold auto-submission.
- Copy/paste blocking and fullscreen management (no intrusive webcams required).

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    Frappe Web & Desk                      │
│             http://localhost:8000 (Site: coding.localhost) │
│  - Coding Question Bank        - Coding Problem DocType    │
│  - Unified CodeRunner / Vue 3  - OutputPanel (Console+TCs) │
│  - 3-Step Lab Course Workflow  - Section Scoping Engine    │
└────────────────────────────┬───────────────────────────────┘
                             │ REST API (port 2358)
                             ▼
┌────────────────────────────────────────────────────────────┐
│               Judge0 Sandbox Execution Engine              │
│       - PostgreSQL 13          - Redis 6.0 Server          │
│       - Judge0 API Server      - Judge0 Worker (isolate)   │
│       - Sandboxed Environments (Python, C++, C, Java, JS)  │
└────────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation

### Option A: Install on Existing Frappe Bench

```bash
# 1. Fetch app into your bench
bench get-app https://github.com/jeevatrippy/coding_lms

# 2. Install app on your site
bench --site your-site.localhost install-app coding_lms

# 3. Configure Judge0 endpoint
bench --site your-site.localhost set-config judge0_url "http://localhost:2358"

# 4. Run migrations
bench --site your-site.localhost migrate
```

### Option B: Local Docker Stack

```bash
# 1. Start Judge0 Sandbox
cd judge0_docker
docker compose up -d

# 2. Start Frappe LMS Stack
cd ../frappe_docker
docker compose up -d
```

---

## 📋 DocTypes Included

- `Coding Question Bank` (Category, domain & department taxonomy)
- `Coding Problem` (Starter code, solution, whitelist/blacklist keywords, limits)
- `Coding Testcase` (Public/hidden testcases, regex matching, tolerance)
- `Coding Submission` (Execution logs, test results, scores)
- `Lab Experiment` (Pre-Lab, In-Lab, Viva configuration)
- `Lab Section Access` (Section unlock state and session password)
- `Lab Submission` (Student write-up, PDF record link, viva marks, score overrides)
- `Proctored Session` (Tab switch violation tracking)

---

## 🧪 Testing

Run the automated 10-point end-to-end integration test suite:

```bash
bench --site coding.localhost execute coding_lms.test_runner.run_test
```

---

## 📄 License

MIT License. Designed for easy publication on the **Frappe Marketplace**.
