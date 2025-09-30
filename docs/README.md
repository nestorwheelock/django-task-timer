# Django Task Timer Documentation

This directory contains all project documentation following the AI-Native Development Workflow.

## Directory Structure

```
docs/
├── README.md              # This file - documentation index
├── specs/                 # Specification documents for each version
│   └── v0.1.0-spec.md    # Version 0.1.0 specification and approval package
├── approvals/             # Client approval records
│   ├── approval-log.md   # Chronological log of all approvals
│   └── v0.1.0-spec-approval-form.md
├── acceptance/            # Acceptance test results
│   └── v0.1.0-acceptance.md (created during testing)
└── architecture/          # Technical architecture documentation
    └── (created as needed)
```

## Development Phases

This project follows a 5-phase workflow with 2 mandatory client approval gates:

1. **SPEC Phase** - Requirements and planning
2. **🚦 CLIENT APPROVAL GATE #1** - Client approves spec before build
3. **BUILD Phase** - TDD implementation
4. **VALIDATION Phase** - Internal QA
5. **ACCEPTANCE TEST Phase** - Client hands-on testing
6. **🚦 CLIENT APPROVAL GATE #2** - Client approves before ship
7. **SHIP Phase** - Deployment and release

## Current Status

**Epoch 1 (v0.1.0) - Foundation**
- ✅ SPEC Phase: Complete
- ⏳ CLIENT APPROVAL GATE #1: Pending review
- ⬜ BUILD Phase: Not started
- ⬜ VALIDATION Phase: Not started
- ⬜ ACCEPTANCE TEST Phase: Not started
- ⬜ CLIENT APPROVAL GATE #2: Not started
- ⬜ SHIP Phase: Not started

## Quick Links

- [v0.1.0 Specification](specs/v0.1.0-spec.md) - Full requirements and approval package
- [Approval Log](approvals/approval-log.md) - History of all client approvals
- [Project README](../README.md) - Main project documentation

## For Reviewers

If you're reviewing a specification:
1. Read the SPEC document in `specs/`
2. Review user stories and acceptance criteria
3. Check scope boundaries (what IS and IS NOT included)
4. Review technical architecture and risks
5. Complete the approval form in `approvals/`
6. Return signed form to development team

## For Developers

- Never start BUILD without CLIENT APPROVAL GATE #1 sign-off
- Never ship without CLIENT APPROVAL GATE #2 sign-off
- Keep documentation current throughout development
- Update status section above as phases complete
