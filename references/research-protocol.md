# 统一研究协议

## 输入契约

把可得字段标准化为下列结构。缺失字段按默认规则处理，并在输出开头披露。

```yaml
security:
  ticker: ""                     # required
  exchange: ""                   # required
  company_name: ""
  security_type: "common_stock"  # common_stock / ADR / REIT / BDC / ETF / other
  country_of_listing: ""
  reporting_currency: ""

research:
  analysis_date: ""              # 空白时使用当前日期并写明
  price_as_of: ""                # 历史时点不得使用后来公开的信息
  horizon_months: 12
  base_currency: ""
  modules: "ALL"
  depth: "standard"              # quick / standard / deep
  known_thesis: ""
  known_questions: []
  user_data: []

investor:
  mandate: "long_only"           # long_only / long_short / income / trading / hedging
  benchmark: ""
  minimum_required_return: 0.10
  active_return_premium: 0.03
  position_status: "new"         # new / owned / watchlist / short
  position_weight: null
  cost_basis: null
  risk_tolerance: "medium"
  max_acceptable_drawdown: null
  constraints: []

scenario_assumptions:
  user_probabilities: null
  tax_rate: null
  fx_assumption: null
  risk_free_rate: null
  equity_risk_premium: null
  terminal_growth: null

options:
  enabled: false
  objective: ""
  max_loss: null
  contract_budget: null
  shares_held: 0
  allowed_structures: []
  prohibited_structures: ["undefined_risk"]
  preferred_expiry_window_days: null
```

默认 12 个月持有期、10% 最低绝对回报和 3 个百分点主动回报溢价。基准缺失时选择主要上市市场宽基指数，另列行业 ETF 只作次级比较。基础币种缺失时使用证券报价币种。不得机械套用固定情景概率。

## 身份与点时性

先验证 ticker、交易所、证券类型、普通股/ADR/REIT/ETF/合约属性、报价币种、股类和 ADR 比例。遇到同名 ticker、多市场上市或现货/衍生品歧义时，先解决标的身份。

历史 `price_as_of` 模式只使用当时已经公开的信息。无法取得点时数据时，标记“无法完成无前视偏差的历史复盘”，不得使用后来财报、修订宏观数据、当前指数成分或当前共识倒填。

每个市场数字记录：

- 数值、单位与币种；
- 统计期间与发布日期；
- 报价/快照时间和时区；
- 来源与访问日期；
- 是否盘中、延迟、复权或估计。

不得把不同时间的股价、IV、利率、盈利预测和期权链拼接成同步快照。

## 来源优先级

1. 监管申报、交易所公告、公司正式财报/业绩稿/IR、电话会原文、债券契约、官方宏观和监管数据。
2. 交易所、指数公司、产品发行人、评级机构、同行正式披露和有可追溯方法的行业数据。
3. 可靠财经媒体、券商公开摘要和聚合行情。
4. 搜索摘要、论坛、社交媒体和无日期转载，仅作寻找原始来源的线索。

公司管理层是公司事实和正式指引的一级来源，但对长期市场空间、竞争地位和自身预测不是中立来源；为这些判断寻找外部验证。

## 事实标签与证据账本

使用：

- `[F]` 已核验事实；
- `[C]` 外部共识/市场预期；
- `[E]` 分析估计；
- `[A]` 假设；
- `[D]` 由已列数据推导；
- `[U]` 无法核验/不可得。

标签不能替代引用。把改变评级的核心主张编号为 `K01…`，来源编号为 `S01…`。

| Claim ID | 可证伪主张 | 类型 | 来源 | 截止日 | 最强反证/冲突 | 模型影响 | 状态 |
|---|---|---|---|---|---|---|---|
| K01 |  | F/C/E/A/D/U | Sxx |  |  |  | 支持/混合/反对/未知 |

| Source ID | 标题/发布者 | URL | 发布日 | 访问日 | 支撑内容 |
|---|---|---|---|---|---|
| S01 |  |  |  |  |  |

至少建立 3—5 条核心论点。并列报告冲突来源并解释口径、时间或定义差异。重复转载同一原始消息不算独立交叉验证；搜索不到只能标 `[U]`。

## 财务口径

- 分列 GAAP/IFRS 与 adjusted 指标，指出 SBC、重组、收购摊销、资产处置和一次性项目。
- 写明 FCF 公式；默认 `经营现金流 - 资本开支`，但银行/保险不得套用工业企业 FCF。
- REIT 使用 FFO/AFFO；银行使用 P/TBV、ROE、CET1、NIM、资产质量与流动性；保险使用 P/B、偿付能力和综合成本率。
- 处理拆股、稀释股数、期权/可转债、ADR 比例、币种、少数股权和企业价值到股权价值。
- 把现金股息计入持有期现金分配；把回购通过净股数和每股价值体现，禁止重复加入总回报。
- 负利润、周期峰值或重大一次性项目下不机械使用 P/E。

## 能力降级

| 缺失能力/数据 | 必须执行 | 禁止输出 |
|---|---|---|
| 无专业终端 | 使用正式文件与可访问的可靠数据，披露来源层级 | “终端一致预期” |
| 无点时数据库 | 披露前视偏差，改为待执行验证方案 | 历史共识、成分股或点时倍数的伪数据 |
| 无代码执行器 | 只做可展示、可人工复核的计算 | 声称完成回归、蒙特卡洛或回测 |
| 无完整价格序列 | 给数据清单、公式和有限观察 | RSI、MACD、beta、波动率、回撤的猜测 |
| 无同步期权链 | 给参数化结构、选链规则与刷新清单 | 具体权利金、Greeks、胜率和可执行合约 |
| 无可靠共识 | 使用正式指引和透明自建估计 | 把无日期聚合值写成当前共识 |
| 无资金流 | 使用相对强弱等代理并明确区别 | 把成交量称为机构净流入 |

## 研究预算与停止规则

- `quick`：最多 8 个主要来源、1 次冲突复核。
- `standard`：最多 20 个主要来源、2 次冲突复核。
- `deep`：最多 40 个主要来源、3 次冲突复核。

预算耗尽仍无法核验关键数据时停止搜索，报告已查范围、未解决项和对结论的影响。每次重试必须基于新证据或不同来源，不重复搜索同义关键词。

## HANDOFF 规则

每个模块只输出本模块能支持的证据、结论、反证和 HANDOFF，不单独给最终股票评级。HANDOFF 中的数值必须包含：

```text
value | unit | currency | period | as_of | [F/C/E/A/D/U] | Source ID/公式
```

遇到模块冲突时使用：

```text
冲突 ID：X01
模块 A：结论、来源、日期
模块 B：结论、来源、日期
冲突类型：口径 / 时间 / 事实 / 假设 / 模型
优先规则：更高来源层级；同层级时更近且口径匹配
未解决部分：
对 ETR / SL / ECS / 评级的影响：
```
