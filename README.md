# DPort iOS

DPort is the DPort-branded iOS build layer for the MIT-licensed Locus open-source project.

## Build

GitHub Actions builds an unsigned IPA from the current upstream Locus source, then applies DPort branding and Traditional Chinese (Taiwan) localization.

Use **Actions → DPort iOS Build → Run workflow** to build manually.

The generated artifact is named **DPort-iOS-unsigned** and contains:

`DPort-6.9.2-Build39-TW.ipa`

## Base project

Upstream core:
https://github.com/ChrisMack32/Locus

Locus uses Apple developer location simulation / on-device developer tunnel mechanisms and includes the upstream MIT license and third-party notices.

## DPort identity

- App name: DPort
- Bundle ID: `com.dicky.dport`
- Marketing version: 6.9.2
- Build number: 39
- UI localization: 繁體中文（台灣）
- Brand: Dicky / DPort

The IPA produced by this workflow is unsigned and is intended to be signed by the sideloading tool used on the target device.


## 授權與第三方元件

DPort iOS 基於 MIT 授權的 Locus 專案修改而成，並保留 upstream 的 MIT 授權與著作權聲明。DPort 自有修改包含 DPort 品牌、繁體中文（台灣）在地化，以及 DPort-specific build/packaging 調整。

完整資訊請參閱 [LICENSE](LICENSE) 與 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。