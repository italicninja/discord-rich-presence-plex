#!/ Release Process for Discord Rich Presence for Plex

## Creating a New Release

### 1. Update Version

Edit `config/constants.py` and update the version:

```python
version = "2.13.0"  # Update to new version
```

### 2. Test Build Locally

Run the build script to ensure everything works:

```bash
build.bat
```

Verify:
- Build completes without errors
- `dist/PlexDiscordRPC-v2.13.0.exe` is created
- Executable runs correctly
- Version info is embedded (right-click exe → Properties → Details)

### 3. Commit Version Bump

```bash
git add config/constants.py
git commit -m "Bump version to 2.13.0"
git push
```

### 4. Create and Push Git Tag

```bash
# Create annotated tag
git tag -a v2.13.0 -m "Release v2.13.0"

# Push tag to trigger GitHub Actions
git push origin v2.13.0
```

### 5. GitHub Actions Automatically:
- ✅ Builds the executable
- ✅ Creates GitHub Release
- ✅ Uploads executable as release asset
- ✅ Generates release notes

### 6. Edit Release Notes (Optional)

Go to GitHub Releases and edit the auto-generated release to add:
- Changelog
- New features
- Bug fixes
- Breaking changes

## Version Numbering

We use Semantic Versioning (semver): `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes or major new features
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes

Examples:
- `2.12.0` → `2.13.0` - New feature (Windows tray app)
- `2.13.0` → `2.13.1` - Bug fix
- `2.13.0` → `3.0.0` - Breaking change

## Manual Release (Fallback)

If GitHub Actions fails, you can create a release manually:

1. Build locally:
   ```bash
   build.bat
   ```

2. Go to GitHub → Releases → Draft a new release

3. Create tag: `v2.13.0`

4. Upload `dist/PlexDiscordRPC-v2.13.0.exe`

5. Write release notes

6. Publish release

## Testing a Release

Before publishing:

1. Download the release artifact
2. Test on a clean Windows machine (no Python)
3. Verify:
   - Executable launches
   - System tray icon appears
   - Plex authentication works
   - Discord IPC connects
   - Config/log files created correctly

## Release Checklist

- [ ] Version updated in `config/constants.py`
- [ ] Local build successful
- [ ] Executable tested manually
- [ ] Version committed to git
- [ ] Git tag created and pushed
- [ ] GitHub Actions workflow succeeded
- [ ] Release published on GitHub
- [ ] Release tested by downloading from GitHub
- [ ] README updated if needed
- [ ] CHANGELOG updated (if exists)

## Troubleshooting

### Build Fails on GitHub Actions

Check:
- All dependencies in `requirements.txt`
- PyInstaller spec file is correct
- Version info generation works
- Icon files exist

### Executable Not Created

Check:
- PyInstaller logs in GitHub Actions
- Build artifacts uploaded
- File naming matches pattern `PlexDiscordRPC-v*.exe`

### Release Not Created

Check:
- Git tag starts with `v` (e.g., `v2.13.0`)
- `GITHUB_TOKEN` permissions
- GitHub Actions workflow permissions

## GitHub Actions Workflows

### build-release.yml
- Triggers on: Git tags (`v*.*.*`)
- Builds Windows executable
- Creates GitHub Release
- Uploads release asset

### ci.yml
- Triggers on: Push to main, Pull Requests
- Builds executable for testing
- Uploads artifact (7-day retention)
- Does NOT create release

## Viewing Builds

### CI Builds (main/PRs)
- Go to Actions tab
- Click on "CI Build" workflow
- Download artifacts for testing

### Release Builds
- Go to Releases tab
- Download official release executable
