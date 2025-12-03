"""
Generate version_info.txt for PyInstaller from version_info.py template
"""

from config.constants import version

# Parse version string
version_parts = version.split('.')
major = int(version_parts[0])
minor = int(version_parts[1]) if len(version_parts) > 1 else 0
# Handle comments in patch version
patch_str = version_parts[2] if len(version_parts) > 2 else '0'
patch = int(patch_str.split()[0].split('#')[0].strip())
build = 0

version_info = f"""# UTF-8
#
# For more details about fixed file info:
# See https://docs.microsoft.com/en-us/windows/win32/api/verrsrc/ns-verrsrc-vs_fixedfileinfo

VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({major}, {minor}, {patch}, {build}),
    prodvers=({major}, {minor}, {patch}, {build}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Discord Rich Presence for Plex'),
        StringStruct(u'FileDescription', u'Discord Rich Presence for Plex - System Tray Application'),
        StringStruct(u'FileVersion', u'{version}'),
        StringStruct(u'InternalName', u'PlexDiscordRPC'),
        StringStruct(u'LegalCopyright', u'Open Source - See LICENSE file'),
        StringStruct(u'OriginalFilename', u'PlexDiscordRPC-v{version}.exe'),
        StringStruct(u'ProductName', u'Discord Rich Presence for Plex'),
        StringStruct(u'ProductVersion', u'{version}')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [0x409, 1200])])
  ]
)
"""

# Write to file
with open('version_info.txt', 'w', encoding='utf-8') as f:
    f.write(version_info)

print(f"Generated version_info.txt for version {version}")
print(f"File version: {major}.{minor}.{patch}.{build}")
