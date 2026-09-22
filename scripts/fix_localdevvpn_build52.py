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

print("DPort Build 53 LocalDevVPN state detection fix applied.")
