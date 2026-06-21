# FII/DII Intelligence Layer

## Overview
The FII/DII Intelligence Layer is a fully isolated, production-grade subsystem designed strictly for monitoring the Indian Cash Market. 

Unlike the Options Intelligence Layer (which tracks high-frequency intraday derivative flows), this layer tracks the macroscopic, end-of-day capital deployments by Foreign Institutional Investors (FII) and Domestic Institutional Investors (DII). 

## Core Philosophy
1. **Raw Preservation First:** This layer unconditionally saves the atomic Gross Buy, Gross Sell, and Net figures directly into `fii_dii_raw_archive`. It ensures that downstream pipelines are built on top of immutable historical truth.
2. **Strict Chronology Constraints:** Because FII/DII data is released post-market close, it is fundamentally impossible to trade the current day based on the current day's flow. This engine guarantees that Friday's flow data is strictly restricted from being accessed by prediction algorithms until Monday morning, enforcing mathematical prevention of Look-Ahead Bias.

## Structure
- `ingestion/`: Handles daily arithmetic validation and upsert logic.
- `analytics/`: Computes Streaks, Divergence, and Rolling flows dynamically.
- `validation/`: Enforces the chronology safety checks.
- `feature_store.py`: Extracts the final, ML-ready dataset for downstream training.

## Current Objective
Begin daily collection of institutional flow data. DO NOT attempt to scrape historical data due to unreliability. This system will now accumulate purely forward-looking records over the next 30-60 trading days before any Alpha validation is conducted.
