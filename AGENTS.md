# Standalone `coding_lms` Repository Rules & Architecture Guide

Welcome to **`coding_lms`**, a high-performance, marketplace-ready Frappe LMS extension integrated with the **Judge0** execution sandbox engine.

---

## 1. Core Architecture & Marketplace Guarantees
1. **Marketplace & Upgrade-Proof Design**:
   - Zero monkey-patching or core Frappe LMS modifications.
   - All custom logic connects via `hooks.py`, custom DocTypes, and Frappe `@frappe.whitelist()` APIs.
   - Uses Frappe's standard PDF engine (`frappe.utils.pdf.get_pdf`) and Jinja templates.
2. **Decoupled Execution Microservice**:
   - Judge0 handles raw code sandboxing (C, C++, Python, Java, JS).
   - Frappe backend handles question management, dynamic testcase evaluation, regex matching, and score tracking.

---

## 2. Core Functional Modules

### A. Coding Question Bank
- Dedicated, searchable Question Bank (Topics, Difficulty, Tags).
- Dynamic testcase configurations: Empty input (`stdin: ""`), Full Match, Regex Match (`fullmatch`, `search`, flags), Hidden testcases, and Dynamic Marks per testcase.

### B. Unified CodeRunner / Test Module
- Single, embeddable component inside Frappe LMS lessons or standalone exams.
- Dynamic mode switching:
  - **`practice` mode**: Run sample testcases + optional hidden testcase verification for lesson completion.
  - **`exam` mode**: Full proctoring enabled (tab switch threshold, auto-submit on limit, copy/paste block). Evaluates all testcases on submit.

### C. 3-Step Lab Course Workflow
- **Pre-Lab (Self-Paced)**: Basic coding questions, auto-graded, gates access to In-Lab.
- **In-Lab (Instructor Unlocked & Secure)**:
  - Locked by default; unlocked per section by instructor with section password.
  - Mandatory fields: Aim, Algorithm / Procedure, Conclusion.
  - Intermediate/advanced coding work.
  - **Automated PDF Lab Record**: Generates `Experiment_<RollNo>_<ID>.pdf` on submit and stores it as an immutable record.
- **Post-Lab (Review & Viva)**:
  - Instructor reviews generated PDF report.
  - Reviews Pre-Lab and In-Lab auto scores.
  - Enters Viva marks and optional score overrides (system audits both original and updated scores).
  - Final score calculation: `Pre-Lab + In-Lab + Viva`.

### D. Multi-Section Scoping & Security
- Single Lab Course assigned across multiple sections/departments.
- Instructor for Section A can ONLY view, unlock, evaluate, and access reports for Section A students. Section B data is strictly hidden. Admins can view all.

---

## 3. Prompt Engineering & Code Standards
- **Frappe ORM**: Use `frappe.get_doc`, `frappe.db.get_value`, no raw SQL strings.
- **Permission Hooks**: Enforce section scoping via `permission_query_conditions` in `hooks.py`.
- **Defensive Execution**: Always handle empty inputs safely and wrap regex in `re.error` try/except blocks.
- **Client Security**: Atomic tab-switch counters, immediate auto-submit triggers, and proper event listener cleanup on component unmount.
