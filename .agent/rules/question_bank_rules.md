# Question Bank Rules & Schema Standards

1. Question Metadata & Taxonomy:
   - Category, Subject / Topic, Difficulty (Easy, Medium, Hard), Order, Timer (optional).
   - Problem Details: Title, Description (Markdown), Input Format, Output Format, Constraints, Expected Time & Space Complexity.

2. Multi-Snippet Architecture:
   - `starter_code`: Code template provided to the student in the editor.
   - `skeleton_code`: Optional wrapper or function signature.
   - `solution_code`: Reference author solution. Used to auto-generate expected outputs for testcases.
   - `programming_language_id`: Language selection.

3. Testcase Schema:
   - `description`: Testcase label or description.
   - `input`: Standard input string (supports `allow_empty_input: true`).
   - `expected_output`: Expected output string.
   - `is_public`: Boolean (1 = Public/Visible to student, 0 = Hidden).
   - `weightage`: Dynamic marks allocated to this specific testcase.
   - Evaluation Modes:
     - `mode`: `normal` (exact string comparison) or `regex` (`expected_regex`, `match_mode`: fullmatch/search/match, `regex_flags`: IGNORECASE, MULTILINE).
     - Text Normalizers: `ignore_space` (trim whitespace), `ignore_case` (case-insensitive).
     - Numeric Tolerance: `numeric_tolerance` (e.g. 0.001 tolerance for floating point outputs).

4. Whitelist & Blacklist Keyword Constraints:
   - `blacklist_keywords`: Comma-separated list of forbidden functions/keywords (e.g., `sort`, `reverse`, `eval`, `import os`).
     - Pre-execution AST check: Rejects submission if any blacklisted keyword is found.
   - `whitelist_keywords`: Comma-separated list of mandatory constructs (e.g., `while`, `recursion`, `malloc`).
     - Pre-execution check: Rejects submission if mandatory keyword is absent.
