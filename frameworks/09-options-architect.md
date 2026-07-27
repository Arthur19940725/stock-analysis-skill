# 09 · 定义风险期权策略

**触发：** 期权、options、看涨、看跌、covered call、cash-secured put、价差、iron condor、Greeks。

## 输入

核验标的与主交易所、方向/区间、期限、最大损失、持股数量、是否接受指派、账户权限、波动率观点，以及是否跨越财报/除息日。

## 可执行数据闸门

只有取得与标的价同步、带时间戳的双边期权链时，才给具体 strike、expiry 和权利金。每条腿必须有：

```text
buy/sell | call/put | expiry | strike | bid | ask | mid
quantity | actual multiplier | volume | open interest | IV
American/European | settlement | quote timestamp/delay
```

要求 `bid > 0`。单边报价、错时链、零 bid、异常价差、非标准调整合约或缺少关键字段时，标“仅参数化/不可执行”。

## 策略与计算

1. 从备兑看涨、现金担保卖权、牛/熊垂直价差、日历、铁鹰和其他最大损失封顶结构中选一个主策略，并给“不交易期权”的基准选项。
2. 默认禁止裸卖 call 和损失不封顶结构。
3. 用逐腿权利金、数量和实际 multiplier 计算初始现金流。
4. 独立复算最大收益、最大损失、全部盈亏平衡和到期分段损益。
5. 把 mid 标为理论价，同时给保守成交成本范围；佣金、交易所和指派费用另列。
6. 分开到期损益与到期前市值变化。
7. 给 Greeks 的模型、估值时间和单位。
8. 不把 Delta 直接称为盈利概率。无经校准样本外真实世界模型时写“真实世界盈利概率=不可得”；风险中性结果明确标模型隐含。
9. 单列提前行权、除息前指派、pin risk、Gamma、Theta、IV、流动性、滑点和跳空。
10. 用可观察条件定义止盈/止损、剩余期限、标的失效位、IV、滚动/指派和事件后处理。
11. 股票论点 NR 或存在关键否决项时，除保护已有仓位外不使用杠杆方向策略。

无合格链时只给适用结构、DTE/Delta/行权价选取规则、必要字段和计算步骤。

## 输出

顶部：

```text
数据状态｜方向｜策略｜到期｜理论成本/信用｜最大收益｜最大损失｜盈亏平衡｜关键风险｜刷新要求
```

HANDOFF：`chain_status`、`timestamp`、`underlying_price`、`implied_move`、`term_structure`、`skew`、`liquidity`、`strategy_status`、`strategy`、`management_plan`、`assignment_and_dividend_risk`、`refresh_requirements`。
