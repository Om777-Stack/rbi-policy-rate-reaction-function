# How the RBI's policy rate responds to inflation, October 2016 to December 2025

I wanted to know how much the RBI raises its policy repo rate when CPI inflation rises, and how sure we can be of the answer. I used public monthly data and a simple model of gradual adjustment, then checked the result against individual MPC meetings.

## Question

By how much does the RBI raise the repo rate when CPI inflation goes up, and how sure can I be of that number?

## Data

I used 111 monthly observations from October 2016 to December 2025, downloaded from RBI's Database on Indian Economy (DBIE) on 4 November 2026. The files are in `data/`.

| Series | What it is | Source |
|---|---|---|
| Repo rate | Policy repo rate in force on the last day of the month | RBI, Handbook of Statistics on the Indian Economy, Table 40 |
| CPI inflation | All-India combined, year-on-year, base 2012=100 | NSO, MoSPI, via RBI Bulletin Table 19 |
| IIP growth | General index, year-on-year, base 2011-12=100 | NSO, MoSPI, via RBI Bulletin Table 23 |

The sample ends in December 2025 because CPI switched to base 2024 in February 2026 and IIP to base 2022-23. I kept both series on their old bases so they stay consistent. I recomputed the year-on-year rates from the published indices, and they match the published rates (IIP exactly, CPI within 0.005 points). December 2025 CPI is provisional.

The repo rate moves in steps. It changed in 21 of the 111 months.

## Method

### 1. Monthly model

I estimated a partial-adjustment model by OLS with Newey-West standard errors (6 lags):

repo(t) = a + rho * repo(t-1) + b * inflation + c * IIP growth + d * COVID dummy + error

- Last month's repo rate is in the model because the RBI adjusts gradually. Without it the model breaks: the inflation coefficient comes out negative (-0.11) and the Durbin-Watson statistic is 0.12.
- The COVID dummy covers March 2020 to June 2021.
- In my preferred version, inflation is the average of months t-2 to t-4 and IIP growth is lagged two months. CPI for month t comes out in the middle of month t+1, so a decision early in month t can only use CPI up to month t-2. The October 2026 MPC minutes, for example, cite August CPI.
- The long-run effect is b / (1 - rho). I put a confidence interval on it with the delta method.
- I picked the preferred version after seeing the results of the others. That is why I report all nine.

### 2. Decisions at each meeting

The MPC decides at meetings, not every month. So I also modelled each meeting's outcome (cut, hold or hike) with an ordered logit and robust (HC1) standard errors. The regressors are the average inflation known at the time minus the 4% target, IIP growth lagged two months, and the COVID dummy.

The calendar has 57 rate-decision meetings from October 2016 to December 2025. I took it from the titles of the "Minutes of the Monetary Policy Committee Meeting" press releases on rbi.org.in (searched on 6 November 2026). It is six meetings a year, except 2020 (February, March, May, August, October, December) and 2022 (February, April, May, June, August, September, December). Every rate change in my data falls inside it. RBI's numbering (October 2026 was the 63rd meeting) also counts an unscheduled meeting on 3 November 2022 that made no rate decision, so I left it out. The 57 meetings, that one, and the 5 meetings of 2026 make 63.

### 3. Unit roots and cointegration

I ran ADF and KPSS tests on the repo rate and inflation, Engle-Granger cointegration tests, and an ARDL bounds test.

## Results

### Monthly model

| | Estimate | 95% CI |
|---|---|---|
| Short-run effect of a 1-point rise in inflation (preferred, n = 107) | 0.042 points | 0.019 to 0.066 |
| Long-run effect (preferred) | 1.02 | -0.31 to 2.35 |

- The short-run effect is positive and significant in all nine specifications (0.030 to 0.055 points, p <= 0.006). The chart is `short_run_response.png` and the full table is `results_table.csv`.
- The long-run effect is not pinned down. In every specification its confidence interval includes both zero and 1, the value at which the RBI raises the real rate when inflation rises. The repo rate moves slowly (rho is about 0.96), and about 110 months is too little data to estimate a long-run effect precisely.
- Averaging inflation over several months gives larger short-run estimates (0.041 to 0.055) than using a single month (0.031 to 0.035). That fits a response to persistent inflation, but I did not test it formally.

### Meeting-level model

I could use 55 meetings after the lags: 12 cuts, 35 holds and 8 hikes.

| | Odds ratio | p |
|---|---|---|
| Inflation, per point above the 4% target | 3.3 | < 0.001 |
| IIP growth (lagged two months), per point | 1.02 | 0.009 |

- Each extra point of inflation above the target multiplies the odds of a tighter decision by about 3.3. At average IIP growth the model gives roughly 18% cut, 78% hold and 4% hike when inflation is at 4%. At 6% it gives 2% cut, 65% hold and 33% hike.
- The inflation result holds when I drop the meetings from February 2020 to December 2021 (odds ratio 3.6) and when I use only meetings from 2019 on (4.2, p = 0.001).
- When I add the lagged real policy rate, the inflation effect weakens (odds ratio 2.2, p = 0.096). Inflation and the real rate move together so closely that I can't separate them in this sample.
- The IIP result is fragile. It loses significance (p = 0.63) once I drop the COVID-period meetings. I don't claim IIP matters.

### Unit roots and cointegration

- ADF can't reject a unit root in the levels of the repo rate (p = 0.35) or inflation (p = 0.66). KPSS doesn't reject stationarity. With 111 observations both tests have little power, so they don't settle it.
- Engle-Granger finds no cointegration (p = 0.39, or 0.82 with IIP added). The ARDL bounds test is inconclusive (F = 4.93 against 5% bounds of 3.80 and 4.81, and F = 4.60 with two lags).
- So I read the level regression as a short-run relationship, not a long-run equilibrium.

## Limits

- I used headline CPI, not core. Core CPI exists only on the 2024 base, from January 2025, so I couldn't build it for this sample. The October 2026 MPC minutes say policy responds mainly to second-round effects of supply shocks, and headline CPI doesn't separate those out.
- The model uses past inflation only. The RBI decides on projected inflation, and I don't have forecast or expectations data.
- Only 20 of the 55 meetings I could use changed the rate. The meeting-level result shows direction and rough size, not a precise number.
- IIP covers industry only and swings a lot, so it is a weak stand-in for the output gap.
- When I split the sample into 2016 to 2019 (37 months) and 2022 to 2025 (48 months), the estimates disagreed. I don't report either as a finding.
- The data are as I downloaded them in November 2026. They are not the real-time versions the committee saw.
- This shows association in one sample, not cause. The sample stops at December 2025.

## Reproduce

1. Download the files in `data/` and put them in a Google Drive folder called `rbi_macro`.
2. Open `RBI_reaction_function.ipynb` in Google Colab.
3. Run all the cells from the top. The first cell connects to your Drive.

The notebook starts from `macro_monthly.csv`. I built that file from the three RBI Excel files with `build_dataset.py`. To rebuild it, run `python build_dataset.py <CPI file> <IIP file> <Table 40 file> macro_monthly.csv`.
