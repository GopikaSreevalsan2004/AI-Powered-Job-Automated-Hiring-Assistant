# ATS Production Performance Report

**Date:** 2026-06-01 13:57:09
**Environment:** Windows Production Simulation

## 1. Speed Benchmarks
| Component | Standard Mode | Optimized Mode | Improvement |
|-----------|---------------|----------------|-------------|
| PDF Extraction | 0.1693s | 0.1438s | 15.1% |
| Text Cleaning | 0.001s | 0.0005s | 50.0% |
| Entity Detection | 0.0708s | 0.0468s | 33.9% |
| **Total Pipeline** | **0.2411s** | **0.1911s** | **20.7%** |

## 2. Resource Utilization
- **Avg Memory Consumption:** 7.52 MB per process
- **Stability Check:** Passed. Concurrent handling ready.

## 3. Optimization Summary
- **Fuzzy Matching:** Improved $O(N)$ with exact-match caching and RapidFuzz support.
- **Parser Fast Mode:** Optional table extraction for metadata-only parsing.
- **Noisy Text Handling:** Enhanced regex stripping for watermarks and UTF-8 noise.
- **Memory Efficiency:** Avoided redundant text copies by processing stream segments.
