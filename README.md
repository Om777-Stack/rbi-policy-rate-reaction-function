# How the RBI's policy rate responds to inflation, October 2016 to December 2025

A small empirical study of the Reserve Bank of India's policy repo rate under flexible inflation targeting. It uses monthly public data and a partial-adjustment model, then checks the result at the level of individual Monetary Policy Committee (MPC) meetings.

## Question

By how much does the RBI raise the repo rate when CPI inflation rises, and how sure can we be of the answer?

## Data

All series are monthly, October 2016 to December 2025 (111 months), downloaded from RBI's Database on Indian Economy (DBIE) on 4 November 2026. The files are in `data/`.

| Series | Definition | Source |
|---|---|---|
| Repo rate | Policy repo rate in force on the last day of the month | RBI, Handbook of Statistics on the Indian Economy, Table 40 |
| CPI inflation | All-India combined, year-on-year, base 2012=100 | NSO, MoSPI, via RBI Bulletin Table 19 |
| IIP growth | General index, year-on-year, base 2011-12=100 | NSO, MoSPI, via RBI Bulletin Table 23 |

The sample ends in December 2025 because CPI moved to base 2024 in February 2026 and IIP to base 2022-23. Both series stay on their old bases throughout. Year-on-year rates were recomputed from the published indices and match the published rates (IIP exactly, CPI within 0.005 points). December 2025 CPI is provisional.

The repo rate is a step series: it changed in 21 of the 111 months.

## Method

### 1. Monthly partial-adjustment model

Estimated by OLS with Newey-West (HAC, 6 lags) standard errors:

repo(t) = a + rho * repo(t-1) + b * inflation + c * IIP growth + d * COVID dummy + error

- The lagged repo rate captures gradual adjustment. Without it the model fails: the inflation coefficient has the wrong sign (-0.11) and the Durbin-Watson statistic is 0.12.
- The COVID dummy covers March 2020 to June 2021.
- Preferred specification: inflation is the average of months t-2 to t-4, and IIP growth is lagged two months. CPI for month t is published in mid t+1, so a decision early in month t can use CPI only up to month t-2 (the October 2026 MPC minutes, for example, cite August CPI).
- Long-run effect = b / (1 - rho), with a delta-method confidence interval.
- The preferred specification was chosen after seeing the results of the others. All 9 are reported for that reason.

### 2. Meeting-level ordered logit

The MPC decides at meetings, not every month. For each meeting the outcome is cut, hold or hike, modelled with an ordered logit and robust (HC1) standard errors. The regressors are the average inflation known at the meeting minus the 4% target, IIP growth lagged two months, and the COVID dummy.

The meeting calendar has 57 policy meetings from October 2016 to December 2025, taken from the titles of RBI's "Minutes of the Monetary Policy Committee Meeting" press releases (rbi.org.in, searched on 6 November 2026). It is six meetings a year, except 2020 (February, March, May, August, October, December) and 2022 (February, April, May, June, August, September, December). Every rate change in the data falls inside it. RBI's numbering (October 2026 was the 63rd meeting) also counts an unscheduled meeting on 3 November 2022 that made no rate decision, so it is not in the model. The 57 meetings, that one, and the 5 meetings of 2026 make 63.

### 3. Unit-root and cointegration checks

ADF and KPSS tests on the repo rate and inflation, Engle-Granger cointegration tests, and an ARDL bounds test.

## Results

### Monthly model

| | Estimate | 95% CI |
|---|---|---|
| Short-run response to a 1-point rise in inflation (preferred, n = 107) | 0.042 points | 0.019 to 0.066 |
| Long-run response (preferred) | 1.02 | -0.31 to 2.35 |

- The short-run response is positive and statistically significant in all 9 specifications (0.030 to 0.055 points, p <= 0.006). See `short_run_response.png` and `results_table.csv`.
- The long-run response is not pinned down. Its confidence interval includes zero and the Taylor-principle value of 1 in every specification. The repo rate moves slowly (rho about 0.96), and about 110 monthly observations are too few to estimate a long-run effect precisely.
- Specifications that average inflation over several months give larger short-run estimates (0.041 to 0.055) than those using a single month (0.031 to 0.035). That is consistent with a response to persistent inflation, but I did not test it formally.

### Meeting-level model

55 meetings are usable after lags: 12 cuts, 35 holds, 8 hikes.

| | Odds ratio | p |
|---|---|---|
| Inflation, per point above the 4% target | 3.3 | < 0.001 |
| IIP growth (lagged two months), per point | 1.02 | 0.009 |

- Each extra point of inflation above target multiplies the odds of a tighter decision by about 3.3. At average IIP growth the model gives roughly 18% cut, 78% hold and 4% hike at 4% inflation, and 2% cut, 65% hold and 33% hike at 6%.
- The inflation result holds when the meetings from February 2020 to December 2021 are dropped (odds ratio 3.6) and when only meetings from 2019 onward are used (4.2, p = 0.001).
- When the lagged real policy rate is added, the inflation effect weakens (odds ratio 2.2, p = 0.096). Inflation and the real rate overlap heavily, so the two cannot be separated in this sample.
- The IIP result is fragile. It loses significance (p = 0.63) once the COVID-period meetings are dropped. I do not claim IIP matters.

### Unit roots and cointegration

- ADF cannot reject a unit root in the levels of the repo rate (p = 0.35) or inflation (p = 0.66). KPSS does not reject stationarity. With 111 observations both tests have low power, so they do not settle the question.
- Engle-Granger finds no cointegration (p = 0.39; 0.82 with IIP added). The ARDL bounds test is inconclusive (F = 4.93 against 5% bounds of 3.80 and 4.81; F = 4.60 with two lags).
- I therefore read the level regression as a short-run relationship, not as a long-run equilibrium.

## Limits

- Headline CPI, not core. Core CPI (excluding food and fuel) is available only for the 2024 base, from January 2025. The MPC minutes (October 2026) state that monetary policy acts mainly on the second-round effects of supply shocks, which headline CPI does not isolate.
- No inflation forecasts or expectations. The RBI's decisions rest on projected inflation; this model uses past inflation only.
- Only 20 of the 55 usable meetings changed the rate, so the meeting-level model gives direction and rough size, not precision.
- IIP covers industry only and is volatile, so it is a rough proxy for the output gap.
- Estimates for the sub-periods 2016-19 (37 months) and 2022-25 (48 months) are unstable and are not reported as findings.
- Data are as downloaded in November 2026, not real-time vintages that the committee saw.
- The results describe association in this sample. They are not causal estimates, and events after December 2025 are outside the sample.

## Reproduce

Open `RBI_reaction_function.ipynb` in Google Colab, place the data files from `data/` in a Drive folder named `rbi_macro`, and run all cells from the top.
