# DPort iOS

DPort iOS 是以 **MIT 授權的 Locus 開源專案**為基礎製作的 DPort 品牌版本。

## 功能

- iPhone 定位模擬
- 地圖定位與圖釘
- GPX 匯入與匯出
- 路線播放與模擬移動
- 開發者配對
- LocalDevVPN / 開發者通道相關功能
- 繁體中文（台灣）介面
- DPort 品牌與圖示

## Build

GitHub Actions 會從目前的 upstream Locus source 建置未簽署 IPA，再套用 DPort 品牌與繁體中文（台灣）在地化，以及 DPort-specific build / packaging 修改。

使用：

**Actions → DPort iOS Build → Run workflow**

產生的 Artifact：

`DPort-iOS-unsigned`

範例檔名：

`DPort-6.9.2-Build39-TW.ipa`

此 IPA 不包含 Apple 簽章，需由目標裝置上的側載工具完成簽署與安裝。

## 系統需求

- iOS / iPadOS 15 或更新版本
- 依功能需求使用 Developer Mode、配對及開發者通道
- 側載安裝時需使用適合目標裝置的簽署方式

## Base Project

Upstream project:

**Locus**

https://github.com/ChrisMack32/Locus

Locus 採 **MIT License** 授權。

DPort iOS 在 Locus 基礎上進行品牌、介面文字、在地化與建置流程修改。原始 Locus 著作權與 MIT 授權仍然適用於上游程式碼。

## DPort Identity

- App name: DPort
- Bundle ID: `com.dicky.dport`
- Marketing version: 6.9.2
- Build number: 39
- UI localization: 繁體中文（台灣）
- Brand: Dicky / DPort

## 授權與第三方元件

DPort iOS 使用 Locus 的 MIT 授權程式碼，並保留原始 MIT License 與著作權聲明。

DPort 的修改內容主要包括：

- DPort 品牌與 App 名稱
- DPort 圖示與視覺識別
- 繁體中文（台灣）在地化
- DPort-specific build / packaging scripts
- DPort UI 與功能調整

完整授權與第三方資訊請參閱：

- [LICENSE](LICENSE)
- [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)

DPort 不主張擁有 Locus 或其他第三方元件的著作權；第三方元件仍依其原始授權條款使用。

## 開源來源與致謝

DPort iOS 感謝以下開源專案及其貢獻者：

- Locus: https://github.com/ChrisMack32/Locus

第三方元件與完整授權資訊以 upstream Repository 以及 `THIRD_PARTY_NOTICES.md` 為準。

## 作者

Dicky / DPort

GitHub:
https://github.com/DickyR15/DPort-iOS
