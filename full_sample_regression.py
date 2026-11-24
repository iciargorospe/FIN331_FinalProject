
# FIN331 Checkpoint 3: Full-sample panel regressions

from pathlib import Path
import numpy as np
import pandas as pd
import scipy.sparse as sparse
from scipy.sparse.linalg import lsqr
from scipy.sparse.csgraph import connected_components
import statsmodels.api as sm
from statsmodels.stats.sandwich_covariance import cov_cluster
from scipy.stats import norm

OUTPUT_DIR = Path("outputs")

# 1. Load the 209-anomaly dataset
df = pd.read_csv(OUTPUT_DIR / "full_sample_analysis.csv")

assert df["signalname"].nunique() == 209
assert len(df) == 135466

n = len(df)

# Give each anomaly and calendar month a numeric ID
anomaly_id, anomalies = pd.factorize(
    df["signalname"], sort=True
)
month_id, months = pd.factorize(
    df["month"], sort=True
)

n_anomalies = len(anomalies)
n_months = len(months)
row_ids = np.arange(n)

# Our dependent variable and two regression indicators
y = df["ret"].to_numpy(dtype=float)
X = df[["post_sample", "post_publication"]].to_numpy(dtype=float)

assert np.isfinite(y).all()
assert np.isfinite(X).all()


# 2. Create a SPARSE fixed-effects matrix
# This avoids storing thousands of mostly-zero dummy columns
def make_fixed_effects(include_month_fe):

    if include_month_fe:

        # Each observation belongs to one anomaly and one month
        rows = np.concatenate([row_ids, row_ids])
        cols = np.concatenate([
            anomaly_id,
            n_anomalies + month_id
        ])

        Z = sparse.csr_matrix(
            (np.ones(2 * n), (rows, cols)),
            shape=(n, n_anomalies + n_months)
        )

        # Count independent fixed-effect parameters.
        # Connected components account for any disconnected groups.
        graph = sparse.csr_matrix(
            (
                np.ones(2 * n),
                (
                    np.concatenate([anomaly_id, n_anomalies + month_id]),
                    np.concatenate([n_anomalies + month_id, anomaly_id])
                )
            ),
            shape=(
                n_anomalies + n_months,
                n_anomalies + n_months
            )
        )

        components = connected_components(
            graph, directed=False, return_labels=False
        )

        fe_rank = n_anomalies + n_months - components

    else:

        # Anomaly fixed effects only
        Z = sparse.csr_matrix(
            (np.ones(n), (row_ids, anomaly_id)),
            shape=(n, n_anomalies)
        )

        fe_rank = n_anomalies

    return Z, fe_rank


# 3. Remove the variation explained by the fixed effects
# This is called "absorbing" or "partialling out" fixed effects
def absorb(values, Z):

    solution = lsqr(
        Z, values,
        atol=1e-11,
        btol=1e-11,
        iter_lim=20000
    )

    if solution[1] not in (1, 2):
        raise RuntimeError(
            f"Fixed-effect solver did not converge: {solution[1]}"
        )

    return values - Z @ solution[0]


# 4. Estimate a model with month-clustered standard errors
def run_model(model_name, include_month_fe):

    print(f"\nRunning: {model_name}", flush=True)

    Z, fe_rank = make_fixed_effects(include_month_fe)

    y_adjusted = absorb(y, Z)

    X_adjusted = np.column_stack([
        absorb(X[:, 0], Z),
        absorb(X[:, 1], Z)
    ])

    # Ensure both coefficients can be estimated
    assert np.linalg.matrix_rank(X_adjusted) == 2

    # Estimate only the two coefficients after removing FE
    model = sm.OLS(y_adjusted, X_adjusted).fit()

    # Cluster covariance by calendar month
    covariance = cov_cluster(
        model,
        month_id,
        use_correction=False
    )

    # Finite-sample adjustment, accounting for absorbed FE
    clusters = n_months
    parameters = fe_rank + 2

    correction = (
        clusters / (clusters - 1)
        * (n - 1) / (n - parameters)
    )

    covariance = covariance * correction

    # Report the two coefficients and their combined effect
    tests = {
        "post_sample": np.array([1.0, 0.0]),
        "post_publication": np.array([0.0, 1.0]),
        "total_post_vs_original": np.array([1.0, 1.0])
    }

    rows = []

    for variable, weights in tests.items():

        coefficient = float(weights @ model.params)

        standard_error = float(
            np.sqrt(weights @ covariance @ weights)
        )

        assert standard_error > 0

        z_stat = coefficient / standard_error
        p_value = float(2 * norm.sf(abs(z_stat)))

        rows.append({
            "model": model_name,
            "variable": variable,
            "coefficient": coefficient,
            "standard_error": standard_error,
            "z_stat": z_stat,
            "p_value": p_value,
            "ci_lower": coefficient - 1.96 * standard_error,
            "ci_upper": coefficient + 1.96 * standard_error,
            "observations": n,
            "anomalies": n_anomalies,
            "calendar_months": n_months
        })

    return rows


# 5. Run both regression specifications
results = []

results.extend(
    run_model("Without Month FE", include_month_fe=False)
)

results.extend(
    run_model("With Month FE", include_month_fe=True)
)

# 6. Validate and save our results
results = pd.DataFrame(results)

assert len(results) == 6
assert np.isfinite(results["coefficient"]).all()
assert np.isfinite(results["standard_error"]).all()
assert results["p_value"].between(0, 1).all()

output_file = OUTPUT_DIR / "full_sample_regression.csv"
results.to_csv(output_file, index=False)

print("\nFULL-SAMPLE PANEL REGRESSION RESULTS")
print(
    results[[
        "model", "variable", "coefficient",
        "standard_error", "p_value"
    ]].round(5).to_string(index=False)
)

print("\nSaved to:", output_file)
