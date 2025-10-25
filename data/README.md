# Sample Market History Dataset

This repository bundles a curated snapshot of Yahoo Finance closing prices in
`market_history_sample.csv`. It covers Bitcoin, Gold, the U.S. Dollar Index, the
S&P 500, and twelve large-cap cryptocurrencies across 210 trading days. The
classifier automatically falls back to this dataset whenever a live API pull is
unavailable or missing required macro drivers, ensuring the project can be
executed offline or during classroom demos without network access.

The snapshot was downloaded on 25 October 2025 and resampled to daily closes
with forward-filled gaps so macro and crypto assets share the same timestamp
index.
