#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path.cwd()
PROJECT = ROOT / "project.yml"

def rw(rel, transform):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    p.write_text(transform(s), encoding="utf-8")

def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

# DPort iOS UI release — Build 39, version 6.9.2.
project = PROJECT.read_text(encoding="utf-8")
project = project.replace('MARKETING_VERSION: "6.8.2"', 'MARKETING_VERSION: "6.9.2"')
project = project.replace('CURRENT_PROJECT_VERSION: "35"', 'CURRENT_PROJECT_VERSION: "39"')
project = project.replace('CURRENT_PROJECT_VERSION: "38"', 'CURRENT_PROJECT_VERSION: "39"')
PROJECT.write_text(project, encoding="utf-8")

# Home/status/quick controls.
def patch_root(s):
    s = s.replace('@State private var showPlaces = false', '@State private var showPlaces = false\n    @State private var showCoordinates = false')
    s = s.replace('''            BottomControlsView(
                showSettings: $showSettings,
                showPlaces: $showPlaces
            )''', '''            BottomControlsView(
                showSettings: $showSettings,
                showPlaces: $showPlaces,
                showCoordinates: $showCoordinates
            )''')
    s = s.replace('''        .sheet(isPresented: $showPlaces) {
            PlacesView()
        }''', '''        .sheet(isPresented: $showPlaces) {
            PlacesView()
        }
        .sheet(isPresented: $showCoordinates) {
            CoordinateInputView()
        }''')
    s = s.replace('.alert("Locus", isPresented:', '.alert("DPort", isPresented:')
    s = s.replace('return .status("Connecting…")', 'return .status("正在連線…")')
    s = s.replace('return .status("Spoofing")', 'return .status("模擬定位中")')
    s = s.replace('return .status("Reconnecting…")', 'return .status("重新連線中…")')
    s = s.replace('return .status(reason.isEmpty ? "Disconnected" : "Disconnected — \\(reason)")',
                  'return .status(reason.isEmpty ? "已中斷" : "已中斷：\\(reason)")')
    s = s.replace('case .notSpoofing: return "Not Spoofing"', 'case .notSpoofing: return "尚未模擬定位"')
    s = s.replace('case .connectVPN: return "Connect LocalDevVPN"', 'case .connectVPN: return "連線 LocalDevVPN"')
    s = s.replace('''struct BottomControlsView: View {
    @EnvironmentObject private var session: SpoofSession
    @EnvironmentObject private var pairing: PairingStore
    @Binding var showSettings: Bool
    @Binding var showPlaces: Bool''', '''struct BottomControlsView: View {
    @EnvironmentObject private var session: SpoofSession
    @EnvironmentObject private var pairing: PairingStore
    @Binding var showSettings: Bool
    @Binding var showPlaces: Bool
    @Binding var showCoordinates: Bool''')
    s = s.replace('''                trayIcon("gearshape.fill") { showSettings = true }
                trayIcon("star.fill") { showPlaces = true }''', '''                trayIcon("gearshape.fill") { showSettings = true }
                trayIcon("star.fill") { showPlaces = true }
                trayIcon("mappin.and.ellipse") { showCoordinates = true }''')
    return s

rw("Locus/Features/Map/RootView.swift", patch_root)

# Recent list is intentionally limited to 10.
rw("Locus/Engine/SpoofSession.swift",
   lambda s: s.replace('if recents.count > 20 { recents = Array(recents.prefix(20))}',
                       'if recents.count > 10 { recents = Array(recents.prefix(10))}'))

# Settings: explicit pairing state + diagnostics.
def patch_settings(s):
    s = s.replace('@State private var showPairOnDevice = false',
                  '@State private var showPairOnDevice = false\n    @State private var showDiagnostics = false')
    s = s.replace('@State private var showNameEasterEgg = false',
                  '@State private var showNameEasterEgg = false\n    @State private var showDiagnostics = false')
    s = s.replace('Label("Pair on this iPhone", systemImage:',
                  'Label("在此 iPhone 上配對", systemImage:')
    marker = '''                Section {
                    Text("Fully on-device. Favorites and recents stay in UserDefaults. No analytics, no accounts, nothing uploaded.")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }'''
    replacement = '''                Section("工具") {
                    LabeledContent("配對狀態") {
                        Text(pairing.hasPairingFile ? "已配對" : "未配對")
                            .foregroundStyle(pairing.hasPairingFile ? LocusTheme.statusGood : LocusTheme.statusWarn)
                    }
                    Button {
                        showDiagnostics = true
                    } label: {
                        Label("診斷中心", systemImage: "stethoscope")
                    }
                }

                Section("隱私權") {
                    Text("完全在裝置端處理。我的最愛與最近使用會保存在 UserDefaults，不進行分析、不需要帳號，也不會上傳資料。")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }'''
    s = s.replace(marker, replacement)
    s = s.replace('''            .sheet(isPresented: $showPairOnDevice) {
                PairOnDeviceView()
                    .environmentObject(pairing)
            }''', '''            .sheet(isPresented: $showPairOnDevice) {
                PairOnDeviceView()
                    .environmentObject(pairing)
            }
            .sheet(isPresented: $showDiagnostics) {
                DiagnosticsView()
                    .environmentObject(pairing)
                    .environmentObject(session)
            }''')
    s = s.replace('.navigationTitle("Places")', '.navigationTitle("位置")')
    s = s.replace('Section("Favorites")', 'Section("我的最愛")')
    s = s.replace('Section("Recents")', 'Section("最近使用")')
    s = s.replace('Text("Star a pin from the map to save it.")', 'Text("在地圖上為圖釘加上星號即可儲存。")')
    s = s.replace('Text("Teleports show up here.")', 'Text("最近使用的位置會顯示在這裡。")')
    s = s.replace('Label("Delete", systemImage:', 'Label("刪除", systemImage:')
    s = s.replace('Label("Rename", systemImage:', 'Label("重新命名", systemImage:')
    s = s.replace('Button("Done")', 'Button("完成")')
    s = s.replace('TextField("Name", text:', 'TextField("名稱", text:')
    s = s.replace('Button("Cancel", role:', 'Button("取消", role:')
    s = s.replace('Button("Save")', 'Button("儲存")')
    s = s.replace('.alert("Rename Favorite"', '.alert("重新命名我的最愛"')
    s = s.replace('Text("Choose a name you’ll recognize later.")', 'Text("輸入一個方便之後辨識的名稱。")')
    return s

rw("Locus/Features/Settings/SettingsView.swift", patch_settings)

# Tunnel IP: explicit save button with validation and visible feedback.
def patch_tunnel_settings(s):
    # LocalDevVPN itself owns VPN configuration. DPort only detects whether
    # the app is installed/connected and opens LocalDevVPN when requested.
    # Do not expose the tunnel IP as a normal user setting.
    s = s.replace(
        '    @State private var vpnConfigured = LocalDevVPN.isConfigured\n',
        ''
    )
    s = s.replace(
        '    @State private var tunnelSaveMessage = ""\n',
        ''
    )
    s = s.replace(
        '    @State private var showTunnelSaveMessage = false\n',
        ''
    )

    # Replace the entire tunnel/settings block with a simple LocalDevVPN card.
    # It intentionally distinguishes:
    #   not installed -> App Store
    #   installed + not connected -> open LocalDevVPN
    #   connected -> connected
    section_re = re.compile(
        r'\n                Section \{\n'
        r'                    TextField\("(?:Device tunnel IP|裝置通道 IP|通道 IP)", text: \$tunnelIP\).*?'
        r'\n                \} header: \{\n'
        r'                    Text\("(?:Tunnel|通道|定位通道)"\)\n'
        r'                \} footer: \{\n'
        r'                    Text\(".*?10\.7\.0\.1.*?"\)\n'
        r'                \}',
        re.S
    )

    replacement = r'''
                Section("VPN 連線") {
                    LabeledContent("LocalDevVPN") {
                        Text(
                            !LocalDevVPN.isInstalled
                                ? "尚未安裝"
                                : (LocalDevVPN.isConnected ? "已連線" : "已安裝，尚未連線")
                        )
                        .foregroundStyle(
                            LocalDevVPN.isConnected
                                ? LocusTheme.statusGood
                                : (!LocalDevVPN.isInstalled ? LocusTheme.statusWarn : .secondary)
                        )
                    }

                    Button {
                        LocalDevVPN.openOrInstall()
                    } label: {
                        Label(
                            !LocalDevVPN.isInstalled
                                ? "安裝 LocalDevVPN"
                                : (LocalDevVPN.isConnected ? "開啟 LocalDevVPN" : "開啟並連線 VPN"),
                            systemImage: LocalDevVPN.isConnected
                                ? "checkmark.shield.fill"
                                : "lock.shield.fill"
                        )
                    }

                    if LocalDevVPN.isConnected {
                        Label("VPN 通道正常", systemImage: "checkmark.circle.fill")
                            .foregroundStyle(LocusTheme.statusGood)
                    } else if LocalDevVPN.isInstalled {
                        Text("請在 LocalDevVPN 中啟用連線。連線完成後返回 DPort，狀態會自動更新。")
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                    } else {
                        Text("尚未安裝 LocalDevVPN。點選上方按鈕即可前往 App Store。")
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                    }
                }
'''

    if section_re.search(s):
        s = section_re.sub(replacement, s, count=1)
    else:
        # Also support the previously patched VPN card.
        vpn_re = re.compile(
            r'\n                Section\("VPN 連線"\) \{.*?\n                \}\n'
            r'(?:\n                Section\("進階通道設定"\) \{.*?\n                \}\n)?',
            re.S
        )
        if vpn_re.search(s):
            s = vpn_re.sub(replacement, s, count=1)
        else:
            privacy = s.find('                Section("隱私權")')
            if privacy < 0:
                privacy = s.find('                Section("Privacy")')
            if privacy < 0:
                raise SystemExit("VPN section not found and privacy anchor missing")
            s = s[:privacy] + replacement + s[privacy:]

    # No manual tunnel configuration is needed. Keep only the installed state
    # used elsewhere by the settings page and refresh it when returning.
    s = s.replace(
        """            .onAppear {
                localDevVPNInstalled = LocalDevVPN.isInstalled
                tunnelIP = TunnelConfig.targetIP
            }""",
        """            .onAppear {
                localDevVPNInstalled = LocalDevVPN.isInstalled
            }""",
        1
    )
    return s

rw("Locus/Features/Settings/SettingsView.swift", patch_tunnel_settings)


write("Locus/Features/Map/CoordinateInputView.swift", r'''import SwiftUI
import CoreLocation

struct CoordinateInputView: View {
    @EnvironmentObject private var session: SpoofSession
    @Environment(\.dismiss) private var dismiss

    @State private var latitude = ""
    @State private var longitude = ""

    var body: some View {
        NavigationStack {
            Form {
                Section("座標") {
                    TextField("緯度", text: $latitude)
                        .keyboardType(.numbersAndPunctuation)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()

                    TextField("經度", text: $longitude)
                        .keyboardType(.numbersAndPunctuation)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                }

                Section {
                    Button {
                        apply()
                    } label: {
                        Label("套用座標", systemImage: "location.fill")
                    }
                    .disabled(!isValid)
                } footer: {
                    Text("支援十進制度 WGS84。緯度範圍 -90～90，經度範圍 -180～180。")
                }

                if let pin = session.pin {
                    Section("目前圖釘") {
                        LabeledContent("緯度", value: String(format: "%.6f", pin.latitude))
                        LabeledContent("經度", value: String(format: "%.6f", pin.longitude))
                    }
                }
            }
            .navigationTitle("輸入座標")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("取消") { dismiss() }
                }
            }
            .onAppear {
                if let pin = session.pin {
                    latitude = String(format: "%.6f", pin.latitude)
                    longitude = String(format: "%.6f", pin.longitude)
                }
            }
        }
    }

    private var parsed: CLLocationCoordinate2D? {
        guard let lat = Double(latitude.trimmingCharacters(in: .whitespacesAndNewlines)),
              let lon = Double(longitude.trimmingCharacters(in: .whitespacesAndNewlines)),
              (-90...90).contains(lat),
              (-180...180).contains(lon) else { return nil }
        return CLLocationCoordinate2D(latitude: lat, longitude: lon)
    }

    private var isValid: Bool { parsed != nil }

    private func apply() {
        guard let coordinate = parsed else { return }
        session.pin = coordinate
        session.pushNamedRecent(
            name: String(format: "%.5f, %.5f", coordinate.latitude, coordinate.longitude),
            coordinate: coordinate
        )
        dismiss()
    }
}
''')

write("Locus/Features/Settings/DiagnosticsView.swift", r'''import SwiftUI
import CoreLocation
import NetworkExtension

struct DiagnosticsView: View {
    @EnvironmentObject private var pairing: PairingStore
    @EnvironmentObject private var session: SpoofSession
    @Environment(\.dismiss) private var dismiss

    @State private var vpnConnected = LocalDevVPN.isConnected

    var body: some View {
        NavigationStack {
            List {
                Section("系統狀態") {
                    DiagnosticRow(title: "DPort 配對",
                                  detail: pairing.hasPairingFile ? "已配對" : "未配對",
                                  good: pairing.hasPairingFile)
                    DiagnosticRow(title: "LocalDevVPN",
                                  detail: vpnConnected ? "已連線" : "未連線",
                                  good: vpnConnected)
                    DiagnosticRow(title: "定位服務",
                                  detail: CLLocationManager.locationServicesEnabled() ? "已開啟" : "已關閉",
                                  good: CLLocationManager.locationServicesEnabled())
                    DiagnosticRow(title: "模擬定位",
                                  detail: session.isSpoofing ? "模擬定位中" : "未啟用",
                                  good: session.isSpoofing,
                                  neutralWhenFalse: true)
                }

                Section("位置") {
                    if let sim = session.simulated {
                        LabeledContent("模擬座標", value: String(format: "%.6f, %.6f", sim.latitude, sim.longitude))
                    } else {
                        Text("目前沒有模擬座標").foregroundStyle(.secondary)
                    }

                    if let real = session.realCoordinate {
                        LabeledContent("真實 GPS", value: String(format: "%.6f, %.6f", real.latitude, real.longitude))
                    } else {
                        Text("尚未取得真實 GPS").foregroundStyle(.secondary)
                    }
                }

                Section("快速操作") {
                    Button {
                        vpnConnected = LocalDevVPN.isConnected
                    } label: {
                        Label("重新檢查狀態", systemImage: "arrow.clockwise")
                    }

                    Button {
                        let version = Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "—"
                        let build = Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? "—"
                        let lines = [
                            "DPort 診斷資訊",
                            "配對：\(pairing.hasPairingFile ? "已配對" : "未配對")",
                            "LocalDevVPN：\(vpnConnected ? "已連線" : "未連線")",
                            "模擬定位：\(session.isSpoofing ? "啟用" : "未啟用")",
                            "版本：\(version) (\(build))"
                        ]
                        UIPasteboard.general.string = lines.joined(separator: "\n")
                    } label: {
                        Label("複製診斷資訊", systemImage: "doc.on.doc")
                    }
                }
            }
            .navigationTitle("診斷中心")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("完成") { dismiss() }
                }
            }
            .onReceive(NotificationCenter.default.publisher(for: .NEVPNStatusDidChange)) { _ in
                vpnConnected = LocalDevVPN.isConnected
            }
        }
    }
}

private struct DiagnosticRow: View {
    let title: String
    let detail: String
    let good: Bool
    var neutralWhenFalse = false

    var body: some View {
        HStack {
            Image(systemName: good ? "checkmark.circle.fill" : "exclamationmark.circle.fill")
                .foregroundStyle(good ? LocusTheme.statusGood : (neutralWhenFalse ? .secondary : LocusTheme.statusWarn))
            Text(title)
            Spacer()
            Text(detail)
                .foregroundStyle(good ? LocusTheme.statusGood : .secondary)
        }
    }
}
''')


# Final UI polish: remove remaining user-visible English/Locus branding.
def patch_pair_view(s):
    reps = {
        'navigationTitle("Pair on this iPhone")':'navigationTitle("在此 iPhone 上配對")',
        'Button("Close")':'Button("關閉")',
        'Text("No computer needed")':'Text("不需要電腦")',
        'Text("Locus advertises a pairable host. iOS connects from Developer Mode, then Locus shows a 6-digit code for you to type.")':'Text("DPort 會建立可配對連線。請從「開發者模式」連線，接著在 DPort 輸入 6 位數驗證碼。")',
        'Text("Follow these steps")':'Text("請依照以下步驟操作")',
        'Text("Keep Locus open. You’ll leave briefly for Settings, then come back with a code.")':'Text("請保持 DPort 開啟。暫時前往「設定」，完成配對後再回到 DPort。")',
        'Tap Start pairing and allow Local Network + Location when asked.':'點選「開始配對」，並在系統詢問時允許「區域網路」與「定位」。',
        'Allow notifications — the code can appear as a banner over Settings.':'允許通知，驗證碼可能會以通知橫幅顯示在「設定」畫面上。',
        'Open Settings › Privacy & Security › Developer Mode › Pair with Locus → Pair.':'開啟「設定」›「隱私權與安全性」›「開發者模式」›「與 DPort 配對」→「配對」。',
        'Enter your unlock passcode first. On the next prompt, type Locus’s 6-digit code.':'先輸入裝置解鎖密碼，再於下一個畫面輸入 DPort 的 6 位數驗證碼。',
        'Label("If the code isn’t here yet", systemImage:':'Label("如果還沒看到驗證碼", systemImage:',
        'Text("Keep the app listening while you confirm in Developer Mode. Don’t force-quit. If “Pair with Locus” vanishes, stop/start pairing and reopen Developer Mode.")':'Text("在「開發者模式」確認時，請保持 DPort 開啟，不要強制關閉。如果「與 DPort 配對」消失，請停止後重新開始配對，再開啟「開發者模式」。")',
        'Label("Ready when you are", systemImage:':'Label("準備就緒，等待開始", systemImage:',
        'Text("Waiting for Settings…")':'Text("等待「設定」連線…")',
        'Text("In Developer Mode tap Pair with Locus → Pair.")':'Text("請在「開發者模式」點選「與 DPort 配對」→「配對」。")',
        'Text("iPhone connected")':'Text("iPhone 已連線")',
        'Text("Generating your 6-digit code…")':'Text("正在產生 6 位數驗證碼…")',
        'Text("Enter this code in Settings")':'Text("請在「設定」輸入此驗證碼")',
        'Text("Second prompt only — after your unlock passcode.")':'Text("這是第二個提示畫面的驗證碼，請先完成裝置解鎖驗證。")',
        'Text("Paired")':'Text("已配對")',
        'Next we’ll set up LocalDevVPN.':'接下來設定 LocalDevVPN。',
        'RPPairing file saved. Connect LocalDevVPN, then teleport.':'配對檔案已儲存。請連線 LocalDevVPN 後即可使用定位。',
        'Text("Pairing failed")':'Text("配對失敗")',
        'Text(host.phase == .idle ? "Start pairing" : "Try again")':'Text(host.phase == .idle ? "開始配對" : "再試一次")',
        'Text(mode == .embedded ? "Continue" : "Done")':'Text(mode == .embedded ? "繼續" : "完成")',
        'return "Type the code above into the second Settings prompt."':'return "請在「設定」的第二個提示畫面輸入上方驗證碼。"',
        'return "Connected — code coming next."':'return "已連線，驗證碼即將產生。"',
        'default: return "Waiting for iOS to connect… don’t force-quit Locus."':'default: return "等待 iOS 連線…請不要強制關閉 DPort。"'
    }
    for (a,b) in reps.items():
        s = s.replace(a, b)
    return s

rw("Locus/Features/Settings/PairOnDeviceView.swift", patch_pair_view)

def patch_setup_view(s):
    reps = {
        'Text("Locus")':'Text("DPort")',
        'Text("Teleport your location.\\\nNo computer required.")':'Text("模擬你的定位位置。\\\n不需要電腦。")',
        'Text("A short setup — about two minutes.")':'Text("簡單設定，大約需要兩分鐘。")',
        'primaryButton("Get started")':'primaryButton("開始設定")',
        'Text("Connect this iPhone")':'Text("連線此 iPhone")',
        'Text("Locus needs a one-time pairing so it can set your location. You’ll confirm a short code in Settings.")':'Text("DPort 需要完成一次配對，才能設定你的定位位置。請在「設定」確認驗證碼。")',
        'Text("Import a pairing file from your computer — Locus uses it to set your location securely on this device.")':'Text("從電腦匯入配對檔案，DPort 會在此裝置上安全地使用它設定定位。")',
        'primaryButton("Import pairing file")':'primaryButton("匯入配對檔案")',
        'Text("Paste from clipboard")':'Text("從剪貼簿貼上")',
        '.alert("Locus", isPresented:':' .alert("DPort", isPresented:',
        'Button("OK", role: .cancel)':'Button("確定", role: .cancel)'
    }
    for (a,b) in reps.items():
        s = s.replace(a, b)
    return s
rw("Locus/Features/Setup/SetupFlowView.swift", patch_setup_view)

def patch_map_view(s):
    reps = {
        'TextField("Search places", text: $searchText)':'TextField("搜尋地點", text: $searchText)',
        'Button("Done")':'Button("完成")',
        'accessibilityLabel("Clear and dismiss keyboard")':'accessibilityLabel("清除並關閉鍵盤")',
        'accessibilityLabel("Current location")':'accessibilityLabel("目前位置")',
        'Annotation("Spoof", coordinate: sim)':'Annotation("模擬位置", coordinate: sim)',
        'session.lastError = "Set a route start and end."':'session.lastError = "請設定路線起點與終點。"',
        'session.lastError = "Build or draw a route first."':'session.lastError = "請先建立或繪製路線。"',
        'session.lastError = "Nothing to export."':'session.lastError = "目前沒有可匯出的路線。"',
        'appendingPathComponent("Locus-Route.gpx")':'appendingPathComponent("DPort-Route.gpx")'
    }
    for (a,b) in reps.items():
        s = s.replace(a, b)
    return s
rw("Locus/Features/Map/MapHomeView.swift", patch_map_view)

rw("Locus/Resources/Info.plist", lambda s:
   s.replace("<string>Locus</string>", "<string>DPort</string>", 1)
    .replace("Locus uses your real location so you can aim the map and return home after teleporting.",
             "DPort 會使用你的實際位置，協助地圖定位與返回目前位置。")
    .replace("Locus keeps a light location session alive so simulated GPS can stay active in the background.",
             "DPort 會維持必要的定位工作階段，讓模擬定位可在背景持續運作。")
    .replace("Locus uses the local network to advertise as a pairable host (iOS 27 pairing) and to reach the developer tunnel (LocalDevVPN) for GPS override.",
             "DPort 會使用區域網路進行 iOS 27 配對，並透過 LocalDevVPN 連線至開發者定位通道。"))


# Build 51: automatic LocalDevVPN setup/status integration.
# DPort cannot edit another app's VPN profile directly, but the LocalDevVPN
# public deep-link starts its own manager and creates the configuration when
# missing. We use that supported entry point and return to DPort automatically.
def patch_vpn_integration(s):
    s = s.replace(
        'static let enableURL = URL(string: "localdevvpn://enable?scheme=locus")!',
        'static let enableURL = URL(string: "localdevvpn://enable?scheme=dport")!'
    )
    if 'static let setupKey = "dport.localdevvpn.setupRequested"' not in s:
        s = s.replace(
            '    static let detectURL = URL(string: "localdevvpn://")!\n',
            '    static let detectURL = URL(string: "localdevvpn://")!\n    static let setupKey = "dport.localdevvpn.setupRequested"\n'
        )
    anchor = '''    static var isInstalled: Bool {
        UIApplication.shared.canOpenURL(detectURL)
    }
'''
    replacement = '''    static var isInstalled: Bool {
        UIApplication.shared.canOpenURL(detectURL)
    }

    static var isConfigured: Bool {
        UserDefaults.standard.bool(forKey: setupKey) || isConnected
    }

    static func markConfigured() {
        UserDefaults.standard.set(true, forKey: setupKey)
    }

    /// Opens LocalDevVPN's supported enable deep-link. LocalDevVPN creates
    /// its provider configuration automatically if one does not exist.
    static func autoConfigureAndConnect() {
        markConfigured()
        if isInstalled {
            UIApplication.shared.open(enableURL)
        } else {
            openAppStore()
        }
    }
'''
    if anchor not in s:
        raise SystemExit("LocalDevVPN isInstalled anchor not found")
    s = s.replace(anchor,replacement,1)
    return s

vpn=ROOT / "Locus" / "Support" / "LocalDevVPN.swift"
if vpn.exists():
    vpn.write_text(patch_vpn_integration(vpn.read_text(encoding="utf-8")), encoding="utf-8")

# Return callback from LocalDevVPN and remember that DPort setup succeeded.
app=ROOT / "Locus" / "App" / "LocusApp.swift"
if app.exists():
    s=app.read_text(encoding="utf-8")
    old='''    private func handleIncoming(_ url: URL) {
        let ext = url.pathExtension.lowercased()
'''
    new='''    private func handleIncoming(_ url: URL) {
        if url.scheme == "dport" {
            LocalDevVPN.markConfigured()
            NotificationCenter.default.post(name: .dportVPNStatusChanged, object: nil)
            return
        }

        let ext = url.pathExtension.lowercased()
'''
    if old not in s:
        raise SystemExit("LocusApp handleIncoming anchor not found")
    s=s.replace(old,new,1)
    if 'static let dportVPNStatusChanged' not in s:
        s=s.replace(
            'static let locusImportGPX = Notification.Name("locusImportGPX")',
            'static let locusImportGPX = Notification.Name("locusImportGPX")\n    static let dportVPNStatusChanged = Notification.Name("dportVPNStatusChanged")'
        )
    app.write_text(s,encoding="utf-8")

# Automatic DPort-side tunnel default: no manual IP is required on first use.
tun=ROOT / "Locus" / "Engine" / "DeviceTunnel.swift"
if tun.exists():
    s=tun.read_text(encoding="utf-8")
    if 'static let configuredKey = "dport.tunnelIPConfigured"' not in s:
        s=s.replace(
            '    static let defaultsKey = "locus.targetDeviceIP"\n',
            '    static let defaultsKey = "locus.targetDeviceIP"\n    static let configuredKey = "dport.tunnelIPConfigured"\n'
        )
    if 'static var isConfigured:' not in s:
        s=s.replace(
            '''    static func setTargetIP(_ value: String) {
        UserDefaults.standard.set(value, forKey: defaultsKey)
    }
''',
            '''    static var isConfigured: Bool {
        if UserDefaults.standard.bool(forKey: configuredKey) { return true }
        return UserDefaults.standard.string(forKey: defaultsKey) != nil
    }

    static func ensureConfigured() {
        guard !isConfigured else { return }
        UserDefaults.standard.set(defaultIP, forKey: defaultsKey)
        UserDefaults.standard.set(true, forKey: configuredKey)
    }

    static func setTargetIP(_ value: String) {
        UserDefaults.standard.set(value, forKey: defaultsKey)
        UserDefaults.standard.set(true, forKey: configuredKey)
    }

    static func resetToDefault() {
        UserDefaults.standard.set(defaultIP, forKey: defaultsKey)
        UserDefaults.standard.set(true, forKey: configuredKey)
    }
''',
            1
        )
    tun.write_text(s,encoding="utf-8")

# Make the Settings screen behave like a first-run setup, not an IP form.
settings=ROOT / "Locus" / "Features" / "Settings" / "SettingsView.swift"
if settings.exists():
    s=settings.read_text(encoding="utf-8")
    s=s.replace(
        '    @State private var tunnelIP = TunnelConfig.targetIP',
        '    @State private var tunnelIP = TunnelConfig.targetIP\n    @State private var vpnConfigured = LocalDevVPN.isConfigured'
    )
    # Insert a dedicated automatic LocalDevVPN section before the existing
    # tunnel section. The section is idempotent so reruns do not duplicate it.
    if 'Section("VPN 連線")' not in s:
        needle='''                Section {
                    TextField("通道 IP", text: $tunnelIP)'''
        block='''                Section("VPN 連線") {
                    LabeledContent("LocalDevVPN") {
                        Text(
                            LocalDevVPN.isConnected
                                ? "已連線"
                                : (vpnConfigured ? "已設定" : "尚未設定")
                        )
                        .foregroundStyle(
                            LocalDevVPN.isConnected
                                ? LocusTheme.statusGood
                                : (vpnConfigured ? .secondary : LocusTheme.statusWarn)
                        )
                    }

                    LabeledContent("裝置通道") {
                        Text(TunnelConfig.targetIP)
                            .font(.system(.body, design: .monospaced))
                    }

                    if !vpnConfigured {
                        Button {
                            TunnelConfig.ensureConfigured()
                            vpnConfigured = true
                            LocalDevVPN.autoConfigureAndConnect()
                        } label: {
                            Label("自動設定並連線", systemImage: "wand.and.stars")
                        }
                    } else if !LocalDevVPN.isConnected {
                        Button {
                            LocalDevVPN.autoConfigureAndConnect()
                        } label: {
                            Label("開啟並連線 VPN", systemImage: "lock.shield.fill")
                        }
                    }

                    if LocalDevVPN.isConnected {
                        Label("VPN 通道正常", systemImage: "checkmark.shield.fill")
                            .foregroundStyle(LocusTheme.statusGood)
                    } else if vpnConfigured {
                        Text("VPN 已設定，目前尚未連線。")
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                    } else if !LocalDevVPN.isInstalled {
                        Text("尚未安裝 LocalDevVPN，點選「自動設定並連線」會前往 App Store。")
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                    }
                }

                Section("進階通道設定") {
                    TextField("通道 IP", text: $tunnelIP)'''
        if needle not in s:
            raise SystemExit("Settings tunnel section needle not found")
        s=s.replace(needle,block,1)

    # The old manual save remains available as advanced configuration but now
    # also records the setting state.
    s=s.replace(
        'TunnelConfig.setTargetIP(value)\n                            tunnelIP = TunnelConfig.targetIP',
        'TunnelConfig.setTargetIP(value)\n                            vpnConfigured = true\n                            tunnelIP = TunnelConfig.targetIP'
    )
    # On returning from LocalDevVPN, refresh the state and show configured.
    s=s.replace(
        '''            .onAppear {
                localDevVPNInstalled = LocalDevVPN.isInstalled
                tunnelIP = TunnelConfig.targetIP
            }''',
        '''            .onAppear {
                localDevVPNInstalled = LocalDevVPN.isInstalled
                TunnelConfig.ensureConfigured()
                tunnelIP = TunnelConfig.targetIP
                vpnConfigured = LocalDevVPN.isConfigured
            }
            .onReceive(NotificationCenter.default.publisher(for: .dportVPNStatusChanged)) { _ in
                vpnConfigured = LocalDevVPN.isConfigured
                localDevVPNInstalled = LocalDevVPN.isInstalled
                tunnelIP = TunnelConfig.targetIP
            }'''
    )
    settings.write_text(s,encoding="utf-8")

# Add DPort callback URL + LocalDevVPN query permission to the app Info.plist.
plist=ROOT / "Locus" / "Resources" / "Info.plist"
if plist.exists():
    s=plist.read_text(encoding="utf-8")
    if "<string>dport</string>" not in s:
        marker="</dict>\n</plist>"
        insert='''\t<key>CFBundleURLTypes</key>
\t<array>
\t\t<dict>
\t\t\t<key>CFBundleURLName</key>
\t\t\t<string>com.dicky.dport</string>
\t\t\t<key>CFBundleURLSchemes</key>
\t\t\t<array>
\t\t\t\t<string>dport</string>
\t\t\t</array>
\t\t</dict>
\t</array>
'''
        # Existing Info.plist already has URL types on upstream/Locus; insert
        # only a second URL declaration before the closing plist dictionary.
        s=s.replace(marker,insert+marker,1)
    # iOS requires LocalDevVPN to be declared in LSApplicationQueriesSchemes
    # before UIApplication.canOpenURL("localdevvpn://") can reliably detect
    # the installed app. Do not depend on the exact upstream plist ordering.
    if "<string>localdevvpn</string>" not in s:
        query='''\t<key>LSApplicationQueriesSchemes</key>
\t<array>
\t\t<string>localdevvpn</string>
\t</array>
'''
        if "<key>LSApplicationQueriesSchemes</key>" in s:
            raise SystemExit("LSApplicationQueriesSchemes exists but localdevvpn is missing")
        marker="</dict>\n</plist>"
        if marker not in s:
            raise SystemExit("Info.plist closing marker not found")
        s=s.replace(marker, query+marker, 1)
    plist.write_text(s,encoding="utf-8")

# New version without the digit 4.
project=PROJECT.read_text(encoding="utf-8")
project=project.replace('MARKETING_VERSION: "6.9.2"','MARKETING_VERSION: "6.9.5"')
project=project.replace('CURRENT_PROJECT_VERSION: "39"','CURRENT_PROJECT_VERSION: "51"')
PROJECT.write_text(project,encoding="utf-8")

print("DPort Build 51 automatic VPN setup layer applied.")

