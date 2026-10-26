<<<REPORT_BEGIN>>>
---
research_status: COMPLETE
report_type: MACRO_TAIWAN_EARLY_WARNING
run_id: MTW-20261023-0800-stock-bond-volatility
generated_at_taipei: 2026-10-23T08:17:35.647362+08:00
coverage_start_taipei: 2026-10-23T07:00:00+08:00
coverage_end_taipei: 2026-10-23T08:08:21+08:00
report_name: Global Macro Early Warning
title: Global Macro Early Warning｜股債波動同步升溫，科技估值壓力獲跨資產確認
format_version: 2
trigger_status: TRIGGERED
risk_light: YELLOW
classification: TACTICAL
slug: stock-bond-volatility
---
# Global Macro Early Warning｜股債波動同步升溫，科技估值壓力獲跨資產確認

## 核心警報摘要（EXECUTIVE TAKE）

> 新可得的10月22日MOVE，補上美債選擇權波動確認，與官方VIX形成股債雙市場同日升溫。新增的是跨資產證據，不是第二個交易日，也不是債券價格下跌；名目利率下降仍提供估值支撐。

- **觸發理由：**MOVE由95.94升至106.84，日增11.36%；官方VIX為19.03，日增14.09%。兩種風險市場的波動同步上升，足以新增戰術性確認。
- **機制辨識：**名目殖利率（Yield）下降降低折現率；利率波動上升則可能提高避險成本與風險預算壓力。兩條通道方向相反，不能合稱「利率上升打擊科技股」。
- **反向證據：**美國股票跌勢集中科技，並非普遍拋售；TSMC與Lam的已公布營收（Revenue）及前瞻指引（Guidance）仍強，當期信用利差（Credit Spread）與美元融資壓力尚未確認惡化。
- **亞洲新增：**日本9月核心CPI升至2.1%，但符合共識，且缺發布後日圓／日債確認。列政策觀察，不另開新警報。
- **台灣與風險定位：**優先觀察科技估值及外資風險預算；10月23日台股、期貨休市，不製造新增現貨資金流（Flow）。維持YELLOW → YELLOW、TACTICAL → TACTICAL。

## 訊號變化總覽（SIGNAL DELTA）

| 訊號 | 前值→目前 | 原始變化／風險方向 | 嚴重度 | 信心 | 跨資產確認 | 台灣關聯 |
|---|---|---|---|---|---|---|
| rates_shock | MOVE 95.94→106.84 | ↑11.36%；波動影響↘ | 3/5 | 中 | 同日VIX↑14.09% | 避險成本、科技估值 |
| 名目利率分項 | 10Y 5.146%→4.955% | ↓19.1bp；折現率影響↗ | 抵銷項 | 中 | 2Y、30Y亦下降 | 長久期估值支撐 |
| semiconductor_relative_weakness | 五檔盤後價較前次觀察皆低 | 約↓0.39–0.76%；影響↘ | 4/5 | 中 | 支持主卡；非獨立五市場 | 科技權重與海外價格發現 |
| japan_cycle | 核心CPI 1.7%→2.1% | ↑0.4pp；預期內觀察 | 3/5觀察 | 實際高／傳導低 | 發布後JPY／JGB未確認 | 區域折現率與日圓部位 |
| energy_inflation | 四項價格高於明示前日值 | 成本影響↘；無新觸發 | 3/5 | 中低 | 換月與同源限制 | LNG、電力、進口成本 |

↑／↓只表示原始數值方向；↗／↘表示對風險資產的改善／惡化。表中MOVE與VIX使用同一觀測日，不宣稱同一秒報價；只有rates_shock展開為本輪觸發卡。

### Signal #1｜美債波動補上股債雙市場確認
**狀態：TRIGGERED｜嚴重度：3/5｜信心：中｜分類：TACTICAL｜風險燈號：YELLOW → YELLOW**

- **變化／目前值／前值（What changed／Current／Prior）：**首次取得10月22日MOVE 106.84，前日95.94；Cboe官方VIX 19.03，前日16.68。新增債券波動證據，並非重報科技股全天跌幅。
- **變化幅度（Rate of change）：**MOVE ↑10.90點、↑11.36%；VIX ↑2.35點、↑14.09%。同日10Y殖利率↓19.1bp，故波動惡化與名目折現率改善須分開評價。
- **持續性／廣度（Persistence／Breadth）：**目前只有一個交易日的股債波動共振；重讀同日值不延長持續性。盤後代工、GPU、CPU、記憶體及設備股偏弱，僅作產業廣度佐證。
- **共識／修訂（Consensus／Revision）：**未取得可核驗的MOVE共識或政策機率，標為UNAVAILABLE。VIX由先前vendor 19.04微調至官方19.03，不是新增拋售；行情更新也不是經濟數據修訂。
- **市場反應／證據（Market reaction／Evidence）：**Nasdaq收跌2.60%、SOX收跌6.72%，國債價格反而上漲。MOVE日期列與官方VIX屬不同風險市場，來源及時間限制見下列機制與稽核。

#### 機制

**事實（FACT）：**國債殖利率下降、股債隱含波動同日上升。**推論（INFERENCE）：**利率路徑不確定性可能抬升避險成本、風險值（VaR）與部位（Positioning）調整需求，即使無風險折現率下降，科技估值仍可承壓。

這是rates_shock的「波動」分項，不是新的上升殖利率衝擊。隱含波動上升也不直接證明被迫平倉、保證金追繳或美元短缺；這些機制須有融資價格與成交深度的另外證據。

#### 市場定價

**市場預期（MARKET EXPECTATION）：**MOVE與VIX反映選擇權隱含風險定價，不等同已實現獲利下修。當期Fed期貨機率及10月22日實質殖利率（Real Yield）未取得，不從名目債券反彈推算降息機率。

[日期化MOVE](https://www.investing.com/indices/ice-bofaml-move-historical-data)與[Cboe官方VIX](https://www.cboe.com/tradable-products/vix/)確認同日方向。前者精確數值仍只有單一供應商，後者官方原始頁可核；因此信心維持中，不宣稱完全同步。

#### 反向證據

MOVE仍低於10月5日113.60，並非20日新高；市場尚未提供第二個交易日的延續確認。美國多數股票上漲的新聞證據，以及台灣金融股相對抗跌，均反對「所有資產全面拋售」。

10月22日SOFR、信用利差與美元basis仍未取得，不能用10月21日數值保證當日安全，也不能用缺值推定危機。TSMC、Lam指引與台韓出口仍構成基本面反證。

#### 台灣傳導

**即時：**科技估值與外資風險預算最敏感；名目折現率下降可部分抵銷。**數週至數月：**觀察匯率、融資與外銷訂單（Export Orders）；**1–3季：**只有訂單（Order）、收入與毛利率（Gross Margin）轉弱，才升格為獲利週期風險。

日本通膨與中國投資是區域放大器，不是本卡已確認的因果來源。台灣10月23日休市，海外價格可更新，但當日現貨資金流不能填零或假定續賣；能源成本另列條件式中期通道。

#### 下一確認條件

下一交易日須看到MOVE／VIX延續，並核驗10月22日後的SOFR、信用利差及國債買賣價差。若波動回落、融資與信用穩定，且科技股廣度修復，則本輪「波動擴散」命題失效。

## 為何重要（WHY IT MATTERS）

1. **資料／政策：**新資訊是債券波動讀數，而不是新的美國政策決議。日本CPI雖加速，但符合共識；不應把所有價格變動歸因於新增央行緊縮。
2. **利率／匯率／信用／流動性：**殖利率下降提供折現率改善，波動升高則可能提高避險成本；當期信用與融資缺口，仍限制系統性危機判讀。
3. **產業／資金流：**科技與半導體弱勢跨子產業，可能使集中持倉與風險預算更敏感；五檔股票同跌不是五個獨立市場，也未證明被迫去槓桿。
4. **獲利／估值：**較高股票風險溢酬可壓低估值（Valuation），即使每股盈餘（EPS）預期不變。股價跌幅不能直接換算成營收或訂單損失。
5. **台灣：**海外科技價格先傳估值與避險，再由實際外資流、匯率和訂單決定後續強度；休市空窗延後本地驗證，並不等於基本面已惡化。

## 總經與政策細節（MACRO / POLICY DETAIL）

### 成長、物價、勞動與Fed

| 訊號家族 | 最新可核觀測 | 比較／預期差 | 本輪解讀 |
|---|---|---|---|
| Growth | GDPNow第三季3.5%，10/20更新；8月實質PCE月增0.6% | 7月實質PCE +0.1%；GDPNow前估未重驗 | 消費韌性，不是新實現GDP |
| Inflation | 9月CPI月增0.6%、核心0.3%；8月核心PCE 0.2% | CPI前月0.4%；核心PCE前月0.1% | 通膨約束仍在，未新增美國發布 |
| Labor | 初領19.4萬；續領172.8萬 | 初領共識20萬；續領前值修訂至170.3萬 | 初領較強、續領增加，訊號分化 |
| Fed / Monetary Policy | 9/16升息25bp至3.75–4.00% | 當期期貨機率UNAVAILABLE | 舊決議，不冒稱本輪轉向 |

GDPNow是模型估計，不是分析師共識；8月實質可支配所得月增0%，低於7月0.3%，故消費加快不能直接外推。KC製造業本輪原始頁讀取失敗，不把先前報告數值冒充最新核驗。

初領統計週至10月17日，前週由19.9萬修訂為20萬；續領統計週至10月10日，前週由171萬修訂為170.3萬。不同統計週不可混為同一時間點的勞動市場反應。

9月新增就業2.9萬、失業率4.2%；7月與8月就業合計下修6萬。這些較慢資料顯示就業動能偏弱，卻不能替代當日融資條件，也不抵銷低初領所提供的反向訊息。

### 利率、流動性、信用與財政

| 訊號家族 | 可核驗內容 | 原期別／限制 | 解讀 |
|---|---|---|---|
| Rates / Term Premium | MOVE↑11.36%；名目曲線三期限下移 | 10/22；當期實質利率、期限溢酬（Term Premium）缺 | 波動風險與折現率分拆 |
| Liquidity / Market Plumbing | 準備金週均減595.33億美元；TGA增686.29億 | H.4.1截至10/21週；非當日流量 | 流動性（Liquidity）收縮背景，未證融資失靈 |
| Credit / Bank Credit | HY 327bp、IG 88bp；銀行信用存量增加 | OAS僅10/21；H.8僅10/7週 | 當期信用擴散仍待核 |
| Fiscal / Treasury Supply | 20Y拍賣BTC 2.73，尾差0.9bp | 10/21；單一次級來源 | 不足認定新增供給失序 |

H.4.1週均準備金為2.963兆美元、TGA為9,520.02億美元；主要信用借款由113.12億降至89.35億美元。週均值不能與週三單日值混用，也不能把準備金下降直接稱為融資危機。

10月21日SOFR為3.88%，與前日持平；HY利差由333降至327bp，IG由87升至88bp。兩者方向分歧且落後本次波動日，既不是當日安全證明，也不是信用全面惡化確認。

H.8的10月7日週銀行信用為19,948.5十億美元，前週19,891.4；9月年化增速3.3%，低於8月5.0%。第二季SLOOS工商貸款標準大致不變、信用卡偏緊，不能改寫成10月全銀行同步急縮。

### 外匯、貿易與中日台週期

| 訊號家族 | 可核驗主證據 | 反向證據／限制 | 台灣含義 |
|---|---|---|---|
| FX / Global Dollar | DXY 101.59、USDJPY 156.55 | 頁首已換日；basis缺 | 不以美元指數替代TWD |
| Commodities / Inflation Chain | 四項能源日表高於明示前日值 | 換月、結算衝突、庫存缺口 | 進口成本仍需追蹤 |
| Global Trade / Supply Chain | 台韓出口強；WTO貨物預測上修 | 名目量價、工作日及服務分化 | 外需是基本面反證 |
| China / Asia / Taiwan Cycle | 中國GDP回升；日本CPI新加速；台灣領先指標升 | 中國投資弱；日本預期內；台灣資料較慢 | 區域放大器尚未共振 |

台灣9月外銷訂單114.21十億美元、年增62.4%，高於58.7%共識；海關出口87.22十億、年增60.9%。訂單、出口及部會10月預估屬不同概念，不合併成已實現營收。

韓國10月1–20日出口年增105.4%，工作日調整後65.9%，半導體增222.5%。這是月初初值，不是全月；高基期差、工作日及記憶體價格均會影響名目增幅。

WTO將2026年貨物貿易量預測由1.9%上修至3.9%，但服務貿易預測由4.8%下修至3.3%。預測修訂不是本輪實現貿易量，不能用AI貨物需求代表全球所有終端同步擴張。

中國第三季GDP年增4.5%，較第二季4.3%改善；前九月民間投資年減10.4%、房地產投資年減20.6%。台灣8月領先指標月增0.51%、連13月上升，屬較慢的實體循環反證。

### 日本CPI新發布，但不是預期外衝擊

| CPI口徑 | 8月→9月年增 | 9月季調月增 | 預期／判讀 |
|---|---|---|---|
| 總體 | 1.9%→2.1% | 0.4% | 年增提高0.2pp |
| 剔除生鮮核心 | 1.7%→2.1% | 0.5% | Reuters共識2.1%，無驚喜 |
| 剔除生鮮與能源 | 1.9%→2.4% | 0.5% | 非能源單獨推升 |

[日本官方9月CPI](https://www.stat.go.jp/data/cpi/sokuhou/tsuki/pdf/zenkoku.pdf)於10月23日08:30 JST、即台北07:30發布。核心值符合[Reuters預先調查](https://www.marketscreener.com/news/japan-core-inflation-likely-exceeded-boj-target-for-first-time-since-december-ce785dd3d080f02d)；實際數據與共識分開，不將預期內加速寫成鷹派意外。

能源年減0.6%，較前月年減0.7%改善，對總體年增貢獻變化僅0.01pp。剔能源仍加速值得追蹤，但住宿、水費、行政價格與基期效應須分辨，單月尚不足推定新通膨制度。

#### 發布後市場反應仍待核

**推論（INFERENCE）：**較高核心通膨可能支持BOJ維持緊縮傾向，惟尚無新決議。08:13 JST日圓報價在發布前，其他頁面時區未暴露、日債前收欄已重設，故發布後JPY／JGB反應仍UNCONFIRMED。

### 能源五項強制更新

| 核心輸入 | 本輪值／單位 | 明示前日值 | 1D比較 | 觀測／可得性 |
|---|---|---|---|---|
| lng_jkm | 30.625 USD/MMBtu | 30.06 | ↑1.88% | 10/22每日代理；assessment時間未知 |
| gas_ttf | 90.30 EUR/MWh | 87.50 | ↑3.20% | 10/22每日代理；非ICE拼接 |
| oil_brent | 113.17 USD/bbl | 108.82 | ↑4.00% | 10/22日期列；非確認官方結算 |
| oil_wti | 99.01 USD/bbl | 97.15 | ↑1.91% | 10/22日期列；非確認官方結算 |
| eu_gas_storage | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | AGSI當期數值未呈現 |

| 核心輸入 | 5D／7D raw | 20D raw | 前20D高／低 | 季節區間／百分位／z-score |
|---|---|---|---|---|
| JKM | +15.43%／+15.43% | +16.09% | 30.060／25.435 | UNAVAILABLE |
| TTF | +4.48%／+4.48% | +20.23% | 89.725／69.000 | UNAVAILABLE |
| Brent | +6.84%／+6.84% | +6.16% | 111.99／95.12 | UNAVAILABLE |
| WTI | +2.60%／+2.60% | +4.65% | 101.37／86.86 | UNAVAILABLE |
| EU storage | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | 當期五年容量百分點差UNAVAILABLE |

5D與7D均以10月15日為基準；20D以9月24日為基準，前20D高低排除10月22日。連續合約比較不是純同合約報酬；季節五年價位區間、百分位與z-score未取得，不以短樣本硬算。

#### 報價時間與換月辨識

JKM頁首18:09:13、TTF 11:50:45、Brent Closed 17:59:55、WTI 19:20:46均未暴露時區；上述表格選日期列，不把頁首時計解讀為台北即時行情。

Brent日期列113.17與頁首112.92不一致，WTI日期列99.01與頁首99.18不一致；官方10月22日結算未獨立取得。WTI頁首負變動的基準未知，不能因此宣告能源壓力反轉。

JKM raw 5D升15.43%跨越10月16日轉12月合約，已知換月污染使其不能機械觸發。TTF部分歷史OHLC內部不一致，價格區間只作暫定比較，不提高信心。

Brent高於前20D高點、單日升逾3%，仍屬既有連續合約突破候選；其1D／5D未達5%／10%重大門檻。JKM與TTF單日亦未達8%，本輪不新增能源觸發。

#### 庫存、供給與需求反證

EIA截至10月16日週原油庫存減3.1百萬桶、汽油減3.0百萬桶，餾分增1.7百萬桶。原油去庫支持價格廣度，餾分回補提供反證；這是既有發布，不是新一小時庫存意外。

EU最新可比代理仍為10月20日：庫存74.6%、844.6TWh，低於五年均量1,017.5TWh約17%。這是**相對庫存量差，不是17個容量百分點**；不可取代當期容量調整季節缺口。

代理頁所列「週」減0.3TWh實際涵蓋10月18日至20日，不能當七日消耗路徑。當期AGSI、正常季節七日路徑與容量百分點差均UNAVAILABLE，因此不套用storage stress門檻。

挪威最新完整gas day仍10月21日，流量3,412GWh／日，接近五年平均3,424GWh。近期事件feed顯示零但非完整事件清單，不能推論維護結束、供給恢復或不存在活躍中斷。

日本即期LNG需求偏弱、韓國煤核替代與冬季採購，可能分別抑制或支撐價格；資料期別仍須保留。當期LNG運費及M1／M2曲線UNAVAILABLE，不補造運價衝擊或逆價差確認。

## 跨資產確認（CROSS-ASSET CONFIRMATION）

| 市場 | 最新可核值 | 原始變化 | 時間／限制 | 對判斷的作用 |
|---|---|---|---|---|
| MOVE | 106.84 | ↑11.36% | 10/22日期列；精確值單一vendor | 新增債券波動確認 |
| VIX | 19.03 | ↑14.09% | Cboe as-of 10/22；時計時區未知 | 官方股票波動確認 |
| UST 2Y／10Y／30Y | 4.661／4.955／5.286% | ↓16.2／19.1／15.1bp | 10/22對10/21日期列 | 名目折現率改善，不是債券拋售 |
| 2s10s／10s30s | 29.4／33.1bp | 日期列算術差 | 非同步可成交曲線 | 不能據此推算期限溢酬 |
| 10Y實質／通膨補償代理 | 2.76%／2.37% | 前值2.77%／2.35% | H.15僅10/21 | 不當成10/22即時確認 |
| HY／IG OAS | 327／88bp | ↓6／↑1bp | 僅10/21 | 同日信用擴散未證 |
| SOFR／美元basis | 3.88%／UNAVAILABLE | SOFR持平 | SOFR僅10/21 | 融資危機未確認 |

| 外匯／黃金 | 最新可核值 | 來源顯示變化 | 基準限制 |
|---|---|---|---|
| DXY | 101.59 | ↓0.02% | 新交易時段基準101.61；非10/22全日報酬 |
| USDJPY | 156.55 | ↓0.14% | 新交易時段基準156.77；不證明CPI後反應 |
| EURUSD | 1.1221 | ↑0.04% | 新交易時段基準1.1216；時區未暴露 |
| Gold GCZ6 | 4,043.37 USD/oz | ↓0.42% | 頁首基準4,060.40，非確認前日結算 |

黃金與國債的時計、完整交易日基準不同，不能確認新的同步日線背離。外匯頁首已換日，小幅美元走弱不等於美元融資緩解；DXY亦不能替代台幣實際進口成本。

| 股票 | 10/22正規盤 | 日變動 | 盤後最新觀察 | 盤後相對收盤／時計 |
|---|---|---|---|---|
| S&P 500 | 7,663.39 | ↓1.21% | 不適用 | vendor Closed 15:59:59，時區未暴露 |
| Nasdaq | 26,008.86 | ↓2.60% | 不適用 | vendor Closed 15:59:59，時區未暴露 |
| SOX | 官方10,731.98／vendor 10,732.00 | vendor ↓6.72% | 不適用 | 官方僅日期；0%重設欄排除 |
| TSM ADR | 412.35 USD | ↓4.52% | 409.55 | ↓0.68%；19:38 EDT |
| NVDA | 212.21 USD | ↓4.40% | 212.16 | ↓0.02%；19:44 EDT |
| AMD | 507.93 USD | ↓8.10% | 505.70 | ↓0.44%；19:55 EDT |
| MU | 856.49 USD | ↓6.26% | 843.00 | ↓1.58%；19:44 EDT |
| LRCX | 230.15 USD | ↓11.76% | 227.50 | ↓1.15%；19:51 EDT |

五檔個股正規盤皆明示16:00 EDT收盤；盤後價分布19:38–19:55 EDT，非同步、深度未核，亦不保證為20:00終盤。相較07:00輪的原始觀察皆較低，但不能組成新的SOX報酬。

| 亞洲現貨 | 最近觀測 | 期別 | 主要限制 |
|---|---|---|---|
| TAIEX | 46,041.43，↓1.81% | 10/22收盤 | 10/23休市，無新增現貨流量 |
| Nikkei／TOPIX | 62,907.84／3,997.50 | 10/22收盤，↓2.65%／↓1.14% | 日本CPI發布前的市場 |
| HSI／HSTECH | 22,934.68／3,793.93 | 10/22收盤，↓3.00%／↓5.00% | 不代表10/23新現貨反應 |
| KOSPI | 5,533.77，↓3.52% | 10/22收盤 | ETNews 16:01報導；非10/23新增反應 |

> 跨資產確認成立於「股債兩類隱含波動同日升高」，不成立於「所有資產同步下跌」或「融資市場已斷裂」。科技壓力與國債避險上漲可以同時存在。

## 證據與反向證據（EVIDENCE VS COUNTER-EVIDENCE）

| 命題 | 支持證據 | 反向證據／缺口 | 判斷 |
|---|---|---|---|
| 波動壓力跨出股票市場 | 新日期MOVE與官方VIX同日上升 | 單日、MOVE單一精確vendor | 成立，新增戰術性觸發 |
| 已全面失去市場流動性 | 科技重挫、波動升高 | 多數美股上漲；當期融資價格缺 | 未證實 |
| 科技基本面已轉折 | 股價及盤後廣度弱 | TSM／Lam指引與台韓外需仍強 | 未證實 |
| 日本CPI帶來新鷹派意外 | 三種CPI口徑加速 | 核心符合共識；JPY／JGB未確認 | 不成立為獨立觸發 |
| 能源構成第二個新衝擊 | 油氣對明示前日同向上升 | 換月、結算差異、時點不新 | 保留背景，不另開卡 |

[AP當日市場報導](https://apnews.com/article/1970e79d013cbddcae89c53b4b98f384)的本輪搜尋摘錄指出，多數美股其實上漲。此證據支持跌勢集中科技的反論，但未取得完整廣度原表，不進一步發布精確上漲家數。

[Reuters跨資產報導](https://www.marketscreener.com/news/stocks-drop-as-meta-fans-ai-worries-treasuries-gain-ce785cdede89f223)支持國債上漲與科技下跌的機制；本輪全文開啟失敗，僅使用搜尋內容，不把它當作MOVE精確數值的第二來源。

同源四項能源價格不算四個獨立機制；五檔晶片股也不等於五個獨立市場。Cboe與MOVE可驗證風險市場廣度，但仍需要信用、融資與持續性證據，才能討論更高燈號。

## 台灣傳導（TAIWAN TRANSMISSION）

| 通道 | 時間範圍 | 已有證據／機制 | 下一驗證與失效條件 |
|---|---|---|---|
| 估值（Valuation） | 即時 | 海外股債波動提高科技風險溢酬敏感度 | MOVE／VIX與科技相對強弱修復則減壓 |
| 外需 | 數週至數月／1–3季 | 訂單與出口仍強，尚無新增砍單 | 多個客戶指引轉弱才改寫獲利 |
| 金融條件 | 即時／數週 | 既有外資賣超與期貨淨空部位 | 下一開市實際Flow與融資價差 |
| 匯率 | 即時／數週 | USD/TWD 32.488→32.508 | 台幣變動、避險及進口合約共同決定 |
| 日本／中國放大器 | 數週至數月／1–3季 | 日本通膨加速、中國投資弱 | 發布後日債／日圓與區域訂單確認 |
| LNG／電力成本 | 數週至數月／1–3季 | 能源成本偏高，電價未核准上調 | LNG採購、政策與毛利實際傳導 |

10月22日外資現貨淨賣超816.56億元；TAIFEX外資台指期多單8,126口、空單95,423口，淨空87,297口。現貨淨流量與未平倉存量不同，不能把淨空口數當作本輪新增賣出。

台灣上漲247家、下跌756家、持平74家；金融漲0.62%、電子跌2.11%、半導體跌1.91%。既有廣度偏弱但產業分化，並非本輪新增成交，也不支持所有部門同程度失序。

### 跨市場時差與休市空窗

TSM ADR日跌4.52%，較先收盤台灣現貨約跌1.45%多3.07pp；SOX跌6.72%，較台灣半導體跌1.91%多4.81pp。這是非同步日報酬比較，不是可套利價差或同步相對強弱。

本輪未重驗ADR轉換比例，故不發布溢價率。USD/TWD微升0.020、約0.062%，可能放大美元能源進口成本，但出口美元收入與避險可部分抵銷，不能直接推定淨毛利變化。

[CNA停市資訊](https://www.cna.com.tw/news/afe/202610220388.aspx)與期交所公告確認10月23日現貨及期貨日夜盤休市。下一合法交易時段仍須核實，不自行假設日期，也不把金融市場停市等同晶圓廠停產。

### 能源成本與政策緩衝

[台電成本報導](https://focustaiwan.tw/business/202610220015)估計，若天然氣高價維持至年底，全年燃料成本可能增加1,600億元。此為條件式估計，9月電價方案未獲核准，下次檢討在12月，並非科技業電價已上調。

能源成本可透過LNG採購、公用事業與財政吸收，再逐步傳到電力密集產業。台塑化、航運及科技製造的實際受益受損，仍取決於產品價差、合約與避險，不以油價方向直接指定個股結論。

## 產業／股票敏感度（INDUSTRY / EQUITY SENSITIVITY）

| 類別 | 市場敏感度 | 基本面對照 | 判讀界線 |
|---|---|---|---|
| 晶圓代工／TSMC | 長久期估值、ADR與外資部位 | 第三季營收46.72十億美元；第四季指引52.3–54.3十億 | 股價跌不等於EPS已下修 |
| GPU／CPU | AI回收期間、融資及集中持倉 | NVIDIA已公告供應鏈（Supply Chain）擴產 | 預付款與產能承諾非已認列收入 |
| 記憶體 | 科技因子與供需預期 | DDR5 61.10、日升0.38%；DDR4持平 | NAND當期缺，不能判全面崩跌 |
| 設備／Lam | 資本支出（CapEx）倍數與客戶回收疑慮 | 季營收增22%；12月指引8.6±0.4十億美元 | 強財報可與估值修正並存 |
| 封測／載板 | AI產能擴張及執行風險 | NVIDIA供應鏈安排延伸至2027–28 | 不把遠期規劃算成當期訂單 |
| 塑化／航運／電力密集 | 燃料、匯率及轉嫁能力 | 合約與政策可緩衝 | 無公司證據不定單股盈虧 |

TSMC庫存天數由87降至82天，但庫存金額由3,855.3億增至4,277.5億元；毛利率由67.7%降至66.4%。週轉改善與金額增加可並存，不能只選其中一項宣告全然改善或惡化。

Lam營收由6.722增至8.219十億美元，GAAP毛利率由51.7%升至52.3%；非GAAP毛利率另為52.4%。管理層指引不是市場共識，GAAP與非GAAP口徑亦不可混用。

美光桃園11名工會幹部的象徵性罷工，工會表示無意中斷生產；目前未取得量化產量損失。不能把人數、天候停市或工程事故直接推成記憶體／晶圓供應中斷。

本報告提供產業風險敏感度，而非個人化交易指令。短期價格警報可早於獲利下修，但是否調整部位仍須結合實際持倉、期限與損失承受能力，不由單日波動機械決定。

## 市場週期 vs 基本面週期

**市場週期（Market Cycle）：**股債波動同日升溫與半導體盤後偏弱，支持風險溢酬及風險預算重估。這是本輪新增證據；即使名目利率下降，科技倍數仍可能受壓。

**基本面週期（Fundamental Cycle）：**台韓出口、TSMC／Lam營收與前瞻指引仍具韌性。台灣領先指標較慢，不能覆蓋即時市場風險；但尚無多個獨立供應鏈環節同步下修的證據。

SIA／WSTS的8月全球半導體銷售三個月移動平均為159.7十億美元，月增8%、年增144.3%。這是較慢需求反證；SIA與WSTS共享同一底層資料，不計作兩個獨立確認。

> 只有新訂單（New Orders）、庫存（Inventory）週轉、毛利率與資本支出展望開始一致轉弱，才有理由把估值調整升格為獲利週期轉折。市場可以先行，不能取代基本面；強基本面也不保證短線股價立即修復。

## 分類與風險燈號變化（CLASSIFICATION & RISK LIGHT DELTA）

| 項目 | 前值 → 目前 | 理由 | 升級約束 |
|---|---|---|---|
| Trigger | 新增跨資產確認 → TRIGGERED | MOVE補上債券波動證據 | 只觸發rates_shock |
| Risk Light | YELLOW → YELLOW | 壓力跨兩個風險市場 | 非全面拋售，融資／信用未證 |
| Classification | TACTICAL → TACTICAL | 單日市場定價變化 | 未見持續基本面下修 |
| Regime Shift | 未確認 → 未確認 | 波動廣度增加但持續性不足 | 不是多日、多family制度轉折 |

兩個不同市場指標提供新增戰術性證據，但不自動滿足升燈條件。仍須檢查持續性、信用／融資擴散及台灣實際傳導；資料缺失既不自動推高，也不自動降低風險燈號。

日本CPI、能源成本與半導體盤後價分別作政策觀察、成本背景及價格佐證。本輪不把三者機械加總成三項新衝擊，亦不將NDC景氣紅燈混同本報告的市場風險燈號。

## 情境矩陣（SCENARIO MATRIX）

| 情境 | 確認條件 | 市場含義 | 台灣傳導 | 研究反應 |
|---|---|---|---|---|
| 基準：波動擴散但可吸收 | MOVE／VIX偏高、需求指引維持 | 估值與避險成本調整 | 科技與外資風險預算敏感 | 維持YELLOW／TACTICAL |
| 惡化：信用與融資加入 | 更新OAS、SOFR／basis與市場深度同向轉差 | 不只是選擇權風險定價 | 匯率、融資與外流相互放大 | 重評升燈，非預設結果 |
| 基本面轉折 | 多家公司砍單、下修指引、庫存週轉轉差 | 從倍數壓力轉向EPS風險 | 出口、產能利用與毛利受壓 | 評估TREND_FORMATION |
| 改善：波動消退 | MOVE／VIX回落、科技廣度修復、融資穩定 | 風險溢酬回吐 | ADR與外資部位壓力減輕 | 撤銷新增波動擴散命題 |

未配置數值機率，因同日信用、融資及亞洲發布後價格仍不完整。日本通膨若引發可核驗政策重定價，或能源上行獲通膨補償確認，才提高相應惡化情境權重。

## 下一確認條件（NEXT CONFIRMATION）

1. **波動持續性：**取得下一交易日MOVE與官方VIX，觀察是否共同延續，而非重讀同日數字；同步檢查科技與非科技廣度、SOX相對Nasdaq。
2. **融資與信用：**補10月22日後SOFR分布、HY／IG OAS、美元basis及國債深度／買賣價差，區分避險需求、成長定價與資金壓力。
3. **日本政策通道：**取得CPI發布後可比較JPY／JGB時間戳，追蹤服務價格、薪資與BOJ 10月29–30日決議，不提前宣告套息交易平倉。
4. **台灣下一開市：**先核實合法交易時段，再檢查外資現貨、期貨未平倉變化、USD/TWD與市場廣度；休市期間不虛構流量。
5. **基本面與能源：**核對AI客戶及供應商新指引、訂單／庫存；補同合約氣價、正式油價結算、AGSI季節路徑及挪威10月22日實測流量。

> 失效條件：MOVE與VIX回落，信用與融資穩定，科技廣度修復，且公司需求反證仍有效。只有名目殖利率下降，不足單獨解除波動警報；只有波動上升，也不足宣告融資危機。

## SOURCE AUDIT

研究涵蓋12個families、21個canonical signals與每訊號18項核心研究欄位。COMPLETE表示本輪研究、缺口揭露及判斷完成，不表示所有市場數據即時可得；未取得項目明示UNAVAILABLE或UNCONFIRMED。

### 時間、口徑與獨立性

- **實際檢索：**台北08:03:53–08:08:21；宏觀至08:04:57、能源至08:04:28、亞洲至08:08:21。獨立複核另讀MOVE／VIX及日本共識；抓取時間不是觀測或發布時間。
- **主訊號時鐘：**MOVE採10/22日期列，Delayed 01:00:00時區未暴露；Cboe採as-of 10/22的19.03，8:15 PM widget時區未知。不把任何widget解讀為未來或同步成交。
- **收盤與盤後：**指數vendor有Closed標記但時區未暴露；五檔個股正規盤為16:00 EDT，盤後19:38–19:55 EDT，並非確認20:00終盤。
- **來源衝突：**官方SOX的0%與點數欄重設不採用；VIX舊搜尋20.17不覆蓋官方19.03；油價頁首與日期列不平均；前收欄換日後不反推虛構報酬。
- **證據層級：**官方政策、統計、公司與Cboe資料優先；MOVE精確值仍單一vendor。新聞說明機制，不增加同一價格的獨立樣本數；同源能源與晶片股分別保留相關性限制。
- **存取限制：**KC官方頁本輪技術錯誤，數值不採；SEMI維持既有403 hold，未重試或繞過。Reuters跨資產及CNA部分頁全文錯誤，只使用已取得搜尋內容並明示層級。

### 總經與市場來源

- **MOVE／VIX：**[MOVE日期表](https://www.investing.com/indices/ice-bofaml-move-historical-data)、[Cboe原始頁](https://www.cboe.com/tradable-products/vix/)；10/22觀測，10/21比較；主表與獨立複核均讀回，不把重讀算成新交易日。
- **美債曲線：**[2Y](https://www.investing.com/rates-bonds/u.s.-2-year-bond-yield-historical-data)、[10Y](https://www.investing.com/rates-bonds/u.s.-10-year-bond-yield-historical-data)、[30Y](https://www.investing.com/rates-bonds/u.s.-30-year-bond-yield-historical-data)；採10/22日期列。頁首19:49:54／19:35:55／19:49:59時區未知，且部分值不同。
- **實質利率：**[Fed H.15](https://www.federalreserve.gov/releases/h15/)；10/22發布、觀測僅10/21；10/22實質利率與期限溢酬UNAVAILABLE。
- **流動性：**[Fed H.4.1](https://www.federalreserve.gov/releases/h41/current/)、[NY Fed SOFR](https://markets.newyorkfed.org/api/rates/secured/sofr/last/5.json)；前者10/22 16:30 Eastern發布、截至10/21週均，後者僅10/21觀測。
- **信用與銀行：**[HY OAS](https://fred.stlouisfed.org/series/BAMLH0A0HYM2)、[IG OAS](https://fred.stlouisfed.org/series/BAMLC0A0CM)、[H.8](https://www.federalreserve.gov/releases/h8/current/default.htm)、[SLOOS](https://www.federalreserve.gov/data/sloos/sloos-202607.htm)；OAS至10/21、H.8至10/7週、SLOOS為第二季。
- **財政供給：**[20Y拍賣](https://www.newsquawk.com/headlines/us-treasury-sells-usd-13bln-of-20-year-bonds-tails-09bps)；10/21結果，次級來源；不當作本輪新拍賣或系統性證據。
- **成長與物價：**[GDPNow](https://www.atlantafed.org/research-and-data/data/gdpnow)、[BEA PCE](https://www.bea.gov/news/2026/personal-income-and-outlays-August-2026)、[BLS CPI](https://www.bls.gov/news.release/cpi.nr0.htm)；分別10/20模型估計、8月及9月統計，不是新小時發布。
- **勞動與共識：**[DOL初領](https://www.dol.gov/ui/data.pdf)、[初領共識](https://www.investing.com/economic-calendar/initial-jobless-claims-294)、[BLS就業](https://www.bls.gov/news.release/empsit.nr0.htm)；初領10/22 08:30 Eastern發布，不同統計週與修訂見正文。
- **Fed政策：**[9/16決議](https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm)；已存在決議，本輪未取得可核驗當期期貨機率。
- **外匯與黃金：**[DXY](https://www.investing.com/indices/usdollar)、[USDJPY](https://www.investing.com/currencies/usd-jpy)、[EURUSD](https://www.investing.com/currencies/eur-usd)、[GCZ6](https://www.investing.com/commodities/gold)；頁首時計19:24:07／19:10:12／19:41:55／19:20:19，時區未知、基準非共同全日。
- **廣泛股指：**[S&P 500](https://www.investing.com/indices/us-spx-500)、[Nasdaq](https://www.investing.com/indices/nasdaq-composite)；Closed 15:59:59、來源時區未暴露。指數跌幅與個股廣度不互相替代。
- **新聞反證：**[AP](https://apnews.com/article/1970e79d013cbddcae89c53b4b98f384)、[Reuters](https://www.marketscreener.com/news/stocks-drop-as-meta-fans-ai-worries-treasuries-gain-ce785cdede89f223)；本輪搜尋內容層級，Reuters標10/22 19:00 EDT發布，未取得完整原表或全文。

### 亞洲、台灣與公司來源

- **半導體指數：**[Nasdaq官方SOX](https://indexes.nasdaq.com/Index/Breakdown/SOX)、[SOX vendor](https://www.investing.com/indices/phlx-semiconductor)；官方10/22日期、vendor Closed 15:59:59。官方值與日變動欄分開處理。
- **個股收盤／盤後：**[TSM](https://stockanalysis.com/stocks/tsm/)、[NVDA](https://stockanalysis.com/stocks/nvda/)、[AMD](https://stockanalysis.com/stocks/amd/)、[MU](https://stockanalysis.com/stocks/mu/)、[LRCX](https://stockanalysis.com/stocks/lrcx/)；16:00 EDT收盤與19:38–19:55 EDT盤後分列。
- **台灣市場與匯率：**[TWSE日報](https://www.twse.com.tw/exchangeReport/MI_INDEX?date=%25s&response=html&type=ALLBUT0999)、[TAIFEX](https://www.taifex.com.tw/cht/3/futContractsDate)、[央行匯率](https://www.cbc.gov.tw/tw/lp-645-1.html)；頁內日期為10/22，不把讀取時刻當新交易日。
- **外資及停市：**[CNA外資](https://www.cna.com.tw/news/afe/202610220329.aspx)、[CNA停市](https://www.cna.com.tw/news/afe/202610220388.aspx)；分別10/22 18:58、更新19:21及20:39報導，搜尋內容層級；期交所另確認10/23日夜盤休市。
- **日本CPI／共識：**[總務省官方PDF](https://www.stat.go.jp/data/cpi/sokuhou/tsuki/pdf/zenkoku.pdf)、[Reuters 10/16調查](https://www.marketscreener.com/news/japan-core-inflation-likely-exceeded-boj-target-for-first-time-since-december-ce785dd3d080f02d)；實際10/23 08:30 JST發布，核心共識2.1%；預期不是第二個實際值來源。
- **日本市場：**[Stockweather](https://finance.stockweather.co.jp/contents/market.aspx)、[JGB 10Y](https://www.investing.com/rates-bonds/japan-10-year-bond-yield)；日股為10/22，日圓08:13 JST早於CPI；JGB日期未暴露、前收重設，不採發布後反應推論。
- **韓國現貨：**[ETNews收盤報導](https://www.etnews.com/20261022000405)；10/22 16:01報導KOSPI收5,533.77、跌3.52%，本輪全文讀回；排除不一致vendor搜尋摘錄。
- **中港市場與中國週期：**[信報市場](https://stock360.hkej.com/)、[中國官方GDP／投資](https://english.www.gov.cn/archive/statistics/202610/19/content_WS6ad589d8c6d00ca5f9a0dc71.html)；前者10/22收盤，後者10/19公布第三季及前九月資料。
- **貿易與訂單：**[台灣外銷訂單](https://uk.marketscreener.com/news/taiwan-september-export-orders-hit-record-value-on-solid-ai-demand-ce785cdbd08cf32d)、[財政部出口](https://www.mof.gov.tw/singlehtml/384fb3077bb349ea973e7fc6f13b6974?cntId=856cf6c5ea4646208d3b8345b3bb46e2)、[韓國1–20日出口](https://www.marketscreener.com/news/south-korea-october-1-20-exports-surge-105-on-record-chip-sales-ce785cd8df89f52d)；訂單與台灣出口均為9月，韓國為10月初值。
- **區域循環：**[WTO展望](https://www.wto.org/english/news_e/news26_e/stat_08oct26_510_e.htm)、[NDC指標報導](https://focustaiwan.tw/business/202609290019)；分別10/8預測修訂、9/29公布8月指標，非本輪即時實體量。
- **半導體銷售：**[SIA發布](https://www.semiconductors.org/year-to-date-global-semiconductor-sales-top-1-trillion-through-august/)、[WSTS](https://www.wsts.org/)；10/5發布8月三個月移動平均，本輪重讀；同一底層資料，不重複計為獨立來源。
- **公司基本面：**[TSMC第三季資料](https://www.sec.gov/Archives/edgar/data/1046179/000104617926000726/a3q26presentatione.htm)、[Lam財報](https://investor.lamresearch.com/2026-10-21-Lam-Research-Corporation-Reports-Financial-Results-for-the-Quarter-Ended-September-27,-2026)、[NVIDIA供應鏈公告](https://nvidianews.nvidia.com/news/nvidia-and-supply-chain-partners-expand-capacity-to-accelerate-ai-infrastructure-buildout/)；分別10/15、10/21、10/21發布，實際、指引與產能承諾分開。
- **記憶體：**[DRAM現貨](https://www.trendforce.com/price/dram/dram_spot)、[NAND頁](https://www.trendforce.com/price/flash/flash_spot)、[美光勞資報導](https://focustaiwan.tw/business/202610220016)；DRAM為10/22 18:10 GMT+8，NAND停留10/12故當期UNAVAILABLE；勞資報導10/22 19:07，未量化損失。
- **台電成本：**[CNA英文報導](https://focustaiwan.tw/business/202610220015)；10/22 18:48台北發布，本輪重讀；條件式全年成本估計不是已核准電價變動。

### 能源與供給來源

- **每日價格代理：**[JKM](https://www.investing.com/commodities/lng-japan-korea-marker-platts-futures-historical-data)、[TTF](https://www.investing.com/commodities/dutch-ttf-gas-c1-futures-historical-data)、[Brent](https://www.investing.com/commodities/brent-oil-historical-data)、[WTI](https://www.investing.com/commodities/crude-oil-historical-data)；10/22日期列與10/21明示比較，頁首及長區間限制見正文。
- **EU庫存：**[AGSI](https://agsi.gie.eu/)、[Storagecurve代理](https://storagecurve.com/natural-gas/europe/storage/)；AGSI當期數值未呈現，代理觀測10/20、發布10/21；不用舊值補current。
- **實體供需：**[EIA週報](https://ir.eia.gov/wpsr/overview.pdf)、[挪威流量](https://voltstack.energy/norway-gas-flows)；EIA週至10/16，挪威完整gas day至10/21；頁面更新及近期事件feed不等於新實測流量。
- **換月與需求：**[ENGINE換月說明](https://www.engine.online/news/lng-bunker-snapshot-jkm-contract-roll-lifts-singapores-lng-bunker-price-82e9)、[Kpler需求背景](https://www.kpler.com/blog/asian-lng-prices-to-rise-amid-simmering-geopolitical-tensions-elevated-ttf)；分別10/19說明10/16換月與10/15背景，非本輪新供給事件。

## 結論（BOTTOM LINE）

> 本輪新增的是美債波動與股票波動的雙市場確認，讓科技估值壓力具有更完整的跨資產證據；不是名目殖利率上升，也不是已證實融資危機。維持YELLOW與TACTICAL，等待持續性、信用及台灣下一交易時段驗證。

正式Markdown已核對內容、標題層級與表格結構；未指定實際renderer，不宣稱CSS色彩、間距或像素呈現已驗證。
<<<REPORT_END>>>
