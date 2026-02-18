# Cline Marketplace Submission Package

This directory contains all materials needed for submitting `atlas-session-lifecycle` to the Cline AI extension marketplace.

---

## Package Contents

```
cline-submission/
├── README.md                    # This file
├── marketplace-listing.md       # Full marketplace submission details
├── assets/                      # Images and media
│   ├── icon.png                # 128x128px extension icon
│   ├── banner.png              # 1280x640px promotional banner
│   └── screenshots/            # In-app screenshots (4-8 recommended)
│       ├── init-mode.png
│       ├── reconcile-mode.png
│       ├── memory-bank.png
│       └── file-organization.png
└── verification/               # Installation testing results
    └── test-results.md
```

---

## Installation Test Procedure

To verify the installation works in a clean environment:

```bash
# 1. Clean test (no existing installation)
docker run --rm -it python:3.11 bash -c "
  apt-get update && apt-get install -y git curl
  curl -fsSL https://raw.githubusercontent.com/anombyte93/atlas-session-lifecycle/main/install.sh | bash
  ls -la ~/.claude/skills/start/
  cat ~/.claude/skills/start/SKILL.md | head -20
"

# 2. Upgrade test
docker run --rm -it python:3.11 bash -c "
  apt-get update && apt-get install -y git curl
  # Install v1 first
  curl -fsSL https://raw.githubusercontent.com/anombyte93/atlas-session-lifecycle/main/install.sh | bash -s -- --version v1
  # Then upgrade to v2
  curl -fsSL https://raw.githubusercontent.com/anombyte93/atlas-session-lifecycle/main/install.sh | bash
  grep -q 'session-init.py' ~/.claude/skills/start/SKILL.md && echo 'Upgrade successful'
"
```

---

## Submission Steps

1. **Create assets** (icon, banner, screenshots)
   - Use Figma, Canva, or similar
   - Follow Cline marketplace guidelines for dimensions
   - Ensure brand consistency

2. **Test installation** in clean environments
   - Linux (Ubuntu/Debian)
   - macOS
   - Windows (WSL)

3. **Prepare submission form**
   - Copy content from `marketplace-listing.md`
   - Fill in all required fields
   - Upload assets

4. **Submit for review**
   - Double-check all fields
   - Ensure license is correctly specified
   - Verify repository link

5. **Post-submission**
   - Monitor for review feedback
   - Respond to any questions promptly
   - Make requested adjustments

---

## Current Status

| Step | Status | Notes |
|------|--------|-------|
| Content preparation | ✅ Complete | All copy written |
| llms-install.md | ✅ Complete | Created at project root |
| Marketplace listing | ✅ Complete | Full details documented |
| Icon | ⏳ Pending | Need 128x128px PNG |
| Banner | ⏳ Pending | Need 1280x640px PNG |
| Screenshots | ⏳ Pending | Need 4-8 screenshots |
| Installation test | ⏳ Pending | Run in Docker |

---

## Brand Guidelines

### Colors
- Primary: #00D4AA (Atlas Teal)
- Secondary: #1A1A2E (Dark Navy)
- Accent: #FF6B6B (Coral)

### Typography
- Headings: Inter, Bold
- Body: Inter, Regular
- Code: JetBrains Mono

### Voice
- Direct and concise
- No fluff or unnecessary words
- Action-oriented
- Developer-focused

---

## Contact

For questions about this submission:
- **GitHub**: https://github.com/anombyte93/atlas-session-lifecycle
- **Author**: Atlas AI (https://atlas-ai.au)
