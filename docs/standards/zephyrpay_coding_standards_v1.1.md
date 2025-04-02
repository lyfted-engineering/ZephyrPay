# ZephyrPay Coding Standards V1.1
*Updated: April 1, 2025*

## Introduction
These coding standards guide our development team in building the secure ZephyrPay cryptocurrency payment platform. The principles focus on code quality, security, collaboration, and Behavior-Driven Development (BDD) specifically tailored for our FastAPI and PostgreSQL backend.

## 📋 Backlog Management
We manage our backlog via GitHub Issues, ensuring all work follows a structured workflow.

### Standard Workflow
1. Start with the next prioritized issue in the backlog
2. Branch Naming Convention:
   - `feature/{id}` for new features (e.g., feature/15 for wallet linking)
   - `bug/{id}` for bug fixes
   - `chore/{id}` for maintenance tasks (e.g., dependency updates, refactoring)
3. TDD Workflow:
   - Write BDD-style tests first (WIP: Red Tests)
   - Implement code to make them pass (WIP: Green Tests)
   - Refactor and commit with clear message (Refactor complete)
4. Pull Request Process:
   - Mark issue as Finished in issues.md
   - Create a PR with detailed description of changes
   - **Ensure test coverage meets or exceeds 90%**
   - Merge with --no-ff to preserve feature branch history
5. Issue Closure: Update issues.md to reflect completed work.

## 📖 Issue Types & Estimation
We classify work into Features, Bugs, and Chores with complexity-based prioritization.

### Story Estimation Guidelines
- Small: Quick implementations like schema updates, single endpoint additions.
- Medium: Features requiring multiple components like Registration, Login.
- Large: Complex features with external integrations like Wallet Linking, Lightning Payments.

### Current Roadmap Priority
1. User Authentication (Registration, Login, Password Recovery) 
2. Role-Based Access Control (RBAC) 
3. Wallet Integration (ETH and LN) 
4. Payment Processing

## 🎨 Coding Style Guidelines
We enforce a consistent style across the ZephyrPay codebase.

### Python-Specific Standards
- Naming Conventions: Use snake_case for functions/variables, PascalCase for classes
- Module Structure: Group by feature (auth, payments, wallets)
- Docstrings: Use descriptive docstrings with Args/Returns/Raises sections
- Type Hints: Include typing annotations for all function parameters and returns
- Error Handling: Use custom error classes from core.errors

### FastAPI Standards
- Endpoint Organization: Group under appropriate routers by feature
- Response Models: Define explicit Pydantic models for all responses
- Status Codes: Use appropriate HTTP status codes consistently
- Dependency Injection: Use FastAPI's dependency injection for database sessions

## 🧪 Testing Strategy (TDD/BDD) - UPDATED
We implement Test-Driven Development (TDD) and Behavior-Driven Development (BDD) for all features.

### Test Coverage Requirements - UPDATED
- **Minimum Coverage Requirement: 90%** for all components
- Security-Critical Components (auth, roles, payments): Target 95%+ coverage
- For financial applications like ZephyrPay, comprehensive test coverage is essential
- PRs will not be approved without meeting the 90% threshold
- Current RBAC coverage: 98% (Core: 100%, Schemas: 100%, Services: 95%, API: 97%)

### RBAC Testing Guidelines - NEW
- **Permission Tests**: Every role-restricted endpoint must have tests for:
  - Successful access by authorized roles
  - Denied access by unauthorized roles
  - Anonymous access attempts
- **Integration Tests**: All RBAC components must be tested together:
  - User creation with role assignment
  - Role verification and validation
  - Admin role management operations
  - Permission enforcement across endpoints
- **Edge Cases**: Must test boundary conditions:
  - Self-role modification attempts
  - Non-existent user role operations
  - Invalid role values
  - Token manipulation attempts

### SQLAlchemy Session Handling - NEW
When writing tests with async SQLAlchemy:
- Store needed model attributes as primitive values before session closes
- Never access model attributes after the session might close
- Use early data extraction to avoid MissingGreenlet errors
- Consider using dictionaries for fixtures to avoid session dependency

```python
# GOOD: Extract data before session closes
@pytest.fixture
async def test_user(db: AsyncSession):
    user = User(email="test@example.com")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Extract needed data before returning
    user_id = user.id
    return {"id": user_id, "email": user.email}

# BAD: Returning model directly can cause session issues
@pytest.fixture
async def bad_test_user(db: AsyncSession):
    user = User(email="test@example.com")
    db.add(user)
    await db.commit()
    return user  # Don't do this - will cause session issues
```

### Test Structure
- Unit Tests: For service and utility functions
- API Tests: For testing endpoint behavior
- Integration Tests: For database and external service interactions
- End-to-End Tests: For testing complete user workflows across multiple components

### No-Mock Policy
- Database Interactions: Must use real database connections (in-memory SQLite for tests)
- API Calls: External API integrations must be tested against actual endpoints or local test servers
- No Mock Libraries: Do not use mocking libraries to simulate database or API behavior
- Test Data: Use actual database seeding and test fixtures rather than mocked responses
- Exceptions: Any exception to this policy requires explicit justification and approval

### Example ZephyrPay BDD Test:
```python
def test_login_success(self, client: TestClient):
    """
    Scenario: Successful login
    Given I am a registered user
    When I submit valid credentials
    Then I should receive a JWT token
    And the response status should be 200 OK
    """
    # Arrange - Create a test user (using actual DB operations)
    register_data = {
        "email": "logintest@example.com",
        "password": "StrongP@ssw0rd",
        "username": "loginuser"
    }
    # Act & Assert implementation using real database interactions
```

## 🔄 Continuous Integration
We maintain code quality through testing standards.

### Test Requirements
- All tests must pass before merge
- Coverage must meet or exceed 90%
- New features require BDD-style test scenarios
- Tests must run against actual in-memory SQLite database
- External API tests must use real endpoints or local test servers
- No mocking of database or API calls permitted

## 🔧 Version Control Practices
Our GitHub workflow ensures collaboration and code quality.

### Key GitHub Practices
- Feature Branches: Create a new branch for each issue
- Commit Messages: Follow pattern "Issue #{id}: Action - Details"
- WIP Commits: Use descriptive messages indicating TDD phase
- PR Descriptions: Summarize changes, testing approach, and coverage
- Non-Fast-Forward Merges: Use --no-ff to maintain branch history

## ⚙️ ZephyrPay Architecture
The platform follows a clean architecture pattern:

- API Layer: FastAPI endpoints and routers
- Services Layer: Business logic and operations
- Data Layer: SQLAlchemy models and database interaction
- Core: Configuration, security, and utilities

### Technology Stack:
- Backend: Python with FastAPI
- Database: PostgreSQL with SQLAlchemy ORM (SQLite for testing)
- Authentication: JWT tokens
- Validation: Pydantic models
- Testing: Pytest with coverage reporting and real database connections

### Testing Environment
- Use in-memory SQLite for test database
- Set up proper seed data for each test suite
- Reset database state between tests
- Never mock database calls or external API responses
- Use dependency injection to swap production services with test versions while maintaining real behavior

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
    body: "Implements role assignment feature with tests and 95% coverage",
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
    body: "Completed with feature/15 branch. All tests passing with 94.75% coverage."
)
```

Reference: Always use the proper `mcp0_` prefix for GitHub operations to maintain workflow consistency.

## Change Log
- v1.0 (March 15, 2025): Initial standards document
- v1.1 (April 1, 2025): 
  - Updated test coverage requirement to 90% minimum
  - Added comprehensive integration testing requirement
  - Formalized documentation standards for API endpoints
  - Added RBAC completion to roadmap priority
  - Updated Testing Strategy section with more detailed RBAC testing standards
  - Added GitHub MCP API Call Reference Guide
