<<<REPORT_BEGIN>>>
---
research_status: COMPLETE
report_type: MACRO_TAIWAN_EARLY_WARNING
run_id: MTW-20261023-0400-chip-pressure-persistence
generated_at_taipei: 2026-10-23T04:13:26.397917+08:00
coverage_start_taipei: 2026-10-23T03:00:00+08:00
coverage_end_taipei: 2026-10-23T04:06:01+08:00
report_name: Global Macro Early Warning
title: Global Macro Early Warning｜晶片股弱勢延伸至交易尾段，估值壓力獲持續性確認
format_version: 2
trigger_status: TRIGGERED
risk_light: YELLOW
classification: TACTICAL
slug: chip-pressure-persistence
---
# Global Macro Early Warning｜晶片股弱勢延伸至交易尾段，估值壓力獲持續性確認

## 核心警報摘要（EXECUTIVE TAKE）

> 晶片股跌勢延伸至美國交易尾段，新增的是持續性與個股收盤廣度，不是把全天跌幅再報一次。科技估值壓力升高，但台積電 ADR 與廣泛股指部分修復，尚不支持升為系統性融資危機。

- **觸發理由：**官方 SOX 再弱、Nasdaq 跌幅加深，較新的 VIX 報價與 NVDA、AMD 明示收盤提供不同面向確認；各報價並非同時點。
- **機制辨識：**美債殖利率下降仍未拉起晶片股，較符合股票風險溢酬上升與 AI 投資回收疑慮，而非新的上升折現率衝擊。
- **反向證據：**TSMC、Lam 與 NVIDIA 供應鏈資料仍支持訂單及產能需求；股價修正尚不能直接改寫為基本面週期轉折。
- **台灣意涵：**既有外資賣超與期貨淨空部位提高估值敏感度；休市期間的美股價格訊號不能冒充新的台灣現貨資金流。
- **風險定位：**YELLOW → YELLOW、TACTICAL → TACTICAL。能源廣度警戒保留，但換月污染與報價基準衝突不容許機械加碼警報。

## 訊號變化總覽（SIGNAL DELTA）

| 訊號 | 前值→目前 | 方向／Delta | 嚴重度 | 信心 | 跨資產確認 | 台灣關聯 |
|---|---|---|---|---|---|---|
| semiconductor_relative_weakness | SOX 日跌幅 −6.40%→−7.21% | ↘ 惡化；觀測跌幅再擴大 | 4/5 | 中 | Nasdaq、VIX、個股收盤；非同步 | 科技估值與外資部位 |
| energy_inflation | JKM 30.06→30.625 | ↘ 惡化候選；非新增觸發 | 3/5 | 中低 | 油氣同向與 EIA 庫存 | LNG、電力與進口成本 |
| rates_shock | 10Y 前收 5.149%→4.965% | 名目折現率影響 ↗ 改善 | 2/5 | 中 | 2Y、30Y 同向；實質利率缺 | 抵銷部分估值壓力 |

SOX 的前值是較早實際觀測，不是精確整點成交。能源表內 JKM 是每日代理觀測，並非本小時瞬間跳升；只有第一項展開為觸發卡。

### Signal #1｜晶片股弱勢延伸至交易尾段
**Severity 4/5｜Confidence 中｜TACTICAL｜Risk Light：YELLOW → YELLOW**

- **What changed：**官方 SOX 顯示日跌幅進一步擴大；自較早晚間警報的日跌幅約 −5.18% 後，弱勢未消退。這是序列觀測，不宣稱整段同步報酬。
- **Current / prior：**官方值 10,676.57，前收 11,505.56；vendor 10,682.4。兩者來源時計不同，保留差異，不平均成虛構即時價。
- **Rate / persistence：**相較前次官方觀測，日跌幅擴大約 0.81 個百分點；NVDA、AMD 已明示 16:00 EDT 收盤，支持壓力延續至交易終段。
- **Breadth / reaction：**GPU、CPU、記憶體與設備股均有弱勢證據；MU、LRCX 仍是盤中報價。Nasdaq 走弱與 VIX 上升相容風險重估，不等於所有資產同步下跌。
- **Consensus / revision：**價格無分析師共識值；未確認本輪新增公司財測下修。管理層前瞻指引與市場共識分開，盤中報價更新不是財報修訂。

#### 機制

**FACT：**名目美債殖利率（Yield）下降、晶片股仍弱。**INFERENCE：**市場對 AI 資本支出（CapEx）的融資、稀釋與回收期間要求更高補償，股票風險溢酬上升可能超過無風險利率下降的好處。

Reuters 報導 Meta 融資與新股類別疑慮，提供可辨識催化劑，但不證明供應商訂單（Order）已取消。個別公司 CDS 敘述缺乏當期可比較利差，不外推為全市場美元融資壓力。

#### 市場定價

**MARKET EXPECTATION：**股價反映對未來回收與估值（Valuation）的要求，並非直接量測訂單。最新可核公司指引仍強，因而主要分類是市場週期修正，而非基本面週期崩解。

證據獨立性來自 Nasdaq 原始指數、個股明示收盤、公司原始財報及 Reuters 機制報導。不同市場資料頁可能共享上游行情，不能把多個網頁當成等量獨立來源。

#### 反向證據

TSM ADR 跌幅由較早 −4.81% 收斂至 −4.54%；SPX 亦部分回升。這些反證否定「所有科技及大盤同步新增惡化」，但未推翻晶片族群跨子產業的持續重估。

TSMC 與 Lam 的營收（Revenue）、毛利率（Gross Margin）及前瞻指引（Guidance）仍支持基本面。當期信用利差（Credit Spread）、實質殖利率與美元 basis 缺口，限制系統性判斷信心。

#### 台灣傳導

**即時：**美國晶片風險溢酬重估可能傳至台灣科技估值及避險部位（Positioning）。**數週至數月：**須追蹤外資資金流（Flow）與公司訂單；**1–3季：**只有支出轉弱傳至收入與利潤，才升格獲利週期風險。

#### 下一確認條件

確認 SOX 與 TSM 的最終收盤及下一可交易時段相對強弱，檢查弱勢是否擴散至當期信用、外資現貨和公司指引。若晶片相對強弱修復、波動回落且訂單指引維持，則取消新增持續性惡化判讀。

---

## 為何重要（WHY IT MATTERS）

1. **資料／政策：**企業 AI 投資規模仍大，市場轉而重估資金來源、稀釋與回收時間；沒有新 Fed 決策可解釋本輪加速。
2. **利率／匯率／信用／流動性：**名目利率下降及日圓偏強相容避險，卻未解除科技風險溢酬壓力；當期信用及流動性（Liquidity）證據仍不足。
3. **產業／資金流：**晶片子產業共同下跌，提高集中持倉、風險預算及被動資金調整的敏感度；實際被迫平倉尚未核驗。
4. **獲利／估值：**即使每股盈餘（EPS）預期不變，較高風險溢酬也可能壓低倍數。不能把股價下跌當作等額獲利下修。
5. **台灣：**既有外資去風險、科技權重與海外價格發現交互作用；休市後反應取決於匯率、籌碼及基本面反證是否仍有效。

## 總經與政策細節（MACRO / POLICY DETAIL）

### 成長、物價與勞動

| Family | 可核驗最新觀測 | 比較／含義 | 本輪判斷 |
|---|---|---|---|
| Growth | GDPNow Q3 3.5%；8月實質 PCE +0.6%月增 | 模型估計非共識；消費較7月強 | 不支持全面衰退定論 |
| Inflation | 9月 CPI 月增0.6%、核心0.3%；8月核心 PCE 0.2% | 核心 PCE 前月0.1%，不可說降溫 | 通膨約束仍在 |
| Labor | 初領19.4萬；續領172.8萬 | 初領低於20萬共識；續領增加 | 分化，不是單向崩落 |
| Fed / Monetary Policy | 9月16日升息25bp至3.75–4.00% | 舊決策；當期機率不可得 | 不冒稱新增轉鷹或轉鴿 |

Kansas City Fed 10月製造業綜合指數由14降至11，未來指數由19升至22；積壓與出口新訂單（New Orders）為負。投入價格增速上升、成品價格增速放慢，顯示成本轉嫁壓力，而不是已證實整體衰退。

官方調查精確顯示16%企業完全無法轉嫁成本、35%只能轉嫁1–20%，53%認為客戶更在意價格。這是當日已發布資訊的重新核驗，不是本小時新衝擊，也不將投入成本全部歸因能源。

初領前週由19.9萬修訂為20萬；續領前週由171萬修訂為170.3萬，兩者統計週不同。9月新增就業2.9萬、失業率4.2%屬較慢資料，不能拿來替代當日融資或需求狀態。

### 利率、流動性、信用與財政

| Family | 可核驗觀測 | 限制 | 解讀 |
|---|---|---|---|
| Rates / Term Premium | 名目曲線三期限下移 | 當期實質殖利率（Real Yield）、期限溢酬（Term Premium）缺 | 名目折現率改善與股票風險溢酬惡化並存 |
| Liquidity / Market Plumbing | 10/21 SOFR 3.88%，持平 | H.4.1僅10/14週；當期repo/basis缺 | 未驗證新增資金市場斷裂 |
| Credit / Bank Credit | 10/21 HY 327bp、IG88bp；H.8信用存量增加 | 當日OAS不可得；SLOOS為Q2調查 | 不能用舊利差宣告當日安全 |
| Fiscal / Treasury Supply | 10/21 20Y拍賣BTC2.73、尾差0.9bp | 單一次級來源、非當期新供給衝擊 | 不足構成國債供給失序 |

H.8 10/7週銀行信用19,948.5十億美元，前週19,891.4；9月年化增速放慢至3.3%。7月 SLOOS 的工商貸款標準大致不變，信用卡偏緊，尚非全銀行信用一致急縮。

### 外匯、能源、貿易與亞洲

| Family | 主證據 | 反向證據／限制 | 台灣敏感度 |
|---|---|---|---|
| FX / Global Dollar | 美元偏弱、日圓偏強 | 美元basis缺；TWD與DXY未必同向 | 避險與進口成本 |
| Commodities / Inflation Chain | 四項能源代理對明示前收同向上升 | JKM換月、油價基準、庫存時效 | LNG／電力及實質需求 |
| Global Trade / Supply Chain | 台灣出口／外銷訂單與韓國晶片出口強 | 高基期、工作日與期別不同 | 外需仍是重要反證 |
| China / Asia / Taiwan Cycle | 中國GDP改善但投資弱；台灣領先指標仍升 | 日本出口低於共識、景氣資料落後 | 區域需求與估值放大器 |

台灣9月外銷訂單（Export Orders）114.21十億美元、年增62.4%；海關出口87.22十億、年增60.9%，兩者不可混用。韓國10月1–20日出口年增105.4%，工作日調整65.9%，半導體222.5%，不是全月結果。

中國第三季 GDP 年增4.5%、季增1.2%，前九月民間投資年減10.4%、房地產投資年減20.6%。日本9月出口年增16.7%，低於共識20.1%；前期增速本輪未完整取得；台灣8月領先指標月增0.51%，屬落後觀測。

### 能源五項強制更新

| Core input | 本輪值／單位 | 明示前值 | 1D或明示比較 | 資料狀態 |
|---|---|---|---|---|
| lng_jkm | 30.625 USD/MMBtu | 30.06 | +1.88% | 10/22每日期貨代理；非hourly assessment |
| gas_ttf | 90.30 EUR/MWh | 87.50 | +3.20% | delayed proxy；11:50:45時區未暴露 |
| oil_brent | 113.09 USD/bbl | 10/21結算108.82 | +3.92% | 前日結算至目前；不是provider live 1D |
| oil_wti | 99.22 USD/bbl | 10/21結算97.15 | +2.13% | 前日結算至目前；不是provider live 1D |
| eu_gas_storage | UNAVAILABLE | 10/20 proxy 74.6% full | UNAVAILABLE | AGSI未暴露本日值，不沿用為current |

| Core input | 5D／7D raw | 20D raw | 前20D高／低 | 時效與比較限制 |
|---|---|---|---|---|
| JKM | +15.43%／+15.43% | +16.09% | 30.060／25.435 | 10/16換月至12月，長區間非純價格變化 |
| TTF | +4.48%／+4.48% | +20.23% | 89.725／69.000 | 舊OHLC有不一致；信心降低 |
| Brent | +6.77%／+6.77% | +6.09% | 111.99／95.12 | clock15:54:05時區未知；連續合約待核 |
| WTI | +2.82%／+2.82% | +4.87% | 101.37／86.86 | clock15:44:40時區未知；到期換月干擾 |
| EU storage | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | 最新可比觀測仍10/20 |

#### 歷史比較與換月限制

5D與7D恰同以10/15為基準；20D為9/24至本輪代理比較。所有價格歷史百分位、z-score及當季五年價位區間均 UNAVAILABLE，未用不足樣本硬算。

JKM 的 raw 5D 超過候選門檻，但 ENGINE 說明10/16換月，不能當成同合約氣價衝擊。TTF及JKM單日未達5%中度門檻；Brent高於歷史高點僅為待核同合約的暫定突破，不獨立觸發。

油頁首分別顯示負變動，但基準未暴露；日表又與頁首不同步。因此不推算新結算、不稱日跌反轉，也不將日表113.46／99.42冒稱正式10/22結算。

#### 庫存與供給確認

EIA截至10/16週原油庫存（Inventory）減3.1百萬桶、汽油減3.0百萬桶，但餾分增1.7百萬桶。此庫存證據支持油氣廣度，卻是前日已發布的背景，不是新一小時供給意外。

EU proxy庫存844.6TWh相對五年平均1,017.5TWh低172.9TWh，約17%相對量差，**不是17個百分點**。容量調整後五年百分點差及七日正常路徑不可得，不能套用storage stress門檻。

挪威最新完整gas day仍10/21，約3,412GWh／日、較前日低4.59%，但接近五年平均3,424GWh。個別維護不可用容量占資產約17.8%、5.5%、24.7%，重疊事件不相加，也不當成實際新增流量損失。

#### 能源反證與判斷邊界

需求破壞、冬季備貨、餾分回補與挪威供給接近常態均列反證；當期LNG運價、M1/M2曲線不可得。能源訊號仍為邊際惡化候選，未證成新政策或融資衝擊。

## 跨資產確認（CROSS-ASSET CONFIRMATION）

| 資產 | 最新可核值 | 變化／比較 | 時間／限制 |
|---|---|---|---|
| UST 2Y／10Y／30Y | 4.640／4.965／5.284% | ↓18.3／18.4／15.3bp | 15:09／15:55／15:19；時區未暴露 |
| 曲線 | 2s10s 32.5bp；10s30s31.9bp | 僅非同步算術 | 非可成交同步曲線 |
| Real Yield | current UNAVAILABLE | 10/20 10Y實質2.77% | 舊值不可當本輪即時 |
| DXY／USDJPY／EURUSD | 101.62／156.80／1.1219 | ↓0.16%／↓0.83%／↓0.12% | 15:31／15:34／15:35，時區未知 |
| Gold GCZ6 | 4,046.82 | ↓0.33%，基準4,060.4 | 15:30；不與舊百分比混算 |
| Credit Spread／MOVE | current UNAVAILABLE | 10/21 HY327、IG88bp；MOVE95.94 | 舊資料不是當日融資解除證據 |

| 股票／波動 | 最新可核值 | 當日原始方向 | 對判斷的作用 |
|---|---|---|---|
| S&P 500 | 7,662.82 | ↓1.22% | 部分修復，反對全面惡化 |
| Nasdaq | 25,930.23 | ↓2.89% | 科技壓力延續；15:49時計 |
| SOX官方／vendor | 10,676.57／10,682.4 | ↓7.21%／↓7.15% | 官方date-only；vendor15:49時計 |
| VIX | 19.68 | ↑17.99% | 15:22時計；不是與SOX同步成交 |
| TSM ADR／台灣現貨 | 412.27 USD／2,385 TWD | ↓4.54%／↓1.45% | ADR15:55EDT；現貨較早收盤 |
| NVDA／AMD | 212.28／508.19 USD | ↓4.37%／↓8.06% | 明示16:00EDT收盤 |
| MU／LRCX | 849.92／229.89 USD | ↓6.98%／↓11.86% | 15:48／15:51EDT盤中，不稱收盤 |

SPX時計15:59:48，Nasdaq15:49:11、VIX15:22:01的來源時區未暴露。檢索發生在美股一般收盤時點之後，不自動使來源成為最終收盤值；SOX與TSM最終收盤仍待核。

| 亞洲市場 | 最近已核驗觀測 | 時段 | 限制 |
|---|---|---|---|
| TAIEX／OTC | 46,041.43 −1.81%／381.69 −3.47% | 10/22現貨 | 不是本輪新增交易 |
| Nikkei／TOPIX | 62,907.84 −2.65%／3,997.50 −1.14% | 10/22現貨 | 採已核相符資料，排除先前衝突值 |
| HSI／HSTECH | 22,934.68 −3.00%／3,793.93 −5.00% | 10/22現貨 | 不與夜期直接算同一報酬 |
| HSI夜期 | 23,133，+0.78% | 10/23 03:00 HKT，延遲15分 | 部分反向證據，另有期貨基準 |
| KOSPI | UNAVAILABLE | 當日可靠確認缺 | 不補造亞洲全面同跌 |

> 跨資產結果支持科技與半導體風險重新定價，不支持「殖利率上升造成此次加速」；同時缺少當期融資確認，不能把戰術性警報改稱系統性危機。

## 證據與反向證據（EVIDENCE VS COUNTER-EVIDENCE）

| 命題 | 支持證據 | 反向證據 | 判斷 |
|---|---|---|---|
| 晶片壓力獲持續性確認 | 官方SOX再弱、個股明示收盤仍跌 | TSM ADR修復 | 成立，觸發本報告 |
| 已變成全面市場失序 | Nasdaq、VIX相容風險趨避 | SPX修復、當期信用/basis缺 | 不成立或未證 |
| AI基本面已轉折 | 融資／稀釋疑慮、設備股跌 | TSM、Lam指引及產能承諾強 | 未證，市場週期先行 |
| 能源新增極端衝擊 | 四價同向、庫存支持 | JKM換月、油價基準未知 | 保留候選，不另開卡 |
| 台灣成本將立刻全面上調 | 台電燃料成本壓力 | 電價未核准調升 | 有條件中期風險 |

高影響判斷以原始指數及公司資料優先，新聞只解釋機制。Meta個股CDS、CoreWeave上週債券殖利率不能代表本輪廣泛信用惡化；相同供應商的多個行情頁也不是多個獨立機制。

## 台灣傳導（TAIWAN TRANSMISSION）

| 通道 | Horizon | 已有證據 | 待確認／失效條件 |
|---|---|---|---|
| 估值（Valuation） | 即時 | 美國晶片風險溢酬重估、台灣科技權重高 | 若相對強弱及ADR修復延續，壓力減弱 |
| 外需 | 數週至數月／1–3季 | 外銷訂單、出口與公司指引仍強 | 新訂單及指引下修才改寫獲利 |
| 金融條件 | 即時／數週 | 10/22外資現貨淨賣816.56億元 | 新交易日外流是否延續；不是夜間新流量 |
| 匯率 | 即時／數週 | USD/TWD 32.508，前32.488 | 微幅貶值放大進口成本，不能單看DXY |
| 日本／中國放大器 | 數週至數月／1–3季 | 日圓避險、中國投資弱、日本出口放慢 | 區域需求改善可抵銷 |
| LNG／電力成本 | 數週至數月／1–3季 | 台電條件式燃料成本估計 | 進口合約與電價政策決定傳導速度 |

TWSE上漲247家、下跌756家、持平74家，顯示10/22台灣現貨廣度偏弱；半導體類股跌1.91%、電子跌2.11%、金融漲0.62%。這是既有市場分化，不是本輪新成交。

TAIFEX外資多單8,126口、空單95,423口，淨空87,297口為未平倉部位存量，不當成當日交易流。台積電ADR與現貨時段、匯率及存託比例不同，本報告不製造未校準溢價率。

期交所已確認10/23日夜盤休市；台股停市相關資訊亦有CNA報導。精確下一可交易日期未於本輪完整確認，不自行假設週一復市，也不把營建工地停工或天候停市誤當晶圓廠生產中斷。

台電估計若天然氣高價持續至年底，全年燃料成本可能增加新台幣1,600億元；這是條件式估計。電價尚未核准調升、下次檢討在12月，短期先由公用事業及財政吸收，不能直接推定科技毛利率已下修。

## 產業／股票敏感度（INDUSTRY / EQUITY SENSITIVITY）

| 類別 | 市場敏感度 | 基本面反證 | 研究界線 |
|---|---|---|---|
| 晶圓代工／TSMC | 長久期估值、ADR價格發現 | Q4收入指引52.3–54.3十億美元 | 不把價格跌幅等同EPS下修 |
| GPU／CPU | AI資本回收與集中部位 | 產能擴張承諾仍在 | 個股收盤證明價格，不證明訂單取消 |
| 記憶體 | 科技因子及供需預期 | DDR5現貨61.10、單次+0.38% | NAND最新值不可得 |
| 半導體設備／Lam | CapEx回收疑慮、週期倍數 | 季營收增22%，12月指引仍高 | 強財報與股價下跌可並存 |
| 封測／供應鏈 | 美國需求與擴產承諾 | NVIDIA供應鏈（Supply Chain）安排 | 預付款不等於當期收入 |
| 台塑化／航運／電力密集產業 | 燃料、匯率與轉嫁能力 | 合約、避險及政策可吸收 | 無公司證據不下單股受益受害結論 |

TSMC第三季庫存天數82天，較前季87天下降；毛利率66.4%，並維持強勁管理層展望。Lam採GAAP毛利率52.3%對前季51.7%，不與非GAAP數值混用；預期收入不是已實現訂單。

本報告提供風險敏感度，而非個人化買賣指令或價格保證。若要採取部位調整，應另以實際持倉、資金期限及可承受損失設定風險預算。

## 市場週期 vs 基本面週期

**市場週期（Market Cycle）：**價格、波動與產業相對強弱已支持新的持續性警報。即使營收創高，較低估值倍數仍可造成明顯跌幅；財報強不保證股價立即止跌。

**基本面週期（Fundamental Cycle）：**WSTS／SIA的8月三個月平均銷售159.7十億美元、月增8%，屬落後需求反證；TSMC與Lam的前瞻指引仍強。尚未取得兩個以上獨立供應鏈環節同步下修。

> 市場訊號可以領先基本面，卻不能取代基本面證據。只有訂單、庫存、毛利率與資本支出展望開始同向轉弱，才有理由把此次估值調整升格為獲利週期轉折。

## 分類與風險燈號變化（CLASSIFICATION & RISK LIGHT DELTA）

| 判定項目 | Prior → Current | 理由 | 限制 |
|---|---|---|---|
| Trigger | 未新增重大Delta → TRIGGERED | 半導體弱勢延伸至尾段、增加收盤廣度 | 不把各時計當精確整點 |
| Risk Light | YELLOW → YELLOW | 部門壓力有確認，系統性傳導不足 | ADR/SPX修復、當期信用缺 |
| Classification | TACTICAL → TACTICAL | 估值與融資敘事重估 | 基本面核心反證未失效 |
| Regime Shift | 未確認 → 未確認 | 不足兩families的新持續共振 | 能源舊廣度不自動當第二新衝擊 |

升燈需要至少兩項獨立市場指標同步惡化，但這只是必要、不是充分條件。本輪非同步Nasdaq與VIX支持戰術性判斷，未滿足更強的同步系統性確認；不能因資料缺失把燈號推高或推低。

## 情境矩陣（SCENARIO MATRIX）

| 情境 | 確認條件 | 市場含義 | 台灣傳導 | 研究反應 |
|---|---|---|---|---|
| 基準：估值修正 | 晶片仍弱、指引維持、信用未廣泛惡化 | 波動高於基本面變化 | 科技倍數與籌碼承壓 | 保持YELLOW／TACTICAL |
| 惡化：跨資產擴散 | 同時點信用、美元融資及外流轉差 | 風險預算收縮擴大 | 匯率與融資放大估值壓力 | 重新評估升燈，不預設 |
| 基本面轉折 | 多家公司訂單／指引下修、庫存升高 | 從倍數轉為EPS風險 | 出口與產能利用率受壓 | 評估TREND_FORMATION |
| 改善：壓力吸收 | 相對強弱修復、VIX回落、指引持穩 | 風險溢酬回吐 | ADR及外資籌碼改善 | 撤銷新增惡化論點 |

情境未配置數值機率，因當期信用、融資與完整收盤資料不足。能源上行若獲通膨定價確認，才加入政策約束放大的情境權重，而非僅憑原油價格機械調整。

## 下一確認條件（NEXT CONFIRMATION）

1. **價格終局：**取得SOX、TSM、Nasdaq與VIX最終收盤及來源時區，檢查晶片相對弱勢是否保留，而非只看全天跌幅。
2. **跨資產：**補當期實質殖利率、breakeven、Fed期貨機率、HY／IG利差、MOVE與美元basis，辨識估值、成長與資金壓力。
3. **台灣籌碼：**核實下一可交易時段，再查外資現貨、期貨未平倉、USD/TWD與廣度，避免休市空窗製造虛構流量。
4. **基本面：**檢查TSMC／Lam與主要AI客戶指引、新訂單、庫存及毛利率是否轉差；產能預付款與已認列收入分開。
5. **能源：**核驗同合約序列與正式結算、補AGSI當期庫存及季節路徑；排除JKM換月後再評估5D候選門檻。

> 失效條件是晶片相對強弱、波動與籌碼修復，同時公司需求反證維持有效。若只有名目殖利率下跌而科技仍弱，不能單憑債券反彈解除警報。

## SOURCE AUDIT

- **SPX**：本輪20:03:38UTC讀取；報價15:59:48，時區NOT_EXPOSED，非確認收盤。https://www.investing.com/indices/us-spx-500

- **Nasdaq**：本輪20:03:38UTC讀取；報價15:49:11，時區NOT_EXPOSED，非確認收盤。https://www.investing.com/indices/nasdaq-composite

- **VIX**：本輪20:03:38UTC讀取；報價15:22:01，時區NOT_EXPOSED，非同步報價。https://www.investing.com/indices/volatility-s-p-500


實際資料檢索窗口：2026-10-23 04:03:38–04:06:01（Asia/Taipei）。檢索時間不等於觀測、發布或結算時間；本報告coverage起點為03:00，但月／週資料保留原期別。完整研究涵蓋21個canonical signals、每訊號18欄及12 families；資料缺口明示，不以「COMPLETE」代表所有市場輸入皆可取得。

- **核心時間稽核：**Nasdaq官方SOX僅10/22日期；NVDA、AMD為10/22 16:00 EDT明示收盤。TSM 15:55、MU15:48、LRCX15:51 EDT仍為盤中。其他vendor時計若無時區，標NOT_EXPOSED；不同來源快照不平均、不冒稱同步。

- **可得性：**當期信用／MOVE、實質利率、basis、Fed機率、NAND、AGSI數值與KOSPI可靠當日確認為UNAVAILABLE或UNKNOWN。SEMI維持歷史403 hold，原始回應NOT_RETRIEVED；未繞過限制。KC直接頁初讀技術錯誤後由官方索引合法連結讀回，內容已核。

- **獨立性：**Nasdaq及公司原始資料優先；Reuters為獨立新聞機制佐證，Investing能源四價可能共享上游，不能算四個獨立確認。CNA轉載也不重複計為獨立來源。市場來源中的自動生成因果敘述與實際利率衝突者已排除。

### 總經與市場來源

- **auction**：Source vintage in observations; retrieval is not observation timestamp。https://www.newsquawk.com/headlines/us-treasury-sells-usd-13bln-of-20-year-bonds-tails-09bps

- **claims**：Source vintage in observations; retrieval is not observation timestamp。https://www.dol.gov/ui/data.pdf

- **consensus**：Source vintage in observations; retrieval is not observation timestamp。https://www.investing.com/economic-calendar/initial-jobless-claims-294

- **cpi**：Source vintage in observations; retrieval is not observation timestamp。https://www.bls.gov/news.release/cpi.nr0.htm

- **dxy**：Source vintage in observations; retrieval is not observation timestamp。https://www.investing.com/indices/usdollar

- **eurusd**：Source vintage in observations; retrieval is not observation timestamp。https://www.investing.com/currencies/eur-usd

- **fed**：Source vintage in observations; retrieval is not observation timestamp。https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm

- **fx_reuters**：Source vintage in observations; retrieval is not observation timestamp。https://www.investing.com/news/economy-news/dip-in-the-dollar-takes-a-breather-with-fed-in-focus-4964546

- **gdpnow**：Source vintage in observations; retrieval is not observation timestamp。https://www.atlantafed.org/research-and-data/data/gdpnow

- **gold**：Source vintage in observations; retrieval is not observation timestamp。https://www.investing.com/commodities/gold

- **h15**：Source vintage in observations; retrieval is not observation timestamp。https://www.federalreserve.gov/releases/h15/

- **h41**：Source vintage in observations; retrieval is not observation timestamp。https://www.federalreserve.gov/releases/h41/current/

- **h8**：Source vintage in observations; retrieval is not observation timestamp。https://www.federalreserve.gov/releases/h8/current/default.htm

- **hy**：Source vintage in observations; retrieval is not observation timestamp。https://fred.stlouisfed.org/series/BAMLH0A0HYM2

- **ig**：Source vintage in observations; retrieval is not observation timestamp。https://fred.stlouisfed.org/series/BAMLC0A0CM

- **jobs**：Source vintage in observations; retrieval is not observation timestamp。https://www.bls.gov/news.release/empsit.nr0.htm

- **kcfed**：Source vintage in observations; retrieval is not observation timestamp。https://www.kansascityfed.org/surveys/manufacturing-survey/tenth-district-manufacturing-activity-increased-steadily-in-october-2026/

- **move**：Source vintage in observations; retrieval is not observation timestamp。https://www.investing.com/indices/ice-bofaml-move-historical-data

- **pce**：Source vintage in observations; retrieval is not observation timestamp。https://www.bea.gov/news/2026/personal-income-and-outlays-August-2026

- **sloos**：Source vintage in observations; retrieval is not observation timestamp。https://www.federalreserve.gov/data/sloos/sloos-202607.htm

- **sofr**：Source vintage in observations; retrieval is not observation timestamp。https://markets.newyorkfed.org/api/rates/secured/sofr/last/5.json

- **usdjpy**：Source vintage in observations; retrieval is not observation timestamp。https://www.investing.com/currencies/usd-jpy

- **ust10**：Source vintage in observations; retrieval is not observation timestamp。https://www.investing.com/rates-bonds/u.s.-10-year-bond-yield

- **ust2**：Source vintage in observations; retrieval is not observation timestamp。https://www.investing.com/rates-bonds/u.s.-2-year-bond-yield

- **ust30**：Source vintage in observations; retrieval is not observation timestamp。https://www.investing.com/rates-bonds/u.s.-30-year-bond-yield

### 台灣、亞洲與公司來源

- **sox_official**：Oct22 date only, clock NOT_EXPOSED。https://indexes.nasdaq.com/Index/Breakdown/SOX

- **sox_vendor**：Oct22 15:49:37; timezone NOT_EXPOSED; not final close。https://www.investing.com/indices/phlx-semiconductor

- **adr**：2026-10-22T15:55:00-04:00 Market open, not final close。https://stockanalysis.com/stocks/tsm/

- **cbc**：Oct22 close。https://www.cbc.gov.tw/tw/lp-645-1.html

- **taifex**：Oct22 OI; Oct23 closure。https://www.taifex.com.tw/cht/3/futContractsDate

- **dram**：2026-10-22T18:10:00+08:00 daily assessment。https://www.trendforce.com/price/dram/dram_spot

- **nand**：2026-10-12T14:40:00+08:00 stale。https://www.trendforce.com/price/flash/flash_spot

- **hk**：Cash Oct22 16:08; night Oct23 03:00 HKT delayed 15 minutes。https://stock360.hkej.com/

- **tsm**：2026-10-15 quarterly release。https://www.sec.gov/Archives/edgar/data/1046179/000104617926000726/a3q26presentatione.htm

- **nvda**：2026-10-21 announcement。https://nvidianews.nvidia.com/news/nvidia-and-supply-chain-partners-expand-capacity-to-accelerate-ai-infrastructure-buildout/

- **orders**：2026-10-20 09:43 BST September data。https://uk.marketscreener.com/news/taiwan-september-export-orders-hit-record-value-on-solid-ai-demand-ce785cdbd08cf32d

- **korea**：2026-10-20 20:37 EDT October1–20 data。https://www.marketscreener.com/news/south-korea-october-1-20-exports-surge-105-on-record-chip-sales-ce785cd8df89f52d

- **japan**：2026-10-21 release September data。https://www.investing.com/news/economy-news/japan-september-exports-rise-167-yy-slower-than-forecast-4961386

- **china**：2026-10-19 11:09 NBS quarterly release。https://english.www.gov.cn/archive/statistics/202610/19/content_WS6ad589d8c6d00ca5f9a0dc71.html

- **ndc**：2026-09-29 19:44 August data。https://focustaiwan.tw/business/202609290019

- **wsts**：August2026 latest listed。https://www.wsts.org/

- **wto**：2026-10-08 forecast。https://www.wto.org/english/news_e/news26_e/stat_08oct26_510_e.htm

- **customs**：2026-10-08 September data。https://www.mof.gov.tw/singlehtml/384fb3077bb349ea973e7fc6f13b6974?cntId=856cf6c5ea4646208d3b8345b3bb46e2

- **twse_daily**：2026-10-22 official report header。https://www.twse.com.tw/exchangeReport/MI_INDEX?date=%25s&response=html&type=ALLBUT0999

- **sia_wsts**：2026-10-05 08:00 August3monthmovingaverage。https://www.semiconductors.org/year-to-date-global-semiconductor-sales-top-1-trillion-through-august/

- **otc**：2026-10-22 close。https://toalpha.tw/market

- **tsm_construction**：2026-10-21 03:42 BST。https://uk.marketscreener.com/news/tsmc-says-four-construction-workers-killed-at-taiwan-site-halting-work-ce785cd8df8af524

- **flow**：2026-10-22 18:15 Taipei。https://www.cna.com.tw/news/afe/202610220289.aspx

- **japan_quotes**：Oct22 15:45 Nikkei/15:30 TOPIX; clock local inferred。https://finance.stockweather.co.jp/contents/market.aspx

- **taipower**：2026-10-22 18:48 Taipei。https://focustaiwan.tw/business/202610220015

- **semi**：歷史403 hold；本輪未重試；原始回應NOT_RETRIEVED。https://www.semi.org/en/news-resources/press

- **company_quotes**：NVDA/AMD Oct22 16:00EDT explicit close; MU15:48/LRCX15:51 intraday。https://stockanalysis.com/stocks/nvda/

- **lam**：Oct21 results。https://investor.lamresearch.com/2026-10-21-Lam-Research-Corporation-Reports-Financial-Results-for-the-Quarter-Ended-September-27,-2026

- **ai_financing**：Oct22 14:36 provider timezone unexposed。https://www.investing.com/news/economy-news/steep-bill-for-ai-buildout-punishes-meta-other-tech-favorites-4967187

- **flow_detail**：Oct22 15:06:29；SEARCH_SNIPPET_ONLY，非全文讀回。https://news.pchome.com.tw/finance/cna/20261022/index-17926527891270818003.html

- **AMD**：原研究10/22 16:00EDT明示收盤。https://stockanalysis.com/stocks/amd/

- **MU**：原研究10/22 15:48EDT盤中快照；稍後僅驗證URL可讀，不將更新頁面當原值再次確認。https://stockanalysis.com/stocks/mu/

- **LRCX**：原研究10/22 15:51EDT盤中快照。https://stockanalysis.com/stocks/lrcx/

### 能源與供給來源

- **jkm**：本輪重新讀取；觀測日期見正文。https://www.investing.com/commodities/lng-japan-korea-marker-platts-futures-historical-data

- **ttf**：本輪重新讀取；觀測日期見正文。https://www.investing.com/commodities/dutch-ttf-gas-c1-futures-historical-data

- **brent**：本輪重新讀取；觀測日期見正文。https://www.investing.com/commodities/brent-oil-historical-data

- **wti**：本輪重新讀取；觀測日期見正文。https://www.investing.com/commodities/crude-oil-historical-data

- **storage**：本輪重新讀取；觀測日期見正文。https://storagecurve.com/natural-gas/europe/storage/

- **agsi**：本輪重新讀取；觀測日期見正文。https://agsi.gie.eu/

- **eia**：本輪重新讀取；觀測日期見正文。https://ir.eia.gov/wpsr/overview.pdf

- **norway**：本輪重新讀取；觀測日期見正文。https://voltstack.energy/norway-gas-flows

- **engine**：本輪重新讀取；觀測日期見正文。https://www.engine.online/news/lng-bunker-snapshot-jkm-contract-roll-lifts-singapores-lng-bunker-price-82e9

- **kpler**：本輪重新讀取；觀測日期見正文。https://www.kpler.com/blog/asian-lng-prices-to-rise-amid-simmering-geopolitical-tensions-elevated-ttf

- **settlement**：本輪重新讀取；觀測日期見正文。https://au.investing.com/news/commodities-news/oil-rises-on-middle-east-supply-worries-4702921

- **oil_today**：本輪重新讀取；觀測日期見正文。https://au.investing.com/news/commodities-news/oil-prices-rise-as-meast-tensions-fuel-fears-of-supply-disruptions-4706166

- **wti_roll**：SEARCH_EXCERPT，僅搜尋摘錄，非全文讀回。https://www.spa.gov.sa/en/N2706425

## 結論（BOTTOM LINE）

> 此次報告新增確認的是晶片股壓力的持續性，而非宣告AI需求已崩解。維持YELLOW與TACTICAL，讓價格警報保有敏感度，同時保留強基本面、ADR修復與信用資料缺口對升級判斷的約束。

正式MD僅驗證原始內容與結構；未指定實際renderer基準，不宣稱CSS顏色、間距或像素呈現已驗證。
<<<REPORT_END>>>
