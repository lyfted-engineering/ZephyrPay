## GitHub MCP API Call Reference Guide for ZephyrPay

All GitHub API calls in Cascade must be prefixed with `mcp0_` to function correctly.

### Issue Management
- `mcp0_create_issue`: Creates a new issue
  - Required parameters: owner, repo, title, body
  - Optional parameters: assignees, labels, milestone
  
- `mcp0_get_issue`: Get details of a specific issue
  - Required parameters: owner, repo, issue_number

- `mcp0_update_issue`: Update an existing issue
  - Required parameters: owner, repo, issue_number
  - Optional parameters: title, body, state ("open" or "closed"), labels, assignees

- `mcp0_add_issue_comment`: Add a comment to an existing issue
  - Required parameters: owner, repo, issue_number, body

- `mcp0_list_issues`: List issues in a repository
  - Required parameters: owner, repo
  - Optional parameters: state ("open", "closed", "all"), direction, sort, labels

### Branch and Pull Request Management
- `mcp0_create_branch`: Create a new branch
  - Required parameters: owner, repo, branch
  - Optional parameters: from_branch

- `mcp0_create_pull_request`: Create a new pull request
  - Required parameters: owner, repo, title, head, base
  - Optional parameters: body, draft, maintainer_can_modify

- `mcp0_merge_pull_request`: Merge a pull request
  - Required parameters: owner, repo, pull_number
  - Optional parameters: commit_title, commit_message, merge_method

### Example ZephyrPay GitHub Workflow

1. Create a new branch for issue #30:
```
mcp0_create_branch(
    owner: "lyfted-engineering",
    repo: "ZephyrPay",
    branch: "feature/30",
    from_branch: "main"
)
```

2. After implementation, create a PR:
```
mcp0_create_pull_request(
    owner: "lyfted-engineering",
    repo: "ZephyrPay",
    title: "Issue #30: Implement Role Assignment",
    body: "Implements role assignment feature with tests and 85% coverage",
    head: "feature/30",
    base: "main"
)
```

3. Update an issue to closed status:
```
mcp0_update_issue(
    owner: "lyfted-engineering",
    repo: "ZephyrPay",
    issue_number: 15,
    state: "closed",
    body: "Completed with feature/15 branch. All tests passing with 84.75% coverage."
)
```

Reference: Always use the proper `mcp0_` prefix for GitHub operations to maintain workflow consistency.
