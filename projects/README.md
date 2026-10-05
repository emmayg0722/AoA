# Client project data

The live workspace stores project data on the `codex/project-data` branch of this repository. This folder on `main` describes the format; it is not a separate copy of live projects.

```
projects/
  index.json
  <project-uuid>/
    project.json
    engagement.json
    phase-01-discovery-assessment/
      use-case-discovery-board/state.json
      ai-maturity-assessment/state.json
      ...
    phase-02-strategy-roadmap/
      ai-strategy-planning/state.json
      ...
    ...
    phase-10-roi-analysis-cost-optimization/
      roi-analysis/state.json
      ...
```

Each project initializes every existing saved tool listed in `project-workspace/registry.json`. State files contain `schemaVersion`, the original tool storage `key`, and `data` (`null` until the tool is used). The manifest holds client/project names and durable members keyed by GitHub login. No credentials or raw profiler uploads are stored here.

AoA is public. Project names, client names, saved tool contents and commit history are publicly readable. Participants acknowledge this before writing. Each participant uses their own GitHub write permission; a display name alone does not grant access.

Project updates use atomic Git trees and commits with a non-forced branch update. Independent object fields merge. Competing edits to the same field or an array require an explicit choice. The browser retains pending edits for recovery and offers a JSON download. Saving succeeds only after GitHub accepts the branch update.
