# Economy workflow
Optimize total work, not just answer length. Preserve correctness and necessary checks.
For each task, identify the requested result and acceptance criteria. Keep plans short.
Search filenames and matching lines first; read only relevant file sections. Expand when evidence requires it.
Do not load dependency directories, generated bundles, full logs or unrelated files by default.
Keep raw diagnostic output in local files; report relevant errors and exit status. Never hide failures.
Make focused edits. Do not rewrite working files or redesign unrelated parts of a site.
Run relevant checks once after the final edit; repeat only after changes or new evidence.
After two failed attempts with the same approach, reassess the cause before trying again.
Use tools for deterministic calculations and text processing rather than reproducing them in prose.
Do simple work directly. Use economy-scout only for a bounded search that would otherwise flood context.
Do not start agent teams, background loops or repeated audits merely to save tokens.
Do not switch models, reduce reasoning or remove tools mid-task without a concrete need.
At a task boundary, offer a compact handoff if useful: goal, completed work, changed paths, checks, remaining work.
Never clear context automatically or claim to know usage statistics that were not measured.
Final answer: result, checks, unresolved issues. Be brief unless detail is requested.
For website changes, preserve existing URLs, metadata and working checkout unless the task requires changes.
