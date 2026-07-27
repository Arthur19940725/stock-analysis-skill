# Stock Analysis Skill

一个面向 AI Agent 的证券研究 skill，用于分析股票、ETF、行业轮动、财报、股息、技术面、风险、期权与宏观市场。

它的目标不是生成“听起来合理”的投资结论，而是把研究组织成一套可核验、可复算、可证伪的决策流程。

## 如何使用

将本仓库复制到 Agent 的 skills 目录，例如：

```text
~/.agents/skills/stock-analysis/
```

然后在支持 skills 的 Agent 中直接描述任务：

```text
使用 stock-analysis 全面分析 AAPL，持有期 12 个月。
使用 stock-analysis 分析 NVDA 的基本面与估值。
使用 stock-analysis 给出 SPY 的技术面、支撑位和风险。
使用 stock-analysis 设计一个最大损失有限的期权策略。
```

也可以显式调用：

```text
$stock-analysis 分析 MSFT 是否值得买入
```

完整分析前，建议提供 ticker、交易所、持有期、基准、风险承受能力和当前持仓状态。缺失信息会按 `references/research-protocol.md` 的默认规则处理并明确披露。

## 工作原理

Skill 先验证证券身份、价格时间、币种和数据来源，再按任务选择对应框架。完整单股研究遵循有向依赖：

```text
宏观与行业
→ 经营、财务与催化剂
→ 条件估值与市场校验
→ 风险审计与压力测试
→ 交易执行与最终评级
```

核心机制：

- **Source-first**：优先监管文件、交易所公告、公司 IR 和官方数据。
- **Evidence labels**：区分事实 `[F]`、共识 `[C]`、估计 `[E]`、假设 `[A]`、推导 `[D]` 和未知 `[U]`。
- **Data gates**：数据不足时自动降低结论精度，不编造价格、指标、共识或期权报价。
- **Scenario valuation**：用熊/基/牛三情景计算预期总回报、压力损失和回报覆盖。
- **Deterministic rating**：最终评级由 `scripts/decision_math.py` 按固定阈值计算，避免为了叙事手工调整结论。
- **Falsifiable thesis**：每个核心论点都要求支持证据、最强反证和失效条件。

## 目录

```text
stock-analysis/
├── SKILL.md                  # Skill 入口与路由
├── frameworks/              # 研究总控及 10 个专项框架
├── references/              # 数据协议、评级模型与输出规范
└── scripts/
    ├── decision_math.py      # 确定性评级计算
    └── test_decision_math.py # 边界与降级测试
```

运行测试：

```powershell
python scripts/test_decision_math.py
```

## 说明

本项目仅供一般信息与研究用途，不构成个性化投资、法律或税务建议。市场数据具有时效性，任何结论都应结合最新的一手资料复核。
