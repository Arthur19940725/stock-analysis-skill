---
name: stock-analysis
description: This skill should be used when the user asks to analyze this stock, find a target price or buy zone, review fundamentals or technicals, assess risk/earnings/dividends, screen stocks, analyze sector rotation, build an ETF portfolio, design an options strategy, or analyze the macro market; also for Chinese requests such as "分析这只股票", "给出买入区间或目标价", "做基本面/技术面/风险/财报/股息分析", "筛选股票", "分析板块轮动", "构建 ETF 组合", "设计期权策略", "分析宏观市场"; or when they provide a stock ticker, security, ETF, portfolio, earnings event, or investment thesis that requires source-backed market research and an actionable decision.
---

# Stock Analysis

把股票、ETF、组合、板块、期权与宏观请求转换为可核验、可复算、可证伪的研究结论。围绕一个决策问题组织完整单股研究：

> 在指定持有期内，以当前可验证价格持有该证券，其情景加权总回报是否超过要求回报，并足以补偿永久损失、事件风险和证据不确定性？

## 先选择运行模式

| 用户意图 | 运行模式 | 加载文件 |
|---|---|---|
| “全面分析”“是否值得买”“目标价”“完整投资报告” | 单股总控 | `references/research-protocol.md`、`references/decision-model.md`、`frameworks/00-thesis-driven-research.md`、`references/output-quality.md` |
| “基本面”“估值”“商业模式”“护城河” | 专项研究 | `references/research-protocol.md` + `frameworks/01-coverage-memo.md` |
| “技术面”“买入区间”“支撑/阻力”“RSI/MACD” | 专项研究 | `references/research-protocol.md` + `frameworks/02-technical-panel.md` |
| “风险”“回撤”“压力测试”“对冲” | 专项研究 | `references/research-protocol.md` + `frameworks/03-risk-framework.md` |
| “财报”“业绩”“EPS”“guidance” | 专项研究 | `references/research-protocol.md` + `frameworks/04-earnings-analyzer.md` |
| “股息”“分红”“收益率”“DRIP” | 专项研究 | `references/research-protocol.md` + `frameworks/05-dividend-analyzer.md` |
| “板块”“轮动”“行业配置” | 专项研究 | `references/research-protocol.md` + `frameworks/06-sector-rotation.md` |
| “筛选”“量化”“多因子”“Top 10” | 专项研究 | `references/research-protocol.md` + `frameworks/07-quant-screener.md` |
| “ETF 组合”“资产配置”“再平衡”“定投” | 专项研究 | `references/research-protocol.md` + `frameworks/08-etf-portfolio.md` |
| “期权”“价差”“covered call”“iron condor” | 专项研究 | `references/research-protocol.md` + `frameworks/09-options-architect.md` |
| “宏观”“利率”“通胀”“美联储”“市场状态” | 专项研究 | `references/research-protocol.md` + `frameworks/10-macro-outlook.md` |
| 财报/公告后更新、持仓复核 | 增量更新 | 原研究结论 + `frameworks/00-thesis-driven-research.md` 的增量流程 |

命中多个专项时，只加载真正改变决策的文件。完整单股研究不得把多个 framework 并行生成后直接拼接；严格按总控依赖链执行。

## 输入核验

先核验证券身份、主交易所、证券类型、报价币种、分析截止时间和持有期。遇到会实质改变结论的歧义时，只问一个最关键问题并停止；否则显式列出默认值后继续。

至少取得或可靠核验：

- `ticker` 与 `exchange`；
- 当前价格 `P0`、币种、价格时间戳和来源；
- 最近正式财务披露及发布日期；
- 用户任务类型和期望持有期。

完整单股评级还需要基准、最低要求回报、三情景价值桥、风险压力情景和证据评分。输入字段与默认值见 `references/research-protocol.md`。

## 取证与数据纪律

1. 优先读取用户提供的文件、模型与链接；把用户假设与外部事实分开。
2. 优先监管申报、交易所公告、公司 IR、正式财报、官方宏观数据和产品发行人页面。
3. 再使用有方法说明的可靠数据源；财经媒体和聚合行情只作补充或价格来源。
4. 把搜索摘要、论坛和社交媒体仅作为寻找原始资料的线索。
5. 给每个会改变结论的市场数字附 `as of`；不得把错时价格、共识、利率、IV 或财务数据伪装成同步快照。
6. 先解析精确标的再调用行情工具。验证市场、证券类型、合约/现货属性与币种，避免同名 ticker 错配。
7. 若当前环境没有某个特定 MCP，直接使用可用的行情连接器、交易所/发行人页面或可靠网页；不要因固定工具名不存在而停止。
8. 在可访问来源全部失败后才向用户索取当前价。不得凭记忆估算当前价、估值倍数或期权报价。

对关键事实使用 `[F]`，外部共识 `[C]`，分析估计 `[E]`，假设 `[A]`，计算推导 `[D]`，无法核验 `[U]`。使用 `K01…` 标识可证伪主张，使用 `S01…` 标识来源。

## 数据闸门与降级

缺失数据时降低输出精度，不补造数字：

- 无完整价格序列：不给 RSI、MACD、波动率、beta 或最大回撤，只列所需 OHLCV、参数和观察计划。
- 无点时共识：不用今天的网页数字倒填历史预期，改用公司指引与透明自建估计。
- 无同步双边期权链：只给参数化结构和取链清单，不给具体合约、权利金、Greeks、胜率或“可执行”标签。
- 无历史点时股票池/退市样本/真实发布日期：不声称完成回测，不报 Alpha、Sharpe 或胜率。
- 无资金流数据：不把成交量、持仓或 ETF 价格变化称为机构净流入。
- 无可靠情景概率或价值桥：输出条件估值或暂不评级，不套用固定 20/60/20。

## 单股总控执行

加载 `frameworks/00-thesis-driven-research.md`，按以下有向依赖执行：

1. `M10 → M4`：确定宏观状态、基准、行业利润池与竞争约束。
2. `M4 → M1 → M8 → M3`：建立经营现实、现金回报与验证日历。
3. `M2-A → M5`：形成条件估值/反向估值草案，再用因子、盈利修正和价格隐含预期挑战。
4. `M7 → M2-B`：把风险回写到经营假设、估值参数、情景概率和压力情景，再形成最终目标价。
5. `M6 + M9 → 总控`：制定现货执行；仅在期权闸门通过时设计期权实施；最后统一计算评级。

只允许总控层给最终评级。各模块仅输出证据、反证、模型输入和 HANDOFF。若 M6/M9 揭示重大新风险，最多回查一次 `M7 → M2-B`；仍未解决则降低证据分或暂不评级。

## 确定性计算

把三情景、要求回报、证据分和否决项写入 JSON，调用：

```bash
python scripts/decision_math.py path/to/input.json
```

Forward slashes work with Python on Windows and Unix. On Windows you may also use `path\to\input.json`.

使用 `scripts/decision_math.py` 计算 `TR_s`、`ETR`、`EU`、`ED`、`PCR`、`SL`、`H`、`ECS` 与机械评级。禁止手工改变阈值以配合叙事。输入结构、公式和评级门槛见 `references/decision-model.md`。

专项任务若没有完整三情景和证据基础，只给该专项能支持的“技术倾向、风险状态、条件估值、候选清单或参数化结构”，不要冒充完整股票评级。

## 输出

默认用简体中文，保留 ticker、指标、机构名和行业术语的英文。短问题先给行动结论，再给依据和失效条件；完整研究使用 `references/output-quality.md` 模板。

所有行动建议至少包含：

- 数据截止时间与来源层级；
- 当前行动或观察状态；
- 触发/确认条件；
- 技术止损与基本面失效分别列示；
- 目标、风险回报与持有期；
- 数据缺口及其对结论的影响。

结尾添加：

> 本报告仅供一般信息与研究用途，不构成个性化投资、法律或税务建议。

## 资源索引

- `references/research-protocol.md`：统一输入、来源、同步、标签、降级与研究预算。
- `references/decision-model.md`：情景回报、证据评分、机械评级和脚本输入。
- `references/output-quality.md`：完整报告模板、检查清单、自动失败与更新纪律。
- `frameworks/00-thesis-driven-research.md`：十模块总控依赖、HANDOFF 和专项工作流。
- 专项框架（与上方路由表一致）：
  - `frameworks/01-coverage-memo.md`
  - `frameworks/02-technical-panel.md`
  - `frameworks/03-risk-framework.md`
  - `frameworks/04-earnings-analyzer.md`
  - `frameworks/05-dividend-analyzer.md`
  - `frameworks/06-sector-rotation.md`
  - `frameworks/07-quant-screener.md`
  - `frameworks/08-etf-portfolio.md`
  - `frameworks/09-options-architect.md`
  - `frameworks/10-macro-outlook.md`
- `scripts/decision_math.py`：确定性评级计算与输入验证。
- `scripts/test_decision_math.py`：核心边界与降级测试。
