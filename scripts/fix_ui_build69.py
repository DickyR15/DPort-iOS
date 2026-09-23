# DPort Nearby Places + Map Drawing: keep both controls independent.
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
    @State private var toastMessage: String?
    @State private var toastTask: Task<Void, Never>?

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
                    JoystickPad { vector in
                        if !LocalDevVPN.isConnected {
                            session.lastError = "請先連線 LocalDevVPN，才能使用搖桿。"
                            return
                        }
                        if !session.joystickActive {
                            session.startJoystick(pairing: pairing)
                        }
                        session.updateJoystick(vector: vector)
                    }
                    .frame(width: compact ? 132 : 144, height: compact ? 132 : 144)
                    .contentShape(Circle())

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
                            showToast(session.isSpoofing ? "✓ 已更新定位" : "✓ 定位完成")
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
                            showToast("✓ 已停止定位")
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
                                    session.lastError = "已停止定位，保留目前圖釘位置"
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
        .overlay(alignment: .top) {
            if let toastMessage {
                Text(toastMessage)
                    .font(.caption.weight(.bold))
                    .foregroundStyle(.primary)
                    .padding(.horizontal, 14)
                    .padding(.vertical, 8)
                    .background(.ultraThinMaterial, in: Capsule())
                    .shadow(radius: 6)
                    .transition(.move(edge: .top).combined(with: .opacity))
                    .padding(.top, 34)
            }
        }
        .onDisappear { modeNoticeTask?.cancel(); toastTask?.cancel() }
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
            modeNotice = "\(title) · 最高 \(speed)"
        }
        modeNoticeTask = Task {
            try? await Task.sleep(for: .milliseconds(1100))
            guard !Task.isCancelled else { return }
            await MainActor.run {
                withAnimation(.easeIn(duration: 0.2)) { modeNotice = nil }
            }
        }
    }

    private func showToast(_ message: String) {
        toastTask?.cancel()
        withAnimation(.easeOut(duration: 0.18)) { toastMessage = message }
        toastTask = Task {
            try? await Task.sleep(for: .milliseconds(1200))
            guard !Task.isCancelled else { return }
            await MainActor.run {
                withAnimation(.easeIn(duration: 0.18)) { toastMessage = nil }
            }
        }
    }

    private func modeButton(_ mode: TravelMode, title: String) -> some View {
        let selected = session.travelMode == mode

        return Button {
            session.travelMode = mode
            showModeNotice(title)
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



# DPort nearby places: make the top 「附近地點」 control explicit instead of
# silently doing a generic search. It opens categories and lets the user apply
# a selected POI directly as the simulated position.
if MAP_HOME.exists():
    mh = MAP_HOME.read_text(encoding="utf-8")

    state_anchor = '''    @State private var pinPlaceName: String?
'''
    state_new = '''    @State private var pinPlaceName: String?
    @State private var showNearbyPlaces = false
    @State private var nearbyCategory: NearbyCategory = .restaurant
    @State private var nearbyPlaces: [NearbyPlace] = []
    @State private var nearbyLoading = false
'''
    if state_anchor in mh and "showNearbyPlaces" not in mh:
        mh = mh.replace(state_anchor, state_new, 1)

    # Replace the entire top map toolbar using simple source indexes so the
    # result remains syntactically identical to the surrounding Swift.
    toolbar_start = mh.find("    private var mapChromeButtons: some View {")
    toolbar_end = mh.find("\n    private var locateButton: some View {", toolbar_start)
    if toolbar_start < 0 or toolbar_end < 0:
        raise SystemExit("DPort toolbar replacement failed: mapChromeButtons block not found")
    toolbar_replacement = '''    private var mapChromeButtons: some View {
        HStack(spacing: 4) {
            chromeIconButton("square.3.layers.3d") {
                session.mapStyleIndex = (session.mapStyleIndex + 1) % 3
            }
            chromeIconButton("point.topleft.down.to.point.bottomright.curvepath") {
                showRouteSheet = true
            }
            // IMPORTANT: Nearby Places must never touch drawMode.
            Button {
                showNearbyPlaces = true
                searchNearbyPlaces()
            } label: {
                Image(systemName: "mappin.and.ellipse")
            }
            .buttonStyle(.plain)
            .frame(width: 48, height: 48)
            .contentShape(Circle())
            .accessibilityLabel("附近地點")

            // Drawing is a completely separate control.
            chromeIconButton(drawMode ? "pencil.tip.crop.circle.badge.minus" : "pencil.tip.crop.circle") {
                drawMode.toggle()
                if !drawMode { drawnPath.removeAll() }
            }
            .foregroundStyle(drawMode ? LocusTheme.accentSecondary : .primary)
            .accessibilityLabel(drawMode ? "停止繪製" : "繪製路徑")

            if session.pin != nil {
                chromeIconButton("star.circle") {
                    if let pin = session.pin {
                        let name = session.suggestedFavoriteName(for: pin, fallback: pinPlaceName)
                        session.addFavorite(name: name, coordinate: pin)
                    }
                }
            }
        }
        .padding(6)
        .locusGlass(.clear, in: Capsule())
        .contentShape(Capsule())
    }'''
    mh = mh[:toolbar_start] + toolbar_replacement + mh[toolbar_end:]
    sheet_anchor = '''        .sheet(isPresented: $showRouteSheet) {
'''
    sheet_block = '''        .sheet(isPresented: $showNearbyPlaces) {
            NearbyPlacesSheet(
                category: $nearbyCategory,
                places: nearbyPlaces,
                isLoading: nearbyLoading,
                onSelect: { place in
                    session.pin = place.coordinate
                    pinPlaceName = place.name
                    pinSelected = false
                    position = .region(MKCoordinateRegion(
                        center: place.coordinate,
                        latitudinalMeters: 1200,
                        longitudinalMeters: 1200
                    ))
                    session.pushNamedRecent(name: place.name, coordinate: place.coordinate)
                    showNearbyPlaces = false
                },
                onSearch: { searchNearbyPlaces() }
            )
            .presentationDetents([.medium, .large])
        }
'''
    if sheet_anchor in mh and "NearbyPlacesSheet(" not in mh:
        mh = mh.replace(sheet_anchor, sheet_block + sheet_anchor, 1)

    route_marker = '''    private func buildRoadRoute() {
'''
    nearby_method = r'''    private func searchNearbyPlaces() {
        let center = session.isSpoofing ? session.simulated : session.realCoordinate
        guard let center else {
            session.lastError = "目前沒有可用的位置，無法搜尋附近地點。"
            return
        }

        nearbyLoading = true
        nearbyPlaces.removeAll()

        Task {
            let request = MKLocalSearch.Request()
            request.naturalLanguageQuery = nearbyCategory.query
            request.region = MKCoordinateRegion(
                center: center,
                latitudinalMeters: 3000,
                longitudinalMeters: 3000
            )
            request.resultTypes = [.pointOfInterest]

            let response = try? await MKLocalSearch(request: request).start()
            let found = (response?.mapItems ?? []).prefix(20).compactMap { item -> NearbyPlace? in
                guard let name = item.name else { return nil }
                return NearbyPlace(
                    name: name,
                    address: item.placemark.title ?? "",
                    coordinate: item.placemark.coordinate
                )
            }

            await MainActor.run {
                nearbyPlaces = Array(found)
                nearbyLoading = false
            }
        }
    }

'''
    if route_marker in mh and "private func searchNearbyPlaces()" not in mh:
        mh = mh.replace(route_marker, nearby_method + route_marker, 1)

    ext_marker = '''private extension UIWindowScene {
'''
    nearby_types = r'''private enum NearbyCategory: String, CaseIterable, Identifiable {
    case restaurant = "餐廳"
    case cafe = "咖啡廳"
    case convenience = "便利商店"
    case gas = "加油站"
    case hospital = "醫院"
    case restroom = "公共廁所"
    case shopping = "賣場"
    case hotel = "飯店"
    case attraction = "景點"

    var id: String { rawValue }

    var icon: String {
        switch self {
        case .restaurant: return "fork.knife"
        case .cafe: return "cup.and.saucer.fill"
        case .convenience: return "storefront.fill"
        case .gas: return "fuelpump.fill"
        case .hospital: return "cross.case.fill"
        case .restroom: return "figure.stand"
        case .shopping: return "cart.fill"
        case .hotel: return "bed.double.fill"
        case .attraction: return "camera.fill"
        }
    }

    var query: String {
        switch self {
        case .restaurant: return "餐廳"
        case .cafe: return "咖啡廳"
        case .convenience: return "便利商店"
        case .gas: return "加油站"
        case .hospital: return "醫院"
        case .restroom: return "公共廁所"
        case .shopping: return "購物中心 賣場"
        case .hotel: return "飯店"
        case .attraction: return "景點"
        }
    }
}

private struct NearbyPlace: Identifiable {
    let id = UUID()
    let name: String
    let address: String
    let coordinate: CLLocationCoordinate2D
}

private struct NearbyPlacesSheet: View {
    @Binding var category: NearbyCategory
    let places: [NearbyPlace]
    let isLoading: Bool
    let onSelect: (NearbyPlace) -> Void
    let onSearch: () -> Void

    var body: some View {
        NavigationStack {
            VStack(spacing: 10) {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(NearbyCategory.allCases) { item in
                            Button {
                                category = item
                                onSearch()
                            } label: {
                                Label(item.rawValue, systemImage: item.icon)
                                    .font(.caption.weight(.semibold))
                                    .padding(.horizontal, 11)
                                    .padding(.vertical, 8)
                                    .background(
                                        Capsule().fill(
                                            category == item
                                            ? LocusTheme.accent
                                            : Color.primary.opacity(0.08)
                                        )
                                    )
                                    .foregroundStyle(category == item ? .black : .primary)
                            }
                            .buttonStyle(.plain)
                        }
                    }
                    .padding(.horizontal, 2)
                }

                if isLoading {
                    Spacer()
                    ProgressView("正在搜尋附近\(category.rawValue)…")
                    Spacer()
                } else if places.isEmpty {
                    Spacer()
                    ContentUnavailableView(
                        "找不到附近\(category.rawValue)",
                        systemImage: "mappin.slash",
                        description: Text("請選擇其他分類或重新搜尋。")
                    )
                    Spacer()
                } else {
                    List(places) { place in
                        Button {
                            onSelect(place)
                        } label: {
                            VStack(alignment: .leading, spacing: 3) {
                                Text(place.name)
                                    .font(.body.weight(.semibold))
                                    .foregroundStyle(.primary)
                                if !place.address.isEmpty {
                                    Text(place.address)
                                        .font(.caption)
                                        .foregroundStyle(.secondary)
                                        .lineLimit(2)
                                }
                            }
                            .zIndex(2)
                        }
                    }
                    .listStyle(.plain)
                }
            }
            .padding(.top, 8)
            .navigationTitle("附近地點")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("重新搜尋", action: onSearch)
                }
            }
        }
    }
}

'''
    if ext_marker in mh and "private enum NearbyCategory" not in mh:
        mh = mh.replace(ext_marker, nearby_types + ext_marker, 1)

    MAP_HOME.write_text(mh, encoding="utf-8")

# DPort 6.9.0: keep the selected location pin visible during and after spoofing.
if MAP_HOME.exists():
    mh = MAP_HOME.read_text(encoding="utf-8")
    mh = mh.replace(
        """                    if let pin = session.pin {
                        Annotation("", coordinate: pin, anchor: .bottom) {""",
        """                    if let pin = session.pin {
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
project = re.sub(r'MARKETING_VERSION:\s*"[^"]+"', 'MARKETING_VERSION: "6.9.0"', project, count=1)
project = re.sub(r'CURRENT_PROJECT_VERSION:\s*"\d+"', 'CURRENT_PROJECT_VERSION: "1"', project, count=1)
PROJECT.write_text(project, encoding="utf-8")

print("DPort 6.9.0 UI applied: separate locate/stop buttons; locating can replace the active simulated coordinate.")
