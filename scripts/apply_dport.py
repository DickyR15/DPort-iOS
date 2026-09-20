#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path.cwd()
PROJECT = ROOT / "project.yml"

# The upstream project uses SwiftUI's automatic Localizable.strings lookup for
# most view literals.  The extra replacements below cover runtime Strings
# used by status labels, errors, notifications, and the pairing service name.

TRANSLATIONS = {
    "Search places": "搜尋地點",
    "Clear and dismiss keyboard": "清除並關閉鍵盤",
    "Done": "完成",
    "Current location": "目前位置",
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
    "Routes follow Apple Maps roads/footpaths for the selected travel mode. Speed gets light random variation so motion looks less robotic.": "路線會依所選交通方式沿 Apple 地圖道路／步道行進，速度會加入些微自然變化，讓移動不會過於機械。",
    "Routes": "路線",
    "No computer needed": "不需要電腦",
    "Pair on this iPhone": "在此 iPhone 上配對",
    "Close": "關閉",
    "No computer needed": "不需要電腦",
    "Locus advertises a pairable host. iOS connects from Developer Mode, then Locus shows a 6-digit code for you to type.": "DPort 會提供可配對的主機。iOS 會從開發者模式連線，接著 DPort 會顯示 6 位數驗證碼供你輸入。",
    "Follow these steps": "請依照以下步驟操作",
    "Keep Locus open. You’ll leave briefly for Settings, then come back with a code.": "請保持 DPort 開啟。你會暫時離開前往「設定」，再回到這裡查看驗證碼。",
    "Tap Start pairing and allow Local Network + Location when asked.": "點選「開始配對」，依提示允許「區域網路」與「定位」權限。",
    "Allow notifications — the code can appear as a banner over Settings.": "允許通知，驗證碼可以在「設定」畫面上方以橫幅顯示。",
    "Open Settings › Privacy & Security › Developer Mode › Pair with Locus → Pair.": "開啟「設定」›「隱私權與安全性」›「開發者模式」›「與 DPort 配對」→「配對」。",
    "Enter your unlock passcode first. On the next prompt, type Locus’s 6-digit code.": "先輸入 iPhone 解鎖密碼，下一個提示再輸入 DPort 的 6 位數驗證碼。",
    "If the code isn’t here yet": "還沒看到驗證碼嗎？",
    "Keep the app listening while you confirm in Developer Mode. Don’t force-quit. If “Pair with Locus” vanishes, stop/start pairing and reopen Developer Mode.": "在開發者模式確認配對時，請保持 DPort 持續監聽，不要強制關閉 App。若「與 DPort 配對」消失，請停止後重新開始配對，再重新開啟開發者模式。",
    "Ready when you are": "準備就緒",
    "Waiting for Settings…": "等待設定…",
    "In Developer Mode tap Pair with Locus → Pair.": "在開發者模式中點選「與 DPort 配對」→「配對」。",
    "iPhone connected": "iPhone 已連線",
    "Generating your 6-digit code…": "正在產生 6 位數驗證碼…",
    "Enter this code in Settings": "請在設定中輸入此驗證碼",
    "Second prompt only — after your unlock passcode.": "請先輸入解鎖密碼，再輸入此驗證碼。",
    "Paired": "已配對",
    "Pairing failed": "配對失敗",
    "Type the code above into the second Settings prompt.": "請在「設定」第二個提示中輸入上方驗證碼。",
    "Connected — code coming next.": "已連線，驗證碼即將顯示。",
    "Waiting for iOS to connect… don’t force-quit Locus.": "等待 iOS 連線…請勿強制關閉 DPort。",
    "Connect this iPhone": "連接這台 iPhone",
    "Import pairing file": "匯入配對檔案",
    "Paste from clipboard": "從剪貼簿貼上",
    "Get started": "開始使用",
    "Teleport your location.\\nNo computer required.": "傳送你的定位。\\n不需要電腦。",
    "A short setup — about two minutes.": "簡單設定，大約需要兩分鐘。",
    "Tap Import, or Paste from clipboard if the picker doesn’t work (LiveContainer).": "點選「匯入」，若檔案選擇器無法使用（LiveContainer），請改用「從剪貼簿貼上」。",
    "LocalDevVPN creates a private tunnel Locus uses to talk to your phone’s location system. Install it, turn it on, then you’re ready to teleport.": "LocalDevVPN 會建立 DPort 用來連線手機定位系統的私人通道。安裝並開啟它後，就可以開始傳送定位。",
    "Get LocalDevVPN": "取得 LocalDevVPN",
    "Get LocalDevVPN from the App Store.": "從 App Store 取得 LocalDevVPN。",
    "Open LocalDevVPN": "開啟 LocalDevVPN",
    "Open it and turn the VPN on. Leave the default IP alone.": "開啟 App 並啟用 VPN，預設 IP 請保持不變。",
    "I’ve connected it — continue": "我已連線，繼續",
    "Start your first teleport while on Wi‑Fi. After that, it can keep working on cellular.": "第一次傳送定位請先使用 Wi‑Fi。完成後，即使切換到行動網路仍可繼續運作。",
    "Import an RPPairing file in Settings first.": "請先在「設定」中匯入 RPPairing 檔案。",
    "Drop a pin or teleport somewhere before using the joystick.": "使用搖桿前，請先在地圖放置圖釘或傳送到某個位置。",
    "Not Spoofing": "未啟用模擬定位",
    "Starting…": "正在啟動…",
    "Spoofing": "模擬定位中",
    "Reconnecting…": "重新連線中…",
    "Interrupted": "已中斷",
    "Disconnected": "已中斷",
    "Disconnected — \\(reason)": "已中斷：\\(reason)",
    "Tap the map to drop a pin first.": "請先點選地圖放置圖釘。",
    "Connect LocalDevVPN": "連線 LocalDevVPN",
    "Stop": "停止",
    "Teleport": "傳送定位",
    "On": "開",
    "Joy": "搖桿",
    "Walk": "步行",
    "Run": "跑步",
    "Cycle": "自行車",
    "Drive": "駕車",
    "Movement joystick": "移動搖桿",
    "Remove Pin": "移除圖釘",
    "Selected pin": "已選取圖釘",
    "Map pin": "地圖圖釘",
    "Tap to show remove. Touch and hold to drag.": "點一下顯示移除選項，長按後可拖曳。",
    "Developer pairing": "開發者配對",
    "RPPairing file installed": "RPPairing 檔案已安裝",
    "No pairing file": "尚未安裝配對檔案",
    "Import RPPairing file…": "匯入 RPPairing 檔案…",
    "Paste RPPairing from clipboard": "從剪貼簿貼上 RPPairing",
    "Remove pairing file": "移除配對檔案",
    "Device tunnel IP": "裝置通道 IP",
    "Status": "狀態",
    "Save tunnel IP": "儲存通道 IP",
    "Tunnel": "通道",
    "Connect LocalDevVPN before teleporting. Default tunnel IP is 10.7.0.1. Start a spoof on Wi‑Fi first; it can keep working on cellular afterward.": "傳送定位前請先連線 LocalDevVPN。預設通道 IP 為 10.7.0.1。第一次請先在 Wi‑Fi 上啟動模擬定位，之後可繼續使用行動網路。",
    "Privacy": "隱私權",
    "Fully on-device. Favorites and recents stay in UserDefaults. No analytics, no accounts, nothing uploaded.": "完全在裝置端處理。我的最愛與最近使用會保存在 UserDefaults，不進行分析、不需要帳號，也不會上傳資料。",
    "About": "關於",
    "Version": "版本",
    "Engine": "引擎",
    "Locus is free and open source (MIT). Location injection uses the MIT-licensed idevice FFI.": "DPort 為免費開放原始碼軟體（MIT）。定位注入功能使用採 MIT 授權的 idevice FFI。",
    "locus, n. — a place. From the Latin for where you are.": "locus，名詞——所在之處。源自拉丁文，意指「你所在的地方」。",
    "Settings": "設定",
    "Favorites": "我的最愛",
    "Star a pin from the map to save it.": "在地圖上為圖釘加上星號即可儲存。",
    "Delete": "刪除",
    "Rename": "重新命名",
    "Recents": "最近使用",
    "Teleports show up here.": "傳送定位紀錄會顯示在這裡。",
    "Places": "地點",
    "Name": "名稱",
    "Cancel": "取消",
    "Save": "儲存",
    "Choose a name you’ll recognize later.": "輸入一個方便之後辨識的名稱。",
    "OK": "好",
    "Set a route start and end.": "設定路線的起點與終點。",
    "Nothing to export.": "沒有可匯出的內容。",
    "Build or draw a route first.": "請先建立或繪製路線。",
    "Locus connected": "DPort 已連線",
    "Locus pairing code": "DPort 配對驗證碼",
    "Locus paired": "DPort 已完成配對",
    "Locus spoof dropped": "DPort 模擬定位已中斷",
    "Generating pairing code…": "正在產生配對驗證碼…",
    "RPPairing is ready. Connect LocalDevVPN, then teleport.": "RPPairing 已就緒。請連線 LocalDevVPN 後再傳送定位。",
    "Locus needs a one-time pairing so it can set your location. You’ll confirm a short code in Settings.": "DPort 需要進行一次性配對，才能設定你的定位。請在「設定」中確認驗證碼。",
    "On a Mac, run idevice_pair and create an RPPairing file.": "在 Mac 上執行 idevice_pair 並建立 RPPairing 檔案。",
    "Clipboard is empty. Copy your RPPairing plist text (or the file), then try Paste again.": "剪貼簿是空的。請先複製 RPPairing plist 文字或檔案，再重新嘗試貼上。",
    "That doesn’t look like an RPPairing plist. Copy the full pairing file contents and try again.": "這看起來不像 RPPairing plist。請複製完整的配對檔案內容後再試一次。",
    "Tunnel IP is invalid. Check Settings → Tunnel IP (usually 10.7.0.1).": "通道 IP 無效。請檢查「設定」→「通道 IP」（通常是 10.7.0.1）。",
    "Could not read the RPPairing file. Generate one with idevice_pair in RPPairing mode.": "無法讀取 RPPairing 檔案。請使用 idevice_pair 的 RPPairing 模式產生檔案。",
    "Could not open the developer tunnel. Is LocalDevVPN connected on Wi‑Fi?": "無法開啟開發者通道。請確認 LocalDevVPN 已在 Wi‑Fi 上連線。",
    "Connected to the tunnel but RemoteXPC handshake failed.": "已連線到通道，但 RemoteXPC 交握失敗。",
    "Could not open Apple’s location simulation service.": "無法開啟 Apple 的定位模擬服務。",
    "Failed to set simulated coordinates.": "無法設定模擬座標。",
    "Failed to clear simulated location.": "無法清除模擬定位。",
    "No active simulation session.": "目前沒有啟用中的模擬定位工作階段。",
    "Pairing finished but no pairing file was returned.": "配對完成，但沒有取得配對檔案。",
    "Failed to write pairing file": "無法寫入配對檔案",
    "Paired, but failed to save file: ": "已完成配對，但儲存檔案失敗：",
    "No route found": "找不到符合條件的路線",
    "No track points found in GPX": "GPX 中找不到軌跡點",
}

def swift_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")

# 1) Project identity.
project = PROJECT.read_text(encoding="utf-8")
for old, new in [
    ("name: Locus", "name: DPort"),
    ("  Locus:", "  DPort:"),
    ("com.chrismack.locus", "com.dicky.dport"),
    ("PRODUCT_NAME: Locus", "PRODUCT_NAME: DPort"),
    ('MARKETING_VERSION: "1.0.2"', 'MARKETING_VERSION: "6.8.2"'),
    ('CURRENT_PROJECT_VERSION: "3"', 'CURRENT_PROJECT_VERSION: "35"'),
]:
    project = project.replace(old, new)
PROJECT.write_text(project, encoding="utf-8")

# 2) Brand visible UI text in plist.
for plist in ROOT.joinpath("Locus").rglob("*.plist"):
    content = plist.read_text(encoding="utf-8")
    content = re.sub(r"\bLocus\b", "DPort", content)
    plist.write_text(content, encoding="utf-8")

# 3) Keep internal symbol names (LocusTheme, locusGlass, etc.) intact.
#    Replace only standalone visible display-name occurrences in Swift.
for swift in ROOT.joinpath("Locus").rglob("*.swift"):
    content = swift.read_text(encoding="utf-8")
    content = re.sub(r"\bLocus\b", "DPort", content)

    # Runtime strings that are displayed through String rather than SwiftUI
    # LocalizedStringKey need an explicit localized lookup.
    runtime_literals = [
        "Walk", "Run", "Cycle", "Drive",
        "Not Spoofing", "Starting…", "Spoofing", "Reconnecting…", "Interrupted",
        "Import an RPPairing file in Settings first.",
        "Drop a pin or teleport somewhere before using the joystick.",
        "Tap the map to drop a pin first.",
        "DPort connected", "DPort pairing code", "DPort paired", "DPort spoof dropped",
        "Generating pairing code…",
        "RPPairing is ready. Connect LocalDevVPN, then teleport.",
        "Pairing finished but no pairing file was returned.",
        "Failed to write pairing file",
        "Nothing to export.",
        "No route found",
        "No track points found in GPX",
        "Tunnel IP is invalid. Check Settings → Tunnel IP (usually 10.7.0.1).",
        "Could not read the RPPairing file. Generate one with idevice_pair in RPPairing mode.",
        "Could not open the developer tunnel. Is LocalDevVPN connected on Wi‑Fi?",
        "Connected to the tunnel but RemoteXPC handshake failed.",
        "Could not open Apple’s location simulation service.",
        "Failed to set simulated coordinates.",
        "Failed to clear simulated location.",
        "No active simulation session.",
        "Clipboard is empty. Copy your RPPairing plist text (or the file), then try Paste again.",
        "That doesn’t look like an RPPairing plist. Copy the full pairing file contents and try again.",
    ]
    for s in runtime_literals:
        escaped = swift_escape(s)
        pattern = rf'(?<!String\(localized:\s)"{re.escape(escaped)}"'
        content = re.sub(pattern, f'String(localized: "{escaped}")', content)

    # Status-bar runtime strings.
    content = content.replace(
        'return reason.isEmpty ? "Disconnected" : "Disconnected — \\(reason)"',
        'return reason.isEmpty ? String(localized: "Disconnected") : String(localized: "Disconnected — \\(reason)")'
    )
    content = content.replace(
        'case .dropped: return "Interrupted"',
        'case .dropped: return String(localized: "Interrupted")'
    )
    content = content.replace(
        'case .notSpoofing: return "Not Spoofing"',
        'case .notSpoofing: return String(localized: "Not Spoofing")'
    )
    content = content.replace(
        'case .connectVPN: return "Connect LocalDevVPN"',
        'case .connectVPN: return String(localized: "Connect LocalDevVPN")'
    )

    # Generic String-valued errorDescription returns.
    in_error = "var errorDescription: String? {"
    if in_error in content:
        for en, zh in TRANSLATIONS.items():
            if en in runtime_literals or en in (
                "Failed to write pairing file",
                "No route found",
                "No track points found in GPX",
            ):
                esc = swift_escape(en)
                content = content.replace(
                    f'return "{esc}"',
                    f'return String(localized: "{esc}")'
                )

    swift.write_text(content, encoding="utf-8")

# 4) Pairing service's visible Bonjour device name.
pair_service = ROOT / "Locus" / "Engine" / "PairOnDeviceService.swift"
c = pair_service.read_text(encoding="utf-8")
c = c.replace('let name = "DPort"', 'let name = "DPort"')
pair_service.write_text(c, encoding="utf-8")

# 5) Traditional Chinese localization catalog.
loc = ROOT / "Locus" / "Resources" / "zh-Hant.lproj" / "Localizable.strings"
loc.parent.mkdir(parents=True, exist_ok=True)
entries = []
for en, zh in TRANSLATIONS.items():
    # Branding runs before localization, so keep both original and branded keys.
    branded_key = en.replace("Locus", "DPort")
    entries.append(f'"{swift_escape(branded_key)}" = "{swift_escape(zh)}";')
    if branded_key != en:
        entries.append(f'"{swift_escape(en)}" = "{swift_escape(zh)}";')
loc.write_text("\n".join(entries) + "\n", encoding="utf-8")

print(f"DPort branding/localization applied: {len(TRANSLATIONS)} strings.")
