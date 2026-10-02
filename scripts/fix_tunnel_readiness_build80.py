#!/usr/bin/env python3
from pathlib import Path

ROOT = Path.cwd()
LE = ROOT / "Locus/Engine/LocationEngine.swift"
SS = ROOT / "Locus/Engine/SpoofSession.swift"

if not LE.exists():
    raise SystemExit("LocationEngine.swift not found")

s = LE.read_text(encoding="utf-8")

old = '''        queue.sync {
            let code = setLocked(latitude: latitude, longitude: longitude, pairingPath: pairingPath, deviceIP: deviceIP)
            result = code == ok ? .success(()) : .failure(.from(code: code))
        }'''

new = '''        queue.sync {
            var code = setLocked(
                latitude: latitude,
                longitude: longitude,
                pairingPath: pairingPath,
                deviceIP: deviceIP
            )

            // LocalDevVPN can report a connected utun interface a fraction
            // before the peer endpoint is actually ready. Build 6.9.0 used
            // to surface tunnelCreate immediately in that race. Retry only
            // the tunnel-establishment failure; never repeat an actual
            // location/service error.
            if code == tunnelCreate {
                for delayUS in [250_000, 500_000, 1_000_000] {
                    usleep(useconds_t(delayUS))
                    code = setLocked(
                        latitude: latitude,
                        longitude: longitude,
                        pairingPath: pairingPath,
                        deviceIP: deviceIP
                    )
                    if code != tunnelCreate {
                        break
                    }
                }
            }

            result = code == ok ? .success(()) : .failure(.from(code: code))
        }'''

if old not in s:
    raise SystemExit("LocationEngine.set block not found")
s = s.replace(old, new, 1)
LE.write_text(s, encoding="utf-8")

if SS.exists():
    s = SS.read_text(encoding="utf-8")
    old_err = '''        case .failure(let error):
            lastError = error.localizedDescription
            if simulated != nil {
                status = .dropped(error.localizedDescription)
                postDropNotification(error.localizedDescription)
            } else {
                status = .idle
            }'''
    new_err = '''        case .failure(let error):
            if case .tunnelCreate = error {
                lastError = "LocalDevVPN 已連線，但開發者通道尚未就緒。請確認與電腦使用相同 Wi‑Fi 後再試一次。"
            } else {
                lastError = error.localizedDescription
            }
            if simulated != nil {
                status = .dropped(lastError ?? error.localizedDescription)
                postDropNotification(lastError ?? error.localizedDescription)
            } else {
                status = .idle
            }'''
    if old_err in s:
        s = s.replace(old_err, new_err, 1)
        SS.write_text(s, encoding="utf-8")

print("DPort tunnel readiness retry applied.")
