# 00 · 单股论点驱动总控

## 运行目标

围绕唯一问题组织研究：当前可验证价格下，情景加权总回报是否超过要求回报，并足以补偿永久损失、事件风险和证据不确定性。

先加载：

- `../references/research-protocol.md`
- `../references/decision-model.md`
- `../references/output-quality.md`

各模块只生成证据、反证、模型输入和 HANDOFF。只在总控层调用 `../scripts/decision_math.py` 生成最终评级。

## 依赖顺序

### 1. 外部约束：M10 → M4

使用 `10-macro-outlook.md` 的公司相关宏观部分确定宽基基准、行业代理、利率/汇率/商品/信用传导和基准回报 `BR`。

执行 M4 行业结构审计：

- 定义真正参与的细分市场、价值链与利润池，不停留在宽泛 GICS 标签。
- 估计市场增长、渗透率、供需、产能与周期位置，并分开 `[F]/[E]/[A]`。
- 建立 5—10 家口径匹配的可比公司；说明纳入和剔除理由。
- 用份额、价格实现、留存、单位成本、ROIC、渠道、网络或 IP 证据评价竞争优势。
- 选择宽基和行业 ETF/指数代理；ETF 不是完全对冲。
- 把行业增长、价格、份额、利润率与合理倍数区间传给 M1/M2。

```text
M4_HANDOFF:
industry_definition / cycle_phase / market_growth_range
pricing_environment / capacity_or_supply / company_share
peers / sector_proxy
constraints_for_M1: revenue_growth, pricing, margin, share
constraints_for_M2: multiple_range, cycle_adjustment
leading_indicators: metric, threshold, lag, source
risks_for_M7 / gaps
```

### 2. 经营现实：M4 → M1 → M8 → M3

使用 `01-coverage-memo.md` 建立业务活动到收入、利润、现金流和正常化每股指标的桥。把 M4 约束写入预测，不允许无限份额增长。

使用 `05-dividend-analyzer.md` 分开现金股息、毛回购、股票发行/SBC 和净回购。向每个情景提供从 `P0` 时间戳之后到持有期末的 `Cash_s`。

使用 `04-earnings-analyzer.md` 建立催化剂日历和事件矩阵。每个催化剂只能通过经营变量、估值实现时点或情景概率生效，不单独加分。

```text
M1_HANDOFF:
business_drivers / normalized_metric / revenue_base / margin_base
diluted_shares / cash / debt / net_debt / maturities
accounting_flags / thesis_claims / falsifiers

M8_HANDOFF:
dividend_status / payout / safety_score
cash_distribution_by_scenario
gross_buyback / issuance / net_buyback / share_count_effect
cut_triggers / gaps

M3_HANDOFF:
earnings_status / event_date / date_status
consensus_snapshot / analyst_estimates
catalysts: event, window, base_rate, threshold, model_effect
event_matrix / thesis_falsifiers / gaps
```

### 3. 初始价值与市场校验：M2-A → M5

在 `01-coverage-memo.md` 的估值部分先运行 M2-A：

- 选择一个主方法和至少一个交叉检查。
- 给出牛/基/熊经营—估值—每股目标价桥。
- 做反向估值：当前价格隐含的增长、利润率、倍数或折现率。
- 对两个关键变量做可复核敏感性。
- 只形成条件目标价，不给最终评级。

执行 M5 单股因子校验：

- 明确主要市场、行业/市值同组和 M4 peers。
- 在数据可得时检查价值、质量、增长、1/3/6/12 月动量、盈利修正、风险/流动性和拥挤代理。
- 数据齐备时默认权重为价值 20%、质量 25%、增长 15%、动量 15%、盈利修正 15%、风险/流动性 10%；调整前先解释并保持总和 100%。
- 只有样本、日期、公式和覆盖明确时报告分位。
- 缺失权重超过 30% 时不报综合分。
- 把“低估值但盈利下修”“高动量但基本面恶化”等冲突显式传给 M7/M2-B。
- 无点时样本时给待执行回测规范，不声称已验证。

```text
M2_A_HANDOFF:
current_price / methods / conditional_scenarios
reverse_valuation / sensitivity / key_assumptions / gaps

M5_HANDOFF:
universe / as_of / coverage
factors: raw_value, percentile_or_U, formula, weight, source
revisions / momentum / crowding
reverse_expectation_conflicts / alerts_for_M7
```

### 4. 反方审计与最终价值：M7 → M2-B

使用 `03-risk-framework.md` 审计所有模块：

- 建立风险登记册和传导链；
- 检查流动性、再融资、会计、稀释和持续经营；
- 设计独立于普通熊市的压力情景；
- 把风险回写到收入、利润率、现金流、折现率、倍数或概率；
- 给出关键否决项和论点确认/削弱/失效阈值；
- 检查重复计价。

随后运行 M2-B。输出每项 `M2-A 草案值 → M2-B 最终值 → 变化原因/风险 ID`，再形成最终牛/基/熊目标价与敏感性。

```text
M7_HANDOFF:
risk_register / liquidity / refinancing / accounting
independent_stress: assumptions, target_price, total_return
probability_adjustments / vetoes / falsifiers / unknowns

M2_B_HANDOFF:
primary_method / cross_check
scenarios: probability, operating_inputs, valuation_inputs, Ps, Cash_s
draft_to_final_changes / sensitivity / unresolved_dependencies
```

### 5. 执行与决策：M6 + M9 → 总控

使用 `02-technical-panel.md` 读取 M2-B 目标价，制定入场区、分批规则、技术止损、目标 1/2、有效期和跳空风险。把技术失效与基本面失效分开。

仅当 `options.enabled=true` 时使用 `09-options-architect.md`。无完整同步链时只给参数化结构；股票评级 NR 或存在未解决否决项时，除保护已有仓位外不使用杠杆方向表达。

若 M6/M9 发现会改变事件风险或估值的冲突，最多回查一次 `M7 → M2-B`。

把 P0、最终三情景、压力回报、证据分和否决项交给 `../scripts/decision_math.py`。逐字采用脚本输出的基础评级、降级原因和最终评级。

## 专项工作流

### 财报或重大事件增量更新

1. 用 M3 建立“新事实 vs 旧假设/共识”。
2. 把收入/利润/现金流路由 M1，把竞争路由 M4，把分红/融资路由 M8，把宏观路由 M10，把概率/否决项路由 M7。
3. 只重算受影响的 M2 情景和敏感性。
4. 更新 M6 跳空后的价格结构；刷新链后才更新 M9。
5. 重跑评级脚本，输出旧值到新值的归因。

### 财报前决策

按 `M3 → M9 → M6 → M1 → M7 → M2 → 总控` 执行。突出已定价预期、自建估计、四象限事件矩阵、跳空下最大损失和财报前/后动作。

### 风险审计

由 M7 主导读取 M1/M2/M3/M4/M8/M10。输出永久损失、最强反证、重复计价、独立压力、SL、否决项和降仓/退出/对冲阈值。

### 股息研究

按 `M8 → M1 → M7 → M2 → M10` 执行。检查正常化现金覆盖、资产负债表、股息削减情景和债券/ETF 机会成本。

### 快速筛查

使用 `M4 + M1 + M7 + 条件式 M2`，遵守 quick 预算。结果只能是“进入完整研究 / 观察 / 停止研究”，不得包装成正式评级。
