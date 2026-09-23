frappe.ui.form.on('Coding Problem', {
    refresh(frm) {
        // 1. JSON Importer Button
        frm.add_custom_button(__('Import JSON'), function() {
            open_json_import_dialog(frm);
        }).addClass('btn-primary');

        // 2. Test Problem (Run with Judge0) Button
        frm.add_custom_button(__('Test Problem (Run)'), function() {
            run_problem_test_suite(frm);
        }).addClass('btn-success');

        // 3. Auto-generate outputs under Actions menu
        frm.add_custom_button(__('Auto-Generate Outputs'), function() {
            auto_generate_testcase_outputs(frm);
        }, __('Actions'));
    }
});

// Sample JSON Templates
const SAMPLE_TEMPLATES = {
    'standard_python': {
        title: "Two Sum",
        difficulty: "Easy",
        language: "python",
        timer: 20,
        time_limit: 2.0,
        memory_limit: 256,
        content: "Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to target.\n\nYou may assume each input has exactly one solution.",
        input_format: "First line: space-separated integers nums.\nSecond line: target integer.",
        output_format: "Two indices separated by space.",
        constraints: "2 <= nums.length <= 10^4\n-10^9 <= nums[i] <= 10^9",
        expected_time_complexity: "O(n)",
        expected_space_complexity: "O(n)",
        starter_code: "def two_sum(nums, target):\n    # Write your solution here\n    pass\n\nif __name__ == '__main__':\n    nums = list(map(int, input().split()))\n    target = int(input())\n    res = two_sum(nums, target)\n    print(f'{res[0]} {res[1]}')\n",
        solution_code: "def two_sum(nums, target):\n    lookup = {}\n    for i, num in enumerate(nums):\n        diff = target - num\n        if diff in lookup:\n            return [lookup[diff], i]\n        lookup[num] = i\n    return []\n\nif __name__ == '__main__':\n    nums = list(map(int, input().split()))\n    target = int(input())\n    res = two_sum(nums, target)\n    print(f'{res[0]} {res[1]}')\n",
        whitelist_keywords: "",
        blacklist_keywords: "",
        testcases: [
            {
                description: "Sample 1",
                input: "2 7 11 15\n9",
                expected_output: "0 1",
                weightage: 20,
                is_public: 1,
                mode: "normal",
                ignore_space: 1
            },
            {
                description: "Sample 2 (Adjacent)",
                input: "3 2 4\n6",
                expected_output: "1 2",
                weightage: 40,
                is_public: 1,
                mode: "normal",
                ignore_space: 1
            },
            {
                description: "Hidden Case (Large numbers)",
                input: "1000 2000 3000 4000\n7000",
                expected_output: "2 3",
                weightage: 40,
                is_public: 0,
                mode: "normal",
                ignore_space: 1
            }
        ]
    },
    'regex_parser': {
        title: "Command Calculator (Regex Match)",
        difficulty: "Medium",
        language: "python",
        timer: 30,
        time_limit: 2.0,
        memory_limit: 256,
        content: "Parse commands from stdin in the format `SUM <n1> <n2>` or `MUL <n1> <n2>`. Output `Sum: <res>` or `Product: <res>`. Print `Invalid` otherwise.",
        input_format: "Lines of text commands.",
        output_format: "Formatted calculation result.",
        constraints: "Numbers are non-negative integers.",
        expected_time_complexity: "O(1)",
        expected_space_complexity: "O(1)",
        starter_code: "import sys\nimport re\n\n# Implement command parser\n",
        solution_code: "import sys\nimport re\n\nfor line in sys.stdin:\n    line = line.strip()\n    if not line: continue\n    m = re.fullmatch(r'^(SUM|MUL)\\s+(\\d+)\\s+(\\d+)$', line)\n    if m:\n        op, a, b = m.groups()\n        if op == 'SUM':\n            print(f'Sum: {int(a)+int(b)}')\n        else:\n            print(f'Product: {int(a)*int(b)}')\n    else:\n        print('Invalid')\n",
        whitelist_keywords: "re",
        blacklist_keywords: "eval, exec",
        testcases: [
            {
                description: "Sum Command",
                input: "SUM 10 20",
                expected_regex: "^Sum:\\s*30$",
                match_mode: "fullmatch",
                weightage: 25,
                is_public: 1,
                mode: "regex"
            },
            {
                description: "Mul Command",
                input: "MUL 5 6",
                expected_regex: "^Product:\\s*30$",
                match_mode: "fullmatch",
                weightage: 25,
                is_public: 1,
                mode: "regex"
            },
            {
                description: "Invalid Command",
                input: "DIV 10 2",
                expected_regex: "^Invalid$",
                match_mode: "fullmatch",
                weightage: 25,
                is_public: 1,
                mode: "regex"
            },
            {
                description: "Hidden Edge Case",
                input: "SUM 0 0",
                expected_regex: "^Sum:\\s*0$",
                match_mode: "fullmatch",
                weightage: 25,
                is_public: 0,
                mode: "regex"
            }
        ]
    },
    'tolerance_float': {
        title: "Circle Area with Numeric Tolerance",
        difficulty: "Easy",
        language: "python",
        timer: 15,
        time_limit: 2.0,
        memory_limit: 256,
        content: "Given radius `r`, calculate and print the area of the circle (pi * r^2). Answers within 0.01 tolerance are accepted.",
        input_format: "A single float r.",
        output_format: "Area of the circle.",
        constraints: "0 <= r <= 1000",
        expected_time_complexity: "O(1)",
        expected_space_complexity: "O(1)",
        starter_code: "import math\nr = float(input())\n# Output area\n",
        solution_code: "import math\nr = float(input())\nprint(math.pi * r * r)\n",
        testcases: [
            {
                description: "Radius 1",
                input: "1.0",
                expected_output: "3.14159",
                weightage: 50,
                is_public: 1,
                mode: "normal",
                numeric_tolerance: 0.01
            },
            {
                description: "Radius 5",
                input: "5.0",
                expected_output: "78.5398",
                weightage: 50,
                is_public: 1,
                mode: "normal",
                numeric_tolerance: 0.01
            }
        ]
    }
};

function open_json_import_dialog(frm) {
    const dialog = new frappe.ui.Dialog({
        title: __('Import Coding Problem from JSON'),
        fields: [
            {
                fieldname: 'template',
                label: __('Load Sample Template (Optional)'),
                fieldtype: 'Select',
                options: [
                    '',
                    'Standard Problem (Python Two Sum)',
                    'Regex Pattern Matcher (Calculator)',
                    'Numeric Tolerance (Float Calculation)'
                ],
                change: function() {
                    const val = dialog.get_value('template');
                    if (val === 'Standard Problem (Python Two Sum)') {
                        dialog.set_value('json_data', JSON.stringify(SAMPLE_TEMPLATES.standard_python, null, 2));
                    } else if (val === 'Regex Pattern Matcher (Calculator)') {
                        dialog.set_value('json_data', JSON.stringify(SAMPLE_TEMPLATES.regex_parser, null, 2));
                    } else if (val === 'Numeric Tolerance (Float Calculation)') {
                        dialog.set_value('json_data', JSON.stringify(SAMPLE_TEMPLATES.tolerance_float, null, 2));
                    }
                }
            },
            {
                fieldname: 'json_file',
                label: __('Or Upload JSON File'),
                fieldtype: 'Attach',
                change: function() {
                    const file_url = dialog.get_value('json_file');
                    if (file_url) {
                        fetch(file_url)
                            .then(res => res.text())
                            .then(text => {
                                dialog.set_value('json_data', text);
                            })
                            .catch(err => {
                                frappe.msgprint(__('Failed to read uploaded file: ' + err.message));
                            });
                    }
                }
            },
            {
                fieldname: 'json_data',
                label: __('JSON Data'),
                fieldtype: 'Code',
                options: 'JSON',
                reqd: 1,
                description: __('Paste problem JSON here. Supports standard schemas, test cases, and constraints.')
            }
        ],
        size: 'large',
        primary_action_label: __('Import & Populate Form'),
        primary_action: function(values) {
            let data;
            let auto_repaired = false;
            try {
                data = JSON.parse(values.json_data);
            } catch (e1) {
                try {
                    const repaired = repair_json_text(values.json_data);
                    data = JSON.parse(repaired);
                    auto_repaired = true;
                } catch (e2) {
                    frappe.msgprint({
                        title: __('Invalid JSON Format'),
                        indicator: 'red',
                        message: __('Could not parse JSON: ' + e1.message + '<br><br><b>Tip:</b> If your code contains double quotes (like <code>scanf("%s")</code>), they must be escaped as <code>\\"</code>.')
                    });
                    return;
                }
            }

            // Populate form fields
            if (data.title) frm.set_value('title', data.title);
            if (data.difficulty) {
                const diff = data.difficulty.charAt(0).toUpperCase() + data.difficulty.slice(1).toLowerCase();
                frm.set_value('difficulty', diff);
            }
            if (data.language) {
                const lang = data.language.toLowerCase().replace('python3', 'python').replace('nodejs', 'javascript');
                frm.set_value('language', lang);
            }
            if (data.timer !== undefined) frm.set_value('timer', data.timer);
            if (data.time_limit !== undefined) {
                const tl = parseFloat(data.time_limit);
                frm.set_value('time_limit', tl > 50 ? tl / 1000.0 : tl);
            }
            if (data.memory_limit !== undefined) frm.set_value('memory_limit', parseInt(data.memory_limit));
            if (data.content || data.description) frm.set_value('content', data.content || data.description);
            if (data.input_format) frm.set_value('input_format', data.input_format);
            if (data.output_format) frm.set_value('output_format', data.output_format);
            if (data.constraints) frm.set_value('constraints', data.constraints);
            if (data.expected_time_complexity) frm.set_value('expected_time_complexity', data.expected_time_complexity);
            if (data.expected_space_complexity) frm.set_value('expected_space_complexity', data.expected_space_complexity);
            if (data.starter_code || data.skeleton_code) frm.set_value('starter_code', data.starter_code || data.skeleton_code);
            if (data.skeleton_code) frm.set_value('skeleton_code', data.skeleton_code);
            if (data.solution_code || data.code) frm.set_value('solution_code', data.solution_code || data.code);
            
            if (data.blacklist_keywords) {
                const bl = Array.isArray(data.blacklist_keywords) ? data.blacklist_keywords.join(', ') : data.blacklist_keywords;
                frm.set_value('blacklist_keywords', bl);
            }
            if (data.whitelist_keywords) {
                const wl = Array.isArray(data.whitelist_keywords) ? data.whitelist_keywords.join(', ') : data.whitelist_keywords;
                frm.set_value('whitelist_keywords', wl);
            }

            // Populate Testcases
            const raw_tcs = data.testcases || data.test_cases || [];
            if (Array.isArray(raw_tcs) && raw_tcs.length > 0) {
                frm.clear_table('testcases');
                raw_tcs.forEach((tc, idx) => {
                    const row = frm.add_child('testcases');
                    row.description = tc.description || tc.name || ('Test Case ' + (idx + 1));
                    row.input = tc.input !== undefined ? tc.input : (tc.input_data || '');
                    row.expected_output = tc.expected_output !== undefined ? tc.expected_output : '';
                    row.weightage = tc.weightage !== undefined ? tc.weightage : 10;
                    row.is_public = tc.is_public !== undefined ? (tc.is_public ? 1 : 0) : 1;
                    row.allow_empty_input = tc.allow_empty_input ? 1 : 0;
                    row.mode = (tc.mode || (tc.expected_regex ? 'regex' : 'normal')).toLowerCase();
                    row.expected_regex = tc.expected_regex || '';
                    row.match_mode = tc.match_mode || 'fullmatch';
                    row.regex_flags = tc.regex_flags || '';
                    row.ignore_space = tc.ignore_space !== undefined ? (tc.ignore_space ? 1 : 0) : 1;
                    row.ignore_case = tc.ignore_case ? 1 : 0;
                    row.numeric_tolerance = tc.numeric_tolerance !== undefined && tc.numeric_tolerance !== null ? tc.numeric_tolerance : 0.0;
                });
                frm.refresh_field('testcases');
            }

            frappe.show_alert({
                message: __('Problem details and ' + raw_tcs.length + ' test cases successfully imported!'),
                indicator: 'green'
            });
            dialog.hide();
        }
    });

    dialog.show();
}

function run_problem_test_suite(frm) {
    if (!frm.doc.solution_code) {
        frappe.msgprint({
            title: __('Reference Solution Missing'),
            indicator: 'orange',
            message: __('Please enter Reference Solution Code to test against the test cases.')
        });
        return;
    }

    const tcs = frm.doc.testcases || [];
    if (tcs.length === 0) {
        frappe.msgprint({
            title: __('No Test Cases'),
            indicator: 'orange',
            message: __('Please add at least one test case before running the test suite.')
        });
        return;
    }

    frappe.dom.freeze(__('Submitting solution to Judge0 sandbox across ' + tcs.length + ' test cases...'));

    frappe.call({
        method: 'coding_lms.api.evaluator.test_problem_draft',
        args: {
            solution_code: frm.doc.solution_code,
            language: frm.doc.language || 'python',
            testcases: JSON.stringify(tcs),
            time_limit: frm.doc.time_limit || 2.0,
            memory_limit: frm.doc.memory_limit || 256,
            whitelist_keywords: frm.doc.whitelist_keywords || '',
            blacklist_keywords: frm.doc.blacklist_keywords || ''
        },
        callback: function(r) {
            frappe.dom.unfreeze();
            if (!r || !r.message) {
                frappe.msgprint(__('No response received from evaluation engine.'));
                return;
            }

            const res = r.message;
            if (!res.success) {
                frappe.msgprint({
                    title: res.status || __('Test Error'),
                    indicator: 'red',
                    message: res.error || __('Failed to run testcases.')
                });
                return;
            }

            render_test_results_dialog(frm, res);
        }
    });
}

function render_test_results_dialog(frm, res) {
    const passed = res.all_passed;
    const banner_color = passed ? '#d4edda' : '#f8d7da';
    const banner_text_color = passed ? '#155724' : '#721c24';
    const banner_border = passed ? '#c3e6cb' : '#f5c6cb';
    const icon = passed ? '&#10004;' : '&#10008;';

    let html = `
        <div style="background-color: ${banner_color}; color: ${banner_text_color}; border: 1px solid ${banner_border}; border-radius: 8px; padding: 16px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h4 style="margin: 0; font-weight: bold;">
                    ${icon} ${passed ? 'All ' + res.passed_count + '/' + res.total_testcases + ' Test Cases PASSED!' : res.passed_count + '/' + res.total_testcases + ' Test Cases Passed'}
                </h4>
                <p style="margin: 4px 0 0 0; font-size: 13px; opacity: 0.9;">
                    Compiler: Judge0 Sandboxed Execution &bull; Language: ${frm.doc.language || 'python'}
                </p>
            </div>
            <div>
                <span class="badge ${passed ? 'badge-success' : 'badge-danger'}" style="font-size: 14px; padding: 6px 12px;">
                    ${passed ? 'VALIDATED' : 'ISSUES DETECTED'}
                </span>
            </div>
        </div>

        <div style="max-height: 480px; overflow-y: auto;">
            <table class="table table-bordered table-hover" style="font-size: 12px; margin-bottom: 0;">
                <thead style="background: #f8f9fa;">
                    <tr>
                        <th style="width: 50px;">#</th>
                        <th>Description / Mode</th>
                        <th style="width: 110px;">Status</th>
                        <th style="width: 80px;">Time</th>
                        <th style="width: 90px;">Memory</th>
                        <th>Actual Output (stdout)</th>
                    </tr>
                </thead>
                <tbody>
    `;

    res.results.forEach((r, i) => {
        const badge_class = r.passed ? 'badge-success' : 'badge-danger';
        const expected_label = r.mode === 'regex' ? 'Regex: ' + (r.expected_regex || '(none)') : 'Expected: ' + (r.expected_output || '(blank)');
        
        html += `
            <tr style="${!r.passed ? 'background-color: #fff8f8;' : ''}">
                <td><strong>${r.index}</strong></td>
                <td>
                    <div style="font-weight: 600;">${frappe.utils.escape_html(r.description)}</div>
                    <div style="color: #6c757d; font-size: 11px;">
                        Mode: <span class="badge badge-light" style="border: 1px solid #ddd;">${r.mode.toUpperCase()}</span>
                    </div>
                </td>
                <td>
                    <span class="badge ${badge_class}">${r.status}</span>
                </td>
                <td style="font-family: monospace;">${r.time}</td>
                <td style="font-family: monospace;">${r.memory}</td>
                <td>
                    <pre style="margin: 0; padding: 4px 8px; font-size: 11px; background: #fdfdfd; border: 1px solid #eee; border-radius: 4px; max-height: 80px; overflow-y: auto;">${frappe.utils.escape_html(r.actual_output || '(no output)')}</pre>
                    ${r.error ? '<div class="text-danger" style="font-size: 11px; margin-top: 4px;"><strong>Error:</strong> ' + frappe.utils.escape_html(r.error) + '</div>' : ''}
                    <div style="font-size: 10px; color: #888; margin-top: 2px;">${frappe.utils.escape_html(expected_label)}</div>
                </td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>
    `;

    const d = new frappe.ui.Dialog({
        title: __('Problem Execution Verification (Judge0)'),
        fields: [
            {
                fieldname: 'results_html',
                fieldtype: 'HTML',
                options: html
            }
        ],
        size: 'large'
    });

    // Check if any test cases had blank outputs that were generated
    const has_blank = res.results.some(r => r.is_blank_expected && r.actual_output);
    if (has_blank) {
        d.set_primary_action(__('Fill Blank Expected Outputs with Judge0 Results'), function() {
            res.results.forEach((r, idx) => {
                if (r.is_blank_expected && r.actual_output && frm.doc.testcases[idx]) {
                    if (r.mode === 'regex') {
                        frm.doc.testcases[idx].expected_regex = '^' + r.actual_output.trim() + '$';
                    } else {
                        frm.doc.testcases[idx].expected_output = r.actual_output;
                    }
                }
            });
            frm.refresh_field('testcases');
            frappe.show_alert({ message: __('Expected outputs populated!'), indicator: 'green' });
            d.hide();
        });
    }

    d.show();
}

function auto_generate_testcase_outputs(frm) {
    if (!frm.doc.solution_code) {
        frappe.msgprint(__('Please provide Reference Solution Code first.'));
        return;
    }
    run_problem_test_suite(frm);
}


function clean_inner_quotes(val) {
    return val.replace(/\\"/g, '___ESCAPED_QUOTE___')
              .replace(/"/g, '\\"')
              .replace(/___ESCAPED_QUOTE___/g, '\\"');
}

function repair_json_text(text) {
    if (!text) return text;
    // 1. Fix unescaped \0 (null byte in C strings)
    let s = text.replace(/\\\\0/g, '___ESCAPED_NULL___')
                .replace(/\\0/g, '\\\\0')
                .replace(/___ESCAPED_NULL___/g, '\\\\0');

    // 2. Fix unescaped double quotes inside code and text fields
    const fields = ['starter_code', 'solution_code', 'skeleton_code', 'content'];
    fields.forEach(f => {
        const pattern = new RegExp('("' + f + '"\\s*:\\s*")(.*?)("(?=\\s*,\\s*"[a-zA-Z0-9_]+"\\s*:))', 'gs');
        s = s.replace(pattern, (match, prefix, val, suffix) => {
            return prefix + clean_inner_quotes(val) + suffix;
        });
    });
    return s;
}
