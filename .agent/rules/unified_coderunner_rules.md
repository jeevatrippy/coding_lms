# Unified CodeRunner & Output Panel UI Rules

1. Single Reusable Component: One unified editor component with dynamic props (`mode: 'practice' | 'exam'`).
2. UI/UX OutputPanel Structure (Matching mgc_lms_assessment standard):
   - Dual Tabs: "Console Output" (terminal view) + "Test Cases" (interactive cards).
   - Initial State (Before Run):
     - Displays total testcases count badge (e.g., "5 Test Cases Available").
     - Lists all Public/Sample testcases with "Public" chip, Input box, and Expected Output box.
   - Result State (After Run / Submit):
     - Summary Banner: Green if all passed, Red if any failed (e.g., "Passed: 3 / 5").
     - Individual Testcase Cards:
       - Header: "Test Case N", Public chip (if public), "Passed" (green chip) or "Failed" (red chip).
       - Input & Expected Output: Visible for public testcases, masked as italic "Hidden" for hidden testcases.
       - Actual Output: Red-highlighted box showing student's actual output for failed testcases.
       - Compiler / Runtime Error Box: Formatted error stack trace if compilation or execution failed.
