# DPort iOS

**DPort iOS** 是以開源專案 **Locus** 為基礎開發的 DPort 品牌 iOS / iPadOS 版本，加入 DPort 品牌識別、繁體中文（台灣）在地化、介面調整，以及 DPort 專用的建置與封裝流程。

> **重要：DPort iOS 並非 Apple 官方軟體，也不代表 Apple Inc.**
> DPort iOS 的安裝與使用必須依目標裝置、iOS / iPadOS 版本及適用的側載／開發者環境而定。

---

## 📱 主要功能

- 📍 **位置模擬**
  - 透過支援的開發者通道進行 iPhone / iPad 位置相關操作。
- 🗺️ **地圖定位**
  - 地圖瀏覽、位置選擇及圖釘操作。
  - 📍 附近地點：可搜尋餐廳、咖啡廳、便利商店、加油站、醫院、公共廁所、賣場、飯店及景點，選取後可直接套用為模擬位置。
  - ✏️ 地圖繪製路徑，並可交由路線模擬播放。
- 🧭 **GPX 與完整路線模擬**
  - GPX 路線資料匯入與匯出。
  - 道路／步道路線規劃。
  - 路線播放及模擬移動。
  - 支援暫停、繼續、反向與重新導向。
  - 支援途經點（Waypoint）與路線播放進度。
- 🔐 **開發者配對**
  - 支援與適用的 Apple 裝置進行配對及開發者相關操作。
- 🌐 **LocalDevVPN / 開發者通道**
  - 提供與支援的本機開發者通道相關功能。
- 🇹🇼 **繁體中文（台灣）介面**
  - DPort 專案介面與操作文字以繁體中文（台灣）為主要在地化語言。
- 🎨 **DPort 品牌**
  - DPort App 名稱、圖示、視覺識別與相關介面調整。

實際可用功能會依 iOS / iPadOS 版本、裝置型號、Developer Mode、配對狀態、開發者通道及其他環境條件而有所不同。

---

## 📦 安裝與使用

DPort iOS 的 GitHub Actions 可建立未簽署 IPA。

產生的 Artifact：

`DPort-iOS-unsigned`

範例檔名：

`DPort-6.9.0-TW.ipa`

此 IPA **不包含 Apple 簽章**。

使用者需要依自己的裝置與環境，使用合法且適用的簽署／側載方式完成安裝。

DPort iOS 本身不提供、保證或繞過 Apple 的簽署機制。

---

## 🛠️ GitHub Actions Build

本專案使用 GitHub Actions 建置 iOS 版本。

可由：

**Actions → DPort iOS Build → Run workflow**

執行建置。

主要流程：

1. 取得目前指定的上游 Locus 原始碼。
2. 套用 DPort 品牌及介面相關修改。
3. 套用繁體中文（台灣）在地化。
4. 套用 DPort-specific build / packaging 修改。
5. 建立未簽署 IPA。
6. 上傳 GitHub Actions Artifact。

> GitHub Actions 產生的 IPA 為未簽署版本，不包含 Apple App Store / Apple Developer 的正式發行簽章。

---

## 📋 系統需求

- iOS / iPadOS 18 或更新版本
- 相容的 iPhone / iPad 裝置
- 依功能需求啟用 Developer Mode
- 依功能需求完成裝置配對
- 適用的開發者通道或側載環境

部分功能可能受到 Apple 系統更新、裝置限制或第三方工具變更影響。

---

## 🧩 Base Project：Locus

DPort iOS 的主要上游專案：

**Locus**

https://github.com/ChrisMack32/Locus

Locus 採用 **MIT License**。

DPort iOS 是基於 Locus 進行修改與再開發的專案。上游 Locus 原始程式碼仍保留其原有著作權與 MIT 授權。

DPort iOS 不主張擁有 Locus 原始程式碼、其貢獻者創作內容或其他第三方元件的著作權。

---

## ✏️ DPort 修改內容

相對於上游 Locus，DPort iOS 的修改主要包含：

- DPort App 名稱與品牌識別
- DPort App 圖示與視覺資產
- 繁體中文（台灣）在地化
- DPort UI 文字與介面調整
- DPort-specific build scripts
- DPort-specific packaging 流程
- DPort 專案所需的功能調整與整合

其中哪些內容屬於 DPort 新增或修改，應以本 Repository 的 Git 歷史與實際原始碼為準。

---

## 🪪 DPort App Identity

| 項目 | 資訊 |
|---|---|
| App 名稱 | DPort |
| Bundle Identifier | `com.dicky.dport` |
| Marketing Version | 依正式 Release Tag |
| Build Number | 1 |
| 介面語言 | 繁體中文（台灣） |
| 品牌 | Dicky / DPort |
| 平台 | iOS / iPadOS |

正式版本號以 GitHub Release / Tag 為準。每個正式版本的 Source、建置產物與 Release 應以同一個 Git Tag 對應。

---

## 📜 授權與上游來源

DPort iOS 是基於開源專案 **Locus** 修改與再開發的專案。Locus 官方 Repository 目前標示為 MIT License。

### Locus 上游程式碼

- Project: Locus
- Repository: https://github.com/ChrisMack32/Locus
- License: MIT
- Copyright: Locus contributors

Locus 原始程式碼、原始著作權聲明及 MIT 授權仍適用於 Locus-derived code。

### DPort 原創修改

本 Repository 中由 DickyR15 / DPort 新增的品牌、繁體中文（台灣）在地化、UI 調整、建置與封裝腳本，以及其他由 DPort 自行創作的內容，依 Repository 根目錄 LICENSE 所載 MIT License 授權，除非特定檔案或元件另有明確標示。

### 第三方與 Apple SDK

DPort iOS 也可能使用 Locus 所包含的 Vendor/idevice 元件，以及 Apple SDK / system frameworks。

第三方元件的著作權、授權與使用條件仍由各自權利人控制，不因 DPort README 或品牌名稱而改變。完整資訊請參考 THIRD_PARTY_NOTICES.md。

### 商標

DPort 並非 Apple 官方產品，也不表示 Apple 背書、贊助、認證或官方合作。

Apple、iPhone、iPad、iOS、iPadOS 及相關名稱／商標屬其相關權利人所有。MIT License 不等同於授予任何第三方商標使用權。

---

## ⚠️ 免責聲明

DPort iOS 依「現況」提供，在法律允許的最大範圍內，不提供任何明示或默示保證。

使用 DPort iOS 時，可能受到 iOS / iPadOS 更新、Apple 裝置限制、Developer Mode、配對狀態、開發者通道、第三方工具、側載工具及 GitHub Actions 建置環境變更等因素影響。

使用者應自行確認相關操作符合所在地法律、Apple 適用條款，以及所使用第三方工具與服務的授權規範。

---

## 🔒 安全與隱私

DPort iOS 不應要求使用者將 Apple 帳號密碼、私鑰、憑證或其他敏感資料提交到公開 Repository。

建置、簽署與側載所涉及的憑證或私密金鑰，應由使用者自行安全保存。

請勿將 Apple Developer 私鑰、簽署憑證、個人 API Key、Token、密碼或其他秘密資訊直接提交到公開 Git Repository。

---

## 🙏 開源致謝

DPort iOS 的開發建立在開源社群的成果之上。

特別感謝：

- **Locus**
- Locus 的所有貢獻者
- `Vendor/idevice` 相關開發者
- 其他 DPort 所使用的開源元件作者與維護者

---

## 👤 作者

**DickyR15 / Dicky / DPort**

GitHub：

https://github.com/DickyR15

DPort iOS：

https://github.com/DickyR15/DPort-iOS

---

## 📄 授權文件

Repository 內提供：

- [`LICENSE`](LICENSE)
- [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)

本 Repository 的 MIT 授權不授予 Apple 或其他第三方商標權。

---

## Copyright

Copyright © 2026 DickyR15 / DPort

本 Repository 中的第三方程式碼、名稱、商標與其他內容，其權利仍歸各自權利人所有。