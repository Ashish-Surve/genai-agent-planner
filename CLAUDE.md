# ADHD-Planner Project Memory

## About This Project
This project is maintained by Ashish. All Claude instances working on this codebase should follow the guidelines below.

## Git Workflow for Jira Tickets

When working on any Jira ticket, ALWAYS follow this Pull Request workflow:

### 1. Create a New Branch
- Create a feature branch from `dev` with a descriptive name
- Branch naming convention: `feature/ADHD-XXX-description` (where XXX is the Jira ticket number)
- Example: `feature/ADHD-123-add-task-scheduler`
- For bug fixes: `fix/ADHD-XXX-description`
- For documentation: `docs/ADHD-XXX-description`
- Always verify you're on `dev` before creating a new branch

### 2. Make Changes and Commit
- Make your code changes on the feature branch
- Update the `.jira/README.md` file to document what was completed
- Stage and commit changes with proper commit messages (see format below)
- NEVER commit directly to `dev` or `main` branches

### 3. Push the New Branch
- Push your feature branch to the remote repository
- Use: `git push -u origin <branch-name>` for the first push
- Verify the push was successful before proceeding

### 4. Raise a Pull Request
- Create a pull request from your feature branch to `dev` (NOT main)
- Use `gh pr create --base dev` command with proper title and description
- Include Jira ticket reference in PR title
- Add test plan and summary in PR description
- Link to the Jira ticket in the PR description
- **Important**: For documentation-only PRs, also raise a separate PR to `dev` for tracking

## Commit Message Format

All commits MUST be tagged with: **"Claude by Ashish"**

Use this exact format for commit messages:

```
type(ADHD-XXX): Brief description of changes

Detailed explanation if needed (optional).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Committed-By: Claude by Ashish
```

### Commit Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `style`: Code style/formatting changes
- `perf`: Performance improvements

### Examples
```
feat(ADHD-15): Add task priority sorting feature

Implements drag-and-drop priority sorting for tasks with local storage persistence.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
Committed-By: Claude by Ashish
```

## Important Rules

1. **NEVER push directly to dev or main** - Always work on a feature branch
2. **ALWAYS create a PR** - Even for small changes, create PR to `dev`
3. **ALWAYS tag commits** - Include "Claude by Ashish" in all commit messages
4. **ALWAYS link Jira tickets** - Reference ticket number in branch name, commits, and PRs
5. **ALWAYS update .jira/README.md** - Document completed work before committing
6. **ALWAYS push before creating PR** - Ensure branch is pushed to remote first
7. **Use --base dev flag** - When creating PRs with gh CLI: `gh pr create --base dev`
8. **Separate docs PRs** - Documentation updates should be in separate PRs from code changes
9. **gh location** - /opt/homebrew/bin/gh
## My Identity
I am Claude (Sonnet 4.5), working on behalf of Ashish on the ADHD-Planner project.
