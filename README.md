# Stock Analysis Skill

English | [中文速览](#中文速览)

## Overview

A source-first securities research skill for AI agents. It supports stocks, ETFs, sector rotation, earnings, dividends, technical analysis, risk, options, and macro research.

Its purpose is not to produce plausible-sounding investment conclusions. It organizes research into a verifiable, reproducible, and falsifiable decision process.

This README is English-first. The skill currently generates Simplified Chinese by default; add `Write the report in English` to a request when English output is required.

## Quick start

Copy this repository into the Agent's skills directory, for example:

```text
~/.agents/skills/stock-analysis/
```

Then describe the task in an Agent that supports skills:

```text
Use stock-analysis to analyze Apple Inc. (Nasdaq: AAPL) over a 12-month horizon. Write the report in English.
Use stock-analysis to review the fundamentals and valuation of NVIDIA Corp. (Nasdaq: NVDA). Write the report in English.
Use stock-analysis to assess the technical setup, support levels, and risks of SPDR S&P 500 ETF Trust (NYSE Arca: SPY). Write the report in English.
Use stock-analysis to design a maximum-loss-defined AAPL options strategy using a synchronized bid/ask chain. Write the report in English.
```

The prompts above demonstrate invocation syntax. They are not frozen datasets or reproducible investment cases.

The skill can also be invoked explicitly:

```text
$stock-analysis Analyze Microsoft Corp. (Nasdaq: MSFT) over a 12-month horizon. Write the report in English.
```

Before a full analysis, provide the ticker, primary exchange, holding period, benchmark, risk tolerance, and current position status when possible. Missing fields are handled under [`references/research-protocol.md`](references/research-protocol.md) and must be disclosed.

## How it works

The skill first verifies the security identity, price timestamp, currency, and data sources. It then selects the relevant framework. A full single-stock review follows this dependency chain:

```text
Macro and industry context
-> Operations, financials, and catalysts
-> Conditional valuation and market checks
-> Risk audit and stress testing
-> Execution plan and final rating
```

Core controls:

- **Source-first**: prefer regulatory filings, exchange notices, company investor relations, and official data.
- **Evidence labels**: separate verified facts `[F]`, consensus `[C]`, estimates `[E]`, assumptions `[A]`, derivations `[D]`, and unknowns `[U]`.
- **Data gates**: reduce precision when data is missing instead of inventing prices, indicators, consensus estimates, or option quotes.
- **Scenario valuation**: calculate expected total return, stress loss, and payoff coverage across bear, base, and bull cases.
- **Deterministic rating**: use [`scripts/decision_math.py`](scripts/decision_math.py) and fixed thresholds instead of changing a rating to fit a narrative.
- **Falsifiable thesis**: attach supporting evidence, the strongest counterevidence, and an invalidation condition to each core claim.

## Reproducible stock-analysis practice

This practice uses a public issuer, a fixed filing, and explicit verification steps. It is a frozen fundamental-data exercise, not a current recommendation.

### Research snapshot

| Field | Fixed value |
|---|---|
| Security | Apple Inc. common stock |
| Identifiers | Nasdaq: `AAPL`; SEC CIK `0000320193` |
| Research cutoff | 2025-10-31 16:00 ET (`America/New_York`) |
| Financial period | FY2025, 2024-09-29 through 2025-09-27 |
| Filing | Form 10-K filed 2025-10-31; accession `0000320193-25-000079` |
| Financial units | USD millions, except per-share data |
| Market-price rule | Retrieve the 2025-10-31 regular-session close separately and record its exact field definition |

### Public sources

| Source ID | Publisher and source | Publication / access date | What to verify |
|---|---|---|---|
| S01 | SEC, [filing detail for accession 0000320193-25-000079](https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/0000320193-25-000079-index.htm) | Published 2025-10-31; accessed 2026-07-31 | Issuer identity, form, filing date, report period, accession, and filing documents |
| S02 | SEC, [Apple FY2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm) | Published 2025-10-31; accessed 2026-07-31 | Audited financial statements, product and Services sales, EPS, and cash-flow line items |
| S03 | SEC, [Company Facts JSON](https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json) and [EDGAR API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) | Live API; accessed 2026-07-31 | Programmatic cross-check of standard US-GAAP facts; this is another representation of S02, not independent corroboration |
| S04 | Apple Investor Relations, [historical stock-price lookup](https://investor.apple.com/stock-price/default.aspx) and [FAQ](https://investor.apple.com/investor-relations/faq/default.aspx) | Dynamic; accessed 2026-07-31 | Historical price lookup; Apple states that the quote feed is supplied by Ticker Technologies and delayed by 20 minutes |
| S05 | Nasdaq, [AAPL historical quotes](https://www.nasdaq.com/market-activity/stocks/aapl/historical) | Dynamic; accessed 2026-07-31 | Historical OHLCV and the regular-session price field when the public feed is available |

### Verified facts and calculations

The following filing values were checked against S02. Standard entity-level facts were also reconciled to S03.

| Metric | FY2025 | FY2024 | Evidence |
|---|---:|---:|---|
| Total net sales | 416,161 | 391,035 | `[F]` S02/S03 |
| Services net sales | 109,158 | 96,169 | `[F]` S02 |
| Net income | 112,010 | 93,736 | `[F]` S02/S03 |
| Diluted EPS (USD/share) | 7.46 | 6.08 | `[F]` S02/S03 |
| Cash generated by operating activities | 111,482 | 118,254 | `[F]` S02/S03 |
| Payments for acquisition of property, plant, and equipment | 12,715 | 9,447 | `[F]` S02/S03 |

Reproducible derivations:

- Total net-sales growth = `416,161 / 391,035 - 1` = **6.43%** `[D]`.
- Services net-sales growth = `109,158 / 96,169 - 1` = **13.51%** `[D]`.
- FY2025 Services mix = `109,158 / 416,161` = **26.23%** `[D]`.
- FY2025 net margin = `112,010 / 416,161` = **26.92%** `[D]`.
- FY2025 free-cash-flow proxy = `111,482 - 12,715` = **USD 98,767 million** `[D]`.

The free-cash-flow proxy is the skill's default calculation of operating cash flow less purchases of property, plant, and equipment. It is not an Apple-reported GAAP line item.

### How to verify the practice

1. Open S01 and match `Apple Inc.`, CIK `0000320193`, Form 10-K, report date `2025-09-27`, filing date `2025-10-31`, and accession `0000320193-25-000079`.
2. In S02, find `Products and Services Performance`, `Consolidated Statements of Operations`, and `Consolidated Statements of Cash Flows`; reconcile the table above before calculating any ratio.
3. In S03, filter standard XBRL facts by `form=10-K`, `fy=2025`, `fp=FY`, `end=2025-09-27`, and `accn=0000320193-25-000079`. Useful concepts include:
   - `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax`
   - `us-gaap:NetIncomeLoss`
   - `us-gaap:EarningsPerShareDiluted`
   - `us-gaap:NetCashProvidedByUsedInOperatingActivities`
   - `us-gaap:PaymentsToAcquirePropertyPlantAndEquipment`
4. Do not take the last JSON array item without filtering: later filings and comparative periods can repeat the same fact. Verify Services sales in the S02 table because dimensional product data may not appear as an entity-level Company Facts value.
5. For the historical market price, query 2025-10-31 in S04 and S05. Record:

   ```text
   ticker | exchange | price field | value | currency | trading date |
   timestamp and timezone | delayed status | adjustment definition |
   source URL | retrieval time
   ```

6. Use the regular-session close for historical `P0`; do not silently substitute an adjusted close or an intraday/after-hours quote. If only one feed works, disclose that the price lacks a public cross-check. If neither feed works or a discrepancy cannot be resolved, label `P0` as `[U]` and do not issue a price target or final stock rating.
7. Keep all later information out of the frozen 2025-10-31 analysis to avoid look-ahead bias.

A reproducible prompt:

```text
Use stock-analysis to review Apple Inc. common stock (Nasdaq: AAPL;
SEC CIK 0000320193) using only information public by 2025-10-31
16:00 ET. Reconcile the FY2025 facts and calculations in the README
to sources S01-S03. Retrieve the 2025-10-31 regular-session price
from S04 and S05 when available and record its currency, timestamp,
delay, and adjustment definition. Disclose a missing cross-check; if
neither source works or they conflict, mark P0 as [U] and stop before
a target price or final rating. Write the report in English.
```

The verified snapshot supports a limited operating observation: Services grew faster than total sales in FY2025, while the stated free-cash-flow proxy was USD 98.767 billion. It does not, by itself, supply forecast scenarios, required return, benchmark-relative return, or a defensible buy/hold/sell rating.

## Repository layout

```text
stock-analysis/
├── SKILL.md                  # Skill entry point and routing
├── frameworks/              # Research controller and 10 specialist frameworks
├── references/              # Data protocol, rating model, and output specification
└── scripts/
    ├── decision_math.py      # Deterministic rating calculation
    └── test_decision_math.py # Boundary and degradation tests
```

Run the tests:

```bash
python scripts/test_decision_math.py
```

## Disclaimer

This project is for general information and research only. It is not personalized investment, legal, or tax advice. Market data is time-sensitive; recheck every conclusion against the latest primary sources before acting.

## 中文速览

这是一个面向 AI Agent、以证据和数据闸门为核心的证券研究 skill，覆盖股票、ETF、行业轮动、财报、股息、技术面、风险、期权与宏观市场。README 以英文为主；skill 当前默认输出简体中文，如需英文报告，请在任务中明确写入 `Write the report in English`。

安装时将仓库复制到 Agent 的 skills 目录，然后提供 ticker、主交易所、持有期、基准、风险承受能力和当前持仓状态。完整规则见 [`SKILL.md`](SKILL.md) 与 [`references/research-protocol.md`](references/research-protocol.md)。

上面的实践使用 Apple Inc.（Nasdaq: AAPL；CIK `0000320193`）FY2025 Form 10-K 的固定公开数据，并给出 SEC 原文、Company Facts、Apple IR 与 Nasdaq 行情的具体核验路径。财务事实与动态行情分开处理；若历史价格无法公开核验，必须把 `P0` 标为 `[U]`，停止输出目标价和最终评级。

本项目仅供一般信息与研究用途，不构成个性化投资、法律或税务建议。
