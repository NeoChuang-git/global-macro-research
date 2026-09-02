# 技術規格書：純文字 / Markdown 報告同步與靜態渲染架構

> 本規格書供 **Codex / 開發執行者** 直接閱讀與實作。  
> 目標：在維持現有 Zero-Token 靜態網站架構與 HTML 精美排版（含表格、卡片、燈號、響應式）的前提下，支援純文字 / Markdown 格式的報告輸入與自動化靜態轉譯。

---

## 1. 背景與核心目標

### 1.1 現況
- 目前系統自 Google Drive 同步獨立的 HTML 報告（內嵌 CSS 與 HTML 結構），並由 `report.html` 透過 iframe 呈現。
- **痛點**：產生報告的 Agent / 研究員需自行構造 HTML 標籤與樣式，容易出現標籤未閉合或排版不一致的問題。

### 1.2 目標
1. **雙軌輸入支援**：Google Drive 同步支援 `.html`、`.md`、`.txt` 三種副檔名。
2. **零 Token 靜態轉譯**：在 GitHub Actions 同步與本地建置時，自動將 `.md` / `.txt` 報告套用全站統一的精美 HTML 模板，生成符合語意且具備完整樣式（表格、卡片、燈號）的 HTML 檔案。
3. **完全向下相容**：現有已存在的歷史 HTML 報告維持原樣，不破壞舊有索引與閱讀器。

---

## 2. 純文字 / Markdown 排版語法契約

研究員或 Agent 上傳至 Google Drive 的純文字需遵循以下輕量規範：

### 2.1 表格語法（Markdown Pipe Table）
```markdown
| 監控領域 (Family) | 方向 | 燈號 | 核心證據 (Evidence) | 反證 (Counter-evidence) |
| :--- | :---: | :---: | :--- | :--- |
| Rates & Fed | ↑ | 🔴 | 2Y 利率急升 13bp，9月升息機率達 56% | 就業數據走弱 |
| AI Fundamentals | ↔ | 🟢 | Nvidia 財報展望確認需求強勁 | 記憶體毛利壓力 |
| Energy & FX | ↑ | 🟠 | Brent 原油維持 90 美元上方 | 美元流動性無緊縮 |
```
- 轉譯時需自動包裹在 `<div class="table-scroll"><table>...</table></div>` 中，支援手機端橫向滑動與表頭置頂。

### 2.2 卡片區塊（Cards）與重點摘錄（Quote）
```markdown
### Executive Summary
本週由短端利率重定價主導，新增 Iran 制裁與油價尾端風險...

> **今日 Macro Thesis：** AI Fundamental Strength + Sticky Inflation + Hawkish Fed Repricing
```
- `###` 三級標題與其下方內容自動轉譯或樣式化為具備邊框與陰影的卡片 `.card`。
- `>` 引言自動轉譯為 `.highlight-quote` 或 `.callout-box`。

### 2.3 風險燈號網格（Risk Lights Grid）
```markdown
- Global 🟠
- Growth 🟢🟡
- Inflation 🟠🔴
- Rates 🔴
- Liquidity 🟢🟡
```
- 列表形式的燈號自動透過 CSS 轉換為多欄網格排版（`display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));`）。

---

## 3. 架構與實作流程 (Pipeline)

```
[ Google Drive ] (.md / .txt / .html)
       │
       ▼ (sync_drive.py 鏡像同步)
[ 本地 reports/<category>/ 原始檔 ]
       │
       ▼ (若是 .md / .txt 則調用 render_markdown_to_html)
[ 生成 reports/<category>/<stem>.html ]
       │
       ▼ (build_site.py 建立索引與靜態打包)
[ _site / GitHub Pages ] (由 report.html 沙盒 iframe 安全呈現)
```

---

## 4. 具體程式碼修改規範 (Codex 實作指南)

### 4.1 `scripts/sync_drive.py`

1. **副檔名白名單擴充**：
   ```python
   # 原本只接受 .html：
   # if not name.lower().endswith(".html"):
   #     return None
   
   # 修改為支援 .html, .md, .txt：
   ALLOWED_EXTENSIONS = (".html", ".md", ".txt")
   if not any(name.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
       return None
   ```

2. **新增輕量 Markdown 轉譯器** (`render_markdown_report`)：
   - 可使用標準庫 `html` 搭配正則解析（或引入輕量依賴如 `markdown`）。
   - 轉譯時自動套用標準 HTML5 骨架、內嵌全站一致的 CSS（深色/淺色自適應、表格美化、卡片陰影）。
   - 輸出標準化 HTML 檔案至 `reports/<category>/<stem>.html`。

3. **統一報告標題解析**：
   - 移除檔名中的 `.md` / `.txt` 副檔名後，呼叫 `_display_title(name)` 正常產生標題與日期。

---

### 4.2 統一 HTML 模板樣式規範 (`REPORT_TEMPLATE_HTML`)

轉譯輸出的 HTML 必須包含以下核心樣式（確保與現有 HTML 報告完全一致）：

```html
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ TITLE }} — {{ DATE }}</title>
  <style>
    :root {
      --bg: #ffffff;
      --card-bg: #fafafa;
      --border: #e2e8f0;
      --text: #1e293b;
      --text-muted: #64748b;
      --accent: #0284c7;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #0b1020;
        --card-bg: #131a2e;
        --border: #2b3550;
        --text: #e8edf7;
        --text-muted: #9da9bd;
        --accent: #38bdf8;
      }
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans TC", sans-serif;
      max-width: 1080px;
      margin: 32px auto;
      padding: 0 20px;
      line-height: 1.75;
      background: var(--bg);
      color: var(--text);
    }
    .card {
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 20px;
      margin: 18px 0;
      background: var(--card-bg);
    }
    .table-scroll {
      overflow-x: auto;
      margin: 16px 0;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.95rem;
    }
    th, td {
      border: 1px solid var(--border);
      padding: 10px 14px;
      text-align: left;
    }
    th {
      background: rgba(0, 0, 0, 0.04);
      position: sticky;
      top: 0;
    }
    blockquote {
      border-left: 4px solid var(--accent);
      margin: 16px 0;
      padding: 10px 16px;
      background: rgba(2, 132, 199, 0.05);
      border-radius: 0 8px 8px 0;
    }
  </style>
</head>
<body>
  <h1>{{ TITLE }} — {{ DATE }}</h1>
  {{ CONTENT_HTML }}
  <footer>Global Macro Signal Report · {{ DATE }}</footer>
</body>
</html>
```

---

## 5. 驗收標準與可機檢測試案例 (Acceptance Criteria)

開發者需新增/更新 `tests/test_sync_drive.py`，通過以下機檢測試：

1. **`test_syncs_markdown_file_and_compiles_to_html`**：
   - 建立一份包含表格與標題的 `Test_Report_2026-09-02.md`。
   - 執行 `sync_reports()`。
   - 驗證本地成功生成 `reports/<category>/Test_Report_2026-09-02.html`。
   - 驗證 HTML 內含 `<table>`, `<th>`, `<td>` 與完整樣式。
2. **`test_reports_json_indexes_markdown_converted_reports`**：
   - 驗證 `data/reports.json` 正確記錄該報告的標題、日期、分類與 SHA256。
3. **`test_existing_html_reports_untouched`**：
   - 原有的 `.html` 檔案依然保持 100% 原始位元組不被覆寫。
4. **全套測試執行**：
   - `python3 -m unittest discover -s tests -v` 必須全部通過（16+ 項測試全部 Green）。
   - `python3 scripts/build_site.py` 成功編譯 `_site/`。
