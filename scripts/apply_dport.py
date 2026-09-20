#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path.cwd()
project = ROOT / "project.yml"

text = project.read_text(encoding="utf-8")
replacements = [
    ("name: Locus", "name: DPort"),
    ("  Locus:", "  DPort:"),
    ("com.chrismack.locus", "com.dicky.dport"),
    ("PRODUCT_NAME: Locus", "PRODUCT_NAME: DPort"),
    ('MARKETING_VERSION: "1.0.2"', 'MARKETING_VERSION: "6.8.2"'),
    ('CURRENT_PROJECT_VERSION: "3"', 'CURRENT_PROJECT_VERSION: "35"'),
]
for old, new in replacements:
    text = text.replace(old, new)
project.write_text(text, encoding="utf-8")

for path in (ROOT / "Locus").rglob("*"):
    if path.is_file() and path.suffix in {".swift", ".plist"}:
        content = path.read_text(encoding="utf-8")
        content = re.sub(r"\bLocus\b", "DPort", content)
        path.write_text(content, encoding="utf-8")

strings = {
    "Search places": "搜尋地點",
    "Clear and dismiss keyboard": "清除並關閉鍵盤",
    "Done": "完成",
    "Routes": "路線",
    "Road route": "道路路線",
    "Use current pin / spoof as start": "使用目前定位／模擬位置作為起點",
    "Use current pin as end": "使用目前定位作為終點",
    "Start": "起點",
    "End": "終點",
    "Build walk/drive route on roads": "建立步行／駕車道路路線",
    "Play / draw / GPX": "播放／繪製／GPX",
    "Use drawn path from map": "使用地圖繪製的路徑",
    "Follow route": "沿路線移動",
    "Import GPX": "匯入 GPX",
    "Export GPX": "匯出 GPX",
    "No computer needed": "不需要電腦",
    "Pair on this iPhone": "在此 iPhone 上配對",
    "Close": "關閉",
    "Start pairing": "開始配對",
    "Try again": "再試一次",
    "Continue": "繼續",
    "Paired": "已配對",
    "Pairing failed": "配對失敗",
    "Ready when you are": "準備就緒",
    "Waiting for Settings…": "等待設定…",
    "iPhone connected": "iPhone 已連線",
    "Generating your 6-digit code…": "正在產生 6 位數驗證碼…",
    "Enter this code in Settings": "請在設定中輸入此驗證碼",
    "Second prompt only — after your unlock passcode.": "請先輸入解鎖密碼，再輸入此驗證碼。",
}
loc = ROOT / "Locus" / "Resources" / "zh-Hant.lproj" / "Localizable.strings"
loc.parent.mkdir(parents=True, exist_ok=True)
loc.write_text(
    "".join(f'"{k}" = "{v}";\n' for k, v in strings.items()),
    encoding="utf-8",
)
print("DPort branding applied.")
