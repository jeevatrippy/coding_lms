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

        // 3. Copy AI Master Prompt Button
        frm.add_custom_button(__('Copy AI Prompt'), function() {
            copy_ai_prompt_to_clipboard();
        });

        // 4. Preview Student Editor Views (Approach A vs B)
        frm.add_custom_button(__('Student View Preview'), function() {
            open_student_view_preview(frm);
        }, __('Actions'));

        // 5. Auto-generate outputs under Actions menu
        frm.add_custom_button(__('Auto-Generate Outputs'), function() {
            auto_generate_testcase_outputs(frm);
        }, __('Actions'));
    }
});

const MASTER_AI_PROMPT = "You are an expert competitive programming problem architect and JSON generator for an online coding assessment platform.\n\nI will provide input in one of two formats:\n- FORMAT A: Just the problem title and description.\n- FORMAT B: Problem title, description, code snippets, skeleton, and test cases.\n\nYour task is to return ONLY a single, valid, raw JSON object (strictly NO markdown backticks, NO markdown formatting around the JSON, NO explanations, NO introductory or concluding text).\n\n### APPROACH A vs APPROACH B (STUDENT CODE EDITOR MODES):\n1. APPROACH A (Competitive Programming / Full Boilerplate):\n   - The student sees \"starter_code\" containing the complete file (imports, function stub, and main() driver reading stdin and printing stdout).\n   - Use this when testing I/O handling, low-level pointers, or full program compilation.\n2. APPROACH B (LeetCode / Function-Only Mode):\n   - The student sees \"skeleton_code\" containing ONLY the clean function or class signature (no main, no scanf/cin, no print).\n   - Behind the scenes, the driver wraps this function when submitting to compiler sandbox.\n   - Use this for algorithmic puzzles, LeetCode style problems, and clean logic evaluations.\n\n### STRICT JSON SYNTAX RULES:\n1. Double Quotes Inside Code: Any double quotes inside string fields (like printf(\\\"%d\\\"), scanf(\\\"%d %d\\\"), puts(\\\"\\\"), print(\\\"Hello\\\")) MUST BE STRICTLY ESCAPED AS \\\\\". Never leave unescaped raw double quotes inside JSON code strings.\n2. C Null Terminator: In C strings, write null terminator as '\\\\\\\\0' (double backslash), not '\\\\0'.\n3. Newlines and Tabs: Encode newlines as \\\\n and tabs as \\\\t.\n4. Regex Output: Whenever an output has formatted labels, prefixes, or punctuation (e.g. 'Sum: 40', 'Status: OK'), set mode='regex', expected_regex='^Label:\\\\\\\\s*pattern$', and match_mode='fullmatch'.\n\n### STRICT JSON OUTPUT SCHEMA:\n{\n  \"title\": \"<Problem Title>\",\n  \"difficulty\": \"<Easy | Medium | Hard>\",\n  \"language\": \"<python | java | cpp | c | javascript | typescript | go | rust | csharp | php | ruby | kotlin | swift | sql | bash>\",\n  \"code_editor_mode\": \"<Competitive Mode (Full Code with main & stdin) | LeetCode Mode (Pure Function Signature only)>\",\n  \"timer\": 20,\n  \"time_limit\": 2.0,\n  \"memory_limit\": 256,\n  \"content\": \"<Problem statement in clean Markdown with rules and examples>\",\n  \"input_format\": \"<Explanation of standard input lines>\",\n  \"output_format\": \"<Explanation of expected standard output>\",\n  \"constraints\": \"<Mathematical bounds, e.g. 1 <= N <= 10^5>\",\n  \"expected_time_complexity\": \"<e.g. O(N)>\",\n  \"expected_space_complexity\": \"<e.g. O(1)>\",\n  \"skeleton_code\": \"<Pure function signature only (Approach B / LeetCode style)>\",\n  \"starter_code\": \"<Full runnable code with main() and stdin/stdout (Approach A / Competitive style)>\",\n  \"solution_code\": \"<Complete optimal solution that compiles and passes in Judge0>\",\n  \"whitelist_keywords\": \"<Optional comma-separated mandatory constructs, or empty>\",\n  \"blacklist_keywords\": \"<Optional comma-separated forbidden words like 'eval, exec', or empty>\",\n  \"testcases\": [\n    {\n      \"description\": \"<Label for testcase>\",\n      \"input\": \"<stdin string with \\\\n for newlines>\",\n      \"expected_output\": \"<stdout string for normal mode, or empty string if regex>\",\n      \"weightage\": 20,\n      \"is_public\": 1,\n      \"allow_empty_input\": 0,\n      \"mode\": \"<normal | regex>\",\n      \"expected_regex\": \"<regex pattern if mode is regex, otherwise empty string>\",\n      \"match_mode\": \"<fullmatch | search>\",\n      \"regex_flags\": \"<IGNORECASE | MULTILINE | ''>\",\n      \"ignore_space\": 1,\n      \"ignore_case\": 0,\n      \"numeric_tolerance\": 0.0\n    }\n  ]\n}";

function copy_ai_prompt_to_clipboard() {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(MASTER_AI_PROMPT).then(() => {
            frappe.show_alert({
                message: __('Master AI Prompt copied to clipboard! Paste it into ChatGPT or Claude.'),
                indicator: 'green'
            });
        }).catch(err => {
            fallback_copy();
        });
    } else {
        fallback_copy();
    }
}

function fallback_copy() {
    const ta = document.createElement('textarea');
    ta.value = MASTER_AI_PROMPT;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    frappe.show_alert({
        message: __('Master AI Prompt copied to clipboard!'),
        indicator: 'green'
    });
}

function open_student_view_preview(frm) {
    const current_mode = frm.doc.code_editor_mode || 'Competitive Mode (Full Code with main & stdin)';
    const starter_code = frm.doc.starter_code || '// No starter code configured yet.';
    const skeleton_code = frm.doc.skeleton_code || '// No skeleton signature configured yet.';

    const html = `
        <div style="margin-bottom: 15px;">
            <p style="font-size: 13px; color: #555; margin-bottom: 12px;">
                Choose how students will experience this problem in their editor. You can switch between 
                <strong>Approach A (Competitive Full Boilerplate)</strong> and <strong>Approach B (LeetCode Function-Only)</strong>.
            </p>
            <div class="btn-group" role="group" style="width: 100%; display: flex; margin-bottom: 15px;">
                <button type="button" class="btn btn-default active" id="btn-tab-approach-a" style="flex: 1; font-weight: 600;">
                    Approach A: Competitive Mode (Full Code)
                </button>
                <button type="button" class="btn btn-default" id="btn-tab-approach-b" style="flex: 1; font-weight: 600;">
                    Approach B: LeetCode Mode (Function-Only)
                </button>
            </div>
        </div>

        <!-- APPROACH A CONTAINER -->
        <div id="view-approach-a" style="display: block;">
            <div style="background: #eef7ff; border-left: 4px solid #2085ec; padding: 12px; border-radius: 4px; margin-bottom: 12px; font-size: 12px;">
                <strong>What the student sees on screen:</strong> The full program including <code>#include</code>, function signature, and the <code>main()</code> driver with <code>scanf/cin</code> and <code>printf/cout</code>.
                <br><strong>Best for:</strong> Standard college labs, competitive programming, and pointer/memory manipulation where full I/O control is required.
            </div>
            <div style="background: #1e1e1e; color: #d4d4d4; border-radius: 8px; padding: 16px; font-family: monospace; font-size: 12px; max-height: 320px; overflow-y: auto;">
                <div style="color: #6a9955; margin-bottom: 8px;">// === STUDENT CODE EDITOR (Full Runnable Template) ===</div>
                <pre style="color: #d4d4d4; background: transparent; border: none; padding: 0; margin: 0; font-family: inherit; font-size: inherit;">` + frappe_escape(starter_code) + `</pre>
            </div>
        </div>

        <!-- APPROACH B CONTAINER -->
        <div id="view-approach-b" style="display: none;">
            <div style="background: #fdf3e7; border-left: 4px solid #f39c12; padding: 12px; border-radius: 4px; margin-bottom: 12px; font-size: 12px;">
                <strong>What the student sees on screen:</strong> Only the clean function signature (like LeetCode). The student never deals with <code>scanf</code> or <code>int main()</code>.
                <br><strong>Best for:</strong> Algorithm interview practice and clean data structures where students focus purely on logic while backend drivers handle inputs.
            </div>
            <div style="background: #1e1e1e; color: #d4d4d4; border-radius: 8px; padding: 16px; font-family: monospace; font-size: 12px; max-height: 320px; overflow-y: auto;">
                <div style="color: #6a9955; margin-bottom: 8px;">// === STUDENT CODE EDITOR (Pure Function Contract) ===</div>
                <pre style="color: #d4d4d4; background: transparent; border: none; padding: 0; margin: 0; font-family: inherit; font-size: inherit;">` + frappe_escape(skeleton_code) + `</pre>
            </div>
        </div>
    `;

    const dialog = new frappe.ui.Dialog({
        title: __('Student Editor View Modes (Approach A vs Approach B)'),
        fields: [
            {
                fieldname: 'preview_html',
                fieldtype: 'HTML',
                options: html
            },
            {
                fieldname: 'selected_mode',
                label: __('Apply Mode to this Question'),
                fieldtype: 'Select',
                options: [
                    'Competitive Mode (Full Code with main & stdin)',
                    'LeetCode Mode (Pure Function Signature only)'
                ],
                default: current_mode
            }
        ],
        size: 'large',
        primary_action_label: __('Save Selected Mode'),
        primary_action: function(values) {
            frm.set_value('code_editor_mode', values.selected_mode);
            dialog.hide();
            frappe.show_alert({
                message: __('Student Editor Mode updated to: ' + values.selected_mode),
                indicator: 'green'
            });
        }
    });

    dialog.show();

    setTimeout(() => {
        const btnA = document.getElementById('btn-tab-approach-a');
        const btnB = document.getElementById('btn-tab-approach-b');
        const viewA = document.getElementById('view-approach-a');
        const viewB = document.getElementById('view-approach-b');

        if (btnA && btnB) {
            btnA.onclick = function() {
                btnA.classList.add('active');
                btnB.classList.remove('active');
                viewA.style.display = 'block';
                viewB.style.display = 'none';
                dialog.set_value('selected_mode', 'Competitive Mode (Full Code with main & stdin)');
            };

            btnB.onclick = function() {
                btnB.classList.add('active');
                btnA.classList.remove('active');
                viewA.style.display = 'none';
                viewB.style.display = 'block';
                dialog.set_value('selected_mode', 'LeetCode Mode (Pure Function Signature only)');
            };

            if (current_mode.indexOf('LeetCode') !== -1) {
                btnB.click();
            } else {
                btnA.click();
            }
        }
    }, 200);
}

function frappe_escape(str) {
    if (window.frappe && frappe.utils && frappe.utils.escape_html) {
        return frappe.utils.escape_html(str);
    }
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function clean_inner_quotes(val) {
    let s = val.replace(/\\"/g, '___PROTECTED_ESCAPED_QUOTE___');
    s = s.replace(/"/g, '\\"');
    s = s.replace(/___PROTECTED_ESCAPED_QUOTE___/g, '\\"');
    return s;
}

function repair_json_text(text) {
    if (!text) return text;
    let s = text.replace(/\\0/g, '___ESCAPED_NULL___')
                .replace(/\0/g, '\\0')
                .replace(/___ESCAPED_NULL___/g, '\\0');

    // 1. Repair unescaped quotes in known code / multiline fields
    const fields = ['starter_code', 'solution_code', 'skeleton_code', 'content'];
    fields.forEach(f => {
        const pattern = new RegExp('("' + f + '"\\s*:\\s*")(.*?)("(?=\\s*(?:,\\s*"[a-zA-Z0-9_]+"\\s*:|\\s*})))', 'gs');
        s = s.replace(pattern, (match, prefix, val, suffix) => {
            return prefix + clean_inner_quotes(val) + suffix;
        });
    });

    // 2. Repair invalid regex escape sequences (e.g. \[5,\s*6\])
    s = s.replace(/\\\\/g, '___DOUBLE_BACKSLASH___');
    s = s.replace(/\\([^"\\\/bfnrtu]|u(?!([0-9a-fA-F]{4})))/g, '\\\\$1');
    s = s.replace(/___DOUBLE_BACKSLASH___/g, '\\\\');

    return s;
}

function open_json_import_dialog(frm) {
    const dialog = new frappe.ui.Dialog({
        title: __('Import Coding Problem from JSON'),
        fields: [
            {
                fieldname: 'prompt_help_html',
                fieldtype: 'HTML',
                options: `
                    <div style="background: #f0f7ff; border: 1px solid #cce5ff; border-radius: 6px; padding: 10px 14px; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
                        <span style="font-size: 12px; color: #004085;">
                            Generate problem JSON effortlessly with ChatGPT or Claude.
                        </span>
                        <button type="button" class="btn btn-xs btn-primary" id="btn-copy-prompt-inside" style="font-weight: 600;">
                            Copy Master AI Prompt
                        </button>
                    </div>
                `
            },
            {
                fieldname: 'json_file',
                label: __('Upload JSON File (Optional)'),
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
                description: __('Paste problem JSON here. Supports automatic syntax repair for unescaped code quotes.')
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
                        message: __('Could not parse JSON: ' + e1.message + '<br><br><b>Tip:</b> If your code contains double quotes (like <code>scanf("%s")</code>), they must be escaped as <code>\"</code>.')
                    });
                    return;
                }
            }

            if (data.title) frm.set_value('title', data.title);
            if (data.difficulty) {
                const diff = data.difficulty.charAt(0).toUpperCase() + data.difficulty.slice(1).toLowerCase();
                frm.set_value('difficulty', diff);
            }
            if (data.language) {
                const lang = data.language.toLowerCase().replace('python3', 'python').replace('nodejs', 'javascript');
                frm.set_value('language', lang);
            }
            if (data.code_editor_mode) {
                frm.set_value('code_editor_mode', data.code_editor_mode);
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
            if (data.starter_code) frm.set_value('starter_code', data.starter_code);
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
                message: auto_repaired 
                    ? __('Problem imported successfully (auto-repaired unescaped quotes)!') 
                    : __('Problem details and ' + raw_tcs.length + ' test cases successfully imported!'),
                indicator: 'green'
            });
            dialog.hide();
        }
    });

    dialog.show();

    setTimeout(() => {
        const btn = document.getElementById('btn-copy-prompt-inside');
        if (btn) {
            btn.onclick = function() {
                copy_ai_prompt_to_clipboard();
            };
        }
    }, 200);
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

    frappe.dom.freeze(__('Submitting solution to execution sandbox across ' + tcs.length + ' test cases...'));

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
    const has_compile_err = !!res.compilation_error;
    const has_runtime_err = !!res.runtime_error;

    let banner_color = passed ? '#d4edda' : '#f8d7da';
    let banner_text_color = passed ? '#155724' : '#721c24';
    let banner_border = passed ? '#c3e6cb' : '#f5c6cb';
    let badge_status_text = passed ? 'VALIDATED' : (has_compile_err ? 'COMPILATION ERROR' : (has_runtime_err ? 'RUNTIME ERROR' : 'ISSUES DETECTED'));
    const icon = passed ? '&#10004;' : '&#10008;';

    let html = `
        <div style="background-color: ${banner_color}; color: ${banner_text_color}; border: 1px solid ${banner_border}; border-radius: 8px; padding: 16px; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h4 style="margin: 0; font-weight: bold;">
                    ${icon} ` + (passed ? 'All ' + res.passed_count + '/' + res.total_testcases + ' Test Cases PASSED!' : res.passed_count + '/' + res.total_testcases + ' Test Cases Passed') + `
                </h4>
                <p style="margin: 4px 0 0 0; font-size: 13px; opacity: 0.9;">
                    Sandbox Execution Engine &bull; Language: ${frappe_escape(frm.doc.language || 'c')}
                </p>
            </div>
            <div>
                <span class="badge ${passed ? 'badge-success' : 'badge-danger'}" style="font-size: 13px; padding: 6px 12px; font-weight: 600;">
                    ${badge_status_text}
                </span>
            </div>
        </div>
    `;

    if (has_compile_err) {
        html += `
            <div style="background-color: #fff5f5; border: 1px solid #feb2b2; border-left: 5px solid #e53e3e; border-radius: 6px; padding: 14px 16px; margin-bottom: 16px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                    <span style="font-weight: 700; color: #9b2c2c; font-size: 13.5px;">
                        &#9888; Compilation / Build Error Diagnostics
                    </span>
                    <span class="badge badge-danger" style="font-size: 10.5px; padding: 3px 8px;">BUILD FAILED</span>
                </div>
                <div style="font-size: 12px; color: #742a2a; margin-bottom: 8px;">
                    The solution failed to compile. Inspect the compiler diagnostic messages and line numbers below:
                </div>
                <pre style="background: #1a202c; color: #fc8181; border: 1px solid #2d3748; border-radius: 5px; padding: 12px; font-family: 'Consolas', 'Courier New', monospace; font-size: 11.5px; max-height: 220px; overflow-y: auto; white-space: pre-wrap; margin-bottom: 0;">` + frappe_escape(res.compilation_error) + `</pre>
            </div>
        `;
    } else if (has_runtime_err) {
        html += `
            <div style="background-color: #fffaf0; border: 1px solid #feebc8; border-left: 5px solid #dd6b20; border-radius: 6px; padding: 14px 16px; margin-bottom: 16px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                    <span style="font-weight: 700; color: #9c4221; font-size: 13.5px;">
                        &#9888; Runtime Error (Exception / Signal)
                    </span>
                    <span class="badge badge-warning" style="font-size: 10.5px; padding: 3px 8px;">RUNTIME ERROR</span>
                </div>
                <div style="font-size: 12px; color: #7b341e; margin-bottom: 8px;">
                    An unexpected crash or non-zero exit status occurred during execution:
                </div>
                <pre style="background: #1a202c; color: #fbd38d; border: 1px solid #2d3748; border-radius: 5px; padding: 12px; font-family: 'Consolas', 'Courier New', monospace; font-size: 11.5px; max-height: 180px; overflow-y: auto; white-space: pre-wrap; margin-bottom: 0;">` + frappe_escape(res.runtime_error) + `</pre>
            </div>
        `;
    }

    html += `
        <div style="max-height: 480px; overflow-y: auto;">
            <table class="table table-bordered table-hover" style="font-size: 12px; margin-bottom: 0;">
                <thead style="background: #f8f9fa;">
                    <tr>
                        <th style="width: 40px; text-align: center;">#</th>
                        <th style="width: 220px;">Test Case & Input (stdin)</th>
                        <th style="width: 100px; text-align: center;">Status</th>
                        <th style="width: 85px; text-align: center;">Time / RAM</th>
                        <th style="min-width: 260px;">Output & Verification</th>
                    </tr>
                </thead>
                <tbody>
    `;

    res.results.forEach((r, i) => {
        let badge_class = 'badge-danger';
        if (r.passed) {
            badge_class = 'badge-success';
        } else if (r.status && (r.status.includes('Compilation') || r.status.includes('Compile'))) {
            badge_class = 'badge-danger';
        } else if (r.status && r.status.includes('Runtime')) {
            badge_class = 'badge-warning';
        } else if (r.status && r.status.includes('Time Limit')) {
            badge_class = 'badge-secondary';
        }

        const expected_prefix = (r.mode === 'regex') ? 'Expected Pattern (Regex)' : 'Expected Output';
        const expected_val = (r.mode === 'regex') ? (r.expected_regex || '(none)') : (r.expected_output || '(blank)');
        
        html += `
            <tr style="${!r.passed ? 'background-color: #fff8f8;' : ''}">
                <td style="text-align: center; vertical-align: top;"><strong>${r.index}</strong></td>
                <td style="vertical-align: top;">
                    <div style="font-weight: 600; color: #2d3748;">` + frappe_escape(r.description) + `</div>
                    <div style="color: #718096; font-size: 10.5px; margin-top: 2px;">
                        Mode: <span class="badge badge-light" style="border: 1px solid #cbd5e0; font-size: 10px;">${frappe_escape(r.mode.toUpperCase())}</span>
                    </div>
                    <div style="margin-top: 6px;">
                        <div style="font-size: 10px; font-weight: 700; color: #4a5568;">INPUT (stdin):</div>
                        ` + (r.input ? `
                            <pre style="margin: 2px 0 0 0; padding: 4px 6px; font-size: 11px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px; max-height: 75px; overflow-y: auto; white-space: pre-wrap; font-family: monospace;">` + frappe_escape(r.input) + `</pre>
                        ` : `
                            <div style="font-size: 10.5px; color: #a0aec0; font-style: italic; margin-top: 2px;">(no stdin input)</div>
                        `) + `
                    </div>
                </td>
                <td style="text-align: center; vertical-align: top;">
                    <span class="badge ${badge_class}" style="font-size: 11px; padding: 4px 8px;">${frappe_escape(r.status)}</span>
                </td>
                <td style="font-family: monospace; text-align: center; vertical-align: top; font-size: 11px;">
                    <div>${r.time}</div>
                    <div style="color: #718096; font-size: 10px; margin-top: 2px;">${r.memory}</div>
                </td>
                <td style="vertical-align: top;">
                    ${r.actual_output ? `
                        <div style="font-size: 10px; font-weight: 700; color: #4a5568; margin-bottom: 2px;">ACTUAL OUTPUT (stdout):</div>
                        <pre style="margin: 0 0 6px 0; padding: 6px 8px; font-size: 11px; background: #fdfdfd; border: 1px solid #e2e8f0; border-radius: 4px; max-height: 90px; overflow-y: auto; white-space: pre-wrap; font-family: monospace;">` + frappe_escape(r.actual_output) + `</pre>
                    ` : (has_compile_err ? `
                        <div style="color: #a0aec0; font-style: italic; font-size: 11px; margin-bottom: 4px;">(No stdout: compilation failed)</div>
                    ` : `
                        <div style="color: #a0aec0; font-style: italic; font-size: 11px; margin-bottom: 4px;">(no stdout output)</div>
                    `)}
                    
                    ${r.error ? `
                        <div style="margin: 4px 0; padding: 6px 8px; background: #fff5f5; border: 1px solid #feb2b2; border-radius: 4px;">
                            <div style="font-size: 10px; font-weight: 700; color: #9b2c2c;">ERROR / STDERR:</div>
                            <pre style="margin: 2px 0 0 0; padding: 0; background: transparent; border: none; font-size: 11px; color: #9b2c2c; max-height: 100px; overflow-y: auto; white-space: pre-wrap; font-family: monospace;">` + frappe_escape(r.error) + `</pre>
                        </div>
                    ` : ''}
                    
                    <div style="font-size: 10.5px; color: #4a5568; margin-top: 4px;">
                        <strong>${expected_prefix}:</strong> <code style="font-size: 11px; background: #edf2f7; color: #2d3748; padding: 2px 5px; border-radius: 3px; white-space: pre-wrap; word-break: break-all;">` + frappe_escape(expected_val) + `</code>
                    </div>
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
        title: __('Problem Execution Verification'),
        fields: [
            {
                fieldname: 'results_html',
                fieldtype: 'HTML',
                options: html
            }
        ],
        size: 'large'
    });

    const has_blank = res.results.some(r => r.is_blank_expected && r.actual_output);
    if (has_blank) {
        d.set_primary_action(__('Fill Blank Expected Outputs with Execution Results'), function() {
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
