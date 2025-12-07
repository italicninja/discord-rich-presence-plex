# Documentation Index

Quick reference guide to all documentation files in this repository.

## 📖 User Documentation

### [README.md](README.md)
**Start here!** Main project documentation with installation instructions, configuration guide, and usage examples.

**Contents:**
- Installation (Windows executable & Python script)
- Configuration reference
- Obtaining Imgur client ID
- Dynamic buttons and URLs
- Docker setup

---

### [CHANGELOG.md](CHANGELOG.md)
Version history and release notes for all versions.

**Contents:**
- What's new in each version
- Bug fixes and improvements
- Upgrade instructions

---

## 🛠️ Developer Documentation

### [CLAUDE.md](CLAUDE.md)
Development guide and architecture overview for Claude Code and other developers.

**Contents:**
- Running the application (dev, executable, Docker)
- Architecture overview
- Core components and data flow
- Directory structure
- Key modules
- Testing notes

---

### [RELEASING.md](RELEASING.md)
Complete guide to creating and publishing new releases.

**Contents:**
- Version bump checklist
- GitHub Actions automation
- Manual release process
- Troubleshooting guide

---

## 🔧 Technical Documentation

### [APPDATA_MIGRATION.md](APPDATA_MIGRATION.md)
Technical details of the Windows AppData storage implementation (v2.13.0+).

**Contents:**
- Implementation details
- Migration logic
- Platform compatibility
- Testing procedures
- Troubleshooting
- Future enhancements

---

## 📂 Project Structure Quick Reference

```
discord-rich-presence-plex/
│
├── 📄 README.md                    # User documentation
├── 📄 CHANGELOG.md                 # Version history
├── 📄 CLAUDE.md                    # Developer guide
├── 📄 RELEASING.md                 # Release process
├── 📄 APPDATA_MIGRATION.md         # AppData implementation details
├── 📄 DOCS.md                      # This file
│
├── 📁 core/                        # Core business logic
├── 📁 models/                      # Type definitions
├── 📁 utils/                       # Utility functions
├── 📁 config/                      # Application constants
├── 📁 .github/workflows/           # CI/CD automation
│
├── 🐍 main.py                      # CLI version
├── 🐍 main_tray.py                 # System tray version
├── ⚙️ PlexDiscordRPC.spec          # PyInstaller config
├── 📦 build.bat                    # Build script
│
└── 📁 .archive/                    # Historical docs (deprecated)
```

---

## 🗃️ Archived Documentation

Historical development documents are archived in [.archive/](.archive/) folder:

- Phase completion notes (Phase 1, Phase 3)
- CI/CD setup documentation
- Troubleshooting guides from initial deployment
- Original conversion plan

These are kept for reference but are **no longer maintained**. See [.archive/README.md](.archive/README.md) for details.

---

## 🚀 Quick Links

### For Users
- **Installation**: [README.md#installation](README.md#installation)
- **Configuration**: [README.md#configuration](README.md#configuration)
- **What's New**: [CHANGELOG.md](CHANGELOG.md)

### For Developers
- **Architecture**: [CLAUDE.md#architecture](CLAUDE.md#architecture)
- **Building**: [CLAUDE.md#running-the-application](CLAUDE.md#running-the-application)
- **Releasing**: [RELEASING.md](RELEASING.md)

### For Contributors
- **Code Style**: [CLAUDE.md](CLAUDE.md)
- **Testing**: [CLAUDE.md#testing](CLAUDE.md#testing)
- **CI/CD**: [RELEASING.md](RELEASING.md)

---

## 📝 Documentation Standards

When updating documentation:

1. **README.md** - User-facing changes, new features, configuration options
2. **CHANGELOG.md** - All version changes, following [Keep a Changelog](https://keepachangelog.com/)
3. **CLAUDE.md** - Architecture changes, new modules, development processes
4. **RELEASING.md** - Changes to release process or CI/CD
5. **APPDATA_MIGRATION.md** - Technical implementation details (when applicable)

---

## ❓ Need Help?

- **Installation Issues**: See [README.md](README.md)
- **Configuration Help**: See [README.md#configuration](README.md#configuration)
- **Development Questions**: See [CLAUDE.md](CLAUDE.md)
- **Release Process**: See [RELEASING.md](RELEASING.md)
- **Bug Reports**: [GitHub Issues](https://github.com/italicninja/discord-rich-presence-plex/issues)

---

**Last Updated**: Version 2.13.0 (December 5, 2024)
