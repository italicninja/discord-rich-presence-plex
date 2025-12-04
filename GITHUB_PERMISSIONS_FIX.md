# GitHub Actions Permissions Fix

## ❌ Issue: 403 Error on Release Creation

The workflow is failing with a 403 error when trying to create a GitHub release. This is a permissions issue with the `GITHUB_TOKEN`.

## 🔧 Fix: Enable Workflow Permissions

### Option 1: Repository Settings (Recommended)

1. **Go to your repository settings:**
   ```
   https://github.com/italicninja/discord-rich-presence-plex/settings
   ```

2. **Navigate to Actions settings:**
   - Click "Actions" in the left sidebar
   - Click "General"

3. **Scroll to "Workflow permissions":**
   - Find the section "Workflow permissions"
   - Select: **"Read and write permissions"**
   - Check: **"Allow GitHub Actions to create and approve pull requests"**

4. **Save changes:**
   - Click "Save" button at the bottom

5. **Re-run the workflow:**
   - Go to: https://github.com/italicninja/discord-rich-presence-plex/actions
   - Click on the failed "Build and Release" workflow
   - Click "Re-run all jobs" button

### Option 2: Update Workflow File (Alternative)

If you don't have repository settings access, update the workflow to use explicit permissions:

Edit `.github/workflows/build-release.yml` and add at the top level:

```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*.*.*'
  workflow_dispatch:

permissions:
  contents: write  # Add this section

jobs:
  build-windows:
    # ... rest of workflow
```

## 📋 Step-by-Step Visual Guide

### Finding Workflow Permissions

1. Repository → Settings (⚙️ icon)
2. Sidebar → Actions → General
3. Scroll down to "Workflow permissions" section
4. Radio button: "Read and write permissions" ⚫
5. Checkbox: "Allow GitHub Actions to create and approve pull requests" ✅
6. Click "Save"

### What This Does

- Allows GitHub Actions to:
  - ✅ Create releases
  - ✅ Upload release assets (the .exe file)
  - ✅ Edit release notes
  - ✅ Create tags (if needed)

### Security Note

This is safe for your repository because:
- Only applies to GitHub Actions workflows
- Only works within your repository
- Standard practice for automated releases
- Token is scoped to the repository

## 🔄 After Fixing Permissions

### Re-run the Failed Workflow

1. **Go to Actions:**
   ```
   https://github.com/italicninja/discord-rich-presence-plex/actions
   ```

2. **Click on the failed workflow** (red X)

3. **Click "Re-run all jobs"** (button in top right)

4. **Wait for completion** (~5 minutes)

5. **Check Releases tab** for the new release

### Alternative: Delete and Re-create Tag

If re-running doesn't work:

```bash
# Delete the tag locally
git tag -d v2.12.0

# Delete the tag remotely
git push origin :refs/tags/v2.12.0

# Re-create and push the tag
git tag -a v2.12.0 -m "Release v2.12.0 - Windows System Tray Application"
git push origin v2.12.0
```

This will trigger a fresh workflow run with the new permissions.

## ✅ Verification

After fixing permissions and re-running:

1. **Workflow completes successfully** (green ✅)
2. **Release appears** in Releases tab
3. **Executable is uploaded** (`PlexDiscordRPC-v2.12.0.exe`)
4. **Release notes generated** automatically

## 🐛 Still Not Working?

### Check Organization Settings (if applicable)

If this is an organization repository:

1. Go to Organization Settings
2. Actions → General
3. Ensure "Allow all actions and reusable workflows" is selected
4. Check workflow permissions at organization level

### Check Branch Protection

If `main` branch has protection:

1. Settings → Branches
2. Branch protection rules
3. Ensure GitHub Actions can push to protected branches

### Manual Release (Temporary Workaround)

While fixing permissions, you can create a release manually:

1. Build locally: `build.bat`
2. Go to: https://github.com/italicninja/discord-rich-presence-plex/releases/new
3. Choose tag: `v2.12.0`
4. Title: `v2.12.0`
5. Upload: `dist/PlexDiscordRPC-v2.12.0.exe`
6. Click "Publish release"

## 📞 Need Help?

Common solutions:
- ✅ Enable "Read and write permissions" in repository settings
- ✅ Re-run the failed workflow
- ✅ Delete and re-push the tag
- ✅ Check organization-level settings

---

**Next Step:** Fix the permissions in repository settings, then re-run the workflow!
