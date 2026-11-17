
import pandas as pd
import statsmodels.formula.api as smf
from pathlib import Path

# Load our existing five-anomaly dataset
df = pd.read_csv("outputs/checkpoint1_sample.csv")

# Keep the three research comparison periods
periods = [
    "Original Sample",
    "Pre-Publication Gap",
    "Post-Publication"
]
df = df[df["period"].isin(periods)].copy()

# Create the regression indicators
df["post_sample"] = (
    df["period"] != "Original Sample"
).astype(int)

df["post_publication"] = (
    df["period"] == "Post-Publication"
).astype(int)

# Run both models with standard errors clustered by month
formulas = {
    "Without Month FE":
        "ret ~ post_sample + post_publication + C(signalname)",
    "With Month FE":
        "ret ~ post_sample + post_publication + C(signalname) + C(month)"
}

rows = []

for model_name, formula in formulas.items():

    result = smf.ols(formula, data=df).fit(
        cov_type="cluster",
        cov_kwds={"groups": df["month"]}
    )

    # Record individual regression coefficients
    for variable in ["post_sample", "post_publication"]:
        ci = result.conf_int().loc[variable]

        rows.append({
            "model": model_name,
            "variable": variable,
            "coefficient": result.params[variable],
            "standard_error": result.bse[variable],
            "p_value": result.pvalues[variable],
            "ci_lower": ci.iloc[0],
            "ci_upper": ci.iloc[1]
        })

    # Test the total original-to-post-publication change
    test = result.t_test(
        "post_sample + post_publication = 0"
    )
    ci = test.conf_int()[0]

    rows.append({
        "model": model_name,
        "variable": "total_post_vs_original",
        "coefficient": test.effect.item(),
        "standard_error": test.sd.item(),
        "p_value": test.pvalue.item(),
        "ci_lower": ci[0],
        "ci_upper": ci[1]
    })

# Save the results
results = pd.DataFrame(rows)

Path("outputs").mkdir(exist_ok=True)
results.to_csv(
    "outputs/prototype_regression_results.csv",
    index=False
)

print("Regression analysis completed successfully!")
print("\nREGRESSION RESULTS:")
print(results.round(4).to_string(index=False))
