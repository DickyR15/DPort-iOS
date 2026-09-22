#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path.cwd()
PROJECT = ROOT / "project.yml"
ROOT_VIEW = ROOT / "Locus/Features/Map/RootView.swift"
SPOOF_SESSION = ROOT / "Locus/Engine/SpoofSession.swift"
MAP_HOME = ROOT / "Locus/Features/Map/MapHomeView.swift"

if not ROOT_VIEW.exists():
    raise SystemExit("RootView.swift not found")

s = ROOT_VIEW.read_text(encoding="utf-8")

# DPort Build 76: immediate LocalDevVPN prompt when the app opens without the tunnel.
root_alert = '''        .alert("DPort", isPresented: Binding(
            get: { session.lastError != nil },
            set: { if !$0 { session.lastError = nil } }
        )) {
            if session.lastError?.contains("LocalDevVPN") == true {
                Button("連線 LocalDevVPN") {
                    session.lastError = nil
                    LocalDevVPN.openOrInstall()
                }
            }
            Button("稍後再說", role: .cancel) { session.lastError = nil }
        } message: {
            Text(session.lastError ?? "")
        }
        .onAppear {
            if !LocalDevVPN.isConnected {
                session.lastError = "請先連線 LocalDevVPN，才能使用定位與搖桿。"
            }
        }'''
root_sheet = '        .sheet(isPresented: $showSettings) {'
if root_alert not in s:
    s = s.replace(root_sheet, root_alert + "\n" + root_sheet, 1)


# Keep the joystick available by default. Stopping GPS simulation should not
# disable the joystick; the pad simply waits for the next simulated coordinate.
if SPOOF_SESSION.exists():
    ss = SPOOF_SESSION.read_text(encoding="utf-8")
    # Build 73/74: joystick works without a map pin and gives an immediate VPN prompt.
    if "func startJoystick(pairing: PairingStore)" in ss:
        old_j = """    func startJoystick(pairing: PairingStore) {
        guard pairing.hasPairingFile else {"""
        new_j = """    func startJoystick(pairing: PairingStore) {
        guard LocalDevVPN.isConnected else {
            lastError = "請先連線 LocalDevVPN，才能使用搖桿。"
            return
        }
        guard pairing.hasPairingFile else {"""
        ss = ss.replace(old_j, new_j, 1)
        ss = ss.replace(
            "        let start = simulated ?? pin ?? locationKeeper.lastKnownCoordinate",
            "        locationKeeper.start()\n        let start = simulated ?? pin ?? locationKeeper.lastKnownCoordinate",
            1
        )

        ss = ss.replace(
            """    func updateJoystick(vector: CGVector) {
        joystickVector = vector
    }""",
            """    func updateJoystick(vector: CGVector) {
        joystickVector = vector
    }

    /// Current joystick speed for the DPort UI, in km/h.
    var joystickSpeedKmh: Double {
        let magnitude = min(1.0, hypot(joystickVector.dx, joystickVector.dy))
        return travelMode.baseSpeed * magnitude * 3.6
    }""",
            1
        )

    # Keep joystick alive after Stop. The first joystick movement after Stop
    # reuses the latest real GPS coordinate and starts simulation again.
    if "private func tickJoystick(pairing: PairingStore)" in ss:
        old_tick = """    private func tickJoystick(pairing: PairingStore) {
        guard joystickActive, let current = simulated else { return }"""
        new_tick = """    private func tickJoystick(pairing: PairingStore) {
        guard joystickActive else { return }
        guard let current = simulated ?? locationKeeper.lastKnownCoordinate else { return }"""
        ss = ss.replace(old_tick, new_tick, 1)

    # Build 78: explicit maximum speeds by travel mode.
    ss = ss.replace(
        """        case .walk: return 1.4
        case .run: return 3.3
        case .cycle: return 6.5
        case .drive: return 13.4""",
        """        case .walk: return 1.6667
        case .run: return 4.1667
        case .cycle: return 9.7222
        case .drive: return 33.3333""",
        1
    )

    stop_start = ss.find("    func stop(pairing: PairingStore) {")
    stop_end = ss.find("\n    }\n\n    /// Best-known real device coordinate", stop_start)
    if stop_start >= 0 and stop_end >= 0:
        stop_block = ss[stop_start:stop_end]
        stop_block = stop_block.replace("        stopJoystick()\n", "", 1)
        ss = ss[:stop_start] + stop_block + ss[stop_end:]
        SPOOF_SESSION.write_text(ss, encoding="utf-8")

# Normalize upstream MapHomeView initializer across Locus revisions.
# Build 73 keeps showCoordinates binding and separates Locate / Stop Locate.
s = re.sub(r'MapHomeView\\(\\s*showCoordinates:\\s*\\$showCoordinates\\s*\\)', 'MapHomeView()', s)

# Build 73 UI: match the requested DPort layout and separate locate/stop actions.
# - Joystick is permanently on the LEFT side of the bottom tray.
# - Travel modes are a labeled 4-column row on the RIGHT.
# - Settings / Favorites / Pin / More are a labeled 4-column row.
# - Joystick and Teleport/Stop actions remain together at the bottom.
# - The tray uses explicit width constraints so its rounded corners never clip.

start = s.find("struct BottomControlsView: View {")
end = s.find("\nstruct IconButton: View {", start)
if start < 0 or end < 0:
    raise SystemExit("BottomControlsView block not found")

new_block = r'''struct BottomControlsView: View {
    @EnvironmentObject private var session: SpoofSession
    @EnvironmentObject private var pairing: PairingStore
    @Binding var showSettings: Bool
    @Binding var showPlaces: Bool
    @Binding var showCoordinates: Bool

    private let trayShape = RoundedRectangle(cornerRadius: 28, style: .continuous)
    @State private var modeNotice: String?
    @State private var modeNoticeTask: Task<Void, Never>?

    private var locateTitle: String {
        session.isSpoofing ? "更新定位" : "定位"
    }

    private var locateIcon: String {
        session.isSpoofing ? "location.north.line.fill" : "location.fill"
    }

    var body: some View {
        GeometryReader { proxy in
            let compact = proxy.size.width < 375
            let leftWidth: CGFloat = compact ? 142 : 154

            HStack(spacing: 12) {
                // MARK: Left — joystick
                VStack(spacing: 8) {
                    if session.joystickActive {
                        JoystickPad { vector in
                            session.updateJoystick(vector: vector)
                        }
                        .frame(width: compact ? 132 : 144, height: compact ? 132 : 144)
                    } else {
                        Button {
                            session.startJoystick(pairing: pairing)
                        } label: {
                            ZStack {
                                Circle()
                                    .fill(Color.primary.opacity(0.06))
                                    .overlay(
                                        Circle()
                                            .stroke(Color.primary.opacity(0.14), lineWidth: 1)
                                    )

                                Image(systemName: "dot.circle.and.hand.point.up.left.fill")
                                    .font(.system(size: 34, weight: .medium))
                                    .foregroundStyle(.secondary)
                            }
                            .frame(width: compact ? 132 : 144, height: compact ? 132 : 144)
                            .contentShape(Circle())
                        }
                        .buttonStyle(.plain)
                    }

                    Text("GPS 搖桿")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(.primary)

                    HStack(spacing: 8) {
                        Circle()
                            .fill(session.isSpoofing ? LocusTheme.statusGood : Color.blue)
                            .frame(width: 7, height: 7)
                        Text(session.isSpoofing ? "模擬 GPS" : "真實 GPS")
                            .font(.system(size: 10, weight: .semibold))
                        Text("•")
                            .foregroundStyle(.secondary)
                        Text(session.isSpoofing
                             ? (session.joystickSpeedKmh > 0.1 ? "移動中" : "已停止移動")
                             : "待命")
                            .font(.system(size: 10, weight: .semibold))
                        Text("•")
                            .foregroundStyle(.secondary)
                        Text(String(format: "%.1f km/h", session.joystickSpeedKmh))
                            .font(.system(size: 10, weight: .semibold))
                            .monospacedDigit()
                    }
                    .foregroundStyle(.primary.opacity(0.9))
                }
                .frame(width: leftWidth)
                .frame(maxHeight: .infinity, alignment: .center)

                Rectangle()
                    .fill(Color.primary.opacity(0.18))
                    .frame(width: 1)
                    .padding(.vertical, 8)

                // MARK: Right — all controls
                VStack(spacing: 8) {
                    HStack(spacing: 5) {
                        modeButton(.walk, title: "步行")
                        modeButton(.run, title: "跑步")
                        modeButton(.cycle, title: "腳踏車")
                        modeButton(.drive, title: "開車")
                    }

                    HStack(spacing: 5) {
                        trayIcon("gearshape.fill", title: "設定") {
                            showSettings = true
                        }
                        trayIcon("star.fill", title: "我的最愛") {
                            showPlaces = true
                        }
                        trayIcon("clock.arrow.circlepath", title: "最近使用") {
                            showPlaces = true
                        }
                        trayIcon("mappin.and.ellipse", title: "標記") {
                            showCoordinates = true
                        }
                    }

                    VStack(spacing: 2) {
                        HStack(spacing: 8) {
                            Circle()
                                .fill(LocalDevVPN.isConnected ? LocusTheme.statusGood : LocusTheme.statusBad)
                                .frame(width: 7, height: 7)
                            Text(LocalDevVPN.isConnected ? "LocalDevVPN 已連線" : "LocalDevVPN 未連線")
                                .font(.system(size: 10, weight: .bold))
                            Spacer(minLength: 4)
                            Text(session.isSpoofing ? "🟢 模擬定位中" : "🔵 尚未模擬定位")
                                .font(.system(size: 9, weight: .bold))
                        }
                    }
                    .foregroundStyle(.primary)
                    .padding(.horizontal, 8)
                    .frame(height: 42)

                    HStack(spacing: 7) {
                        // 定位與停止定位分開：定位中也能直接套用新的座標，
                        // 不需要先停止再重新定位。
                        Button {
                            guard LocalDevVPN.isConnected else {
                                session.lastError = "請先連線 LocalDevVPN，再使用定位或搖桿。"
                                return
                            }
                            guard let pin = session.pin ?? session.realCoordinate else {
                                session.lastError = "目前沒有可用的 GPS 座標。"
                                return
                            }
                            session.teleport(to: pin, pairing: pairing)
                        } label: {
                            HStack(spacing: 5) {
                                Image(systemName: locateIcon)
                                Text(locateTitle)
                            }
                            .font(.caption.weight(.bold))
                            .foregroundStyle(.black)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 11)
                            .background(Capsule().fill(LocusTheme.accent))
                            .contentShape(Capsule())
                        }
                        .buttonStyle(.plain)
                        .opacity(LocalDevVPN.isConnected ? 1.0 : 0.45)
                        .disabled(session.isBusy || !LocalDevVPN.isConnected)

                        Button {
                            guard session.isSpoofing || session.simulated != nil else {
                                session.lastError = "目前沒有正在進行的模擬定位。"
                                return
                            }
                            session.stop(pairing: pairing)
                        } label: {
                            HStack(spacing: 5) {
                                Image(systemName: "stop.fill")
                                Text("停止定位")
                            }
                            .font(.caption.weight(.bold))
                            .foregroundStyle(.white)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 11)
                            .background(Capsule().fill(
                                (session.isSpoofing || session.simulated != nil)
                                ? LocusTheme.danger : Color.primary.opacity(0.10)
                            ))
                            .contentShape(Capsule())
                        }
                        .buttonStyle(.plain)
                        .disabled(session.isBusy)
                        .simultaneousGesture(
                            LongPressGesture(minimumDuration: 0.8)
                                .onEnded { _ in
                                    guard session.isSpoofing || session.simulated != nil else { return }
                                    session.stop(pairing: pairing)
                                    session.simulated = nil
                                    session.pin = nil
                                    session.lastError = "已停止並清除模擬位置"
                                }
                        )
                    }
                }
                .frame(maxWidth: .infinity)
            }
            .padding(12)
            .frame(width: proxy.size.width, height: compact ? 258 : 276)
            .locusGlass(.regular, in: trayShape)
            .contentShape(trayShape)
        }
        .frame(height: 276)
        .overlay(alignment: .top) {
            if let modeNotice {
                Text(modeNotice)
                    .font(.caption.weight(.bold))
                    .foregroundStyle(.primary)
                    .padding(.horizontal, 14)
                    .padding(.vertical, 8)
                    .background(.ultraThinMaterial, in: Capsule())
                    .shadow(radius: 6)
                    .transition(.move(edge: .top).combined(with: .opacity))
                    .padding(.top, -10)
            }
        }
        .onAppear {
            if pairing.hasPairingFile && !session.joystickActive && LocalDevVPN.isConnected {
                session.startJoystick(pairing: pairing)
            }
        }
        .onDisappear { modeNoticeTask?.cancel() }
    }

    private func showModeNotice(_ title: String) {
        modeNoticeTask?.cancel()
        let speed: String
        switch session.travelMode {
        case .walk: speed = "6 km/h"
        case .run: speed = "15 km/h"
        case .cycle: speed = "35 km/h"
        case .drive: speed = "120 km/h"
        }
        withAnimation(.easeOut(duration: 0.2)) {
            modeNotice = "(title) · 最高 (speed)"
        }
        modeNoticeTask = Task {
            try? await Task.sleep(for: .milliseconds(1100))
            guard !Task.isCancelled else { return }
            await MainActor.run {
                withAnimation(.easeIn(duration: 0.2)) { modeNotice = nil }
            }
        }
    }

    private func modeButton(_ mode: TravelMode, title: String) -> some View {
        let selected = session.travelMode == mode

        return Button {
            session.travelMode = mode
        } label: {
            VStack(spacing: 3) {
                Image(systemName: mode.icon)
                    .font(.system(size: 18, weight: .semibold))
                    .foregroundStyle(selected ? .black : .primary)

                Text(title)
                    .font(.system(size: 11, weight: .semibold))
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
                    .foregroundStyle(selected ? .black : .primary)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 58)
            .background(
                Capsule().fill(
                    selected
                    ? LocusTheme.accent
                    : Color.primary.opacity(0.08)
                )
            )
            .contentShape(Capsule())
        }
        .buttonStyle(.plain)
    }

    private func trayIcon(
        _ systemName: String,
        title: String,
        action: @escaping () -> Void
    ) -> some View {
        Button(action: action) {
            VStack(spacing: 3) {
                Image(systemName: systemName)
                    .font(.system(size: 18, weight: .semibold))
                    .foregroundStyle(.primary)

                Text(title)
                    .font(.system(size: 10, weight: .semibold))
                    .lineLimit(1)
                    .minimumScaleFactor(0.72)
                    .foregroundStyle(.primary)
            }
            .frame(maxWidth: .infinity)
            .frame(height: 58)
            .background(Capsule().fill(Color.primary.opacity(0.08)))
            .contentShape(Capsule())
        }
        .buttonStyle(.plain)
    }
}
'''
s = s[:start] + new_block + s[end:]

# Root-level safe-area spacing: keep the tray completely inside all four corners.
s = s.replace(
    ".padding(.horizontal, 16)\n            .padding(.bottom, 8)",
    ".padding(.horizontal, 14)\n            .padding(.bottom, 8)",
    1,
)


# Build 81: clean circular simulated GPS marker; never show the selection pin during spoofing.
if MAP_HOME.exists():
    mh = MAP_HOME.read_text(encoding="utf-8")
    mh = mh.replace(
        """                    if let pin = session.pin {
                        Annotation("", coordinate: pin, anchor: .bottom) {""",
        """                    if let pin = session.pin, !session.isSpoofing {
                        Annotation("", coordinate: pin, anchor: .bottom) {""",
        1,
    )
    mh = mh.replace(
        """                    if let sim = session.simulated {
                        Annotation("DPort", coordinate: sim, anchor: .center) {
                            DPortSimulatedMarker(isActive: session.isSpoofing)
                        }
                    }""",
        """                    if let sim = session.simulated {
                        Annotation("模擬位置", coordinate: sim, anchor: .center) {
                            ZStack {
                                Circle()
                                    .fill(LocusTheme.accent.opacity(session.isSpoofing ? 0.22 : 0.14))
                                    .frame(width: session.isSpoofing ? 54 : 48,
                                           height: session.isSpoofing ? 54 : 48)
                                Circle()
                                    .fill(LocusTheme.accent)
                                    .frame(width: 18, height: 18)
                                    .overlay(Circle().stroke(.white, lineWidth: 3))
                            }
                            .shadow(color: LocusTheme.accent.opacity(0.35), radius: 5)
                        }
                    }""",
        1,
    )
    # Remove any legacy DPortSimulatedMarker that an earlier patch appended.
    marker_start = mh.find("\nprivate struct DPortSimulatedMarker: View")
    if marker_start >= 0:
        mh = mh[:marker_start] + "\n"
    MAP_HOME.write_text(mh, encoding="utf-8")

ROOT_VIEW.write_text(s, encoding="utf-8")

# Build 73 is set before xcodegen/build.
project = PROJECT.read_text(encoding="utf-8")
project = re.sub(r'CURRENT_PROJECT_VERSION:\s*"\d+"', 'CURRENT_PROJECT_VERSION: "81"', project, count=1)
PROJECT.write_text(project, encoding="utf-8")

print("DPort Build 81 UI applied: separate locate/stop buttons; locating can replace the active simulated coordinate.")
