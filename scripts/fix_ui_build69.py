#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path.cwd()
PROJECT = ROOT / "project.yml"
root = ROOT / "Locus/Features/Map/RootView.swift"

if not root.exists():
    raise SystemExit("RootView.swift not found")

s = root.read_text(encoding="utf-8")

# Build 69: fix the bottom control tray being laid out wider than the screen.
# The joystick previously used a maxWidth: .infinity frame inside the tray.
# That could force the tray's intrinsic width to the full screen and clip the
# rounded glass corners after the outer horizontal padding was applied.
s = s.replace(
    'VStack(spacing: 12) {',
    'VStack(alignment: .leading, spacing: 12) {',
    1,
)

s = s.replace(
    '''                .frame(width: 148, height: 148)
                .frame(maxWidth: .infinity, alignment: .leading)''',
    '''                .frame(width: 148, height: 148, alignment: .leading)''',
    1,
)

# Keep the tray itself safely inside the iPhone edges. Use a slightly larger
# bottom inset so the rounded lower corners and home-indicator area are clear.
old_call = '''            )
            .padding(.horizontal, 16)
            .padding(.bottom, 8)'''
new_call = '''            )
            .padding(.horizontal, 18)
            .padding(.bottom, 10)'''
if old_call in s:
    s = s.replace(old_call, new_call, 1)

root.write_text(s, encoding="utf-8")

# Keep Build 69 as the next UI-only revision.
project = PROJECT.read_text(encoding="utf-8")
project = re.sub(r'CURRENT_PROJECT_VERSION:\s*"\d+"', 'CURRENT_PROJECT_VERSION: "69"', project, count=1)
PROJECT.write_text(project, encoding="utf-8")

print("DPort Build 69: fixed bottom tray edge clipping and preserved left joystick layout.")
