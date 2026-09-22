from pathlib import Path

p = Path("Locus/Features/Settings/SettingsView.swift")
s = p.read_text(encoding="utf-8")

old = '''    private var appVersion: String {
        let short = Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "—"
        let build = Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? ""
        return build.isEmpty ? short : "\\(short) (\\(build))"
    }'''

new = '''    private var appVersion: String {
        Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "—"
    }'''

if old not in s:
    raise SystemExit("Expected version display block not found")

p.write_text(s.replace(old, new, 1), encoding="utf-8")
print("DPort version display fixed: short version only")
