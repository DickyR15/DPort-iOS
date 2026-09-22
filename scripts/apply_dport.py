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
    "Not Spoofing": "尚未模擬定位",
    "Reconnecting…": "正在重新連線…",
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
    "Engine": "定位引擎",
    "Locus is free and open source (MIT). Location injection uses the MIT-licensed idevice FFI.": "DPort 為免費的開放原始碼軟體（MIT 授權）。定位注入功能使用採 MIT 授權的 idevice FFI。",
    "idevice DVT location simulation": "Apple DVT 定位模擬",
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
    "Get LocalDevVPN (App Store)": "取得 LocalDevVPN（App Store）",
    "Rename Favorite": "重新命名我的最愛",
    "close enough": "差不多就好",
    "Remove Pin": "移除圖釘",
    "Selected pin": "已選取圖釘",
    "Map pin": "地圖圖釘",
    "Movement joystick": "移動搖桿",
    "Connect this iPhone": "連接這台 iPhone",
    "Developer pairing": "開發者配對",
    "Favorites": "我的最愛",
    "Recents": "最近使用",
    "Delete": "刪除",
    "Rename": "重新命名",
    "Cancel": "取消",
    "Save": "儲存",
    "Name": "名稱",
    "Places": "地點",
    "Version": "版本",
    "Engine": "引擎",
    "Settings": "設定",
    "About": "關於",
    "Privacy": "隱私權",
    "Status": "狀態",
    "Tunnel": "通道",
    "Device tunnel IP": "裝置通道 IP",
    "Save tunnel IP": "儲存通道 IP",
    "RPPairing file installed": "RPPairing 檔案已安裝",
    "No pairing file": "尚未安裝配對檔案",
    "Import RPPairing file…": "匯入 RPPairing 檔案…",
    "Paste RPPairing from clipboard": "從剪貼簿貼上 RPPairing",
    "Remove pairing file": "移除配對檔案",
    "Open LocalDevVPN": "開啟 LocalDevVPN",
    "Get LocalDevVPN": "取得 LocalDevVPN",
    "I’ve connected it — continue": "我已連線，繼續",
    "Walk": "步行",
    "Run": "跑步",
    "Cycle": "自行車",
    "Drive": "駕車",
    "Stop": "停止",
    "Teleport": "傳送定位",
    "On": "開",
    "Joy": "搖桿",
    "Done": "完成",
    "OK": "好",
    "Rename Favorite": "重新命名我的最愛",
    "Get started": "開始使用",
    "Import": "匯入",
    "Export": "匯出",
    "No track points found in GPX": "GPX 中找不到軌跡點",
    "Connected": "已連線",
    "Not connected": "未連線",
    "idevice DVT location simulation": "idevice DVT 定位模擬",
        "Connecting…": "連線中…",
        "Locus advertises a pairable host. iOS connects from Developer Mode, then Locus shows a 6-digit code for you to type.": "DPort 會提供可配對的主機。iOS 會從開發者模式連線，接著 DPort 會顯示 6 位數驗證碼供你輸入。",
        "On iOS 27, use Pair on this iPhone — no computer.": "iOS 27 可直接在此 iPhone 上配對，不需要電腦。",
        "Privacy & Security": "隱私權與安全性",
        "Pair with Host": "與主機配對",
        "Pair with Locus": "與 DPort 配對",
        "close enough": "差不多就好",
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
project = project.replace("      - path: AppIcon.icon", "      - path: Assets.xcassets")
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

    # Explicitly replace long Settings/pairing literals from upstream.
    content = content.replace(
        '"On iOS 27, use Pair on this iPhone — no computer. Locus advertises a pairable host; confirm the 6-digit code under Settings › Privacy & Security › Developer Mode › Pair with Host. On older iOS, import an RPPairing file from idevice_pair (not a SideStore lockdown .mobiledevicepairing). LiveContainer: enable Fix File Picker on Locus, or use Paste / Share → LiveContainer → Locus."',
        '"iOS 27 可直接在此 iPhone 上配對，不需要電腦。DPort 會提供可配對的主機，請前往「設定」›「隱私權與安全性」›「開發者模式」›「與主機配對」確認 6 位數驗證碼。較舊版本 iOS 請從 idevice_pair 匯入 RPPairing 檔案（不是 SideStore 的 lockdown .mobiledevicepairing）。若在 LiveContainer 中檔案選擇器無法使用，請在 DPort 啟用「修正檔案選擇器」，或使用「貼上／分享」→ LiveContainer → DPort。"'
    )
    content = content.replace(
        '"Import an RPPairing file from idevice_pair (not a SideStore lockdown .mobiledevicepairing). If the file picker fails (common in LiveContainer), enable Fix File Picker on the app, share the file into LiveContainer → Locus, or copy the plist and use Paste."',
        '"請從 idevice_pair 匯入 RPPairing 檔案（不是 SideStore 的 lockdown .mobiledevicepairing）。如果檔案選擇器失效（LiveContainer 常見），請在 DPort 啟用「修正檔案選擇器」，將檔案分享至 LiveContainer → DPort，或複製 plist 後使用「貼上」。"'
    )
    content = content.replace('Text("Developer pairing")', 'Text("開發者配對")')
    content = content.replace('Text("No computer needed")', 'Text("不需要電腦")')
    content = content.replace(
        'Text("Locus advertises a pairable host. iOS connects from Developer Mode, then Locus shows a 6-digit code for you to type.")',
        'Text("DPort 會提供可配對的主機。iOS 會從「開發者模式」連線，接著 DPort 會顯示 6 位數驗證碼供你輸入。")'
    )
    # Remove the upstream Locus easter-egg footer.
    content = re.sub(r'\n\s*Section \{\n\s*Button \{\n\s*showNameEasterEgg = true.*?\n\s*\} \n', '\n', content, flags=re.S)
    content = content.replace('    @State private var showNameEasterEgg = false\n', '')
    content = content.replace('            .fullScreenCover(isPresented: $showNameEasterEgg) {\n                LocusEasterEggView()\n            }\n', '')

    # Remove the upstream Locus easter-egg footer exactly as written.
    content = content.replace("                Section {\n                    Button {\n                        showNameEasterEgg = true\n                    } label: {\n                        Text(\"locus, n. — a place. From the Latin for where you are.\")\n                            .font(.footnote.italic())\n                            .foregroundStyle(.secondary)\n                            .multilineTextAlignment(.center)\n                            .frame(maxWidth: .infinity)\n                            .padding(.vertical, 4)\n                    }\n                    .buttonStyle(.plain)\n                    .listRowBackground(Color.clear)\n                    .listRowSeparator(.hidden)\n                }\n", "")
    content = content.replace('    @State private var showNameEasterEgg = false\n', '')
    content = content.replace('            .fullScreenCover(isPresented: $showNameEasterEgg) {\n                LocusEasterEggView()\n            }\n', '')
    # Also replace user-visible literals directly. This avoids relying on
    # Localizable.strings being loaded by every Xcode-generated target/container.
    # The shipped UI is therefore deterministically Traditional Chinese.
    for en, zh in TRANSLATIONS.items():
        en_esc = swift_escape(en)
        zh_esc = swift_escape(zh)
        content = content.replace(f'"{en_esc}"', f'"{zh_esc}"')
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
        "Connected", "Not connected",
        "idevice DVT location simulation",
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


# 3.5) Fix current SideStore/LocalDevVPN point-to-point detection.
# Current LocalDevVPN uses utun=10.7.1.1/32 and peer/device=10.7.0.1/32.
# The old check incorrectly required the peer IP to be assigned locally.
vpn_path = ROOT / "Locus" / "Support" / "LocalDevVPN.swift"
if vpn_path.exists():
    vpn = vpn_path.read_text(encoding="utf-8")
    old = '        if addresses.contains(target) { return true }'
    new = '''        if addresses.contains(target) { return true }
        // Current LocalDevVPN uses the phone endpoint 10.7.1.1 while
        // 10.7.0.1 is the peer. Treat the local endpoint as connected.
        if addresses.contains(where: { $0.hasPrefix("10.7.1.") }) { return true }'''
    if old in vpn and 'hasPrefix("10.7.1.")' not in vpn:
        vpn = vpn.replace(old, new, 1)
    vpn_path.write_text(vpn, encoding="utf-8")

# Current LocalDevVPN uses utun=10.7.1.1/32 and peer/device=10.7.0.1/32.
# The old check incorrectly required the peer IP to be assigned locally.
vpn_path = ROOT / "Locus" / "Support" / "LocalDevVPN.swift"
if vpn_path.exists():
    vpn = vpn_path.read_text(encoding="utf-8")
    # Keep installation state separate from tunnel connectivity.
    # canOpenURL may transiently return false on iOS while the VPN is
    # disconnected; once DPort has confirmed/used LocalDevVPN, remember that
    # the app is installed. Connectivity is still determined independently.
    marker = '    static let detectURL = URL(string: "localdevvpn://")!\\n'
    if 'static let installationKey = "dport.localdevvpn.installed"' not in vpn:
        vpn = vpn.replace(
            marker,
            marker
            + '    static let installationKey = "dport.localdevvpn.installed"\\n'
        )
    old_installed = '''    static var isInstalled: Bool {
        UIApplication.shared.canOpenURL(detectURL)
    }'''
    new_installed = '''    static var isInstalled: Bool {
        if UIApplication.shared.canOpenURL(detectURL) {
            UserDefaults.standard.set(true, forKey: installationKey)
            return true
        }
        return UserDefaults.standard.bool(forKey: installationKey)
    }'''
    if old_installed in vpn:
        vpn = vpn.replace(old_installed, new_installed)
    old_connected = '''        if addresses.contains(target) { return true }'''
    new_connected = '''        if addresses.contains(target) {
            UserDefaults.standard.set(true, forKey: installationKey)
            return true
        }'''
    vpn = vpn.replace(old_connected, new_connected)
    vpn = vpn.replace(
        '        return addresses.contains { $0.hasPrefix(prefix) }',
        '''        let connected = addresses.contains { $0.hasPrefix(prefix) }
        if connected {
            UserDefaults.standard.set(true, forKey: installationKey)
        }
        return connected'''
    )
    vpn = vpn.replace(
        '    static func openInstalled() {\n        UIApplication.shared.open(enableURL)\n    }',
        '''    static func openInstalled() {
        UserDefaults.standard.set(true, forKey: installationKey)
        UIApplication.shared.open(enableURL)
    }'''
    )
    vpn_path.write_text(vpn, encoding="utf-8")

# 3.6) Make Save tunnel IP visibly confirm success and reject invalid IPv4.
settings_path = ROOT / "Locus" / "Features" / "Settings" / "SettingsView.swift"
if settings_path.exists():
    settings = settings_path.read_text(encoding="utf-8")
    settings = settings.replace(
        '@State private var tunnelIP = TunnelConfig.targetIP',
        '@State private var tunnelIP = TunnelConfig.targetIP\n    @State private var tunnelSaved = false'
    )
    settings = settings.replace(
        '''                    Button("Save tunnel IP") {
                        TunnelConfig.setTargetIP(tunnelIP)
                    }
''',
        '''                    Button {
                        let candidate = tunnelIP.trimmingCharacters(in: .whitespacesAndNewlines)
                        if isValidIPv4(candidate) {
                            TunnelConfig.setTargetIP(candidate)
                            tunnelIP = candidate
                            tunnelSaved = true
                        } else {
                            session.lastError = "通道 IP 格式無效，請輸入 IPv4 位址，例如 10.7.0.1"
                            tunnelSaved = false
                        }
                    } label: {
                        Label(
                            tunnelSaved ? "已儲存通道 IP" : "儲存通道 IP",
                            systemImage: tunnelSaved ? "checkmark.circle.fill" : "checkmark"
                        )
                    }
''',
        1
    )
    settings = settings.replace(
        '''    }
}

struct PlacesView: View {
''',
        '''    }

    private func isValidIPv4(_ value: String) -> Bool {
        let parts = value.split(separator: ".")
        guard parts.count == 4 else { return false }
        return parts.allSatisfy { part in
            guard let n = Int(part), !part.isEmpty, n >= 0, n <= 255 else { return false }
            return true
        }
    }
}

struct PlacesView: View {
''',
        1
    )
    settings_path.write_text(settings, encoding="utf-8")

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

# 6) DPort app icon: build a conventional AppIcon asset catalog from the
#    checked-in vector artwork. This keeps the icon reproducible in CI.
assets = ROOT / "Assets.xcassets"
appicon = assets / "AppIcon.appiconset"
appicon.mkdir(parents=True, exist_ok=True)
icon_svg = ROOT.parent / "branding" / "DPort-AppIcon.svg"
# Workflow runs from repository root, so ROOT.parent is kept as a fallback.
if not icon_svg.exists():
    icon_svg = ROOT / "branding" / "DPort-AppIcon.svg"
if icon_svg.exists():
    import subprocess
    icon_sizes = [20, 29, 40, 58, 60, 76, 80, 87, 120, 152, 167, 180, 1024]
    for size in icon_sizes:
        subprocess.run([
            "rsvg-convert", "-w", str(size), "-h", str(size), str(icon_svg),
            "-o", str(appicon / f"AppIcon-{size}.png")
        ], check=True)
    (appicon / "Contents.json").write_text(r'''{
  "images" : [
    { "filename" : "AppIcon-40.png", "idiom" : "iphone", "scale" : "2x", "size" : "20x20" },
    { "filename" : "AppIcon-60.png", "idiom" : "iphone", "scale" : "3x", "size" : "20x20" },
    { "filename" : "AppIcon-58.png", "idiom" : "iphone", "scale" : "2x", "size" : "29x29" },
    { "filename" : "AppIcon-87.png", "idiom" : "iphone", "scale" : "3x", "size" : "29x29" },
    { "filename" : "AppIcon-80.png", "idiom" : "iphone", "scale" : "2x", "size" : "40x40" },
    { "filename" : "AppIcon-120.png", "idiom" : "iphone", "scale" : "3x", "size" : "40x40" },
    { "filename" : "AppIcon-120.png", "idiom" : "iphone", "scale" : "2x", "size" : "60x60" },
    { "filename" : "AppIcon-180.png", "idiom" : "iphone", "scale" : "3x", "size" : "60x60" },
    { "filename" : "AppIcon-20.png", "idiom" : "ipad", "scale" : "1x", "size" : "20x20" },
    { "filename" : "AppIcon-40.png", "idiom" : "ipad", "scale" : "2x", "size" : "20x20" },
    { "filename" : "AppIcon-29.png", "idiom" : "ipad", "scale" : "1x", "size" : "29x29" },
    { "filename" : "AppIcon-58.png", "idiom" : "ipad", "scale" : "2x", "size" : "29x29" },
    { "filename" : "AppIcon-40.png", "idiom" : "ipad", "scale" : "1x", "size" : "40x40" },
    { "filename" : "AppIcon-80.png", "idiom" : "ipad", "scale" : "2x", "size" : "40x40" },
    { "filename" : "AppIcon-76.png", "idiom" : "ipad", "scale" : "1x", "size" : "76x76" },
    { "filename" : "AppIcon-152.png", "idiom" : "ipad", "scale" : "2x", "size" : "76x76" },
    { "filename" : "AppIcon-167.png", "idiom" : "ipad", "scale" : "2x", "size" : "83.5x83.5" },
    { "filename" : "AppIcon-1024.png", "idiom" : "ios-marketing", "scale" : "1x", "size" : "1024x1024" }
  ],
  "info" : { "author" : "Dicky", "version" : 1 }
}
''', encoding="utf-8")
else:
    raise SystemExit("Missing branding/DPort-AppIcon.svg")


# 7) Final UI hardening pass for upstream strings that are intentionally kept
#    outside the main translation table.  Upstream Locus changes these strings
#    occasionally, so patch the exact user-visible onboarding/settings text here
#    as a final deterministic pass.
FINAL_UI = {
    "No computer needed": "不需要電腦",
    "Locus advertises a pairable host. iOS connects from Developer Mode, then Locus shows a 6-digit code for you to type.": "DPort 會提供可配對的主機。iOS 會從「開發者模式」連線，接著 DPort 會顯示 6 位數驗證碼供你輸入。",
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
    "In Developer Mode tap Pair with Locus → Pair.": "在「開發者模式」中點選「與 DPort 配對」→「配對」。",
    "iPhone connected": "iPhone 已連線",
    "Generating your 6-digit code…": "正在產生 6 位數驗證碼…",
    "Enter this code in Settings": "請在設定中輸入此驗證碼",
    "Second prompt only — after your unlock passcode.": "請先輸入解鎖密碼，再輸入此驗證碼。",
    "Paired": "已配對",
    "Pairing failed": "配對失敗",
    "Next we’ll set up LocalDevVPN.": "接下來設定 LocalDevVPN。",
    "RPPairing file saved. Connect LocalDevVPN, then teleport.": "RPPairing 檔案已儲存。請連線 LocalDevVPN 後再傳送定位。",
    "Start pairing": "開始配對",
    "Try again": "再試一次",
    "Continue": "繼續",
    "Done": "完成",
    "Type the code above into the second Settings prompt.": "請在「設定」第二個提示中輸入上方驗證碼。",
    "Connected — code coming next.": "已連線，驗證碼即將顯示。",
    "Waiting for iOS to connect… don’t force-quit Locus.": "等待 iOS 連線…請勿強制關閉 DPort。",
    "Close": "關閉",
    "Connect this iPhone": "連接這台 iPhone",
    "Locus needs a one-time pairing so it can set your location. You’ll confirm a short code in Settings.": "DPort 需要進行一次性配對，才能設定你的定位。請在「設定」中確認驗證碼。",
    "Import a pairing file from your computer — Locus uses it to set your location securely on this device.": "從電腦匯入配對檔案，DPort 會使用它在此裝置上安全設定定位。",
    "Import pairing file": "匯入配對檔案",
    "Paste from clipboard": "從剪貼簿貼上",
    "On a Mac, run idevice_pair and create an RPPairing file.": "在 Mac 上執行 idevice_pair 並建立 RPPairing 檔案。",
    "AirDrop / Share into Locus, or copy the plist text.": "透過 AirDrop／分享傳送至 DPort，或複製 plist 文字。",
    "Tap Import, or Paste from clipboard if the picker doesn’t work (LiveContainer).": "點選「匯入」，若檔案選擇器無法使用（LiveContainer），請改用「從剪貼簿貼上」。",
    "Connect LocalDevVPN": "連線 LocalDevVPN",
    "One more app": "還需要一個 App",
    "LocalDevVPN is installed. Open it to turn on the private tunnel Locus needs, then come back here.": "LocalDevVPN 已安裝。請開啟它以啟用 DPort 所需的私人通道，再回到這裡。",
    "LocalDevVPN creates a private tunnel Locus uses to talk to your phone’s location system. Install it, turn it on, then you’re ready to teleport.": "LocalDevVPN 會建立 DPort 用來連線手機定位系統的私人通道。安裝並開啟後，就可以開始傳送定位。",
    "Installed": "已安裝",
    "LocalDevVPN is on this iPhone.": "LocalDevVPN 已安裝在此 iPhone。",
    "Connect": "連線",
    "Tap below to open it and start the tunnel. You’ll bounce back to Locus.": "點選下方按鈕開啟 App 並啟動通道，完成後會回到 DPort。",
    "Install": "安裝",
    "Get LocalDevVPN from the App Store.": "從 App Store 取得 LocalDevVPN。",
    "Open it and turn the VPN on. Leave the default IP alone.": "開啟 App 並啟用 VPN，預設 IP 請保持不變。",
    "First teleport on Wi‑Fi": "首次傳送請使用 Wi‑Fi",
    "Start your first teleport while on Wi‑Fi. After that, it can keep working on cellular.": "第一次傳送定位請先使用 Wi‑Fi。完成後，即使切換到行動網路仍可繼續運作。",
    "Open LocalDevVPN": "開啟 LocalDevVPN",
    "Get LocalDevVPN": "取得 LocalDevVPN",
    "I’ve connected it — continue": "我已連線，繼續",
    "Settings": "設定",
    "Developer pairing": "開發者配對",
    "RPPairing file installed": "RPPairing 檔案已安裝",
    "No pairing file": "尚未安裝配對檔案",
    "Import RPPairing file…": "匯入 RPPairing 檔案…",
    "Paste RPPairing from clipboard": "從剪貼簿貼上 RPPairing",
    "Remove pairing file": "移除配對檔案",
    "Pair on this iPhone": "在此 iPhone 上配對",
    "On iOS 27, use Pair on this iPhone — no computer. Locus advertises a pairable host; confirm the 6-digit code under Settings › Privacy & Security › Developer Mode › Pair with Host. On older iOS, import an RPPairing file from idevice_pair (not a SideStore lockdown .mobiledevicepairing). LiveContainer: enable Fix File Picker on Locus, or use Paste / Share → LiveContainer → Locus.": "iOS 27 可直接在此 iPhone 上配對，不需要電腦。DPort 會提供可配對的主機，請前往「設定」›「隱私權與安全性」›「開發者模式」›「與主機配對」確認 6 位數驗證碼。較舊版本 iOS 請從 idevice_pair 匯入 RPPairing 檔案（不是 SideStore 的 lockdown .mobiledevicepairing）。若在 LiveContainer 中檔案選擇器無法使用，請在 DPort 啟用「修正檔案選擇器」，或使用「貼上／分享」→ LiveContainer → DPort。",
    "Device tunnel IP": "裝置通道 IP",
    "Status": "狀態",
    "Connected": "已連線",
    "Not connected": "未連線",
    "Save tunnel IP": "儲存通道 IP",
    "Get LocalDevVPN (App Store)": "取得 LocalDevVPN（App Store）",
    "Connect LocalDevVPN before teleporting. Default tunnel IP is 10.7.0.1. Start a spoof on Wi‑Fi first; it can keep working on cellular afterward.": "傳送定位前請先連線 LocalDevVPN。預設通道 IP 為 10.7.0.1。第一次請先在 Wi‑Fi 上啟動模擬定位，之後可繼續使用行動網路。",
    "Privacy": "隱私權",
    "Fully on-device. Favorites and recents stay in UserDefaults. No analytics, no accounts, nothing uploaded.": "完全在裝置端處理。我的最愛與最近使用會保存在 UserDefaults，不進行分析、不需要帳號，也不會上傳資料。",
    "About": "關於",
    "Version": "版本",
    "Engine": "定位引擎",
    "idevice DVT location simulation": "Apple DVT 定位模擬",
    "Locus is free and open source (MIT). Location injection uses the MIT-licensed idevice FFI.": "DPort 為免費的開放原始碼軟體（MIT 授權）。定位注入功能使用採 MIT 授權的 idevice FFI。",
}

def patch_final_ui(path: Path):
    content = path.read_text(encoding="utf-8")
    for en, zh in FINAL_UI.items():
        content = content.replace(f'"{en}"', f'"{zh}"')
        content = content.replace(f'("{en}")', f'("{zh}")')
    # Remove the upstream Locus easter-egg footer and state/presentation,
    # regardless of minor whitespace changes in upstream.
    content = re.sub(
        r'\n\s*Section\s*\{\s*Button\s*\{\s*showNameEasterEgg\s*=\s*true.*?\n\s*\}\s*\n\s*\}\s*',
        '\n',
        content,
        flags=re.S,
    )
    content = re.sub(r'\n\s*@State\s+private\s+var\s+showNameEasterEgg\s*=\s*false\s*', '\n', content)
    content = re.sub(
        r'\n\s*\.fullScreenCover\(isPresented:\s*\$showNameEasterEgg\)\s*\{.*?\n\s*\}',
        '',
        content,
        flags=re.S,
    )
    return content

for rel in [
    "Locus/Features/Settings/PairOnDeviceView.swift",
    "Locus/Features/Setup/SetupFlowView.swift",
    "Locus/Features/Settings/SettingsView.swift",
]:
    p = ROOT / rel
    if p.exists():
        p.write_text(patch_final_ui(p), encoding="utf-8")


# 8) Upstream-proof final pass: the branding pass above changes "Locus" to
#    "DPort" before the localization pass.  Keep the post-branding strings
#    here so onboarding/settings cannot regress when upstream wording changes.
POST_BRAND_UI = {
    "Connect this iPhone": "連接這台 iPhone",
    "No computer needed": "不需要電腦",
    "Follow these steps": "請依照以下步驟操作",
    "Keep DPort open. You’ll leave briefly for Settings, then come back with a code.": "請保持 DPort 開啟。你會暫時離開前往「設定」，再回到這裡查看驗證碼。",
    "Tap Start pairing and allow Local Network + Location when asked.": "點選「開始配對」，依提示允許「區域網路」與「定位」權限。",
    "Allow notifications — the code can appear as a banner over Settings.": "允許通知，驗證碼可以在「設定」畫面上方以橫幅顯示。",
    "Open Settings › Privacy & Security › Developer Mode › Pair with DPort → Pair.": "開啟「設定」›「隱私權與安全性」›「開發者模式」›「與 DPort 配對」→「配對」。",
    "Enter your unlock passcode first. On the next prompt, type DPort’s 6-digit code.": "先輸入 iPhone 解鎖密碼，下一個提示再輸入 DPort 的 6 位數驗證碼。",
    "If the code isn’t here yet": "還沒看到驗證碼嗎？",
    "Keep the app listening while you confirm in Developer Mode. Don’t force-quit. If “Pair with DPort” vanishes, stop/start pairing and reopen Developer Mode.": "在開發者模式確認配對時，請保持 DPort 持續監聽，不要強制關閉 App。若「與 DPort 配對」消失，請停止後重新開始配對，再重新開啟開發者模式。",
    "Ready when you are": "準備就緒",
    "Waiting for Settings…": "等待設定…",
    "In Developer Mode tap Pair with DPort → Pair.": "在「開發者模式」中點選「與 DPort 配對」→「配對」。",
    "iPhone connected": "iPhone 已連線",
    "Generating your 6-digit code…": "正在產生 6 位數驗證碼…",
    "Enter this code in Settings": "請在設定中輸入此驗證碼",
    "Second prompt only — after your unlock passcode.": "請先輸入解鎖密碼，再輸入此驗證碼。",
    "Paired": "已配對",
    "Pairing failed": "配對失敗",
    "Next we’ll set up LocalDevVPN.": "接下來設定 LocalDevVPN。",
    "Start pairing": "開始配對",
    "Try again": "再試一次",
    "Continue": "繼續",
    "Done": "完成",
    "Type the code above into the second Settings prompt.": "請在「設定」第二個提示中輸入上方驗證碼。",
    "Connected — code coming next.": "已連線，驗證碼即將顯示。",
    "Waiting for iOS to connect… don’t force-quit DPort.": "等待 iOS 連線…請勿強制關閉 DPort。",
    "Teleport your location.\\nNo computer required.": "傳送你的定位。\\n不需要電腦。",
    "A short setup — about two minutes.": "簡單設定，大約需要兩分鐘。",
    "Get started": "開始使用",
    "Import pairing file": "匯入配對檔案",
    "Paste from clipboard": "從剪貼簿貼上",
    "On a Mac, run idevice_pair and create an RPPairing file.": "在 Mac 上執行 idevice_pair 並建立 RPPairing 檔案。",
    "AirDrop / Share into DPort, or copy the plist text.": "透過 AirDrop／分享傳送至 DPort，或複製 plist 文字。",
    "Tap Import, or Paste from clipboard if the picker doesn’t work (LiveContainer).": "點選「匯入」，若檔案選擇器無法使用（LiveContainer），請改用「從剪貼簿貼上」。",
    "Connect LocalDevVPN": "連線 LocalDevVPN",
    "One more app": "還需要一個 App",
    "Connect": "連線",
    "Install": "安裝",
    "Installed": "已安裝",
    "LocalDevVPN is on this iPhone.": "LocalDevVPN 已安裝在此 iPhone。",
    "Tap below to open it and start the tunnel. You’ll bounce back to DPort.": "點選下方按鈕開啟 App 並啟動通道，完成後會回到 DPort。",
    "Get LocalDevVPN from the App Store.": "從 App Store 取得 LocalDevVPN。",
    "Open it and turn the VPN on. Leave the default IP alone.": "開啟 App 並啟用 VPN，預設 IP 請保持不變。",
    "Start your first teleport while on Wi‑Fi. After that, it can keep working on cellular.": "第一次傳送定位請先使用 Wi‑Fi。完成後，即使切換到行動網路仍可繼續運作。",
    "Open LocalDevVPN": "開啟 LocalDevVPN",
    "Get LocalDevVPN": "取得 LocalDevVPN",
    "I’ve connected it — continue": "我已連線，繼續",
    "No pairing file": "尚未安裝配對檔案",
    "Import RPPairing file…": "匯入 RPPairing 檔案…",
    "Paste RPPairing from clipboard": "從剪貼簿貼上 RPPairing",
    "Remove pairing file": "移除配對檔案",
    "On iOS 27, use Pair on this iPhone — no computer. DPort advertises a pairable host; confirm the 6-digit code under Settings › Privacy & Security › Developer Mode › Pair with Host. On older iOS, import an RPPairing file from idevice_pair (not a SideStore lockdown .mobiledevicepairing). LiveContainer: enable Fix File Picker on DPort, or use Paste / Share → LiveContainer → DPort.": "iOS 27 可直接在此 iPhone 上配對，不需要電腦。DPort 會提供可配對的主機，請前往「設定」›「隱私權與安全性」›「開發者模式」›「與主機配對」確認 6 位數驗證碼。較舊版本 iOS 請從 idevice_pair 匯入 RPPairing 檔案（不是 SideStore 的 lockdown .mobiledevicepairing）。若在 LiveContainer 中檔案選擇器無法使用，請在 DPort 啟用「修正檔案選擇器」，或使用「貼上／分享」→ LiveContainer → DPort。",
    "Import an RPPairing file from idevice_pair (not a SideStore lockdown .mobiledevicepairing). If the file picker fails (common in LiveContainer), enable Fix File Picker on the app, share the file into LiveContainer → DPort, or copy the plist and use Paste.": "從 idevice_pair 匯入 RPPairing 檔案（不是 SideStore 的 lockdown .mobiledevicepairing）。若檔案選擇器失敗（LiveContainer 常見），請在 App 啟用「修正檔案選擇器」、將檔案分享至 LiveContainer → DPort，或複製 plist 後使用「貼上」。",
    "Device tunnel IP": "裝置通道 IP",
    "Status": "狀態",
    "Connected": "已連線",
    "Not connected": "未連線",
    "Save tunnel IP": "儲存通道 IP",
    "Get LocalDevVPN (App Store)": "取得 LocalDevVPN（App Store）",
    "Connect LocalDevVPN before teleporting. Default tunnel IP is 10.7.0.1. Start a spoof on Wi‑Fi first; it can keep working on cellular afterward.": "傳送定位前請先連線 LocalDevVPN。預設通道 IP 為 10.7.0.1。第一次請先在 Wi‑Fi 上啟動模擬定位，之後可繼續使用行動網路。",
    "Fully on-device. Favorites and recents stay in UserDefaults. No analytics, no accounts, nothing uploaded.": "完全在裝置端處理。我的最愛與最近使用會保存在 UserDefaults，不進行分析、不需要帳號，也不會上傳資料。",
    "About": "關於",
    "Version": "版本",
    "Engine": "定位引擎",
    "idevice DVT location simulation": "idevice DVT 定位模擬",
    "DPort is free and open source (MIT). Location injection uses the MIT-licensed idevice FFI.": "DPort 為免費的開放原始碼軟體（MIT 授權）。定位注入功能使用採 MIT 授權的 idevice FFI。",
}

for rel in [
    "Locus/Features/Settings/PairOnDeviceView.swift",
    "Locus/Features/Setup/SetupFlowView.swift",
    "Locus/Features/Settings/SettingsView.swift",
]:
    p = ROOT / rel
    if not p.exists():
        continue
    content = p.read_text(encoding="utf-8")
    for en, zh in POST_BRAND_UI.items():
        content = content.replace(f'"{en}"', f'"{zh}"')
    # Remove the upstream Locus easter-egg footer by its literal, including
    # lowercase "locus"; it is not part of DPort's UI.
    content = re.sub(
        r'\n\s*Section\s*\{\s*Button\s*\{\s*showNameEasterEgg\s*=\s*true\s*\}\s*label:\s*\{\s*Text\("locus, n\. — a place\. From the Latin for where you are\."\).*?\n\s*\}\s*\n\s*\}',
        '\n',
        content,
        flags=re.S,
    )
    content = re.sub(r'\n\s*@State\s+private\s+var\s+showNameEasterEgg\s*=\s*false\s*', '\n', content)
    content = re.sub(
        r'\n\s*\.fullScreenCover\(isPresented:\s*\$showNameEasterEgg\)\s*\{.*?\n\s*\}',
        '',
        content,
        flags=re.S,
    )
    p.write_text(content, encoding="utf-8")



# 9) Absolute final pass for the first-run / pairing UI.
# Apply exact literals after all branding/localization transforms so upstream
# wording cannot leak English into the shipped DPort onboarding screens.
ABSOLUTE_UI = {
    "Pair on this iPhone": "在此 iPhone 上配對",
    "Close": "關閉",
    "No computer needed": "不需要電腦",
    "Start pairing": "開始配對",
    "Try again": "再試一次",
    "Continue": "繼續",
    "Done": "完成",
    "One more app": "還需要一個 App",
    "Install": "安裝",
    "Installed": "已安裝",
    "Connect": "連線",
    "First teleport on Wi‑Fi": "首次傳送請使用 Wi‑Fi",
    "Open LocalDevVPN": "開啟 LocalDevVPN",
    "Get LocalDevVPN": "取得 LocalDevVPN",
    "I’ve connected it — continue": "我已連線，繼續",
    "Connect this iPhone": "連接這台 iPhone",
    "Get started": "開始使用",
    "Import pairing file": "匯入配對檔案",
    "Paste from clipboard": "從剪貼簿貼上",
    "Developer pairing": "開發者配對",
    "RPPairing file installed": "RPPairing 檔案已安裝",
    "No pairing file": "尚未安裝配對檔案",
    "Import RPPairing file…": "匯入 RPPairing 檔案…",
    "Paste RPPairing from clipboard": "從剪貼簿貼上 RPPairing",
    "Remove pairing file": "移除配對檔案",
    "Device tunnel IP": "裝置通道 IP",
    "Status": "狀態",
    "Connected": "已連線",
    "Not connected": "未連線",
    "Save tunnel IP": "儲存通道 IP",
    "Privacy": "隱私權",
    "About": "關於",
    "Version": "版本",
    "Engine": "定位引擎",
    "Settings": "設定",
    "Favorites": "我的最愛",
    "Recents": "最近使用",
    "Places": "地點",
    "Name": "名稱",
    "Cancel": "取消",
    "Save": "儲存",
    "Delete": "刪除",
    "Rename": "重新命名",
    "OK": "好",
    "Search places": "搜尋地點",
    "Clear and dismiss keyboard": "清除並關閉鍵盤",
    "Current location": "目前位置",
    "Road route": "道路路線",
    "Routes": "路線",
    "Follow route": "沿路線移動",
    "Import GPX": "匯入 GPX",
    "Export GPX": "匯出 GPX",
    "Stop": "停止",
    "Teleport": "傳送定位",
    "Walk": "步行",
    "Run": "跑步",
    "Cycle": "自行車",
    "Drive": "駕車",
    "Movement joystick": "移動搖桿",
    "Remove Pin": "移除圖釘",
    "Selected pin": "已選取圖釘",
    "Map pin": "地圖圖釘",
    "Locus advertises a pairable host. iOS connects from Developer Mode, then Locus shows a 6-digit code for you to type.": "DPort 會提供可配對的主機。iOS 會從「開發者模式」連線，接著 DPort 會顯示 6 位數驗證碼供你輸入。",
    "Keep Locus open. You’ll leave briefly for Settings, then come back with a code.": "請保持 DPort 開啟。你會暫時離開前往「設定」，再回到這裡查看驗證碼。",
    "Tap Start pairing and allow Local Network + Location when asked.": "點選「開始配對」，依提示允許「區域網路」與「定位」權限。",
    "Allow notifications — the code can appear as a banner over Settings.": "允許通知，驗證碼可以在「設定」畫面上方以橫幅顯示。",
    "Open Settings › Privacy & Security › Developer Mode › Pair with Locus → Pair.": "開啟「設定」›「隱私權與安全性」›「開發者模式」›「與 DPort 配對」→「配對」。",
    "Enter your unlock passcode first. On the next prompt, type Locus’s 6-digit code.": "先輸入 iPhone 解鎖密碼，下一個提示再輸入 DPort 的 6 位數驗證碼。",
    "Follow these steps": "請依照以下步驟操作",
    "Ready when you are": "準備就緒",
    "Waiting for Settings…": "等待設定…",
    "In Developer Mode tap Pair with Locus → Pair.": "在「開發者模式」中點選「與 DPort 配對」→「配對」。",
    "iPhone connected": "iPhone 已連線",
    "Generating your 6-digit code…": "正在產生 6 位數驗證碼…",
    "Enter this code in Settings": "請在設定中輸入此驗證碼",
    "Second prompt only — after your unlock passcode.": "請先輸入解鎖密碼，再輸入此驗證碼。",
    "Paired": "已配對",
    "Pairing failed": "配對失敗",
    "Type the code above into the second Settings prompt.": "請在「設定」第二個提示中輸入上方驗證碼。",
    "Connected — code coming next.": "已連線，驗證碼即將顯示。",
    "Waiting for iOS to connect… don’t force-quit Locus.": "等待 iOS 連線…請勿強制關閉 DPort。",
    "No computer needed": "不需要電腦",
    "Teleport your location.\nNo computer required.": "傳送你的定位。\n不需要電腦。",
    "A short setup — about two minutes.": "簡單設定，大約需要兩分鐘。",
    "LocalDevVPN is installed. Open it to turn on the private tunnel Locus needs, then come back here.": "LocalDevVPN 已安裝。請開啟它以啟用 DPort 所需的私人通道，再回到這裡。",
    "LocalDevVPN creates a private tunnel Locus uses to talk to your phone’s location system. Install it, turn it on, then you’re ready to teleport.": "LocalDevVPN 會建立 DPort 用來連線手機定位系統的私人通道。安裝並開啟後，就可以開始傳送定位。",
    "LocalDevVPN is on this iPhone.": "LocalDevVPN 已安裝在此 iPhone。",
    "Tap below to open it and start the tunnel. You’ll bounce back to Locus.": "點選下方按鈕開啟 App 並啟動通道，完成後會回到 DPort。",
    "Get LocalDevVPN from the App Store.": "從 App Store 取得 LocalDevVPN。",
    "Open it and turn the VPN on. Leave the default IP alone.": "開啟 App 並啟用 VPN，預設 IP 請保持不變。",
    "Start your first teleport while on Wi‑Fi. After that, it can keep working on cellular.": "第一次傳送定位請先使用 Wi‑Fi。完成後，即使切換到行動網路仍可繼續運作。",
    "On a Mac, run idevice_pair and create an RPPairing file.": "在 Mac 上執行 idevice_pair 並建立 RPPairing 檔案。",
    "AirDrop / Share into Locus, or copy the plist text.": "透過 AirDrop／分享傳送至 DPort，或複製 plist 文字。",
    "Tap Import, or Paste from clipboard if the picker doesn’t work (LiveContainer).": "點選「匯入」，若檔案選擇器無法使用（LiveContainer），請改用「從剪貼簿貼上」。",
    "Locus needs a one-time pairing so it can set your location. You’ll confirm a short code in Settings.": "DPort 需要進行一次性配對，才能設定你的定位。請在「設定」中確認驗證碼。",
    "Fully on-device. Favorites and recents stay in UserDefaults. No analytics, no accounts, nothing uploaded.": "完全在裝置端處理。我的最愛與最近使用會保存在 UserDefaults，不進行分析、不需要帳號，也不會上傳資料。",
    "Connect LocalDevVPN": "連線 LocalDevVPN",
    "Connect LocalDevVPN before teleporting. Default tunnel IP is 10.7.0.1. Start a spoof on Wi‑Fi first; it can keep working on cellular afterward.": "傳送定位前請先連線 LocalDevVPN。預設通道 IP 為 10.7.0.1。第一次請先在 Wi‑Fi 上啟動模擬定位，之後可繼續使用行動網路。",
    "idevice DVT location simulation": "Apple DVT 定位模擬",
    "Locus is free and open source (MIT). Location injection uses the MIT-licensed idevice FFI.": "DPort 為免費的開放原始碼軟體（MIT 授權）。定位注入功能使用採 MIT 授權的 idevice FFI。",
    "locus, n. — a place. From the Latin for where you are.": ""
}

def _absolute_ui_pass(path: Path):
    content = path.read_text(encoding="utf-8")
    for en, zh in ABSOLUTE_UI.items():
        content = content.replace(f'"{en}"', f'"{zh}"')
    content = re.sub(
        r'\n\s*Section\s*\{\s*Button\s*\{\s*showNameEasterEgg\s*=\s*true\s*\}\s*label:\s*\{\s*Text\("locus, n\. — a place\. From the Latin for where you are\."\).*?\n\s*\}\s*',
        '\n',
        content,
        flags=re.S,
    )
    content = re.sub(r'\n\s*@State\s+private\s+var\s+showNameEasterEgg\s*=\s*false\s*', '\n', content)
    content = re.sub(
        r'\n\s*\.fullScreenCover\(isPresented:\s*\$showNameEasterEgg\)\s*\{.*?\n\s*\}',
        '',
        content,
        flags=re.S,
    )
    path.write_text(content, encoding="utf-8")

for rel in [
    "Locus/Features/Settings/PairOnDeviceView.swift",
    "Locus/Features/Setup/SetupFlowView.swift",
    "Locus/Features/Settings/SettingsView.swift",
]:
    p = ROOT / rel
    if p.exists():
        _absolute_ui_pass(p)

egg = ROOT / "Locus" / "Features" / "Settings" / "LocusEasterEggView.swift"
if egg.exists():
    egg.unlink()

critical_english = [
    '"Start pairing"', '"One more app"', '"Install"', '"Connect"',
    '"First teleport on Wi‑Fi"',
    '"Open Settings › Privacy & Security › Developer Mode › Pair with Locus → Pair."',
    '"locus, n. — a place. From the Latin for where you are."',
]
for rel in [
    "Locus/Features/Settings/PairOnDeviceView.swift",
    "Locus/Features/Setup/SetupFlowView.swift",
    "Locus/Features/Settings/SettingsView.swift",
]:
    p = ROOT / rel
    if p.exists():
        source = p.read_text(encoding="utf-8")
        leaked = [s for s in critical_english if s in source]
        if leaked:
            raise SystemExit(f"English UI strings remain in {rel}: {leaked}")



# 10) Settings UI hardening: remove the upstream manual Tunnel section.
# This is deliberately performed here (after localization) so later build
# scripts cannot leave the old "通道 / 10.7.0.1 / 儲存通道 IP" UI behind.
def _hardening_settings_vpn(path: Path):
    content = path.read_text(encoding="utf-8")

    # Remove the upstream Tunnel section by locating the TextField and the
    # next top-level List Section. This is independent of localization.
    markers = [
        'TextField("裝置通道 IP"',
        'TextField("Device tunnel IP"',
    ]
    marker_pos = min(
        [p for p in (content.find(m) for m in markers) if p >= 0],
        default=-1,
    )

    vpn_section = '''                Section("VPN 連線") {
                    LabeledContent("LocalDevVPN") {
                        Text(
                            LocalDevVPN.isConnected
                                ? "已連線"
                                : (LocalDevVPN.isInstalled ? "已安裝" : "未安裝")
                        )
                        .foregroundStyle(
                            LocalDevVPN.isConnected
                                ? LocusTheme.statusGood
                                : (LocalDevVPN.isInstalled ? .secondary : LocusTheme.statusWarn)
                        )
                    }

                    Button {
                        if LocalDevVPN.isInstalled {
                            LocalDevVPN.openInstalled()
                        } else {
                            LocalDevVPN.openAppStore()
                        }
                    } label: {
                        Label(
                            LocalDevVPN.isConnected
                                ? "開啟 LocalDevVPN"
                                : (LocalDevVPN.isInstalled
                                    ? "連線 LocalDevVPN"
                                    : "安裝 LocalDevVPN"),
                            systemImage: LocalDevVPN.isInstalled
                                ? "lock.shield.fill"
                                : "arrow.down.app.fill"
                        )
                    }

                    if LocalDevVPN.isConnected {
                        Label("VPN 通道正常", systemImage: "checkmark.circle.fill")
                            .foregroundStyle(LocusTheme.statusGood)
                    }
                }

'''

    if marker_pos >= 0:
        # The Tunnel section is the top-level Section immediately before the
        # marker. Remove through the next top-level Section (Privacy/About).
        section_start = content.rfind('\n                Section {', 0, marker_pos)
        if section_start < 0:
            raise SystemExit("DPort: tunnel marker found but Section start not found")
        section_start += 1

        next_section = content.find('\n                Section', marker_pos)
        if next_section < 0:
            next_section = content.find('\n            .navigationTitle', marker_pos)
        if next_section < 0:
            raise SystemExit("DPort: tunnel section end not found")

        # Keep the next Section and insert VPN immediately before it.
        content = content[:section_start] + vpn_section + content[next_section + 1:]
    else:
        # If Tunnel was already removed, ensure VPN section exists.
        if 'Section("VPN 連線")' not in content:
            insert_at = content.find('\n                Section("隱私權")')
            if insert_at < 0:
                insert_at = content.find('\n                Section("Privacy")')
            if insert_at < 0:
                insert_at = content.find('\n                Section("關於")')
            if insert_at < 0:
                insert_at = content.find('\n                Section("About")')
            if insert_at < 0:
                raise SystemExit("DPort: unable to find a Settings section insertion point")
            content = content[:insert_at + 1] + vpn_section + content[insert_at + 1:]

    # Remove ALL obsolete tunnel state and side effects. Earlier localization
    # passes may have translated the Done label, so use structural regexes.
    import re
    content = re.sub(r'^[ \t]*@State private var tunnelIP[^\n]*\n', '', content, flags=re.M)
    content = re.sub(r'^[ \t]*@State private var tunnelSaved[^\n]*\n', '', content, flags=re.M)
    content = re.sub(r'^[ \t]*TunnelConfig\.setTargetIP\(tunnelIP\)[^\n]*\n', '', content, flags=re.M)
    content = re.sub(r'^[ \t]*tunnelIP\s*=\s*[^\n]+\n', '', content, flags=re.M)

    # Final validation: the old UI must not remain.
    for leaked in (
        'TextField("裝置通道 IP"',
        'TextField("Device tunnel IP"',
        'Button("儲存通道 IP")',
        'Button("Save tunnel IP")',
        'Text("通道")',
        'Text("Tunnel")',
        '10.7.0.1',
        'TunnelConfig.targetIP',
    ):
        if leaked in content:
            raise SystemExit(f"DPort: legacy tunnel UI remains: {leaked}")

    path.write_text(content, encoding="utf-8")

_settings_path = ROOT / "Locus/Features/Settings/SettingsView.swift"
if _settings_path.exists():
    _hardening_settings_vpn(_settings_path)




# 11) Build 66 UX hardening:
# - Put the live joystick on the LEFT side for easier thumb reach.
# - Reject joystick/teleport immediately when LocalDevVPN is disconnected.
#   This avoids waiting for the developer tunnel timeout (~6 seconds).
# - Keep the working Build 65 LocationEngine / RPPairing path untouched.
_root_path = ROOT / "Locus/Features/Map/RootView.swift"
if _root_path.exists():
    root = _root_path.read_text(encoding="utf-8")

    # The joystick itself moves from the trailing/right side to the
    # leading/left side. This is the only layout change to the pad.
    root = root.replace(
        '.frame(maxWidth: .infinity, alignment: .trailing)',
        '.frame(maxWidth: .infinity, alignment: .leading)',
        1,
    )

    # Instant LocalDevVPN preflight for the joystick button.
    old_joy_action = '''                Button {
                    if session.joystickActive {
                        session.stopJoystick()
                    } else {
                        session.startJoystick(pairing: pairing)
                    }
                } label: {'''
    new_joy_action = '''                Button {
                    if session.joystickActive {
                        session.stopJoystick()
                    } else if !LocalDevVPN.isConnected {
                        session.lastError = "請先連線 LocalDevVPN，再使用搖桿。"
                    } else {
                        session.startJoystick(pairing: pairing)
                    }
                } label: {'''
    if old_joy_action not in root:
        raise SystemExit("DPort Build 66: joystick action block not found")
    root = root.replace(old_joy_action, new_joy_action, 1)

    # Instant LocalDevVPN preflight for Teleport as well. This keeps the
    # error behavior consistent and prevents the same tunnel timeout there.
    old_teleport_action = '''                    Button {
                        guard let pin = session.pin else {
                            session.lastError = "Tap the map to drop a pin first."
                            return
                        }
                        session.teleport(to: pin, pairing: pairing)
                    } label: {'''
    new_teleport_action = '''                    Button {
                        guard LocalDevVPN.isConnected else {
                            session.lastError = "請先連線 LocalDevVPN，再傳送定位。"
                            return
                        }
                        guard let pin = session.pin else {
                            session.lastError = "Tap the map to drop a pin first."
                            return
                        }
                        session.teleport(to: pin, pairing: pairing)
                    } label: {'''
    if old_teleport_action not in root:
        raise SystemExit("DPort Build 66: teleport action block not found")
    root = root.replace(old_teleport_action, new_teleport_action, 1)

    _root_path.write_text(root, encoding="utf-8")


print(f"DPort branding/localization applied: {len(TRANSLATIONS)} strings + final UI hardening.")
