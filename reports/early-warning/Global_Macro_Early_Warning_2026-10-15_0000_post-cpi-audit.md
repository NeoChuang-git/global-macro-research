<<<REPORT_BEGIN>>>
---
research_status: COMPLETE
report_type: MACRO_TAIWAN_EARLY_WARNING
run_id: MTW-20261015-0000-post-cpi-audit
generated_at_taipei: 2026-10-15T00:18:00+08:00
coverage_start_taipei: 2026-10-14T23:00:00+08:00
coverage_end_taipei: 2026-10-15T00:00:00+08:00
report_name: Global Macro Early Warning
title: Global Macro Early Warning｜半導體賣壓再擴大，估值壓力與設備需求背離
format_version: 2
trigger_status: TRIGGERED
risk_light: YELLOW
classification: TACTICAL
slug: post-cpi-audit
---
# Global Macro Early Warning｜半導體賣壓再擴大，估值壓力與設備需求背離

## 核心警報摘要（EXECUTIVE TAKE）

> 半導體相對弱勢在本輪進一步擴大，已獲獨立來源的ETF與台積電ADR報價支持。這是戰術性市場警報；長債殖利率回吐、設備需求仍強，尚不足將風險燈號升為橙燈。

- **新增變化：** 半導體ETF跌幅擴大，明顯落後同一觀察時段的廣泛市場；警報重點由早前通膨意外，轉為產業風險溢酬持續上升。
- **機制判讀：** 高利率及AI融資疑慮壓低估值（Valuation），但目前尚無新的公司訂單取消或資本支出下修證據，不能直接判定需求反轉。
- **跨資產邊界：** 前端殖利率仍高於昨收，長端已回吐盤中升幅；新公布信用利差反映前一日交易，不能當作通膨公布後的即時信用確認。
- **台灣重點：** ADR弱勢將考驗次日現貨，但日間市場廣度與新台幣改善提供緩衝；下一重要基本面確認是10月15日14:00台積電法說。

## 訊號變化總覽（SIGNAL DELTA）

| 訊號 | 前值→目前 | 方向／Delta | 嚴重度 | 信心 | 跨資產確認 | 台灣關聯 |
|---|---|---|---|---|---|---|
| semiconductor_relative_weakness | SOXQ日跌幅約−2.29%→−3.25% | ↘ 惡化；擴大約0.96個百分點 | 3/5 | 中 | 股票內部成立；利率／信用新增共振不足 | ADR隔夜估值傳導 |

前後SOXQ觀察時間分別為10月14日14:53與15:39 UTC；目前SOXX另於15:49 UTC日跌3.50%。資料有非同步及報價供應商限制，沒有把ETF當成費半指數本身。

### Signal #1｜半導體相對弱勢擴大，市場定價先於基本面轉弱

**Severity 3/5｜Confidence 中｜TACTICAL｜Risk Light：YELLOW → YELLOW**

- **原始變化：** SOXQ價格 ↓，跌幅擴大；SOXX相對SPY落後約2.57個百分點，兩筆時間相差9分鐘，僅作同時段近似比較。
- **延續性：** SOXX在10月7日至13日已連續五個交易日收低，本日再跌；本輪是既有賣壓的實質延伸，不以一個新聞標題替代持續性。
- **廣度：** 半導體ETF、台積電ADR與AI雲股票均偏弱，但它們有共同產業曝險，不計為多個獨立總經風險家族。
- **共識／修正：** 價格訊號沒有適用的經濟數據共識或修正值；ASML公司前瞻指引仍正向，未查得本輪新的產業獲利下修。
- **確認與失效：** 收盤相對弱勢、次日外資與公司指引決定是否升為趨勢；若半導體相對強度修復且公司需求維持，戰術警報可失效。

#### 機制

市場定價（Market Pricing）先反映資金成本與風險承擔下降。AI雲業者融資疑慮可能壓縮邊際買家的擴張能力，因而提高半導體估值折價；目前仍屬傳導假說，沒有把單一債券敘事當成已發生的訂單（Order）流失。

#### 市場定價

| 資產 | 報價／日變化 | 觀察時間 UTC | 用途 |
|---|---|---|---|
| SOXQ | 92.91美元／−3.25% | 10/14 15:39 | 半導體ETF代理 |
| SOXX | 524.88美元／−3.50% | 10/14 15:49 | 不同半導體籃子 |
| SPY | 770.81美元／−0.93% | 10/14 15:58 | 廣泛市場比較 |
| TSM ADR | 434.22美元／−2.45% | 10/14 15:35:21 | 台灣隔夜敏感度 |

ETF頁首明示EDT，已換算UTC。QQQ取得的12:04 EDT報價超過本輪截止，未納入；亦未以過時日內高低欄判定突破。[ETF資料](https://stockanalysis.com/etf/soxq/history/)、[SOXX](https://stockanalysis.com/etf/soxx/history/)、[SPY](https://stockanalysis.com/etf/spy/)、[TSM](https://www.investing.com/equities/taiwan-semicond.manufacturing-co)。

#### 反向證據

ASML上調全年營收（Revenue）指引下緣，並表示目前產能規畫不足以滿足2027至2028年客戶需求。這是設備需求仍強的反證；較遠年份的客戶興趣不能等同確定新訂單（New Orders）。[ASML原始公告](https://www.investor.asml.com/news-releases/news-release-details/asml-reports-eu11.7-billion-total-net-sales-and-eu5.0-billion-net-income-q3-2026)、[Reuters獨立報導](https://live.euronext.com/en/financial-news/chip-tool-giant-asml-nudges-outlook-ai-driven-demand-outruns-supply)。

#### 台灣傳導

**即時：** ADR與美國半導體風險溢酬向台股傳導。**數週至數月：** 外資資金流（Flow）、美元金融條件與進口能源成本。**1–3季：** 須由客戶支出、訂單、庫存及毛利率確認是否影響實際獲利。

#### 下一確認條件

> 若半導體弱勢延續至收盤，且下一輪出現獨立的信用、美元融資或公司訂單惡化，才有理由提高風險層級；單靠兩檔高度相關ETF下跌不足以升級燈號。

---

## 為何重要（WHY IT MATTERS）

1. **數據／政策 →** 已公布的通膨意外，使政策寬鬆預期受壓。
2. **利率／匯率／信用／流動性 →** 美元及前端利率偏高，提高資本密集型AI投資的必要報酬；目前未確認全面流動性（Liquidity）失序。
3. **產業／資金流 →** 風險承擔下降集中在半導體與AI相關股，防禦股相對承接。
4. **獲利／估值 →** 即使營收仍增長，投資人也可能降低估值倍數；每股盈餘（EPS）尚未發生已核驗的新下修。
5. **台灣 →** 先影響ADR與次日外資部位（Positioning），再檢驗台積電及供應鏈（Supply Chain）的實際需求。

## 總經與政策細節（MACRO / POLICY DETAIL）

**FACT：** 美國9月CPI月增0.6%、年增3.7%；核心月增0.3%、年增2.6%。核心月增率與8月相同，能源則月增5.2%，汽油貢獻總體月升幅過半。本報保留核心與能源兩條通膨鏈，不將它們混成單一動能。[BLS](https://www.bls.gov/news.release/archives/cpi_10142026.htm)。

**MARKET EXPECTATION：** Reuters稍早引述LSEG，10月升息機率由公布前21.6%提高至46%。這是既有CPI後重定價，不是本小時新的Fed決策或最新期貨截面。[Reuters](https://in.marketscreener.com/news/wall-st-slides-as-hot-cpi-data-fuels-rate-hike-bets-chips-banks-weigh-ce785dd2de8af72d)。

**INFERENCE：** 通膨限制政策緩衝，但不能忽略成長反證。9月非農僅增2.9萬、失業率4.2%；第二季GDP年化成長2.2%，經濟尚未呈全面收縮。[BLS勞動](https://www.bls.gov/news.release/empsit.nr0.htm)、[BEA](https://www.bea.gov/news/glance)。

**能源逐輪檢查：**

| 核心項目 | 最新可用觀察 | 1D／5D | 時效與限制 |
|---|---|---|---|
| JKM，USD/MMBtu | current UNAVAILABLE；次級assessment 26.27 | 次級+0.69%／UNAVAILABLE | 10/13 assessment；不同front-month代理29.61不可拼接 |
| TTF，EUR/MWh | 指示85.60 | 約−1.86%／+9.63% | 10/14 11:36 UTC，非本小時tick |
| Brent，USD/bbl | 105.98，12月合約 | +0.27%／+5.77% | 10/14 15:55 UTC，衍生報價 |
| WTI，USD/bbl | 95.01，近月代理 | +0.92%／+7.62% | 10/14 15:51 UTC，非交易所成交確認 |
| EU儲氣 | current官方UNAVAILABLE；次級73.9% | 1D／7D UNAVAILABLE | 10/12 gas day；同季五年均88.8%，差−14.9pp |

TTF既有ICE 11月同合約10月6日至13日五交易日升幅15.24%仍保留為中等信心候選；CME連續合約資料差異不撤銷此歷史判斷。本輪油價幅度不足、天然氣回落，沒有新的廣度確認；未核驗可量化供應中斷。

能源反證已檢查需求破壞、季節性、庫存（Inventory）、運價、供給恢復及期限結構。需求與運價缺可量化新證據；冬季補庫具季節性，供給恢復報導尚非實際流量。缺同合約長序列的20日區間、百分位／z-score列為UNAVAILABLE，不虛構。

## 跨資產確認（CROSS-ASSET CONFIRMATION）

| 市場 | 本輪可用狀態 | 解讀 |
|---|---|---|
| UST 2Y／10Y／30Y | 4.859%／5.244%／5.563%；日變+6.6／+2.7／0bp | 殖利率（Yield）前端主導，長端回吐 |
| 實質殖利率／曲線 | 10Y實質最新10/9為2.91%；近似10s2s 38.5bp | 實質殖利率（Real Yield）非即時；不能估算新期限溢酬（Term Premium） |
| DXY／JPY／EUR | 102.85／158.82／1.1121 | 美元偏強，但缺交叉貨幣基差失序證據 |
| 黃金 | 12月合約日跌1.66% | 與美元／折現壓力相符，非新金債背離警報 |
| HY／IG | 10/13 OAS 3.16%／0.83%，較前值+5／0bp | 信用利差（Credit Spread）觀察落後CPI |
| MOVE／VIX | MOVE最新10/13且變化欄不一致；VIX直讀超截止 | 當輪精確即時值UNAVAILABLE，不以無時戳sidebar補造 |
| S&P／Nasdaq／亞洲 | 美股同時段約−0.94%／−1.13%；亞洲收盤混合 | 亞洲收盤在美CPI前，不能作公布後驗證 |

報價時鐘非完全同步，Investing頁面未明示時區者依美國交易時段推定EDT並降低信心。HY／IG雖在15:26 UTC新更新，觀察日仍是10月13日。[美債](https://www.investing.com/rates-bonds/u.s.-10-year-bond-yield)、[HY](https://fred.stlouisfed.org/series/BAMLH0A0HYM2)、[IG](https://fred.stlouisfed.org/series/BAMLC0A0CM)。

## 證據與反向證據（EVIDENCE VS COUNTER-EVIDENCE）

| 支持警報 | 反向證據／限制 |
|---|---|
| 半導體ETF持續多日走弱，且本輪跌幅擴大 | ASML需求與指引仍強，未有新CapEx削減 |
| TSM ADR與產業ETF同弱 | 台股日間廣度正、外資賣額收斂；非同時交易 |
| AI雲股票受融資疑慮壓力 | CoreWeave債券15%是昨日社群圖轉述，無本小時原始成交確認 |
| 通膨後美元／前端利率偏高 | 長債回吐、30Y平穩；信用資料滯後，缺新系統共振 |

Fox／FactSet搜尋快照顯示費半15:38 UTC跌3.32%，但直讀返回前日版本；精確費半點位仍有版本限制。另取StockAnalysis／S&P Global的兩檔ETF頁首，以及Investing的ADR報價確認產業壓力，不把同一資料供應商算成多個獨立來源。

## 台灣傳導（TAIWAN TRANSMISSION）

- **估值，即時：** ADR與美國科技風險溢酬先行；現貨與ADR不同時收盤，不能把跌幅差視為可交易套利溢價。
- **外需，1–3季：** 台灣8月外銷訂單（Export Orders）年增71.4%，韓國9月半導體出口仍強，提供基本面緩衝；名目增幅須拆量、價及匯率。
- **金融條件，即時至數週：** 10月14日外資賣超200.37億元，較前日1653.42億元縮小；期交所TX外資淨空86,814口，不能與含小台／微台的等值口數混比。
- **匯率，即時：** 新台幣日收32.073、較前日升值；這筆資料早於美CPI，隔夜美元走強仍可能重新增加進口成本。
- **日本／中國，數週至數月：** 日本能源進口與日圓政策兩難、中國出口強但內需不均，可能放大產業差異，尚非同步全面避險。

台股日間上漲752家、下跌245家；期貨淨空可能包含現貨避險，不能等同單一方向押注。[CNA股匯](https://www.cna.com.tw/news/afe/202610140275.aspx)、[TAIFEX](https://www.taifex.com.tw/cht/3/futContractsDate)、[MOEA訂單](https://www.moea.gov.tw/mns/populace/news/News.aspx?kind=1&menu_id=40&news_id=124026)。

## 產業／股票敏感度（INDUSTRY / EQUITY SENSITIVITY）

**半導體與設備：** 對估值折現與客戶資本支出（CapEx）敏感；ASML營收及毛利率（Gross Margin）指引仍正面，但不能替代台積電即將公布的獲利、庫存和前瞻指引（Guidance）。

**能源與成本：** 台灣LNG／電力成本、台塑化、航運及電力密集製造需同時考慮進口價格、TWD、政策轉嫁與避險。缺公司證據時，不從能源單一價格推導個股必然受益或受害。

**AI融資鏈：** 高槓桿客戶比現金充裕買家更易受資金成本衝擊；先觀察融資能否完成及訂單是否實際調整，不把社群債價圖直接外推整條供應鏈。

## 市場週期 vs 基本面週期

市場週期（Market Cycle）正在反映較高風險溢酬；基本面週期（Fundamental Cycle）的設備需求、台韓出口與台灣領先指標仍有支撐。兩者可暫時背離，後續取決於弱股價是否傳導到融資、CapEx及訂單。

WSTS與SEMI是中長期預測，不是本小時實際成交訂單。國發會8月景氣41分紅燈代表其景氣熱度分類，亦不等同本報風險燈號RED。

## 分類與風險燈號變化（CLASSIFICATION & RISK LIGHT DELTA）

| 項目 | Prior → Current | 理由 |
|---|---|---|
| 分類 | TACTICAL → TACTICAL | 新增產業相對弱勢，未確認基本面趨勢轉折 |
| 風險燈號 | YELLOW → YELLOW | 未滿足兩項獨立市場指標同步跨資產惡化 |
| Regime Shift | 未確認 → 未確認 | 設備／出口反證未失效，缺兩風險家族新共振 |

> 觸發研究報告與升級Risk Light是兩個判斷。這次產業賣壓延伸值得警示，但證據仍不足以宣告系統性融資危機。

## 情境矩陣（SCENARIO MATRIX）

| 情境 | 條件 | 市場含意 | 台灣含意 |
|---|---|---|---|
| 基準：估值調整 | 半導體弱於大盤、公司指引維持 | 戰術壓力延續；YELLOW | ADR／外資影響先於獲利 |
| 下行情境 | 收盤弱勢加上信用／美元融資惡化，或CapEx削減 | 重評ORANGE及趨勢形成 | 外需與金融條件共振 |
| 修復情境 | 相對強度回升、指引強且利率回吐 | 警報失效或降為觀察 | 現貨資金流與廣度改善 |

未提供虛構機率；各情境須用可核驗條件更新。

## 下一確認條件（NEXT CONFIRMATION）

1. 半導體ETF與費半收盤、相對SPY走勢；避免採用截止後數據回填本輪。
2. 下一個可靠信用／repo截面，以及2Y、10Y、美元是否同步再惡化。
3. 10月15日14:00 Asia/Taipei台積電法說：毛利率、庫存、CapEx與Guidance。
4. 次日TWSE外資、TAIFEX同口徑部位與新台幣，檢驗隔夜風險是否落地。
5. 新JKM assessment、ICE同合約TTF及AGSI gas day；供給事件須量化受影響容量。

**Kill condition：** 半導體相對弱勢修復、利率壓力下降，且龍頭需求／毛利指引維持，則本輪戰術判斷失效；只有股價單日反彈不足以斷言所有風險解除。

## SOURCE AUDIT

| 類別 | 來源與觀察期 | 品質／限制 |
|---|---|---|
| 價格確認 | [SOXQ](https://stockanalysis.com/etf/soxq/history/)、[SOXX](https://stockanalysis.com/etf/soxx/history/)、[SPY](https://stockanalysis.com/etf/spy/)；10/14 15:39–15:58 UTC | S&P Global來源；ETF代理，頁首時間明確；日表高低滯後不使用 |
| 獨立產業／市場 | [TSM ADR](https://www.investing.com/equities/taiwan-semicond.manufacturing-co)、[Reuters市場](https://in.marketscreener.com/news/wall-st-slides-as-hot-cpi-data-fuels-rate-hike-bets-chips-banks-weigh-ce785dd2de8af72d) | ADR指示報價；Reuters觀察較早，支持機制而非精確小時增量 |
| 費半限制 | [Fox／FactSet](https://www.foxbusiness.com/quote?stockTicker=I%3ASOX) | 搜尋快照與直讀版本不同；不作唯一觸發依據 |
| 公司基本面 | [ASML官方](https://www.investor.asml.com/news-releases/news-release-details/asml-reports-eu11.7-billion-total-net-sales-and-eu5.0-billion-net-income-q3-2026)、[Reuters ASML](https://live.euronext.com/en/financial-news/chip-tool-giant-asml-nudges-outlook-ai-driven-demand-outruns-supply)、[TSMC法說頁](https://investor.tsmc.com/schinese/quarterly-results/2026/q3) | 當日較早公司資料；TSMC實際Q3結果尚未發布 |
| 美國總經 | [BLS CPI](https://www.bls.gov/news.release/archives/cpi_10142026.htm)、[BLS就業](https://www.bls.gov/news.release/empsit.nr0.htm)、[BEA](https://www.bea.gov/news/glance)、[Fed](https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm) | 事件時間與本輪分開；非新小時發布 |
| 信用／流動性 | [HY](https://fred.stlouisfed.org/series/BAMLH0A0HYM2)、[IG](https://fred.stlouisfed.org/series/BAMLC0A0CM)、[H.4.1](https://www.federalreserve.gov/releases/h41/current/)、[SLOOS](https://www.federalreserve.gov/data/sloos/sloos-202607.htm)、[NYFed SOFR](https://www.newyorkfed.org/markets/reference-rates/sofr) | 信用10/13；H41 10/7；SLOOS季度；SOFR原頁當日數值未暴露 |
| 能源 | [Brent](https://www.investing.com/commodities/brent-oil-historical-data)、[WTI](https://www.investing.com/commodities/crude-oil-historical-data)、[TTF](https://in-crypto.app/commodities/ttf-gas)、[RIM 10/6](https://eng.rim-intelligence.co.jp/news/overseas/1836925.html)、[RIM 10/13](https://www.rim-intelligence.co.jp/news/news-global/1837212.html) | 近月代理與ICE同合約歷史分開；不拼不同合約序列 |
| 天然氣／儲氣缺口 | [CME JKM](https://www.cmegroup.com/markets/energy/natural-gas/lng-japan-korea-marker-platts-swap.html)、[JKM次級](https://energyriskiq.com/data/jkm-lng-price-chart)、[AGSI](https://agsi.gie.eu/)、[次級儲氣](https://commoditynews.morgandowney.com/news/2026-10-14) | 官方current未取得；assessment及gas day不偽裝即時 |
| 台灣／亞洲 | [TAIFEX](https://www.taifex.com.tw/cht/3/futContractsDate)、[CNA](https://www.cna.com.tw/news/afe/202610140275.aspx)、[MOEA](https://www.moea.gov.tw/mns/populace/news/News.aspx?kind=1&menu_id=40&news_id=124026)、[MOF](https://service.mof.gov.tw/)、[MOTIR](https://english.motir.go.kr/eng/article/EATCLdfa319ada/2743/view)、[NDC](https://www.ndc.gov.tw/nc_332_40495) | 日／月資料均早於本輪；官方TWSE介面讀取失敗，以CNA補足現貨資金流 |
| 產業長期 | [WSTS](https://www.wsts.org/76/Recent-News-Release)、[SEMI](https://www.semi.org/en/semi-press-release/global-semiconductor-equipment-sales-forecast-to-reach-a-record-229-billion-dollars-in-2028-semi-reports) | 預測不是即時訂單；DRAM現貨報價UNAVAILABLE |

資料取得時間為10月15日00:01–00:18 Asia/Taipei；僅納入截止00:00前可識別的觀察。共檢查12訊號家族、21個canonical signals；只展開一個真正觸發訊號。缺失資料及反證保留，不降低研究或保存驗收標準。

原始Markdown結構已預檢；未指定renderer基準與實際渲染結果，未聲稱顏色、間距或像素一致性已驗證。

## 結論（BOTTOM LINE）

> 半導體賣壓延伸已足以形成戰術警報；下一關是收盤相對強度與台積電指引。現階段維持YELLOW，將市場估值調整與未被證實的基本面／融資崩塌分開。
<<<REPORT_END>>>
