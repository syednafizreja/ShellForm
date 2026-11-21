# Issue tracker: GitHub

Issues and specs for this repo live as GitHub issues in `syednafizreja/ShellForm`. Use the `gh` CLI for all operations.

## Conventions

- Create an issue: `gh issue create --title "..." --body "..."`
- Read an issue: `gh issue view <number> --json number,title,body,labels,comments`
- List open issues: `gh issue list --state open --json number,title,body,labels,comments`
- Comment on an issue: `gh issue comment <number> --body "..."`
- Apply or remove labels: `gh issue edit <number> --add-label "..."` or `gh issue edit <number> --remove-label "..."`
- Close an issue: add the explanation, then run `gh issue close <number>`

Infer the repository from `git remote -v`. Confirm `gh repo view --json nameWithOwner` targets `syednafizreja/ShellForm` before creating an issue.

## Pull requests

**PRs as a request surface: no.**
