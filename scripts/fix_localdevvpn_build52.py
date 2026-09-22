#!/usr/bin/env python3
from pathlib import Path
import plistlib

ROOT = Path.cwd()

# DPort Build 56 — LocalDevVPN fix.
# Do NOT use canOpenURL() as the gate for the action. Apple documents that
# open(_:options:completionHandler:) itself reports whether an installed app
# could handle the URL, and recommends handling open failures rather than
# relying on canOpenURL() as a validator.

vpn = ROOT / "Locus" / "Support" / "LocalDevVPN.swift"
if not vpn.exists():
    raise SystemExit("LocalDevVPN.swift not found")

s = vpn.read_text(encoding="utf-8")

old_installed = '''    static var isInstalled: Bool {
        // Installation state must reflect the actual presence of
        // LocalDevVPN. Never use UserDefaults as an installation cache:
        // if the user removes LocalDevVPN, canOpenURL() must immediately
        // report false.
        return UIApplication.shared.canOpenURL(detectURL)
            || UIApplication.shared.canOpenURL(enableURL)
    }'''
new_installed = '''    static var isInstalled: Bool {
        UIApplication.shared.canOpenURL(enableURL)
            || UIApplication.shared.canOpenURL(detectURL)
            || isConnected
    }'''

if old_installed in s:
    s = s.replace(old_installed, new_installed, 1)

old_open = '''    static func openInstalled() {
        // Use LocalDevVPN's supported command URL in both states. The
        // callback returns to DPort through dport:// after one second.
        UIApplication.shared.open(enableURL)
    }'''
new_open = '''    static func openInstalled(completion: @escaping (Bool) -> Void = { _ in }) {
        UIApplication.shared.open(enableURL, options: [:]) { success in
            completion(success)
        }
    }'''
if old_open in s:
    s = s.replace(old_open, new_open, 1)
else:
    old_open2 = '''    static func openInstalled() {
        UIApplication.shared.open(enableURL)
    }'''
    if old_open2 in s:
        s = s.replace(old_open2, new_open, 1)

old_or_install = '''    static func openOrInstall() {
        if isInstalled {
            openInstalled()
        } else {
            openAppStore()
        }
    }'''
new_or_install = '''    static func openOrInstall(completion: @escaping (Bool) -> Void = { _ in }) {
        openInstalled { success in
            if !success {
                openAppStore()
            }
            completion(success)
        }
    }'''
if old_or_install in s:
    s = s.replace(old_or_install, new_or_install, 1)

old_auto = '''    static func autoConfigureAndConnect() {
        if isInstalled {
            markConfigured()
            UIApplication.shared.open(enableURL)
        } else {
            openAppStore()
        }
    }'''
new_auto = '''    static func autoConfigureAndConnect() {
        openOrInstall()
    }'''
if old_auto in s:
    s = s.replace(old_auto, new_auto, 1)

vpn.write_text(s, encoding="utf-8")
# RootView still uses the old Button(action:) function reference from the
# upstream DPort patch. The new openOrInstall has a completion parameter, so
# give SwiftUI a zero-argument closure.
root = ROOT / "Locus" / "Features" / "Map" / "RootView.swift"
if root.exists():
    rs = root.read_text(encoding="utf-8")
    rs = rs.replace(
        "Button(action: LocalDevVPN.openOrInstall) {",
        "Button(action: { LocalDevVPN.openOrInstall() }) {"
    )
    root.write_text(rs, encoding="utf-8")



# Settings: never route to the App Store merely because canOpenURL() returned
# false. The actual open result decides whether LocalDevVPN exists.
settings = ROOT / "Locus" / "Features" / "Settings" / "SettingsView.swift"
if settings.exists():
    s = settings.read_text(encoding="utf-8")

    old_button = '''                    Button {
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
                    }'''
    new_button = '''                    Button {
                        LocalDevVPN.openOrInstall { success in
                            if success {
                                localDevVPNInstalled = true
                            }
                        }
                    } label: {
                        Label(
                            localDevVPNInstalled
                                ? "開啟 LocalDevVPN"
                                : "開啟／檢查 LocalDevVPN",
                            systemImage: "lock.shield.fill"
                        )
                    }'''
    if old_button in s:
        s = s.replace(old_button, new_button, 1)

    old_status = '''                        Text(
                            LocalDevVPN.isConnected
                                ? "已連線"
                                : (LocalDevVPN.isInstalled ? "已安裝" : "未安裝")
                        )
                        .foregroundStyle(
                            LocalDevVPN.isConnected
                                ? LocusTheme.statusGood
                                : (LocalDevVPN.isInstalled ? .secondary : LocusTheme.statusWarn)
                        )'''
    new_status = '''                        Text(
                            LocalDevVPN.isConnected
                                ? "已連線"
                                : (localDevVPNInstalled ? "已安裝／未連線" : "尚未連線")
                        )
                        .foregroundStyle(
                            LocalDevVPN.isConnected
                                ? LocusTheme.statusGood
                                : (localDevVPNInstalled ? .secondary : LocusTheme.statusWarn)
                        )'''
    if old_status in s:
        s = s.replace(old_status, new_status, 1)

    # Never initialize the UI to "未安裝" solely from canOpenURL().
    s = s.replace(
        '@State private var localDevVPNInstalled = LocalDevVPN.isInstalled',
        '@State private var localDevVPNInstalled = LocalDevVPN.isConnected',
        1
    )
    s = s.replace(
        '''            .onAppear {
                localDevVPNInstalled = LocalDevVPN.isInstalled
            }
            .onChange(of: scenePhase) { _, phase in
                if phase == .active {
                    localDevVPNInstalled = LocalDevVPN.isInstalled
                }
            }''',
        '''            .onAppear {
                localDevVPNInstalled = localDevVPNInstalled || LocalDevVPN.isConnected
            }
            .onChange(of: scenePhase) { _, phase in
                if phase == .active {
                    localDevVPNInstalled = localDevVPNInstalled || LocalDevVPN.isConnected
                }
            }''',
        1
    )
    settings.write_text(s, encoding="utf-8")

# Ensure canOpenURL is declared, although Build 54 does not depend on it for
# the actual open action.
for plist in ROOT.rglob("Info.plist"):
    try:
        with plist.open("rb") as fh:
            p = plistlib.load(fh)
        if "CFBundleIdentifier" not in p:
            continue
        schemes = list(p.get("LSApplicationQueriesSchemes", []))
        if "localdevvpn" not in schemes:
            schemes.append("localdevvpn")
            p["LSApplicationQueriesSchemes"] = schemes
            with plist.open("wb") as fh:
                plistlib.dump(p, fh, sort_keys=False)
    except Exception:
        pass

project = ROOT / "project.yml"
if project.exists():
    s = project.read_text(encoding="utf-8")
    import re
    s = re.sub(r'CURRENT_PROJECT_VERSION:\s*"\d+"', 'CURRENT_PROJECT_VERSION: "56"', s)
    project.write_text(s, encoding="utf-8")

# Build 57 — make LocalDevVPN status a real three-state check.
# iOS does not expose a supported API for querying whether another app is
# installed. canOpenURL() is unreliable here (it can return false while
# UIApplication.open() succeeds), so the UI must not call that result
# "uninstalled". The only definitive check is the result of open(enableURL).
# Persist only the last confirmed result; a failed open clears the flag.
settings = ROOT / "Locus" / "Features" / "Settings" / "SettingsView.swift"
if settings.exists():
    ss = settings.read_text(encoding="utf-8")

    ss = ss.replace(
        '@State private var localDevVPNInstalled = LocalDevVPN.isInstalled',
        '@AppStorage("dport.localdevvpn.installed") private var localDevVPNInstalled = false',
        1
    )

    old_status = '''                    LabeledContent("Status") {
                        Text(LocalDevVPN.isConnected ? "Connected" : "Not connected")
                            .foregroundStyle(LocalDevVPN.isConnected ? LocusTheme.statusGood : LocusTheme.statusWarn)
                    }'''
    new_status = '''                    LabeledContent("狀態") {
                        Text(
                            LocalDevVPN.isConnected
                                ? "已連線"
                                : (localDevVPNInstalled ? "已安裝／未連線" : "尚未檢查")
                        )
                        .foregroundStyle(
                            LocalDevVPN.isConnected
                                ? LocusTheme.statusGood
                                : (localDevVPNInstalled ? .secondary : LocusTheme.statusWarn)
                        )
                    }'''
    ss = ss.replace(old_status, new_status, 1)

    old_button = '''                    Button {
                        if localDevVPNInstalled {
                            LocalDevVPN.openInstalled()
                        } else {
                            LocalDevVPN.openAppStore()
                        }
                    } label: {
                        Label(
                            localDevVPNInstalled ? "Open LocalDevVPN" : "Get LocalDevVPN (App Store)",
                            systemImage: localDevVPNInstalled ? "lock.shield.fill" : "arrow.down.app.fill"
                        )
                    }'''
    new_button = '''                    Button {
                        LocalDevVPN.openInstalled { success in
                            DispatchQueue.main.async {
                                localDevVPNInstalled = success
                            }
                        }
                    } label: {
                        Label(
                            localDevVPNInstalled
                                ? "開啟 LocalDevVPN"
                                : "檢查／開啟 LocalDevVPN",
                            systemImage: "lock.shield.fill"
                        )
                    }'''
    ss = ss.replace(old_button, new_button, 1)

    # Remove canOpenURL-based lifecycle refresh. Only the VPN tunnel itself
    # determines "已連線"; installation is updated by the real open result.
    old_lifecycle = '''            .onAppear {
                localDevVPNInstalled = LocalDevVPN.isInstalled
            }
            .onChange(of: scenePhase) { _, phase in
                if phase == .active {
                    localDevVPNInstalled = LocalDevVPN.isInstalled
                }
            }'''
    new_lifecycle = '''            .onAppear {
                if LocalDevVPN.isConnected {
                    localDevVPNInstalled = true
                }
            }
            .onChange(of: scenePhase) { _, phase in
                if phase == .active, LocalDevVPN.isConnected {
                    localDevVPNInstalled = true
                }
            }'''
    ss = ss.replace(old_lifecycle, new_lifecycle, 1)

    settings.write_text(ss, encoding="utf-8")

# The actual open flow: success means LocalDevVPN is installed; failure means
# it is not available, and only then should we offer the App Store.
vpn = ROOT / "Locus" / "Support" / "LocalDevVPN.swift"
if vpn.exists():
    vs = vpn.read_text(encoding="utf-8")
    vs = vs.replace(
        '''    static var isInstalled: Bool {
        UIApplication.shared.canOpenURL(enableURL)
            || UIApplication.shared.canOpenURL(detectURL)
            || isConnected
    }''',
        '''    static var isInstalled: Bool {
        isConnected
    }''',
        1
    )
    vs = vs.replace(
        '''    static func openOrInstall(completion: @escaping (Bool) -> Void = { _ in }) {
        openInstalled { success in
            if !success {
                openAppStore()
            }
            completion(success)
        }
    }''',
        '''    static func openOrInstall(completion: @escaping (Bool) -> Void = { _ in }) {
        openInstalled { success in
            if !success {
                openAppStore()
            }
            completion(success)
        }
    }''',
        1
    )
    vpn.write_text(vs, encoding="utf-8")

project = ROOT / "project.yml"
if project.exists():
    ps = project.read_text(encoding="utf-8")
    import re
    ps = re.sub(r'CURRENT_PROJECT_VERSION:\s*"\d+"', 'CURRENT_PROJECT_VERSION: "57"', ps)
    project.write_text(ps, encoding="utf-8")

print("DPort Build 57: reliable LocalDevVPN three-state UI.")




# Build 59 — fix the actual developer-tunnel path and expose the FFI reason.
# Build 58's retry patch was too dependent on an exact upstream source block;
# this version uses regex-based replacement against the current Locus source.
location = ROOT / "Locus" / "Engine" / "LocationEngine.swift"
if not location.exists():
    raise SystemExit("LocationEngine.swift not found")
ls = location.read_text(encoding="utf-8")

# Preserve the public Int32 result API, but retain the actual FFI error text
# so the UI no longer collapses every failure into "VPN is not connected".
ls = ls.replace(
    '    private static var locationSimulation: OpaquePointer?\n',
    '    private static var locationSimulation: OpaquePointer?\n    private static var lastTunnelErrorMessage: String?\n    private static var lastRemoteServerErrorMessage: String?\n',
    1
)
ls = ls.replace(
    '        case .tunnelCreate: return "Could not open the developer tunnel. Is LocalDevVPN connected on Wi‑Fi?"',
    '        case .tunnelCreate: return "無法建立開發者通道：\\(LocationEngine.lastTunnelErrorMessage ?? "未知錯誤")"',
    1
)
ls = ls.replace(
    '        case .remoteServer: return "Connected to the tunnel but RemoteXPC handshake failed."',
    '        case .remoteServer: return "開發者通道已建立，但 RSD 交握失敗：\\(LocationEngine.lastRemoteServerErrorMessage ?? "未知錯誤")"',
    1
)

# Replace the one-shot RPPairing call with a robust retry block and preserve
# the native FFI diagnostic string.
import re
provider_pat = re.compile(
    r'''        let providerError = withUnsafePointer\(to: &address\) \{ pointer in\n'''
    r'''            pointer\.withMemoryRebound\(to: sockaddr\.self, capacity: 1\) \{\n'''
    r'''                tunnel_create_rppairing\(\n'''
    r'''                    \$0,\n'''
    r'''                    socklen_t\(MemoryLayout<sockaddr_in>\.stride\),\n'''
    r'''                    "LocusLocation",\n'''
    r'''                    pairingHandle,\n'''
    r'''                    nil,\n'''
    r'''                    nil,\n'''
    r'''                    &adapter,\n'''
    r'''                    &handshake\n'''
    r'''                \)\n'''
    r'''            \}\n'''
    r'''        \}\n'''
    r'''        if let providerError \{\n'''
    r'''            idevice_error_free\(providerError\)\n'''
    r'''            cleanup\(\)\n'''
    r'''            return tunnelCreate\n'''
    r'''        \}\n''')
provider_repl = '''        lastTunnelErrorMessage = nil
        var tunnelSucceeded = false
        for attempt in 0..<6 {
            cleanup()
            let providerError = withUnsafePointer(to: &address) { pointer in
                pointer.withMemoryRebound(to: sockaddr.self, capacity: 1) {
                    tunnel_create_rppairing(
                        $0,
                        socklen_t(MemoryLayout<sockaddr_in>.stride),
                        "LocusLocation",
                        pairingHandle,
                        nil,
                        nil,
                        &adapter,
                        &handshake
                    )
                }
            }
            if let providerError {
                if let message = providerError.pointee.message {
                    lastTunnelErrorMessage = String(cString: message)
                } else {
                    lastTunnelErrorMessage = "FFI error code \(providerError.pointee.code)"
                }
                idevice_error_free(providerError)
                if attempt < 5 {
                    usleep(500_000)
                    continue
                }
            } else {
                tunnelSucceeded = true
                break
            }
        }
        if !tunnelSucceeded {
            cleanup()
            return tunnelCreate
        }
'''
if not provider_pat.search(ls):
    raise SystemExit("Build59: exact tunnel_create_rppairing block not found")
ls = provider_pat.sub(provider_repl, ls, count=1)

# Replace the one-shot RSD handshake with retries and diagnostics.
rsd_pat = re.compile(
    r'''        if let remoteServerError = remote_server_connect_rsd\(adapter, handshake, &remoteServer\) \{\n'''
    r'''            idevice_error_free\(remoteServerError\)\n'''
    r'''            cleanup\(\)\n'''
    r'''            return remoteServerCode\n'''
    r'''        \}\n''')
rsd_repl = '''        lastRemoteServerErrorMessage = nil
        var rsdSucceeded = false
        for attempt in 0..<4 {
            if let remoteServerError = remote_server_connect_rsd(adapter, handshake, &remoteServer) {
                if let message = remoteServerError.pointee.message {
                    lastRemoteServerErrorMessage = String(cString: message)
                } else {
                    lastRemoteServerErrorMessage = "FFI error code \(remoteServerError.pointee.code)"
                }
                idevice_error_free(remoteServerError)
                remoteServer = nil
                if attempt < 3 {
                    usleep(500_000)
                    continue
                }
            } else {
                rsdSucceeded = true
                break
            }
        }
        if !rsdSucceeded {
            cleanup()
            return remoteServerCode
        }
'''
if not rsd_pat.search(ls):
    raise SystemExit("Build59: exact RSD block not found")
ls = rsd_pat.sub(rsd_repl, ls, count=1)

# Add a tiny route sanity check by probing the configured RSD endpoint before
# the FFI handshake. This is intentionally diagnostic only; it does not alter
# the VPN or send application data.
marker='''        guard let pairingHandle else { return pairingRead }
        defer { rp_pairing_file_free(pairingHandle) }
'''
probe='''        guard let pairingHandle else { return pairingRead }
        defer { rp_pairing_file_free(pairingHandle) }

        // If the VPN route is absent, report it explicitly rather than
        // misleadingly blaming the pairing file.
        let probeFD = socket(AF_INET, SOCK_STREAM, 0)
        if probeFD >= 0 {
            var tv = timeval(tv_sec: 2, tv_usec: 0)
            setsockopt(probeFD, SOL_SOCKET, SO_RCVTIMEO, &tv, socklen_t(MemoryLayout<timeval>.size))
            setsockopt(probeFD, SOL_SOCKET, SO_SNDTIMEO, &tv, socklen_t(MemoryLayout<timeval>.size))
            let probeResult = withUnsafePointer(to: &address) {
                $0.withMemoryRebound(to: sockaddr.self, capacity: 1) {
                    connect(probeFD, $0, socklen_t(MemoryLayout<sockaddr_in>.stride))
                }
            }
            close(probeFD)
            if probeResult != 0 {
                lastTunnelErrorMessage = "無法連線 \(deviceIP):49152（errno \(errno)）。請檢查 LocalDevVPN 的 Device IP／通道路由。"
            }
        }
'''
if marker not in ls:
    raise SystemExit("Build59: pairing marker not found")
ls=ls.replace(marker,probe,1)

location.write_text(ls, encoding="utf-8")

project = ROOT / "project.yml"
if project.exists():
    ps = project.read_text(encoding="utf-8")
    ps = re.sub(r'CURRENT_PROJECT_VERSION:\s*"\d+"', 'CURRENT_PROJECT_VERSION: "59"', ps)
    project.write_text(ps, encoding="utf-8")

print("DPort Build 59: robust RPPairing/RSD retries + real FFI diagnostics + route probe.")
