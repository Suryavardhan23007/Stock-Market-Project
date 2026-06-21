# OI Intelligence Layer – Master Notes

## Current Status

Date: June 2026

Status: COMPLETE (Version 1)

Collection Status: ACTIVE

Collector Status: PRODUCTION READY

Archive Status: FUTURE-PROOF

Current Objective: DATA COLLECTION

Next Engineering Focus: NEWS INTELLIGENCE LAYER

---

# What is the OI Intelligence Layer?

The OI Intelligence Layer is a system that continuously collects option chain data and transforms it into market structure intelligence.

It does NOT predict the market by itself.

Instead, it measures:

* Institutional positioning
* Market conviction
* Dealer hedging pressure
* Support and resistance zones
* Volatility expectations
* Option flow behavior

The goal is to convert raw option chain data into machine-learning-ready features.

---

# What Raw Data Is Collected?

For both:

* NIFTY
* BANKNIFTY

The system archives:

## Contract Information

* Symbol
* Expiry Date
* Strike Price
* CE Scrip Code
* PE Scrip Code

## Option Prices

* CE Premium
* PE Premium
* CE Previous Close
* PE Previous Close

## Open Interest

* Call OI
* Put OI
* CE Change In OI
* PE Change In OI

## Volume

* Call Volume
* Put Volume

## Metadata

* Timestamp

All data is stored in PostgreSQL.

---

# OI Features Currently Implemented (Version 1)

## OI Velocity

Measures:

Rate of OI change.

Purpose:

Detects aggressive positioning.

Status:

Implemented

---

## OI Acceleration

Measures:

Rate of change of Velocity.

Purpose:

Detects sudden market participation shifts.

Status:

Implemented

---

## PCR

Measures:

Put OI / Call OI.

Purpose:

Market sentiment context.

Status:

Implemented

---

## PCR Percentile

Measures:

Relative PCR extremity.

Purpose:

Normalize sentiment across time.

Status:

Implemented

---

## IV

Measures:

Implied Volatility.

Purpose:

Expected future volatility.

Status:

Implemented

---

## IV Percentile

Measures:

Current IV relative to historical IV.

Purpose:

Volatility regime detection.

Status:

Implemented

---

## Call Wall

Measures:

Highest Call OI strike.

Purpose:

Potential resistance.

Status:

Implemented

---

## Put Wall

Measures:

Highest Put OI strike.

Purpose:

Potential support.

Status:

Implemented

---

## Distance To Call Wall

Measures:

Distance from spot to resistance wall.

Status:

Implemented

---

## Distance To Put Wall

Measures:

Distance from spot to support wall.

Status:

Implemented

---

## Writing Detection

Classifies:

* Long Build-up
* Short Build-up
* Long Unwinding
* Short Covering

Purpose:

Identify institutional behavior.

Status:

Implemented

---

## ATM Flow

Measures:

Localized activity around ATM strikes.

Purpose:

Detect immediate directional battle.

Status:

Implemented

---

## GEX (Gamma Exposure)

Measures:

Dealer hedging pressure.

Outputs:

* Call GEX
* Put GEX
* Net GEX

Status:

Implemented

---

## Breadth

Measures:

Participation of underlying constituents.

Status:

Implemented

---

## Regime Engine

Measures:

Current market environment.

Examples:

* Volatility Compression
* Trending Bull
* Trending Bear

Status:

Implemented

---

# What Has Been Completed?

Feature Engineering:

COMPLETE

Raw Data Preservation:

COMPLETE

Collection Infrastructure:

COMPLETE

Backup System:

COMPLETE

Monitoring System:

COMPLETE

Health Dashboard:

COMPLETE

Database Partitioning:

COMPLETE

PM2 Automation:

COMPLETE

Long-Term Collection:

READY

---

# What Is The Current Limitation?

The limitation is NOT engineering.

The limitation is DATA.

Current Situation:

Features exist.

Historical evidence does not.

We need sufficient observations before proving alpha.

---

# What Should Be Done Now?

DO:

* Keep daemon running
* Verify health daily
* Verify backups weekly
* Continue collecting data

DO NOT:

* Add new OI features
* Refactor architecture
* Retrain models
* Optimize storage prematurely

The goal is accumulation, not engineering.

---

# Why Collect 30–60 Trading Days?

To answer:

"Do OI features actually predict future returns?"

Currently:

Nobody knows.

We only have theory.

We need evidence.

---

# What To Do After 30 Trading Days?

Run Alpha Validation.

For each feature:

* Velocity
* Acceleration
* PCR
* IV
* Walls
* Writing Detection
* ATM Flow
* GEX
* Breadth

Measure:

* 5-minute returns
* 15-minute returns
* 30-minute returns
* 60-minute returns

Calculate:

* Correlation
* Hit Rate
* Information Coefficient
* Stability

Determine:

Which features contain predictive information.

---

# What To Do After 60 Trading Days?

Repeat validation.

Compare:

30-day results

vs

60-day results.

Classify every feature:

* Strong Alpha
* Weak Alpha
* No Alpha

Remove anything consistently failing.

Keep only proven signals.

---

# What Happens After OI Validation?

Build ML datasets.

Train:

* XGBoost
* LightGBM
* Random Forest
* CatBoost

Compare:

Price-only model

vs

Price + OI model

Measure incremental alpha.

---

# OI Layer Version 2 Roadmap

These are NOT required now.

These are future enhancements.

Only build them after collecting sufficient data.

---

## 1. OI Z-Score

Purpose:

Normalize OI relative to its rolling distribution.

Benefits:

Detect abnormal positioning.

Priority:

Medium

---

## 2. OI-to-Volume Ratio

Formula:

Volume / OI

Purpose:

Differentiate:

* Temporary trading activity
* Genuine position creation

Benefits:

Measures conviction.

Priority:

Medium

---

## 3. Expiry Rollover Intelligence

Purpose:

Separate:

* Genuine positioning
* Expiry-related contract migration

Benefits:

Reduces expiry noise.

Priority:

High

---

## 4. Multi-Expiry Analysis

Current:

Nearest expiry only.

Future:

Current Week
+
Next Week
+
Monthly

Benefits:

Detect institutional migration before expiry.

Priority:

High

---

## 5. Explicit Gamma Squeeze Detection

Current:

GEX exists.

Future:

Detect exact squeeze conditions.

Benefits:

Identify explosive moves.

Priority:

Medium

---

# Future Architecture

Layer 1

Price Intelligence

Status:

Complete

---

Layer 2

OI Intelligence

Status:

Complete

Collecting Data

---

Layer 3

News Intelligence

Status:

Next Development Phase

---

Layer 4

Macro Intelligence

Status:

Future

---

Layer 5

Fusion Layer

Combines:

* Price
* OI
* News
* Macro

---

Layer 6

ML Layer

Final prediction engine.

---

# Most Important Lesson

Do not confuse:

Building Features

with

Proving Alpha.

The OI Layer has completed feature engineering.

The next mission is proving whether those features contain predictive information.

The most valuable output from the OI Layer now is not code.

It is data.
