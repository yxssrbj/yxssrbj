# Weekly contributions chart

- [x] Add a failing test for weekly totals and chart output.
- [x] Generate a deterministic SVG from GitHub's contribution calendar.
- [x] Add a daily/manual workflow and link the SVG in `README.md`.
- [ ] Run focused tests, typecheck, and a real workflow run.
- [ ] Inspect the profile and update `STATUS.md`.

Decision: use GitHub GraphQL and the built-in workflow token so the chart
stays in this repository. The chart shows public contribution counts if
the token cannot read private activity.
