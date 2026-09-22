# Client Proctoring Rules

1. Tab Switch Limit: Increment counter on `visibilitychange` (document.hidden) or window blur. If `count >= max_allowed`, trigger immediate `auto_submit()`.
2. Event Trap: Block `copy`, `cut`, `paste`, and `contextmenu` during active coding exams.
3. Event Cleanup: Always call `removeEventListener` when component unmounts to prevent memory leaks.
