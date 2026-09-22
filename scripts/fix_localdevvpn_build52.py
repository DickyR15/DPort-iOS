#!/usr/bin/env python3
from pathlib import Path

ROOT = Path.cwd()
vpn = ROOT / "Locus" / "Support" / "LocalDevVPN.swift"
if not vpn.exists():
    raise SystemExit("LocalDevVPN.swift not found")

s = vpn.read_text(encoding="utf-8")

# Build 51 falsely reported "未安裝" when canOpenURL was false even though
# LocalDevVPN was already configured/connected. Keep the original URL-open
# implementation and make installation state also recognize an existing
# LocalDevVPN configuration.
old = '''    static var isInstalled: Bool {
        // Installation state must reflect the actual presence of
        // LocalDevVPN. Never use UserDefaults as an installation cache:
        // if the user removes LocalDevVPN, canOpenURL() must immediately
        // report false.
        return UIApplication.shared.canOpenURL(detectURL)
            || UIApplication.shared.canOpenURL(enableURL)
    }'''
new = '''    static var isInstalled: Bool {
        if UIApplication.shared.canOpenURL(detectURL)
            || UIApplication.shared.canOpenURL(enableURL) {
            return true
        }
        // A configured or connected LocalDevVPN profile is definitive
        // evidence that LocalDevVPN is installed on this device.
        return isConfigured || isConnected
    }'''
if old not in s:
    raise SystemExit("isInstalled block not found")
s = s.replace(old, new, 1)

vpn.write_text(s, encoding="utf-8")

# Keep the action simple and compatible with the upstream implementation:
# once installation is recognized, open LocalDevVPN's supported enable URL.
# Never send an installed/connected LocalDevVPN to the App Store.
settings = ROOT / "Locus" / "Features" / "Settings" / "SettingsView.swift"
if settings.exists():
    s = settings.read_text(encoding="utf-8")
    s = s.replace(
        '''                    Button {
                        LocalDevVPN.openOrInstall { installed in
                            DispatchQueue.main.async {
                                localDevVPNInstalled = installed || LocalDevVPN.isInstalled
                                vpnConfigured = installed || LocalDevVPN.isConfigured
                            }
                        }
                    } label: {
                        Label("開啟 LocalDevVPN", systemImage: "lock.shield.fill")
                    }''',
        '''                    Button {
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
                    }''',
        1
    )
    s = s.replace(
        '''                            LocalDevVPN.openOrInstall { installed in
                                DispatchQueue.main.async {
                                    localDevVPNInstalled = installed || LocalDevVPN.isInstalled
                                    vpnConfigured = installed || LocalDevVPN.isConfigured
                                }
                            }''',
        '''                            LocalDevVPN.autoConfigureAndConnect()''',
    )
    settings.write_text(s, encoding="utf-8")

project = ROOT / "project.yml"
if project.exists():
    s = project.read_text(encoding="utf-8")
    s = s.replace('CURRENT_PROJECT_VERSION: "51"', 'CURRENT_PROJECT_VERSION: "53"')
    project.write_text(s, encoding="utf-8")

print("DPort Build 53 LocalDevVPN state detection fix applied.")vpn=ROOT / "Locus" / "Support" / "LocalDevVPN.swift"
if vpn.exists():
    s=vpn.read_text(encoding="utf-8")
    # iOS 27: canOpenURL() is not reliable enough for this integration in
    # practice. Apple explicitly recommends attempting open() and handling
    # its completion result instead of using canOpenURL() as a gate.
    # Keep canOpenURL only as a fast status hint; the actual button action
    # always uses open(enableURL).
    s=s.replace("import UIKit\n", "import UIKit\n")
    s=s.replace(
        '''    static var isInstalled: Bool {
        // Installation state must reflect the actual presence of
        // LocalDevVPN. Never use UserDefaults as an installation cache:
        // if the user removes LocalDevVPN, canOpenURL() must immediately
        // report false.
        return UIApplication.shared.canOpenURL(detectURL)
            || UIApplication.shared.canOpenURL(enableURL)
    }''',
        '''    static var isInstalled: Bool {
        UIApplication.shared.canOpenURL(enableURL)
            || UIApplication.shared.canOpenURL(detectURL)
            || isConnected
    }''',
        1
    )
    # Replace every installed/open gate with an actual open attempt.
    import re
    s=re.sub(
        r'''    static func openInstalled\(\) \{.*?\n    \}''',
        '''    static func openInstalled(completion: @escaping (Bool) -> Void = { _ in }) {
        UIApplication.shared.open(enableURL, options: [:]) { success in
            completion(success)
        }
    }''',
        s,
        count=1,
        flags=re.S
    )
    s=re.sub(
        r'''    static func autoConfigureAndConnect\(\) \{.*?\n    \}''',
        '''    static func autoConfigureAndConnect() {
        openInstalled { success in
            if !success {
                openAppStore()
            }
        }
    }''',
        s,
        count=1,
        flags=re.S
    )
    s=re.sub(
        r'''    static func openOrInstall\(\) \{.*?\n    \}''',
        '''    static func openOrInstall(completion: @escaping (Bool) -> Void = { _ in }) {
        openInstalled { success in
            if !success {
                openAppStore()
            }
            completion(success)
        }
    }''',
        s,
        count=1,
        flags=re.S
    )
    vpn.write_text(s,encoding="utf-8")

settings=ROOT / "Locus" / "Features" / "Settings" / "SettingsView.swift"
if settings.exists():
    s=settings.read_text(encoding="utf-8")
    import re
    # Button: never decide App Store from a stale/false canOpenURL result.
    s=re.sub(
        r'''                    Button \{\n                        if localDevVPNInstalled \{\n                            LocalDevVPN\.openInstalled\(\)\n                        \} else \{\n                            LocalDevVPN\.openAppStore\(\)\n                        \}\n                    \} label: \{\n                        Label\(\n                            localDevVPNInstalled \? "Open LocalDevVPN" : "Get LocalDevVPN \(App Store\)",\n                            systemImage: localDevVPNInstalled \? "lock\.shield\.fill" : "arrow\.down\.app\.fill"\n                        \)\n                    \}''',
        '''                    Button {
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
                    }''',
        s,
        count=1
    )
    # Status: never call an installed app "未安裝" merely because canOpenURL
    # returned false. "尚未連線" is the only safe state until an open attempt
    # confirms the app.
    s=s.replace(
        '''Text(LocalDevVPN.isConnected ? "Connected" : "Not connected")
                            .foregroundStyle(LocalDevVPN.isConnected ? LocusTheme.statusGood : LocusTheme.statusWarn)''',
        '''Text(
                            LocalDevVPN.isConnected
                                ? "已連線"
                                : (localDevVPNInstalled ? "已安裝／未連線" : "尚未連線")
                        )
                        .foregroundStyle(
                            LocalDevVPN.isConnected
                                ? LocusTheme.statusGood
                                : (localDevVPNInstalled ? .secondary : LocusTheme.statusWarn)
                        )''',
        1
    )
    # Initial state: don't display a false "未安裝". Connected can still be
    # detected from the utun interface immediately.
    s=s.replace(
        '@State private var localDevVPNInstalled = LocalDevVPN.isInstalled',
        '@State private var localDevVPNInstalled = LocalDevVPN.isConnected'
    )
    s=s.replace(
        '''            .onAppear {
                localDevVPNInstalled = LocalDevVPN.isInstalled
            }
            .onChange(of: scenePhase) { _, phase in
                if phase == .active {
                    localDevVPNInstalled = LocalDevVPN.isInstalled
                }
            }''',
        '''            .onAppear {
                localDevVPNInstalled = LocalDevVPN.isConnected
            }
            .onChange(of: scenePhase) { _, phase in
                if phase == .active {
                    localDevVPNInstalled = localDevVPNInstalled || LocalDevVPN.isConnected
                }
            }''',
        1
    )
    settings.write_text(s,encoding="utf-8")

project=ROOT / "project.yml"
if project.exists():
    s=project.read_text(encoding="utf-8")
    s=s.replace('CURRENT_PROJECT_VERSION: "51"','CURRENT_PROJECT_VERSION: "54"')
    s=s.replace('CURRENT_PROJECT_VERSION: "52"','CURRENT_PROJECT_VERSION: "54"')
    s=s.replace('CURRENT_PROJECT_VERSION: "53"','CURRENT_PROJECT_VERSION: "54"')
    project.write_text(s,encoding="utf-8")

print("DPort Build 54: use open() completion for LocalDevVPN; never route an installed app to App Store due to canOpenURL.")

