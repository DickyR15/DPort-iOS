#!/usr/bin/env python3
from pathlib import Path

ROOT = Path.cwd()
PROJECT = ROOT / "project.yml"

def rw(rel, transform):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    p.write_text(transform(s), encoding="utf-8")

# Build 39.
project = PROJECT.read_text(encoding="utf-8")
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

print("DPort Build 39 feature layer applied.")
