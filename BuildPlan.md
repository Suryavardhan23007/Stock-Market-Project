Repo layout (reuse existing .env, .venv, infrastructure/ DB — don't recreate):

main/
├─ core/                    # shared across ALL strategies
│  ├─ data/                 # 5Paisa client, 6-mo windowed backfill, DB I/O
│  ├─ panel/                # cross-sectional bar alignment
│  ├─ features/             # shared feature library
│  ├─ labeling/             # triple barrier
│  ├─ backtest/             # engine + cost model
│  ├─ execution/            # broker adapter (backtest/paper/live modes)
│  ├─ portfolio/            # neutral construction + sizing
│  └─ registry/             # strategy interface + results store
├─ strategies/
│  └─ s1_xsec_relstrength/  # THIS build (later: s2_…, s3_…)
├─ dashboard/               # shared UI, reads results store
└─ infrastructure/          # existing DB config

The linchpin is a single Strategy interface in core/registry/ (methods like build_features, label, fit, predict, construct_portfolio). Every strategy implements it, so the backtester, paper harness, and dashboard are written once and all of S1–S6 plug in. Backtest and paper must share one signal→portfolio code path to avoid train/serve skew.

Phase 0 — Scaffolding & contracts. Create core/ + strategies/s1_xsec_relstrength/ + dashboard/. Define the Strategy ABC, config schema (YAML per strategy), and the results-store tables (trades, equity, metrics, run metadata) in the existing DB. No logic yet — just the skeleton everything else slots into.

Phase 1 — Data ingestion (6-month windowed). 5Paisa Xstream client reading creds from existing .env. Backfill loop that walks history in ≤6-month windows for all 14 constituents (1-min OHLCV) until exhausted; update Nifty50/Sensex/Bank Nifty index OHLC to latest. Idempotent upserts, gap detection, resume-on-failure. Bank Nifty is the neutrality benchmark; Nifty50/Sensex become optional market-factor features.

Phase 2 — Panel construction & QA. Align all 14 names to one 1-min session grid (9:15–15:30), handle missing bars/holidays, validate OHLC integrity, fix corporate-action adjustments, freeze the point-in-time constituent list (survivorship). Output = clean time × stock × OHLCV panel.

Phase 3 — Cross-sectional features. Per-stock features (RSI 7/9, momentum, realized vol, VWAP deviation, distance-to-rolling-high/low, volume) on 20-min rolling normalization, then cross-sectional z-score/rank each bar so the model learns relative, not absolute, behavior. All PIT-safe.

Phase 4 — Labeling. Target = forward return vs equal/weighted-basket return over 15–30 min, passed through triple barrier with vol-scaled (EWMA) barriers, asymmetric upper:lower (e.g. 2:1). Emit purge/embargo intervals for leakage-free CV.

Phase 5 — Pooled ranker. LightGBM trained pooled across all 14 names, expanding-window walk-forward with purge + embargo, stock-ID/rank features included. Output = per-bar cross-sectional scores. Config-driven hyperparams; SHAP diagnostics.

Phase 6 — Market-neutral portfolio. Scores → long top-k / short bottom-k, weights set to net≈0 and beta-neutral vs Bank Nifty, gross-leverage cap, per-name limits, rebalance cadence. Pure ranking→positions mapping, no execution yet.

Phase 7 — Meta-labeler (toggle). Secondary act/skip classifier on primary signals with triple-barrier feedback, behind a config flag. Backtest runs both ways; keep it on only if OOS Sharpe/precision improves.

Phase 8 — Backtest + cost model. Walk-forward OOS backtest with a real Indian-intraday cost model (brokerage, STT, exchange, GST, stamp, slippage/impact, short borrow). Metrics: Sharpe, hit rate, expectancy, turnover, drawdown, capacity, cost drag. This is where S1's edge is confirmed or killed.

Phase 9 — Paper-trading harness. Session-scheduled loop pulling latest bars, reusing the exact Phase 5–7 code path, simulated fills via the paper-mode broker adapter, positions/PnL written to the results store.

Phase 10 — Shared dashboard. Reads the results store; per-strategy tabs; equity curve, metrics table, live paper positions, trade log, feature/model diagnostics, and a side-by-side compare view (ready for S2–S6).

Phase 11 — Registry & promotion. Register each strategy's backtest + paper results, compare, and gate a manual "promote to live" switch — the workflow you'll use to pick the deployed algorithm.
