#!/usr/bin/env python3
from pathlib import Path

ROOT = Path.cwd()
vpn = ROOT / "Locus" / "Support" / "LocalDevVPN.swift"
if not vpn.exists():
    raise SystemExit("LocalDevVPN.swift not found")

s = vpn.read_text(encoding="utf-8")

if "static func openOrInstall" not in s:
    marker = '''    static func openInstalled() {
        // Use LocalDevVPN's supported command URL in both states. The
        // callback returns to DPort through dport:// after one second.
        UIApplication.shared.open(enableURL)
    }'''
    replacement = '''    static func openInstalled() {
        UIApplication.shared.open(enableURL)
    }

    static func openOrInstall(completion: @escaping (Bool) -> Void = { _ in }) {
        UIApplication.shared.open(enableURL, options: [:]) { success in
            if success {
                markConfigured()
            } else {
                openAppStore()
            }
            completion(success)
        }
    }

    static func refreshInstallationStatus(completion: @escaping (Bool) -> Void) {
        if isInstalled {
            completion(true)
            return
        }
        UIApplication.shared.open(detectURL, options: [:]) { success in
            completion(success)
        }
    }'''
    if marker not in s:
        raise SystemExit("openInstalled block not found")
    s = s.replace(marker, replacement, 1)

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
        return isConfigured || isConnected
    }'''
if old not in s:
    raise SystemExit("isInstalled block not found")
s = s.replace(old, new, 1)
vpn.write_text(s, encoding="utf-8")

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
                        LocalDevVPN.openOrInstall { installed in
                            DispatchQueue.main.async {
                                localDevVPNInstalled = installed || LocalDevVPN.isInstalled
                                vpnConfigured = installed || LocalDevVPN.isConfigured
                            }
                        }
                    } label: {
                        Label("開啟 LocalDevVPN", systemImage: "lock.shield.fill")
                    }'''
    if old_button in s:
        s = s.replace(old_button, new_button, 1)

    s = s.replace(
        '''                            LocalDevVPN.autoConfigureAndConnect()''',
        '''                            LocalDevVPN.openOrInstall { installed in
                                DispatchQueue.main.async {
                                    localDevVPNInstalled = installed || LocalDevVPN.isInstalled
                                    vpnConfigured = installed || LocalDevVPN.isConfigured
                                }
                            }''',
    )
    settings.write_text(s, encoding="utf-8")

project = ROOT / "project.yml"
if project.exists():
    s = project.read_text(encoding="utf-8")
    s = s.replace('CURRENT_PROJECT_VERSION: "51"', 'CURRENT_PROJECT_VERSION: "52"')
    project.write_text(s, encoding="utf-8")

print("DPort Build 52 LocalDevVPN fix applied.")
