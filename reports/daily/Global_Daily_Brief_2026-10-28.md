<<<REPORT_BEGIN>>>
---
research_status: COMPLETE
generated_at_taipei: 2026-10-28T07:38:10+08:00
coverage_start_taipei: 2026-10-27T07:30:00+08:00
coverage_end_taipei: 2026-10-28T07:30:00+08:00
us_market_status: AFTER_HOURS
run_id: GDB-20261028-0730
report_type: GLOBAL_DAILY_BRIEF
report_name: Global Daily Brief
title: Global Daily Brief｜Oracle 擴大多晶片雲端，Meta 融資與 ASM 展望凸顯 AI 定價分歧
format_version: 2
risk_light: YELLOW
slug: ai-cloud-funding-divergence
---
# Global Daily Brief｜Oracle 擴大多晶片雲端，Meta 融資與 ASM 展望凸顯 AI 定價分歧

## 執行摘要（EXECUTIVE SUMMARY）

> AI 投資沒有同步轉弱，但「誰取得訂單、誰支付資金、誰承擔稀釋」開始分開定價。Oracle 擴大多晶片平台、Meta 引進供應商股權資金與 ASM 上修展望，是本輪三個不同的基本面事件。

- **需求與競爭並行：** Oracle 擴充 NVIDIA 合作，同時納入 Google TPU 與 Cerebras；不是 GPU 被全面取代，而是訓練與推論架構競爭加深。
- **融資不等於獲利：** Meta 的合作資金提高建置可行性，但新增股權供給與資本回報疑慮，使需求端和供應商股價可能反向。
- **設備證據較具體：** ASM 上修明年營收門檻提供製程投資佐證；仍須看出貨認列、現金轉換與客戶集中度，不能外推所有設備商。
- **盤後另有考驗：** Seagate 財報與展望強於公開預期，股價卻下跌；這是預期與估值門檻的提醒，不是已證實 AI 訂單崩落。

研究區間：台北時間 2026-10-27 07:30 至 2026-10-28 07:30。美股狀態：盤後（AFTER_HOURS）；現貨收盤與盤後報價分開列示。

## 今日三大市場訊號（TODAY TOP 3 MARKET SIGNALS）

| 市場訊號 | 已核實事實 | 邊際解讀 | 不能推導的結論 |
|---|---|---|---|
| 算力供應走向多架構 | Oracle 同時擴充 GPU、TPU 與推論平台 | 對供應鏈需求 ↗ 改善；晶片間競爭升高 | 所有晶片、封裝與 ODM 同比例受益 |
| 資金取得與股東回報分離 | Meta 引入供應商投資，股價弱於科技市場 | 對風險資產 → 混合；建置資金改善被稀釋疑慮抵銷 | 募資額全數已收現，或等同新增採購 |
| 財報門檻高於指引比較 | ASM 上修中期展望；STX 盤後逆財報走弱 | 基本面支撐 ↗，短線定價仍脆弱 | 單一盤後跌幅證實產業景氣反轉 |

### 跨資產只是事件定價背景

| 觀察 | 最新可核驗值 | 比較／時點 | 對事件歸因的限制 |
|---|---|---|---|
| Nasdaq／S&P 500 | 26,477.81／7,722.67 | 10/27 現貨 ↑1.18%／↑0.60% | 廣泛市場漲勢須與公司事件拆開 |
| SOX／VIX | 11,482.5／17.52 | SOX 收盤 ↑3.60%；VIX ↓4.73% | 半導體強於大盤，不是全面避險 |
| 美國 2Y／10Y 殖利率（Yield） | 4.739%／4.984% | 指示報價；相對前值 +0.2／−0.2bp | 平台時間未揭露時區，不作同步事件研究 |
| 10Y 實質殖利率（Real Yield） | 2.66% | FRED 最新觀察 10/26，與 10/23 持平 | 落後資料，不能冒稱當日變動 |
| 美元指數／美元兌新台幣 | 102.35／32.452 | DXY 頁面 +0.03%；台幣 10/27 收盤 | DXY 與頁尾報價不混用；台幣前列為 10/22 |
| MOVE | 未取得可靠當期原始值 | 已搜尋，第三方數值未納入結論 | 不以缺值判斷資金壓力不存在 |

資料為不同交易時段的觀察，不是同步截面。Reuters 收盤敘事將部分晶片反彈歸於先前 Anthropic IPO 消息；該公告不在本輪事件窗，僅作市場背景，不重複排名。[市場與匯率來源](#source-audit)

## 市場影響力前三大事件（TOP 3 MARKET IMPACT EVENTS）

| 排名／事件 | 分數與信心 | 新增事實 | 價格驗證 | 台灣主要環節 |
|---|---|---|---|---|
| 1｜Oracle 多晶片雲端擴張 | 86／中高（來源有全文限制） | 擴大 NVIDIA，加入 TPU／Cerebras 等架構 | ORCL 收盤 ↑3.55% | 先進製程、封裝、伺服器與網通 |
| 2｜Meta 供應商股權資金 | 83／高（承諾非全部交割） | NVIDIA 30 億、AMD 10 億美元承諾 | META 收盤 ↓1.64% | GPU／ASIC 供應鏈、ODM、電力 |
| 3｜ASM 上修明年營收門檻 | 79／高（公司展望） | 2027 年 >57 億歐元，原 >46 億 | 公告後主要現貨市場已收盤 | 先進節點設備與晶圓廠投資 |

分數為研究排序，不是預測報酬率或機率。依規模、影響廣度、基本面、估值傳導、持續性與台灣外溢綜合評估；同一 Oracle 大會的相關公告合併，不分拆灌榜。

### 事件 #1｜Oracle 把雲端算力擴張與多架構競爭綁在一起

- **事實（FACT）：** 10/27 宣布 NVIDIA Vera Rubin 合作擴至多 GW，並引入 Vera CPU；Google TPU 與 Cerebras 亦加入 OCI 路線。
- **時間與預期差：** 多家夥伴同日公告（精確時間依來源）；新增差異是規模、架構與渠道擴張，不是首次宣布 Oracle 使用 Rubin。TPU 服務面向 2027 年。
- **公司目標而非已實現收入：** 公告尚不足以計算增量訂單（Order）、營收（Revenue）、毛利率（Gross Margin）或每股盈餘（EPS）。
- **影響分數 86：** 跨越雲端、晶片、伺服器與網路，廣度與台灣關聯最高；金額與利用率不足，限制確定性。

#### 市場解讀

1. 多種晶片進入同一雲端渠道，降低客戶採用新架構的摩擦。
2. 算力選擇增加，可能擴大推論工作負載，也提高單位成本與效能競爭。
3. 訂單轉化取決於實際部署、客戶使用及機房供電，不能把合作清單相加為新增需求。
4. 對估值（Valuation）的支持來自未來現金流可見度，而非公告數量。

Intel 的多年度 Xeon 合作與 OpenAI 的企業應用整合，也歸入同一 Oracle 生態系事件；產品整合改善採用渠道，但尚無足夠數字拆算各供應商增量收入。

#### 市場定價

ORCL 現貨收盤 130.53 美元；同日 NVIDIA、Alphabet 也上漲，但落後 SOX。這與市場接受雲端擴張相容，卻無法隔離 Oracle 大會、既有 AI 反彈及其他公司消息各自貢獻。

市場定價（Market Pricing）已反映部分正面預期；Google TPU 商業化可能增進雲端渠道價值，同時對 GPU 定價形成競爭。不能只用供應商股價同漲推論所有合作均具正淨現值。

#### 反向證據

Rubin 已在先前合作路線內，部分增量是擴充而非全新平台；多架構也可能是替代既有支出。未取得具約束力的採購金額、付款節奏或客戶利用率，不能直接上修特定台廠獲利。

#### 台灣外溢

即時影響以估值與題材輪動為主；數週至數月看伺服器 ODM、PCB／CCL、散熱／電源、網通／光通訊設計導入。1–3 季則看先進製程、先進封裝（Advanced Packaging）與 HBM 的實際配置及產能認列。

多晶片不等於全由同一家晶圓代工或封裝廠承接；Cerebras 架構亦不可直接套用 GPU 的 CoWoS／HBM 含量。資料中心（Data Center）建置延誤、出口許可與匯率，均可能抵銷帳面需求。

#### 下一催化劑

確認條件是 2027 服務正式可用、部署規模與可核驗客戶負載；失效條件是重大延期、需求由替代而非擴張構成，或利用率與現金回收低於資本支出（CapEx）承諾。官方合作公告與 Reuters 的交叉確認見來源 O1–O4。

---

### 事件 #2｜Meta 引入 NVIDIA／AMD 股權資金，供應商與客戶的風險不同

- **事實：** 10/27 NVIDIA 承諾投資 30 億美元，AMD 承諾 10 億美元；與模型、基礎設施合作一併公布。
- **新增差異：** 本窗確認兩家供應商承諾；定價文件載普通股由 225 億增至 250 億美元，供應商 40 億包含其中。文件內文日期為 10/26、精確時間不明，僅作融資背景，不冒稱本窗新增定價，也不能重算為晶片收入。
- **基本面機制：** 股權資金改善建置資金可得性，卻可能增加每股稀釋；供應商的客戶需求與投資風險同步加深。
- **影響分數 83：** 大型需求端、兩家晶片商與廣泛供應鏈連動；因供應商資金投入不等於獨立最終需求，低於 Oracle 的渠道廣度。

#### 市場解讀

另有 125 億美元、6.50% 優先股與最快 2027 年首季啟動的 600 億美元 ATM 額度；媒體合計的 975 億不是當日收現。普通股初始出售不取得現金，遠期最晚於 2027 年 11 月 19 日交割，優先股預計 10/29 交割仍有條件。

資金籌措方式改變，不能被直接標成需求上修。對供應商，合作有助部署可見度；對 Meta 股東，還需比較新增股數、資金成本、模型收入與自由現金流回收期。

**市場預期（MARKET EXPECTATION）：** 投資人可能要求 AI 支出轉成可持續收入，而非只有容量擴張。**推論（INFERENCE）：** 客戶融資與供應商銷售綁得更緊，會提高需求品質與集中度檢驗的重要性。

#### 市場定價

META 收盤 620.19 美元，與上漲的 Nasdaq／SOX 分歧；NVIDIA 與 AMD 則分別上漲 0.90% 與 5.45%。這提供客戶端稀釋／資本回報與供應端需求題材分離的證據，但不是每段漲跌的單一因果識別。

#### 反向證據

AMD 初期 Helios 系統安裝測試不等於全面部署；先前披露的長期 GW 規模不可當成本日新增訂單。合作承諾仍需交割與執行，新增資金若只支應既有計畫，對總需求的增量會較小。

#### 台灣外溢

數週至數月關注 ODM 排程、GPU／ASIC 比重、PCB／CCL 與散熱電源規格；1–3 季追蹤晶圓、封裝與 HBM 拉貨是否轉成收入。網通光通訊受網路拓樸影響，DRAM／NAND 不能與 HBM 等量外推。

新台幣波動會改變台廠美元收入換算與進口設備成本，並非單向利多。沒有台灣供應商具體訂單、份額或毛利證據，不提供個股受益保證。

#### 下一催化劑

確認投資交割、融資工具條件、實際部署及模型商業化；若稀釋超出回報、建置延後、自由現金流持續惡化，則「資金到位帶動可獲利需求」的論點失效。原始投資公告與 SiliconANGLE 見 M1–M3。

---

### 事件 #3｜ASM 的展望上修，比設備股同日漲幅更有基本面含量

- **事實：** 10/27 歐洲收盤後公布第三季營收 11.594 億歐元，第四季指引 12.3 億歐元、上下 5%。
- **與預期差：** 第四季市場比較約 11.8 億歐元；2027 年目標高於 57 億，對照先前高於 46 億與 LSEG 約 54.1 億。
- **比較限制：** 公司部分展望為固定匯率口徑，共識口徑未完全一致；兩個「高於」門檻不是精確點估值，不能據此聲稱精確百分比上修；7 月已預期下半年 1.4nm 貢獻，本季是進度兌現。
- **影響分數 79：** 具公司數字、需求與中期展望支撐，台灣先進製程關聯高；仍是單一設備供應商且待新交易時段驗證。

#### 市場解讀

先進製程投資提高關鍵製程設備需求，對原子層沉積等技術的收入能見度有利。設備收入認列仍有交付、驗收與客戶進度差，不能由 ASM 展望等比例上修 ASML 或台灣整體半導體獲利。

#### 市場定價

ASML 美國 ADR 當日上漲 2.92%，但不是 ASM 公告後同標的的完整價格反應。ASM 歐洲現貨已收盤，正式事件反應需下一交易日驗證；不把公告前上漲當財報利多的證明。

#### 反向證據

自由現金流較前季下降、庫存（Inventory）增加，提醒出貨成長與現金轉換未必同步；同時營運資金天數下降，不能只挑庫存上升就判斷積壓。高集中度需求與交付時間仍可能造成季間波動。

#### 台灣外溢

1–3 季主要連結為先進節點晶圓廠設備投資及供應鏈（Supply Chain）驗收；短期先反映設備與製程類股估值。CoWoS、HBM、伺服器及散熱是共同 AI 需求的間接關聯，不是 ASM 設備營收的直接等比例受益者。

#### 下一催化劑

台北 10/28 22:00 法說進一步確認訂單、產能及前瞻指引（Guidance）；之後看交付、毛利與現金轉換。若客戶延後投資、目標下修或現金轉換持續落後，則成長可見度論點減弱。公司報告與 Reuters／Dow Jones 見 A1–A3。

## 重要個股事件掃描

| 股票 | 本輪應關注原因 | 價格／時段 | 判讀限制 |
|---|---|---|---|
| NVDA／AMD／GOOGL／INTC | Oracle 或 Meta 根事件的直接參與者 | 10/27 現貨反應 | 已合併根事件，不再另列排行榜 |
| TSM | CoWoS 報價傳聞與 Top 3 高關聯 | 收盤 436.87，↑2.95%；19:00 EDT 436.90 | 傳聞未獲公司確認，不能直接上修毛利 |
| AAPL | M6 產品與創作工具發布，60 分戰術事件 | 收盤 347.10，↑0.93% | 換機及 PC 供應鏈有關聯，但尚無新增銷量／獲利指引 |
| MSFT／AMZN | 未來 24–72 小時財報一級催化劑 | 收盤 531.33／253.10 | 財報未發布，不提前補造雲端結果 |
| DELL | AI 環境資安／韌性產品更新，60 分 | 收盤 ↑7.47% | 產品收入未量化，漲幅混合伺服器 beta |
| SMCI | Argentum 融資洽談與伺服器外溢 | 收盤 ↑7.34% | 洽談非交割，相對強勢不等於已獲訂單 |

其餘固定名單已在內部逐股預檢；無重大新事件者不硬列正文。INTC 與 ARM 亦已檢查，不能用固定 14 檔子清單取代完整研究範圍。

## 其他重要市場事件

| 事件 | 分數／證據 | 真正新增資訊 | 投資意義與反證 |
|---|---|---|---|
| Seagate 財報與展望超預期、盤後走弱 | 75／中高 | 季營收 42.33 億美元、調整 EPS 7.68；下季 48 億／9.20 | 19:15 EDT 629.00，↓5.82%；價格／組合不等於容量出貨同增 |
| Teradyne 財報與季間節奏 | 72／中高 | Q3 營收與 EPS 超過原指引上緣，Q4 EPS 中點高於公開預期 | 19:00 EDT 305.92，↓5.49%；季減不等於低於共識 |
| TSMC CoWoS 報價消息 | 68／中低 | 媒體稱可能漲價 10–20% | 尚未取得官方確認；多篇轉載同一根來源，不算獨立交叉確認 |
| NXP 展望與盤後修正 | 65／中高 | Q4 營收中點約與預期相當 | 19:23 EDT 235.00，↓7.30%；不能把標題「弱指引」當全面未達標 |
| SMCI／Argentum 融資洽談 | 64／中低 | Reuters 稱約 50 億美元 AI 晶片融資洽談 | 尚未取得官方確認；洽談不是成交或已認列收入 |

Seagate 的財報比較支持儲存需求與獲利能力，但盤後反應顯示市場可能採更高門檻；具體賣壓成因仍未被隔離。HDD 與 NAND 亦有替代、互補及不同供給約束，不能將單一公司展望等同所有記憶體報價上升。

## 美國科技股策略（US TECH STRATEGY）

> 優先驗證「收入與現金流轉化」，而不是追逐所有帶有 AI 標籤的股價反彈。

- **供應鏈選擇：** 關注已量化出貨或展望改善、同時現金轉換可驗證的公司；僅有合作名單者保留執行折扣。
- **客戶端風險：** 供應商投資客戶不一定是不良交易，但須另看稀釋、付款能力與資本回報，避免重複計入同一筆需求。
- **事件風險：** 財報前不以盤後薄量價格代表翌日完整定價；雲端成長、資本支出及自由現金流應聯合判讀。

風險燈號為 **YELLOW**：這是本輪獨立的審慎評估，不聲稱相對不可得前輪燈號升降。基本面有支持，但融資、估值與財報門檻仍有張力；不構成跨資產全面危機判斷。

## 台灣 AI／半導體／記憶體／伺服器影響

| 傳導環節 | 主要機制 | 時間 | 確認證據 | 反向條件 |
|---|---|---|---|---|
| 晶圓代工／先進製程 | GPU、TPU、ASIC 設計需求與設備投資 | 1–3 季 | 晶圓投入、製程組合、客戶展望 | 多架構替代、客戶延後 |
| CoWoS／先進封裝 | 算力密度與晶片配置提高複雜度 | 數週至數月 | 真實報價、交期、產能認列 | 傳聞不實、架構改變封裝含量 |
| HBM／DRAM／NAND | 工作負載、記憶體容量與儲存層分工 | 1–3 季 | 公司拉貨、合約價格、庫存 | HDD 與 NAND 不同循環、需求替代 |
| ODM／PCB／CCL | 系統設計與機櫃部署 | 數週至數月 | 客戶訂單、出貨及良率 | 交付／驗收遞延、份額競爭 |
| 散熱／電源／機房 | 功率密度與供電限制 | 數月至 1–3 季 | 實際建置、規格與認證 | 電網、許可與場地瓶頸 |
| 網通／光通訊 | 多機櫃互連與網路拓樸 | 數週至數月 | 網路配置、採購及單機含量 | 拓樸變動、成本壓力 |
| 匯率／估值／出口限制 | 美元收入換算、折現率與可交付市場 | 即時至數月 | 台幣、利率、許可與公司揭露 | 新台幣升值或政策收緊抵銷營收 |

上述是條件式產業傳導，不是台灣個股訂單認證。Oracle 的多架構選擇、Meta 的資金與部署、ASM 的先進製程展望，各自提供不同證據，不能加總成重複的需求增量。

## 下一階段催化劑（NEXT CATALYSTS）

| 催化劑 | 台北時間／觀察窗 | 必看項目 | 確認／失效 |
|---|---|---|---|
| Teradyne 法說 | 10/28 20:30 | 季間節奏與測試需求 | 高於預期不等於所有環節同步加速 |
| ASM 法說與歐洲交易 | 10/28，法說 22:00 | 交付、需求與現金轉換 | 目標可落地才支持中期估值 |
| FOMC | 10/29 凌晨美國公告時段 | 利率與金融條件對長久期股票影響 | 預期不等於決策，公布後再重估 |
| Microsoft／Alphabet 財報 | 美國 10/28，台北 10/29 盤後對應時段 | 雲端成長、AI 收入、CapEx 與自由現金流 | 成長不足以覆蓋支出則削弱回報論點 |
| Intel 財報 | 美國 10/29 收盤後，台北 10/30 | 產品需求、代工與現金流 | 以正式財報確認，不把合作公告當已實現銷售 |
| Amazon 財報 | 美國 10/29，台北 10/30 對應時段 | AWS 需求與資金回收 | 客戶採用與收入實現須共同確認 |
| Oracle／Meta 部署 | 後續數週至 2027 | 可用性、交割、利用率、供應商實際訂單 | 延期或替代性需求使增量假設失效 |

## SOURCE AUDIT

- **O1｜NVIDIA／Oracle**：[原始連結](https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-and-Oracle-Expand-NVIDIA-Vera-Rubin-to-Multi-Gigawatt-Scale-and-Bring-NVIDIA-Vera-CPU-to-Oracle-Cloud-Infrastructure/default.aspx)。10/27；本輪原始路徑 HTTP403，保留 hold；以可見索引摘要及夥伴公告交叉核對，不宣稱完整讀取。
- **O2｜Google Cloud TPU**：[原始連結](https://cloud.google.com/blog/products/infrastructure/bringing-google-tpus-to-oracle-cloud-infrastructure)。10/27；原始頁 HTTP200 但僅 Site Unavailable，不是全文；索引摘要可得，2027 部署屬前瞻。
- **O3｜Reuters／Oracle**：[原始連結](https://www.investing.com/news/stock-market-news/oracle-expands-chip-supply-deal-with-nvidia-adds-google-and-cerebras-offerings-4976437)。10/27；搜尋摘要可得、原始路徑 HTTP403，保留 hold。
- **O4｜Oracle／OpenAI**：[原始連結](https://www.oracle.com/asean/news/announcement/ai-world-oracle-reinvents-enterprise-computing-for-the-ai-era-with-openai-2026-10-27/)。10/27 官方；另見 OpenAI 與 Benzinga。
- **O5｜OpenAI**：[原始連結](https://openai.com/index/oracle-apps-in-chatgpt/)。
- **O6｜Benzinga**：[原始連結](https://www.benzinga.com/trading-ideas/movers/26/10/62628674/oracle-stock-jumps-whats-going-on)。
- **O7｜Intel**：[原始連結](https://www.intel.com/content/www/us/en/newsroom/news/corporate/intel-oracle-collaborate-on-enterprise-and-agentic-ai.html)。
- **M1｜NVIDIA／Meta**：[原始連結](https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-and-Meta-to-Expand-Collaboration-on-Muse-and-Muse-Family-of-Models-Amid-Robust-Growth/default.aspx)。10/27 官方；承諾與交割分開。
- **M2｜AMD／Meta**：[原始連結](https://ir.amd.com/news-events/press-releases/detail/1302/amd-and-meta-advance-strategic-partnership-to-power-metas-superintelligence-infrastructure)。10/27 09:20 EDT 官方。
- **M3｜SiliconANGLE**：[原始連結](https://siliconangle.com/2026/10/27/nvidia-amd-to-buy-4b-in-meta-shares-as-part-of-expanded-chip-partnerships/)。10/27 獨立科技財經確認。
- **M4｜Meta pricing**：[原始連結](https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Announces-Pricing-of-Offering-of-Depositary-Shares-Representing-Series-A-Mandatory-Convertible-Preferred-Stock-and-Offering-of-Class-A-Common-Stock-in-Connection-with-Forward-Sale-Agreements/default.aspx)。官方全文可得；內文 dateline 為 10/26、發布精確時刻不明，只作背景融資條款，不列本窗新增定價。
- **D1｜Dell official**：[原始連結](https://investors.delltechnologies.com/news-events/press-releases/detail/1660/dell-technologies-strengthens-cybersecurity-and-resilience-across-ai-environments-identity-and-infrastructure)。10/27 資安產品公告。
- **A1｜ASM issuer release**：[原始連結](https://www.globenewswire.com/news-release/2026/10/27/3389491/0/en/asm-reports-third-quarter-2026-results.html)。10/27 17:00 UTC；原始財報與公司展望。
- **A2｜Reuters／ASM**：[原始連結](https://www.aol.com/articles/asm-international-expects-q4-sales-175027000.html)。10/27；市場預期比較。
- **A3｜Dow Jones／ASM**：[原始連結](https://www.marketscreener.com/news/chip-equipment-supplier-asm-international-lifts-guidance-again-amid-ai-spending-frenzy-update-ce785cddde89f127)。輔助交叉來源。
- **E-STX｜STX**：[原始連結](https://investors.seagate.com/news/news-details/2026/Seagate-Technology-Reports-Fiscal-First-Quarter-2027-Financial-Results/default.aspx)。STX 原始 URL 既有 403 hold 保留；本輪數字以可讀原始紀錄與獨立報導比對。
- **E-STXsecondary｜STXsecondary**：[原始連結](https://finance.yahoo.com/markets/stocks/articles/seagate-nasdaq-stx-surprises-q3-202625694.html)。
- **E-TER｜TER**：[原始連結](https://investors.teradyne.com/news-events/press-releases/detail/455/teradyne-reports-third-quarter-2026-results)。
- **E-TERsecondary｜TERsecondary**：[原始連結](https://www.streetinsider.com/Earnings/Teradyne%2B%28TER%29%2BTops%2BQ3%2BEPS%2Bby%2B21c%2C%2BBeats%2Bon%2BRevenue%3B%2BOffers%2BQ4%2BEPS%2BGuidance/27241953.html)。
- **E-NXPI｜NXPI**：[原始連結](https://www.globenewswire.com/news-release/2026/10/27/3389631/0/en/nxp-semiconductors-reports-third-quarter-2026-results.html)。
- **E-NXPIsecondary｜NXPIsecondary**：[原始連結](https://ca.investing.com/news/earnings/nxp-semiconductors-falls-on-weak-fourth-quarter-guidance-4907021)。
- **E-TSM｜TSM**：[原始連結](https://www.trendforce.com/news/2026/10/27/news-tsmc-reportedly-eyes-20-cowos-price-hike-skips-equipment-price-renegotiations-amid-ai-demand-surge/)。同 Commercial Times 根來源，非獨立確認。
- **E-TSMsecondary｜TSMsecondary**：[原始連結](https://www.tomshardware.com/tech-industry/semiconductors/tsmc-reportedly-weighs-20-percent-cowos-price-increase-as-nvidia-blackwell-and-rubin-chips-put-pressure-on-packaging-capacity-equipment-lead-times-stretch-to-eight-months)。同 Commercial Times 根來源，非獨立確認。
- **E-SMCIsecondary｜SMCIsecondary**：[原始連結](https://www.investing.com/news/stock-market-news/exclusiveneocloud-firm-argentum-ai-in-talks-for-5-billion-ai-chip-financing-sources-say-4976170)。
- **P1｜Apple**：[原始連結](https://www.apple.com/newsroom/2026/10/apple-unveils-new-imac-with-m6/)。
- **P2｜Reuters／Apple**：[原始連結](https://ca.marketscreener.com/news/apple-launches-m6-macbook-pro-and-imac-pitches-faster-on-device-ai-ce785cdddd81f420)。
- **C1｜Microsoft IR**：[原始連結](https://www.microsoft.com/en-us/investor/default?o=200)。
- **C3｜Intel earnings date**：[原始連結](https://www.intc.com/news-events/press-releases/detail/1782/intel-to-report-third-quarter-2026-financial-results)。10/29 美國收盤後。
- **C2｜Amazon**：[原始連結](https://www.aboutamazon.com/news/company-news/amazon-earnings-q3-2026-report)。官方 10/29 17:00 EDT；Alphabet 日期本輪僅取得二手確認。
- **Q1｜StockAnalysis 個股**：[原始連結](https://stockanalysis.com/stocks/orcl/)。公司報價依各 ticker 頁面，現貨 16:00 EDT；盤後明列觀察時間。
- **Q2｜市場指數**：[原始連結](https://www.investing.com/indices/major-indices)。本輪重新檢查；各資產觀察時點與延遲限制見跨資產表。
- **Q3｜SOX**：[原始連結](https://www.investing.com/indices/phlx-semiconductor)。本輪重新檢查；各資產觀察時點與延遲限制見跨資產表。
- **Q4｜美國公債**：[原始連結](https://www.investing.com/rates-bonds/usa-government-bonds)。本輪重新檢查；各資產觀察時點與延遲限制見跨資產表。
- **Q5｜DXY**：[原始連結](https://www.investing.com/indices/usdollar)。本輪重新檢查；各資產觀察時點與延遲限制見跨資產表。
- **Q6｜FRED DFII10**：[原始連結](https://fred.stlouisfed.org/series/DFII10)。本輪重新檢查；各資產觀察時點與延遲限制見跨資產表。
- **Q7｜CBC USD/TWD**：[原始連結](https://www.cbc.gov.tw/tw/lp-645-1.html)。本輪重新檢查；各資產觀察時點與延遲限制見跨資產表。
- **Q8｜Reuters 收盤**：[原始連結](https://www.investing.com/news/economy-news/us-stock-futures-muted-as-oil-holds-near-april-highs-ahead-of-fed-decision-4974650)。本輪重新檢查；各資產觀察時點與延遲限制見跨資產表。

**查核限制：** 報價來源可能為延遲或指示資料；現貨、盤後、歐洲收盤後及落後官方序列分開使用。TSMC 報價傳聞只有共同媒體根源；MOVE 未取得可靠當期原始值。先前受限的來源未因其他頁面成功而視為解除，不繞過存取限制。

**方法：** 事實、公司／市場預期與研究推論分離；主要事件至少原始公告加獨立媒體確認。價格反應僅作相容性檢查，不以同日相關性識別單一因果。研究內部保留全名單預檢、未入榜原因與來源限制；本文只展開具實際市場價值的事件。

## 免責聲明（DISCLAIMER）

本報告為一般市場研究，不是個人化投資建議或交易指令。公司展望、供應鏈傳聞與研究推論均可能失效；投資決策須自行評估風險、流動性及持有期間。
<<<REPORT_END>>>
