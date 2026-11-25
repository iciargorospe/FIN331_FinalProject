"""Exploratory 2-way cluster sensitivity check for FIN331 checkpoint4-v1.

Reads committed/raw OpenAP full-sample panel and published one-way regression results.
Preserves original research outputs and saves a separate robustness table.
One-way covariance is reconstructed as a check.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import sparse
from scipy.sparse.csgraph import connected_components
from scipy.sparse.linalg import lsqr
from scipy.stats import norm

out = Path('outputs')
raw = out / 'full_sample_analysis.csv'
df = pd.read_csv(raw if raw.exists() else out / 'full_sample_analysis.csv.gz')
assert len(df) == 135466 and df['signalname'].nunique() == 209
assert not df.duplicated(['signalname', 'month']).any()

anomaly_id, anomalies = pd.factorize(df['signalname'], sort=True)
month_id, months = pd.factorize(df['month'], sort=True)
n, a, t = len(df), len(anomalies), len(months)
indices = np.arange(n)
Z = sparse.csr_matrix((np.ones(2*n),
    (np.r_[indices, indices], np.r_[anomaly_id, a + month_id])),
    shape=(n, a+t))
graph = sparse.csr_matrix((np.ones(2*n),
    (np.r_[anomaly_id, a+month_id], np.r_[a+month_id, anomaly_id])),
    shape=(a+t, a+t))
n_components = connected_components(graph, directed=False, return_labels=False)
fe_rank = a+t-n_components
k = fe_rank+2

def absorb(vector):
    fitted = lsqr(Z, vector, atol=1e-11, btol=1e-11, iter_lim=20000)
    assert fitted[1] in (1, 2), f'FE solver failed: {fitted[1]}'
    return vector - Z@fitted[0]

y = absorb(df['ret'].to_numpy(dtype=float))
X = np.column_stack([
    absorb(df['post_sample'].to_numpy(dtype=float)),
    absorb(df['post_publication'].to_numpy(dtype=float)),
])
beta = np.linalg.lstsq(X, y, rcond=None)[0]
resid = y-X@beta
score = X*resid[:,None]
bread = np.linalg.inv(X.T@X)

def clustered_cov(ids, n_groups):
    sums = np.zeros((n_groups,2))
    np.add.at(sums, ids, score)
    factor = n_groups/(n_groups-1) * (n-1)/(n-k)
    return (bread@(sums.T@sums)@bread)*factor

V_month = clustered_cov(month_id,t)
V_anomaly = clustered_cov(anomaly_id,a)
# Every anomaly-month pair is unique, so the 2-way overlap term is HC0.
V_overlap = (bread@(score.T@score)@bread)*(n/(n-k))
V_two_way = V_month+V_anomaly-V_overlap

original = pd.read_csv(out/'full_sample_regression.csv')
original = original.loc[original['model']=='With Month FE'].set_index('variable')
print('TWO-WAY CLUSTERING SENSITIVITY (preferred month-FE model)')
print(f'Observations: {n:,}; anomalies: {a}; months: {t}; absorbed FE rank: {fe_rank}')
print('Original one-way SEs are recalculated below as a check.\n')
rows = []
for name, w in {
    'post_sample':np.array([1.0,0.0]),
    'post_publication':np.array([0.0,1.0]),
    'total_post_vs_original':np.array([1.0,1.0]),
}.items():
    coefficient=float(w@beta)
    se_month=float(np.sqrt(w@V_month@w))
    variance_two=float(w@V_two_way@w)
    assert variance_two>0, f'Nonpositive 2-way variance for {name}'
    se_two=float(np.sqrt(variance_two))
    p_month=float(2*norm.sf(abs(coefficient/se_month)))
    p_two=float(2*norm.sf(abs(coefficient/se_two)))
    assert np.isclose(coefficient,original.loc[name,'coefficient'],atol=1e-6)
    assert np.isclose(se_month,original.loc[name,'standard_error'],atol=1e-5), (name,se_month,original.loc[name,'standard_error'])
    rows.append({
        'variable':name,
        'coefficient':coefficient,
        'se_month_only':se_month,
        'p_month_only':p_month,
        'se_two_way':se_two,
        'p_two_way':p_two,
    })
results = pd.DataFrame(rows)
print(results.round(5).to_string(index=False))

# Save the sensitivity check without changing the primary regression output.
output_file = out / 'full_sample_two_way_clustering.csv'
results.to_csv(output_file, index=False)
print('\nPASS: original month-clustered estimates and SEs reproduced.')
print(f'Saved separate robustness results to: {output_file}')
