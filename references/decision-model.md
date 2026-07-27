# 情景回报、证据与评级模型

只在完整单股总控层生成最终评级。专项模块提供输入，不投票、不独立评级。

## 变量和公式

对 `s ∈ {bull, base, bear}`：

```text
P0      = 当前可验证价格
Ps      = 持有期末、除息口径目标价
Cash_s  = P0 时间戳之后至持有期末实际收到且未计入 Ps 的现金分配
p_s     = 情景概率

TR_s = (Ps - P0 + Cash_s) / P0
ETR  = Σ(p_s × TR_s)             且 Σp_s = 100%
EU   = Σ[p_s × max(TR_s, 0)]
ED   = Σ[p_s × max(-TR_s, 0)]
PCR  = EU / ED                   ED=0 时标 N/M
SL   = min(TR_bear, TR_independent_stress)
H    = max(minimum_required_return,
           benchmark_expected_return + active_return_premium)
```

无法可靠估计基准持有期回报 `BR` 时，令 `H=minimum_required_return`，并把相对基准判断标为未验证。

每个情景必须桥接：

```text
收入/业务量
→ 利润率/单位经济
→ EPS/FCF/AFFO
→ 倍数/折现率/资产价值
→ 股权价值
→ 稀释后每股目标价 Ps
→ 现金分配 Cash_s
→ 总回报 TR_s
```

股息与 `Ps` 必须采用互斥口径。回购、债务偿还和再投资不直接加入 `Cash_s`。

## 证据置信分 ECS

只从离散值中选择并逐项解释：

| 字段 | 可选值 | 依据 |
|---|---:|---|
| `source_quality` | 0 / 10 / 20 / 30 | 关键结论由线索/三级/二级/一级来源支撑 |
| `freshness_sync` | 0 / 8 / 14 / 20 | 过时错位/部分过时/多数当前/全部关键数据同步 |
| `critical_coverage` | 0 / 10 / 18 / 25 | 价格、盈利、资产负债表、估值、催化剂/风险覆盖 |
| `cross_validation` | 0 / 5 / 10 / 15 | 无/少量/多数/全部关键外部主张获独立验证 |
| `assumption_transparency` | 0 / 4 / 7 / 10 | 隐含/部分/多数/全部估计可追溯复算 |

`ECS` 为五项总和。A=80—100，B=65—79，C=50—64，D=0—49。ECS 衡量证据基础，不代表上涨概率，不进入预期收益计算。

## 数据闸门

满足任一条件即暂不评级 `NR`：

- `P0` 或价格日期无法核验；
- 最新正式财务披露不可得且无足够替代证据；
- 三情景无法由经营假设桥接到每股价值；
- 概率不合理或合计不为 100%；
- `ECS < 50`；
- 证券身份、股本、ADR 比例或币种存在重大未解决歧义。

## 基础评级

| 条件 | 基础评级 |
|---|---|
| `ETR ≥ H + 10pct` | 强力买入 |
| `H ≤ ETR < H + 10pct` | 买入 |
| `-5% ≤ ETR < H` | 持有/观察 |
| `-15% ≤ ETR < -5%` | 减持/弱于大盘 |
| `ETR < -15%` | 卖出/回避 |

临界值严格按表处理。

## 风险门槛和否决项

- 强力买入还需 `PCR ≥ 2.0`、`SL > -35%`、`ECS ≥ 75` 且无正面评级否决项。
- 买入还需 `PCR ≥ 1.3`、`SL > -50%`、`ECS ≥ 60` 且无正面评级否决项。
- 基础强力买入不满足强力门槛但满足买入门槛时，降为买入。
- 任何正面基础评级不满足买入门槛时，上限为持有/观察。
- 卖出/回避需 `ECS ≥ 70`；ECS 50—69 时改为“减持/回避新增仓位”。
- ECS 50—64 不得强力买入或高确信度卖出。

下列未解决事项限制正面评级；损失无法建模时直接 NR：

- 未来 12 个月持续经营或再融资实质不确定；
- 重大会计、审计、内控或重述风险；
- 可能造成生存性损失且无法建模的监管/诉讼；
- 流动性不足以按假设价格执行；
- 未入模的重大客户、产品或地区集中；
- 单一未验证关键假设在压力测试下造成永久损失。

## 脚本输入

调用 `scripts/decision_math.py`，百分比全部使用小数：

```json
{
  "current_price": 100,
  "scenarios": [
    {"name": "bear", "target_price": 70, "cash_distribution": 2, "probability": 0.20},
    {"name": "base", "target_price": 125, "cash_distribution": 2, "probability": 0.55},
    {"name": "bull", "target_price": 160, "cash_distribution": 2, "probability": 0.25}
  ],
  "minimum_required_return": 0.10,
  "benchmark_expected_return": 0.08,
  "active_return_premium": 0.03,
  "independent_stress_total_return": -0.40,
  "evidence": {
    "source_quality": 30,
    "freshness_sync": 20,
    "critical_coverage": 25,
    "cross_validation": 15,
    "assumption_transparency": 10
  },
  "data_gate_passed": true,
  "positive_rating_veto": false,
  "unmodelable_veto": false
}
```

脚本对概率、离散证据分、必要字段和数值范围做校验；校验失败时非零退出，不输出乐观默认值。
