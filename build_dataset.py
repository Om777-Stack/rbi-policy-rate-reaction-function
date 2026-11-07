"""Step 1: merge three RBI/MoSPI files into one monthly table.

Usage:
  python build_dataset.py CPI.xlsx IIP.xlsx REPO_TABLE40.xlsx macro_monthly.csv

Series (all monthly, Oct 2016 - Dec 2025, old bases only):
  repo_rate     policy repo rate in force on the last day of the month  (RBI Handbook, Table 40)
  repo_change   change in the repo rate during the month, percentage points
  cpi_infl      all-India combined CPI inflation, y/y %, base 2012=100  (MoSPI via RBI DBIE)
  iip_growth    IIP general index growth, y/y %, base 2011-12=100       (MoSPI via RBI DBIE)
"""
import sys
import pandas as pd

cpi_file, iip_file, repo_file, out_file = sys.argv[1:5]
START, END = '2016-10-31', '2025-12-31'

# ---------- 1. Repo rate: a STEP series. The table lists only the dates it changed.
raw = []
for sheet in ['T_40(i)', 'T_40(ii)']:
    df = pd.read_excel(repo_file, sheet_name=sheet, header=None, skiprows=6)
    raw.append(df.iloc[:, [1, 3]])                      # col B = effective date, col D = repo
raw = pd.concat(raw)
raw.columns = ['date', 'repo']
raw['date'] = pd.to_datetime(raw['date'], errors='coerce')
raw['repo'] = pd.to_numeric(raw['repo'], errors='coerce')    # '-' means "no change" -> NaN
changes = raw.dropna(subset=['date', 'repo']).drop_duplicates('date').set_index('date')['repo'].sort_index()

daily = changes.reindex(pd.date_range(changes.index.min(), END)).ffill()   # carry rate forward
month_end = daily.resample('ME').last().rename('repo_rate')

# ---------- 2. CPI combined, base 2012=100, headline ("A) General Index")
cpi = pd.read_excel(cpi_file, sheet_name='CPI - 2012=100 (All India)', header=None, skiprows=7)
cpi = cpi.iloc[:, [1, 2, 3, 8, 9]]
cpi.columns = ['month', 'item', 'status', 'index', 'infl']
cpi = cpi[cpi['item'].astype(str).str.contains('General Index', na=False)].copy()
cpi['date'] = pd.to_datetime(cpi['month'].astype(str).str.title(), format='%b-%Y', errors='coerce') + pd.offsets.MonthEnd(0)
cpi['infl'] = pd.to_numeric(cpi['infl'], errors='coerce')
cpi['index'] = pd.to_numeric(cpi['index'], errors='coerce')
cpi = cpi.dropna(subset=['date']).set_index('date').sort_index()
cpi_s = cpi['infl'].rename('cpi_infl')
cpi_status = cpi['status'].rename('cpi_status')

# ---------- 3. IIP general index, base 2011-12=100
def read_iip(sheet):
    d = pd.read_excel(iip_file, sheet_name=sheet, header=None)
    d = d.iloc[:, [1, 2]]; d.columns = ['month', 'val']
    d['date'] = pd.to_datetime(d['month'].astype(str).str.replace(' ', '').str.title(), format='%b-%Y', errors='coerce') + pd.offsets.MonthEnd(0)
    d['val'] = pd.to_numeric(d['val'], errors='coerce')
    return d.dropna(subset=['date', 'val']).set_index('date')['val'].sort_index()
iip_idx = read_iip('IIP-2011-12=100')
iip_g = read_iip('(Growth Rate (IIP-2011-12=100))').rename('iip_growth')

# ---------- 4. Merge, trim, and cross-check
m = pd.concat([month_end, cpi_s, cpi_status, iip_g], axis=1).loc[START:END]
m['repo_change'] = m['repo_rate'].diff()
m.loc[m.index[0], 'repo_change'] = month_end.diff().loc[m.index[0]]

# check A: recompute IIP y/y from the index and compare with RBI's published growth
recalc = (iip_idx.pct_change(12) * 100).reindex(m.index)
m['iip_check_diff'] = (recalc - m['iip_growth']).abs()
# check B: recompute CPI y/y from the index
cpi_re = (cpi['index'].pct_change(12) * 100).reindex(m.index)
m['cpi_check_diff'] = (cpi_re - m['cpi_infl']).abs()

m.index.name = 'month_end'
m.to_csv(out_file)
print('rows', len(m), m.index.min().date(), '->', m.index.max().date())
print('missing values per column:\n', m.isna().sum().to_string())
print('max |IIP recalculated - published| (pp):', round(m['iip_check_diff'].max(), 3))
print('max |CPI recalculated - published| (pp):', round(m['cpi_check_diff'].max(), 3))
print('repo changes in sample:\n', m.loc[m['repo_change'].fillna(0) != 0, ['repo_rate', 'repo_change']].to_string())
