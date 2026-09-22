#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path.cwd()
PROJECT = ROOT / "project.yml"
ROOT_VIEW = ROOT / "Locus/Features/Map/RootView.swift"

if not ROOT_VIEW.exists():
    raise SystemExit("RootView.swift not found")

s = ROOT_VIEW.read_text(encoding="utf-8")

# Normalize upstream MapHomeView initializer across Locus revisions.
# Build 70 does not use a showCoordinates binding.
s = re.sub(r'MapHomeView\\(\\s*showCoordinates:\\s*\\$showCoordinates\\s*\\)', 'MapHomeView()', s)

# Build 70 UI: match the requested DPort layout.
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
                    }

                    Text("搖桿模式")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(.primary)
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
                        trayIcon("mappin.and.ellipse", title: "標記") {
                            showCoordinates = true
                        }
                        trayIcon("ellipsis", title: "更多") {
                            showPlaces = true
                        }
                    }

                    HStack(spacing: 7) {
                        Button {
                            if session.joystickActive {
                                session.stopJoystick()
                            } else {
                                session.startJoystick(pairing: pairing)
                            }
                        } label: {
                            HStack(spacing: 5) {
                                Image(systemName: "dot.circle.and.hand.point.up.left.fill")
                                Text(session.joystickActive ? "搖桿關閉" : "搖桿開啟")
                            }
                            .font(.caption.weight(.bold))
                            .foregroundStyle(session.joystickActive ? .black : .primary)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 11)
                            .background(
                                Capsule().fill(
                                    session.joystickActive
                                    ? LocusTheme.accentSecondary
                                    : Color.primary.opacity(0.08)
                                )
                            )
                            .contentShape(Capsule())
                        }
                        .buttonStyle(.plain)

                        if session.isSpoofing {
                            Button {
                                session.stop(pairing: pairing)
                            } label: {
                                Text("停止")
                                    .font(.caption.weight(.bold))
                                    .foregroundStyle(.white)
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, 11)
                                    .background(Capsule().fill(LocusTheme.danger))
                                    .contentShape(Capsule())
                            }
                            .buttonStyle(.plain)
                        } else {
                            Button {
                                guard let pin = session.pin else {
                                    session.lastError = "請先點選地圖放置圖釘。"
                                    return
                                }
                                session.teleport(to: pin, pairing: pairing)
                            } label: {
                                HStack(spacing: 5) {
                                    Image(systemName: "location.fill")
                                    Text("傳送定位")
                                }
                                .font(.caption.weight(.bold))
                                .foregroundStyle(.black)
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 11)
                                .background(Capsule().fill(LocusTheme.accent))
                                .contentShape(Capsule())
                            }
                            .buttonStyle(.plain)
                            .disabled(session.isBusy)
                        }
                    }
                }
                .frame(maxWidth: .infinity)
            }
            .padding(12)
            .frame(width: proxy.size.width, height: compact ? 252 : 268)
            .locusGlass(.regular, in: trayShape)
            .contentShape(trayShape)
        }
        .frame(height: 268)
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

ROOT_VIEW.write_text(s, encoding="utf-8")

# Build 70 is set before xcodegen/build.
project = PROJECT.read_text(encoding="utf-8")
project = re.sub(r'CURRENT_PROJECT_VERSION:\s*"\d+"', 'CURRENT_PROJECT_VERSION: "70"', project, count=1)
PROJECT.write_text(project, encoding="utf-8")

print("DPort Build 70 UI applied: left joystick, labeled 4+4 controls, safe tray corners.")
