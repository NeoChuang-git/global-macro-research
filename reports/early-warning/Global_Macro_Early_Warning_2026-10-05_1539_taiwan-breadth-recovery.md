<<<REPORT_BEGIN>>>
---
research_status: COMPLETE
report_type: MACRO_TAIWAN_EARLY_WARNING
run_id: MTW-20261005-1539-taiwan-breadth-recovery
generated_at_taipei: 2026-10-09T13:00:00+08:00
coverage_start_taipei: 2026-10-05T14:39:21+08:00
coverage_end_taipei: 2026-10-05T15:39:21+08:00
report_name: Global Macro Early Warning
title: Global Macro Early Warning｜台股資金流改善但漲勢集中，長端利率風險尚未全面共振（10月5日回溯補驗）
format_version: 2
trigger_status: TRIGGERED
risk_light: YELLOW
classification: TACTICAL
slug: taiwan-breadth-recovery
recovery_mode: RETROSPECTIVE_RECONSTRUCTION
original_run_id: MTW-20261005-1539-global-term-premium
---
# Global Macro Early Warning｜台股資金流改善但漲勢集中，長端利率風險尚未全面共振（10月5日回溯補驗）

## 核心警報摘要（EXECUTIVE TAKE）
> 台股買盤與權值股價格提供明顯支撐，但多數股票未參與上漲。日本超長債偏弱，尚不足證明全球融資壓力同步擴大；本件判定為戰術性分化，沒有風險燈號升級的充分證據。

- **新增資訊**：盤後外資買盤與市場廣度資料，改變對當日強勢行情的解讀。資金流（Flow）改善屬實，普遍性的風險承擔回升仍待確認。
- **市場反證**：台灣中小型股沒有跟隨大型權值全面走強，日本中短端亦未與超長端同步賣壓，不能把局部利率風險寫成全面緊縮。
- **基本面支撐**：已發布的台韓出口、TSMC營收（Revenue）及設備出貨支持科技需求；記憶體仍有伺服器強、消費弱的分化。
- **研究限制**：能源五項歷史快照、同步信用利差與部分融資指標無法完整回收。不可得不等於低於門檻，也不能據此判斷風險已解除。

本件於10月9日重新查核10月5日15:39:21台北時間以前的資料，原研究與原識別碼另行保留。研究完成指本次回溯評估完成，並不表示所有即時資料已恢復；後來的行情與10月5日晚間美國數據均未納入當時判斷。

## 訊號變化總覽（SIGNAL DELTA）

| 訊號 | 前值→目前 | 方向／Delta | 嚴重度 | 信心 | 跨資產確認 | 台灣關聯 |
|---|---|---|---|---|---|---|
| taiwan_foreign_flow | 連買→當日約718.97億元買超 | ↗ 改善；廣度未確認 | 3/5 | 中高 | 指數及期貨同漲，小型股弱 | 直接影響大型權值流動性 |
| rates_shock | JGB30Y 4.200%→4.230% | ↘ 惡化，限超長端 | 3/5 | 中 | 10Y反而微降；非全面共振 | 估值折現風險 |
| energy_inflation | 歷史完整快照不可得 | UNKNOWN | 未評分 | 低 | 門檻及廣度UNKNOWN | LNG、電力、進口成本 |

後兩項為背景與監測項，未另展開為觸發卡。表中日資料不是本小時成交；只有盤後新增披露能歸入本輪資訊增量。

### Signal #1｜外資買盤改善，權值行情與市場廣度分離
**Severity 3/5｜Confidence 中高｜TACTICAL｜Risk Light：UNKNOWN → YELLOW（回溯重建，非歷史降級）**

- **FACT／變化**：10月5日加權指數由48,475.74升至49,712.04，原始價格 ↑ 2.55%；台指10月合約亦上漲。官方與中央社交叉支持價格反應。[TWSE](https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?response=json&date=20261005&type=ALLBUT0999)、[中央社](https://pchome.megatime.com.tw/m/news/cat8/20261005/17911799718463818003.html)
- **FACT／資金**：截點前盤後報導記錄外資現貨買超約718.97億元，連續第四日買超；期貨淨空仍大，不能把現貨與避險部位（Positioning）互相抵銷。[Newtalk，15:20](https://newtalk.tw/news/view/2026-10-05/1063759)
- **FACT／廣度**：官方歷史股票口徑為上漲364、下跌631、持平87；漲跌比約0.58。原文媒體口徑366／646／98未能解釋差異，不混用。[TWSE](https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?response=json&date=20261005&type=ALLBUT0999)
- **預期與修訂**：無可信外資買超共識；官方歷史表首發版本未取得。四日累計買超在媒體間不一致，故不使用。日比流量前值不可得，不虛構增幅。
- **INFERENCE／方向**：買盤改善大型股流動性（Liquidity）與短期估值（Valuation），故台灣傳導為↗改善；集中度使整體美股風險資產的正面外溢有限，沒有全球轉多結論。

#### 機制
1. 外資現貨買盤集中大型股，推動指數上升。
2. 中小型與非電子參與不足，指數不能代表典型股票。
3. 若長端利率再抬高折現率，集中持倉更容易放大修正；這是條件風險，不是已發生的資金逃逸。

#### 市場定價
台灣50漲2.99%，中型100漲1.03%，小型股300跌0.01%；電子類漲3.00%、金融僅0.10%。相對強度支持權值主導，但沒有日內事件研究，不能把全部漲幅歸因外資買盤。[TWSE](https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?response=json&date=20261005&type=ALLBUT0999)

#### 反向證據
市場廣度偏窄可由指數權重與產業輪動造成，單日不是頂部訊號。期貨淨空也可能包含套保；沒有整體現貨、期貨與選擇權帳戶匹配資料，不能判斷外資淨方向。

#### 台灣傳導
即時影響集中在權值估值與交易流動性。數週至數月仍須訂單（Order）及新訂單（New Orders）支持；一至三季須檢查毛利率（Gross Margin）、每股盈餘（EPS）與資本支出（CapEx）回報，不能由當日股價直接推演獲利。

#### 下一確認條件
觀察接續交易日上漲家數、等權／中小型相對表現及外資買盤是否同步延續。若買盤反轉且領漲權值失守，改善訊號失效；若廣度擴散且利率穩定，集中度警戒可降低。

---

## 為何重要（WHY IT MATTERS）
1. **資料／政策**：就業放慢降低立即升息預期，科技需求仍有基本面支持。
2. **利率／匯率／信用／流動性**：超長端供給疑慮保留折現壓力，但美元融資及信用利差（Credit Spread）尚未完成同步確認。
3. **產業／資金流**：買盤集中AI與大型電子股，反映風險選擇而非普遍追價。
4. **獲利／估值**：訂單轉成營收尚需時間；估值反應快於財報，對利率回升較敏感。
5. **台灣**：若市場廣度未改善，即使指數創高，個股風險分散效果仍可能不足。

## 總經與政策細節（MACRO / POLICY DETAIL）

| 研究領域 | 截點前已知資料 | 經濟解讀 | 限制／下一確認 |
|---|---|---|---|
| Growth | 8月實質PCE月增0.6%，前月0.1% | 消費仍有韌性 | 不外推GDP；與就業交叉檢查 |
| Inflation | 核心PCE月增0.2%、年增3.0% | 核心月度增速溫和，水準仍高 | 共識與完整修訂未重建 |
| Labor | 9月非農增2.9萬、失業率4.2% | 聘僱降溫支持近月政策預期緩和 | 工時與薪資細項不足 |
| Fed / Monetary Policy | 9/16升息25bp至3.75–4% | 緊縮背景仍在 | 近月市場預期不是政策承諾 |
| Rates / Term Premium | 日本超長端漲、10年微降 | 名目利率不能全歸期限溢酬 | 實質殖利率與通膨補償不足 |
| Liquidity / Market Plumbing | 9/30週平均準備金增、TGA降 | 存款準備變化提供背景緩衝 | 非即時QE，SOFR基差未知 |
| Credit / Bank Credit | H8及信用指標來源已檢查 | 無可靠當時數值，不下方向判斷 | 完整歷史利差與授信調查待補 |
| Fiscal / Treasury Supply | 長債風險補償偏高 | 供給疑慮可壓低估值 | 缺拍賣尾差、承接比與可比供給 |
| FX / Global Dollar | 截點前歐元跌至1.1161 | 歐洲財政疑慮支持美元 | 匯價不等於融資危機 |
| Commodities / Inflation Chain | 五核心能源歷史快照不足 | 方向UNKNOWN | 不以更新後價格補入歷史 |
| Global Trade / Supply Chain | 台韓出口強、非科技分化 | 科技外需支撐供應鏈 | 金額需拆價格、數量及基期 |
| China / Asia / Taiwan Cycle | 中國PMI回50.1、台灣領先指標升 | 復甦具區域與規模差異 | 不等於全球同步擴張 |

上述背景來源為[BEA](https://www.bea.gov/news/2026/personal-income-and-outlays-august-2026)、[BLS](https://www.bls.gov/news.release/archives/empsit_10022026.htm)、[Fed](https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm)、[H.4.1](https://www.federalreserve.gov/releases/h41/20261001/)、[中國統計局](https://www.stats.gov.cn/sj/zxfbhjd/202609/t20260930_1965449.html)。低頻發布皆是既知背景，沒有冒充本小時新訊號。

## 跨資產確認（CROSS-ASSET CONFIRMATION）

| 資產群 | 已核驗觀察 | 時間窗口 | 判斷 |
|---|---|---|---|
| UST 2Y／10Y／30Y | 10/2報價約4.827%／5.281%；30Y僅次級收盤約5.628% | 前一美國交易日 | 長端壓力仍在，非10/5即時shock |
| 日本2Y／10Y／30Y | 原始交易商日表1.905%／3.085%／4.230% | 10/5日觀察；上架鐘點未曝露 | 曲線局部陡化，不是全曲線同步升 |
| 實質殖利率、curve | JGB30–10利差114.5bp，前111bp；UST實質值未取 | 不同市場基準不可混算 | 期限溢酬（Term Premium）因子未識別 |
| DXY／JPY／EUR／USDTWD | 僅EUR低點1.1161有截點前報導 | 10/5亞洲時段 | 其餘同步值UNAVAILABLE |
| 黃金／能源 | 黃金報價時間不一致；能源五項不足 | 歷史截點 | 金債背離、能源門檻皆UNKNOWN |
| 信用／MOVE／VIX | 缺同時點可核歷史值 | 歷史截點 | 不以原稿數字替代 |
| S&P／Nasdaq／SOX | 10/2 S&P+0.7%、Nasdaq+1.2%；SOX未核 | 前一美國收盤 | 股漲為全面risk-off的反證 |
| 亞洲股市 | 台灣官方收盤已核；其他主要市場同步值不足 | 10/5 | 不宣稱亞洲全面同向 |

美債與美股分別參考[Reuters 10/2](https://www.marketscreener.com/news/stocks-climb-after-weak-us-jobs-data-but-bonds-resume-selling-ce785ddbd88ff221)、[AP收盤](https://apnews.com/article/48e9066481cba91a5d7c6688aa74a5cd)。日本歷史表與[截點前Reuters](https://m.economictimes.com/markets/bonds/japans-30-year-bond-yields-hit-record-high-ahead-of-pms-remarks/amp_articleshow/134685174.cms)支持超長端偏弱，但盤中高點與收盤不可混用。

### 能源五項核心輸入
| 項目／單位 | current／可比前值 | 1D／5D／7D／20D | 20D區間／百分位 | 季節基準／時效 |
|---|---|---|---|---|
| lng_jkm，USD/MMBtu | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | assessment時間未核 |
| gas_ttf，EUR/MWh | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | 歷史近月合約未核 |
| oil_brent，USD/bbl | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | 索引早盤數字與更新後全文不同 |
| oil_wti，USD/bbl | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | 同上；不混用期貨合約 |
| eu_gas_storage，% full | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | AGSI+截點及五年同期基準未取得 |

JKM、TTF、油價、儲氣均已嘗試搜尋／讀取歷史來源。油價Reuters索引有早盤觀察，但全文已改成截點後收盤；本件不把無法固定版本的報價升格為正式current。[AGSI+](https://agsi.gie.eu/)、[Reuters更新頁](https://live.euronext.com/en/financial-news/oil-slips-rising-mideast-crude-exports-g7-stocks-release)

> 價格門檻A／B、廣度C、突破D、儲氣E與供給中斷F均為UNKNOWN。尚未量化受影響流量，故供給事件只能當催化因素；沒有「未觸發能源警報」的結論。

反向證據逐項檢查結果：需求破壞、季節性、庫存（Inventory）、運價、供給恢復與期貨曲線均缺少截點前可比完整序列。不得以任何一項假說，取代價格或庫存確認。

## 證據與反向證據（EVIDENCE VS COUNTER-EVIDENCE）
| 假說 | 支持證據 | 反向證據 | 本件取捨 |
|---|---|---|---|
| 台股買盤改善 | 外資買超、指數與期貨上漲 | 跌家數較多、小型股近持平 | 保留戰術改善，附集中度警戒 |
| 全球長端供給風險擴散 | 日本30Y升、美債前日高檔 | 日本10Y降、美股前日漲 | 不升級全球系統風險 |
| AI基本面支持行情 | TSMC營收及SEMI設備成長 | 公司獲利、訂單與存貨全套不足 | 支持背景，不推導單股合理價 |
| 通膨壓力解除 | 核心PCE月度增速溫和 | headline仍高、能源資料缺口 | 不宣布通膨勝利 |

原文「法國利差約150bp」的即時新變化及獨立來源未完成重驗，本件撤除作為觸發依據。多家媒體轉載同一Reuters稿只算一個來源，不以轉載數量增加信心。

## 台灣傳導（TAIWAN TRANSMISSION）
| 傳導面 | 機制 | 期限 | 確認與反證 |
|---|---|---|---|
| 估值 | 長端折現率影響AI與半導體高久期股票 | 即時 | 若利率穩定、獲利上修，壓力可抵銷 |
| 外需 | 台韓科技出口連接晶圓、封裝與伺服器訂單 | 數週至數月 | 出口金額須拆單價，不能全視為出貨量 |
| 金融條件 | 外資流量支持大型股；銀行信用另需驗證 | 即時至數月 | 現貨流入不能證明融資利差改善 |
| 匯率 | 台幣波動同時影響出口換算及進口能源成本 | 即時 | USDTWD截點缺失，不能量化淨效應 |
| 日本／中國 | 超長債與中國需求分別放大估值／訂單敏感度 | 1–3季 | 日本中端債穩、中國小企業偏弱 |
| LNG／電力 | 能源成本可能傳至電力密集製程與運輸 | 數週至1–3季 | 缺價格、費率政策與公司避險資料，不能推導單股輸贏 |

台灣8月出口年增41.0%，9月資料在本截止時尚未公布；韓國9月半導體出口年增262.8%，同時非半導體僅較溫和成長，供應鏈（Supply Chain）不能一概而論。[財政部](https://www.mof.gov.tw/singlehtml/384fb3077bb349ea973e7fc6f13b6974?cntId=61f5437eabfe44bcbe442a02eaeea30a)、[韓國MOTIR](https://english.motir.go.kr/eng/article/EATCLdfa319ada/2743/view)

外銷訂單（Export Orders）已檢查經濟部8月發布索引，完整數值未提取；WSTS已檢查預測更新時程，未以舊年度預測冒充current。TSMC ADR對現股、SOX對台灣半導體的同時點匯率換算均UNAVAILABLE。

## 產業／股票敏感度（INDUSTRY / EQUITY SENSITIVITY）
| 環節 | 需求／估值機制 | 主要反證 | 下一核驗 |
|---|---|---|---|
| 晶圓／先進封裝 | AI營收支持需求；長端利率影響估值 | 營收非訂單能見度或毛利保證 | 交期、先進製程產能、前瞻指引（Guidance） |
| 記憶體 | 伺服器需求與供給配置支撐合約價 | 消費端BOM成本與終端需求受壓 | 現貨／合約價、位元出貨與庫存 |
| 伺服器／PCB／散熱電源 | 雲端資本支出傳至零組件 | 客戶集中、備料及產能利用風險 | 訂單、毛利、現金流與驗收時程 |
| 台塑化／航運／電力密集製造 | 能源與運費變化影響成本 | 售價轉嫁、避險與電價政策可抵銷 | 實際採購及公司披露 |

[TSMC8月公告](https://pr.tsmc.com/schinese/news/3340)與[SEMI設備數據](https://www.semi.org/en/semi-press-release/global-semiconductor-equipment-billings-increased-23-percent-year-over-year-in-q2-2026-semi-reports)是需求背景；[TrendForce9/30](https://www.trendforce.cn/presscenter/news/20260930-13257.html)是合約價預測，並非已實現季報。未取得同版本公司訂單、庫存、毛利、資本支出及指引全套，不作個股獲利保證。

## 市場週期 vs 基本面週期
市場週期（Market Cycle）當日由資金與權值定價帶動；基本面週期（Fundamental Cycle）則取決於數月訂單及產能。兩者暫時同向不代表未來報酬無風險，也不能因廣度不足就宣稱AI需求轉折。

國發會8月領先指標月增0.51%，景氣分數41持平，屬已發布的實體週期背景。官方景氣紅燈不等於本研究的金融風險RED。[國發會](https://www.ndc.gov.tw/nc_332_40495)

## 分類與風險燈號變化（CLASSIFICATION & RISK LIGHT DELTA）
- **本件分類**：UNKNOWN → TACTICAL；本件風險燈號UNKNOWN → YELLOW，信心中等。
- **比較限制**：原稿ORANGE只是歷史原稿記載，完整原始基準未回收；本件不宣稱當時曾由ORANGE降為YELLOW。
- **未達制度轉折**：沒有至少兩族持續共振、同步跨資產確認及原核心反證失效。信用與融資缺口更不允許宣稱REGIME_SHIFT。
- **觸發依據**：盤後新增披露顯示買盤改善與集中度分歧，足以形成台灣層戰術警報；觸發報告不等於升級Risk Light。

## 情境矩陣（SCENARIO MATRIX）
| 情境 | 所需觀察 | 市場含意 | 台灣含意 |
|---|---|---|---|
| 分化延續 | 大型股強、廣度弱、長端未惡化 | 集中行情，非全面risk-on | 避免只用指數推斷個股 |
| 改善擴散 | 廣度轉正、外資買盤延續、利率穩 | ↗ 改善，可提高趨勢信心 | 更多產業參與；仍驗證獲利 |
| 風險擴散 | 長端與信用同步惡化、流出且股跌 | ↘ 惡化，進入升級評估 | 估值與匯率壓力放大 |
| 成長轉弱 | 訂單與出口量降、金融條件惡化 | 降息預期未必利多 | 盈利修正可能大於折現好處 |

未賦予機率：資料不足以支持精確情境機率，避免偽精準。

## 下一確認條件（NEXT CONFIRMATION）
1. 逐日核對外資現貨、期貨與股票廣度是否同向延續，避免單日噪音升格趨勢。
2. 用同時點UST／JGB、實質利率、美元基差與信用利差，區別折現率壓力與融資衝擊。
3. 取得JKM及TTF assessment日期、油價合約、儲氣同期五年基準，重算1D／5D／7D／20D。
4. 檢查當時尚待公布的美國服務業數據及台灣9月出口，不能使用其後結果倒灌本件。
5. 若廣度改善且利率壓力解除，撤回集中度警戒；若買盤反轉且信用轉弱，撤回資金流改善方向。

## SOURCE AUDIT
- Coverage cutoff: 2026-10-05 15:39:21 Asia/Taipei. Reconstruction: 2026-10-09 13:00 Asia/Taipei. 原件保留，這是新的回溯研究物件。
- 高影響價格／廣度：TWSE日期指定歷史表；中央社13:59:31、Newtalk15:20發布。歷史API的原始發布鐘點、首發版本不可得，數值差異已揭露。
- 日本利率：Japan Bond Trading歷史日表與Reuters03:44 UTC發布相互確認超長端壓力；日表精確上架時間未知，不把日值當當時逐筆成交。
- 歐元：Reuters04:56 UTC發布。美股及美債採10/2已完成的交易日來源，不冒充10/5即時報價。
- 官方低頻來源：BEA9/30、BLS10/2、Fed9/16、H.4.1 10/1、H.8 10/2、NDC9/29、NBS9/30、MOTIR10/1、財政部9/9、TSMC9/10、SEMI9/3。各連結置於相關正文。
- 未完整提取來源：[Fed H.8](https://www.federalreserve.gov/releases/h8/20261002/)、[FRED信用利差](https://fred.stlouisfed.org/series/BAMLH0A0HYM2)、[NY Fed SOFR](https://www.newyorkfed.org/markets/reference-rates/sofr)、[經濟部外銷訂單](https://www.moea.gov.tw/Mns/dos/content/ContentLink.aspx?menu_id=9423)、[WSTS](https://www.wsts.org/61/Forecasts)、AGSI+。
- TWSE外資歷史API讀取回傳HTTP 307；TAIFEX頁雖可讀，未提取到對應日表。外資精確數字保留次級來源等級，不宣稱官方流量已讀回。
- 來源限制：更新後Reuters油價頁、晚於截止的ISM、當日美股收盤與後續文章均不參與當時判斷。原稿未經重驗數字沒有自動繼承。
- 完整內部研究保留12領域、21 canonical signals的變化、current/prior/consensus/revision、速率、持續性、廣度、市場反應、機制、跨資產、證據、反證、台灣傳導、嚴重度、信心、下一確認與失效條件；不可得均明記。

## 結論（BOTTOM LINE）
> 台股資金流改善值得記錄，行情集中也值得警戒。當時證據支持戰術性分化，無法證成全球融資危機；能源與信用資料不足必須保留未知，而不是被寫成安全訊號。

本件為歷史研究補驗，非即時交易建議；研究判斷與正式檔案保存驗證分開。
<<<REPORT_END>>>
