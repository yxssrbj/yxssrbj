# Weekly contributions chart

- [x] Add a failing test for weekly totals and chart output.
- [x] Generate a deterministic SVG from GitHub's contribution calendar.
- [x] Add a daily/manual workflow and link the SVG in `README.md`.
- [x] Run focused tests, Python compilation, and a real workflow run.
- [x] Inspect the profile and update `STATUS.md`.

No Python type checker is configured in this repository or installed in
the workspace; `compileall` verified syntax instead.

Decision: use GitHub GraphQL and the built-in workflow token so the chart
stays in this repository. The chart shows public contribution counts if
the token cannot read private activity.
