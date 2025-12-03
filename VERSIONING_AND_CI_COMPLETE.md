# Version Tagging and CI/CD Pipeline Complete

## ✅ Completed Features

### 1. Version Embedding System
- ✅ Version sourced from single source of truth: `config/constants.py`
- ✅ Executable filename includes version: `PlexDiscordRPC-v2.12.0.exe`
- ✅ Windows version information embedded in .exe metadata
- ✅ Version visible in file properties (right-click → Properties → Details)

### 2. GitHub Actions CI/CD Pipeline
- ✅ **CI Workflow** (`ci.yml`): Builds on every push/PR
- ✅ **Release Workflow** (`build-release.yml`): Automated releases on git tags
- ✅ Automated executable building
- ✅ Automatic GitHub Release creation
- ✅ Release notes generation

### 3. Release Automation
- ✅ Tag-based releases (`v2.12.0` creates release)
- ✅ Executable uploaded as release asset
- ✅ Release notes auto-generated
- ✅ Manual workflow trigger option

## 📁 New/Modified Files

### New Files
- `generate_version_info.py` - Generates Windows version metadata
- `.github/workflows/ci.yml` - CI pipeline for testing
- `.github/workflows/build-release.yml` - Release automation
- `RELEASING.md` - Complete release process documentation

### Modified Files
- `config/constants.py` - Bumped to version 2.12.0
- `PlexDiscordRPC.spec` - Adds version to executable name
- `build.bat` - Includes version info generation step
- `.gitignore` - Excludes generated version_info.txt

## 🚀 How It Works

### Version System

```
config/constants.py (version = "2.12.0")
           ↓
generate_version_info.py
           ↓
   version_info.txt
           ↓
   PyInstaller build
           ↓
PlexDiscordRPC-v2.12.0.exe (with embedded metadata)
```

### CI/CD Pipeline

#### On Push/PR to Main:
```
Push to main → GitHub Actions → CI Build → Upload artifact (7 days)
```

#### On Version Tag:
```
git tag v2.12.0 → Push tag → GitHub Actions → Build → Create Release → Upload .exe
```

## 📋 Release Process

### Creating a New Release

1. **Update version** in `config/constants.py`:
   ```python
   version = "2.13.0"
   ```

2. **Commit and push**:
   ```bash
   git add config/constants.py
   git commit -m "Bump version to 2.13.0"
   git push
   ```

3. **Create and push tag**:
   ```bash
   git tag -a v2.13.0 -m "Release v2.13.0"
   git push origin v2.13.0
   ```

4. **GitHub Actions automatically**:
   - Builds `PlexDiscordRPC-v2.13.0.exe`
   - Creates GitHub Release
   - Uploads executable
   - Adds release notes

### Manual Build (Local)

```bash
# Generates version_info.txt and builds versioned .exe
build.bat
```

Output: `dist/PlexDiscordRPC-v2.12.0.exe`

## 🎯 GitHub Workflows

### CI Workflow (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `main` branch
- Pull requests to `main`

**Actions:**
1. Checkout code
2. Set up Python 3.13
3. Install dependencies
4. Generate version info
5. Build with PyInstaller
6. Upload artifact (7-day retention)

**Purpose:** Ensure builds work on every code change

### Release Workflow (`.github/workflows/build-release.yml`)

**Triggers:**
- Git tags matching `v*.*.*` (e.g., `v2.12.0`)
- Manual workflow dispatch

**Actions:**
1. Checkout code
2. Set up Python 3.13
3. Install dependencies
4. Generate version info
5. Build with PyInstaller
6. Create GitHub Release
7. Upload .exe as release asset
8. Auto-generate release notes

**Purpose:** Automated production releases

## 📊 Version Information Embedded

When you right-click the .exe → Properties → Details, you'll see:

| Property | Value |
|----------|-------|
| File description | Discord Rich Presence for Plex - System Tray Application |
| Product name | Discord Rich Presence for Plex |
| Product version | 2.12.0 |
| File version | 2.12.0 |
| Original filename | PlexDiscordRPC-v2.12.0.exe |
| Copyright | Open Source - See LICENSE file |
| Internal name | PlexDiscordRPC |

This helps users identify:
- Correct version downloaded
- Legitimate executable
- Professional appearance

## 🧪 Testing the Pipeline

### Test CI Build

1. Make any code change
2. Push to main
3. Go to GitHub → Actions
4. See "CI Build" workflow running
5. Download artifact after completion

### Test Release Build

1. Update version in `config/constants.py` (e.g., `2.12.1`)
2. Commit and push
3. Create tag:
   ```bash
   git tag v2.12.1
   git push origin v2.12.1
   ```
4. Go to GitHub → Actions → See "Build and Release" running
5. Go to GitHub → Releases → See new release created

## 📦 Distribution

### For Users

Users download from GitHub Releases:
1. Go to Releases page
2. Download latest `PlexDiscordRPC-vX.X.X.exe`
3. Run executable
4. No installation needed

### For Developers

Test builds available from CI:
1. Go to Actions tab
2. Click on latest CI build
3. Download "PlexDiscordRPC-Windows-CI" artifact
4. Extract and test

## 🔧 Customization

### Change Version

Edit `config/constants.py`:
```python
version = "3.0.0"  # Your new version
```

### Modify Release Notes

Edit `.github/workflows/build-release.yml`, section `body:` to customize release notes template.

### Change Executable Name

Edit `PlexDiscordRPC.spec`:
```python
name=f'PlexDiscordRPC-v{version}',  # Customize format here
```

## ⚠️ Important Notes

### Semantic Versioning

Follow semver: `MAJOR.MINOR.PATCH`
- **MAJOR**: Breaking changes (2.x.x → 3.0.0)
- **MINOR**: New features (2.12.x → 2.13.0)
- **PATCH**: Bug fixes (2.12.0 → 2.12.1)

### Git Tags

- Tags MUST start with `v` to trigger releases
- Use annotated tags: `git tag -a v2.12.0 -m "Release v2.12.0"`
- Lightweight tags work but annotated tags are recommended

### GitHub Permissions

Ensure GitHub Actions has permissions:
- Settings → Actions → General → Workflow permissions
- Set to: "Read and write permissions"

## 📝 Documentation

See `RELEASING.md` for complete release checklist and troubleshooting.

## ✨ Benefits

### For Users
✅ Easy to identify version from filename
✅ Version info visible in file properties
✅ Professional appearance
✅ Trusted source (GitHub Releases)

### For Developers
✅ Automated builds
✅ No manual executable creation
✅ Consistent versioning
✅ Easy rollback (previous releases available)
✅ CI ensures builds always work

### For Project
✅ Professional release process
✅ Version tracking
✅ Change history
✅ Easy collaboration

## 🎯 Success Criteria

- ✅ Executable includes version in filename
- ✅ Windows version info embedded
- ✅ CI builds on every push
- ✅ Releases automated on tags
- ✅ GitHub Releases created automatically
- ✅ Release notes generated
- ✅ Process documented
- ✅ Single source of truth for version

## 🚀 Next Steps

1. **Test the pipeline** by creating a test tag
2. **Create first official release** with current version
3. **Add to README** - Link to latest release
4. **Consider adding**:
   - CHANGELOG.md for version history
   - Code signing (eliminates Windows warnings)
   - Additional platforms (Linux with Wine?)

---

Version tagging and CI/CD pipeline complete! Your project now has professional automated builds and releases. 🎉
