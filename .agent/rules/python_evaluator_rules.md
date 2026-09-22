# Python Evaluator Rules

1. Null-Safe Inputs: Always handle `stdin: ""` or empty input strings safely without throwing null pointer exceptions.
2. Regex Safety: Always wrap `re.compile()` and `re.fullmatch()` or `re.search()` in `try...except re.error:`.
3. Support Regex Flags: Parse `IGNORECASE` and `MULTILINE` flags dynamically from testcase configuration.
