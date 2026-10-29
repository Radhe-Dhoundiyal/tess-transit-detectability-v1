"""Exact V1 function extraction from run_detectability_modeling_phase6b.py.

Historical fitting helpers, not a new scientific run. Function bodies are
unchanged; private file I/O, plotting and production main are excluded.
The historical numeric_cadence sensitivity branch centers each frame locally;
it is retained as source truth, not advertised as the primary training-only path.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit

SEED = 20260724


BOOT_SEED = 20260725


DIFFICULTY = ["DIFFICULT", "MODERATE", "PATHOLOGICAL_OR_SPECIAL"]


CONT_A = ["log10_expected_snr", "log10_period_days", "observed_transit_count",
          "tess_magnitude", "sector_count", "log10_baseline_days"]


CONT_B = ["log10_depth_ppm", "log10_period_days", "log10_in_transit_points",
          "tess_magnitude", "sector_count", "log10_baseline_days"]


def scaling(train: pd.DataFrame, cols: list[str]) -> dict[str, tuple[float, float]]:
    out = {}
    for c in cols:
        mean = float(train[c].mean())
        sd = float(train[c].std(ddof=0))
        if not np.isfinite(sd) or sd <= 0:
            raise RuntimeError(f"Non-variable predictor {c}")
        out[c] = (mean, sd)
    return out


def design(df: pd.DataFrame, model: str, scale: dict[str, tuple[float, float]],
           interactions: bool = False, numeric_cadence: bool = False) -> tuple[np.ndarray, list[str]]:
    cols = CONT_A if model == "A" else CONT_B
    values = [np.ones(len(df))]
    names = ["Intercept"]
    z = {}
    for c in cols:
        z[c] = (df[c].to_numpy(float) - scale[c][0]) / scale[c][1]
        values.append(z[c])
        names.append("z_" + c)
    if numeric_cadence:
        cad = np.log10(df["cadence_seconds"].to_numpy(float))
        cad = (cad - cad.mean()) / (cad.std() or 1.0)
        values.append(cad)
        names.append("z_log10_cadence_seconds")
    else:
        cad = df["cadence_indicator"].to_numpy(float)
        values.append(cad)
        names.append("cadence_indicator_20s")
    for level in DIFFICULTY:
        values.append((df["difficulty_stratum"] == level).to_numpy(float))
        names.append("difficulty_" + level)
    if interactions:
        signal = z["log10_expected_snr" if model == "A" else "log10_depth_ppm"]
        period = z["log10_period_days"]
        values.extend([signal * period, signal * cad])
        names.extend([
            ("z_log10_expected_snr" if model == "A" else "z_log10_depth_ppm") + ":z_log10_period_days",
            ("z_log10_expected_snr" if model == "A" else "z_log10_depth_ppm") +
            (":z_log10_cadence_seconds" if numeric_cadence else ":cadence_indicator_20s"),
        ])
    return np.column_stack(values), names


def fit_penalized(x: np.ndarray, y: np.ndarray, names: list[str], l2: float = 1.0) -> dict:
    penalty = np.full(x.shape[1], l2)
    penalty[0] = 0.0
    for i, n in enumerate(names):
        if ":" in n:
            penalty[i] = 4.0 if l2 == 1.0 else l2 * 4.0

    def objective(beta):
        eta = np.clip(x @ beta, -35, 35)
        loss = np.logaddexp(0, eta).sum() - y @ eta + 0.5 * np.sum(penalty * beta * beta)
        grad = x.T @ (expit(eta) - y) + penalty * beta
        return float(loss), grad

    result = minimize(lambda b: objective(b), np.zeros(x.shape[1]), jac=True,
                      method="L-BFGS-B", options={"maxiter": 2000, "gtol": 1e-8})
    beta = result.x
    p = expit(np.clip(x @ beta, -35, 35))
    w = p * (1 - p)
    hessian = x.T @ (x * w[:, None]) + np.diag(penalty)
    covariance = np.linalg.pinv(hessian)
    converged = bool(result.success and np.isfinite(beta).all() and np.isfinite(covariance).all())
    return {
        "beta": beta, "covariance": covariance, "converged": converged,
        "message": str(result.message), "iterations": int(result.nit),
        "gradient_max_abs": float(np.max(np.abs(result.jac))),
    }


def predict(fit: dict, x: np.ndarray) -> np.ndarray:
    return np.clip(expit(np.clip(x @ fit["beta"], -35, 35)), 1e-8, 1 - 1e-8)


def auc(y, p) -> float:
    y = np.asarray(y)
    n1, n0 = int(y.sum()), int(len(y) - y.sum())
    if not n1 or not n0:
        return float("nan")
    order = np.argsort(p)
    ranks = np.empty(len(p), float)
    ranks[order] = np.arange(1, len(p) + 1)
    return float((ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def average_precision(y, p) -> float:
    y = np.asarray(y)
    if y.sum() == 0:
        return float("nan")
    order = np.argsort(-np.asarray(p))
    ys = y[order]
    precision = np.cumsum(ys) / np.arange(1, len(ys) + 1)
    return float((precision * ys).sum() / ys.sum())


def calibration_parameters(y, p) -> tuple[float, float]:
    lp = np.log(np.clip(p, 1e-8, 1 - 1e-8) / np.clip(1 - p, 1e-8, 1))
    x = np.column_stack([np.ones(len(lp)), lp])
    fit = fit_penalized(x, np.asarray(y, float), ["Intercept", "calibration_slope"], l2=0.0)
    return float(fit["beta"][0]), float(fit["beta"][1])


def metrics(y, p) -> dict:
    y = np.asarray(y, float)
    p = np.asarray(p, float)
    ci, cs = calibration_parameters(y, p)
    bins = np.linspace(0, 1, 11)
    idx = np.minimum(np.digitize(p, bins[1:-1]), 9)
    ece = 0.0
    for b in range(10):
        mask = idx == b
        if mask.any():
            ece += mask.mean() * abs(float(y[mask].mean() - p[mask].mean()))
    return {
        "log_loss": float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))),
        "brier_score": float(np.mean((y - p) ** 2)),
        "calibration_intercept": ci,
        "calibration_slope": cs,
        "expected_calibration_error": float(ece),
        "roc_auc": auc(y, p),
        "pr_auc": average_precision(y, p),
    }


def cv(data: pd.DataFrame, folds: pd.Series, response: str, model: str,
       interactions: bool = False, l2: float = 1.0, numeric_cadence: bool = False) -> tuple[pd.DataFrame, list[dict]]:
    rows, diagnostics = [], []
    cols = CONT_A if model == "A" else CONT_B
    for fold in sorted(folds.unique()):
        train = data[folds != fold]
        test = data[folds == fold]
        scale = scaling(train, cols)
        xt, names = design(train, model, scale, interactions, numeric_cadence)
        xv, _ = design(test, model, scale, interactions, numeric_cadence)
        fit = fit_penalized(xt, train[response].to_numpy(float), names, l2)
        if not fit["converged"]:
            raise RuntimeError(f"Fit failed: response={response} model={model} fold={fold}: {fit['message']}")
        pred = predict(fit, xv)
        for (_, row), probability in zip(test.iterrows(), pred):
            rows.append({
                "trial_id": row["trial_id"], "target_id": row["target_id"], "fold": int(fold),
                "response": response, "observed_outcome": int(row[response]),
                "predicted_probability": float(probability),
                "model_specification": f"Model_{model}_{'interaction' if interactions else 'base'}",
                "training_target_count": int(train["target_id"].nunique()),
                "validation_target_count": int(test["target_id"].nunique()),
            })
        diagnostics.append({
            "response": response, "model": model, "interactions": interactions, "fold": int(fold),
            "converged": fit["converged"], "iterations": fit["iterations"],
            "gradient_max_abs": fit["gradient_max_abs"], "message": fit["message"],
        })
    return pd.DataFrame(rows).sort_values(["fold", "target_id", "trial_id"]), diagnostics


def baseline_cv(data: pd.DataFrame, folds: pd.Series, response: str, baseline: int) -> pd.DataFrame:
    rows = []
    predictors = {0: [], 1: ["log10_expected_snr"], 2: ["log10_expected_snr", "log10_period_days"]}[baseline]
    for fold in sorted(folds.unique()):
        train, test = data[folds != fold], data[folds == fold]
        if not predictors:
            pred = np.repeat((train[response].sum() + 0.5) / (len(train) + 1), len(test))
        else:
            scale = scaling(train, predictors)
            xt = np.column_stack([np.ones(len(train))] + [
                (train[c].to_numpy(float) - scale[c][0]) / scale[c][1] for c in predictors])
            xv = np.column_stack([np.ones(len(test))] + [
                (test[c].to_numpy(float) - scale[c][0]) / scale[c][1] for c in predictors])
            fit = fit_penalized(xt, train[response].to_numpy(float), ["Intercept"] + predictors)
            pred = predict(fit, xv)
        for (_, row), probability in zip(test.iterrows(), pred):
            rows.append({"trial_id": row["trial_id"], "target_id": row["target_id"],
                         "observed_outcome": int(row[response]), "predicted_probability": float(probability)})
    return pd.DataFrame(rows)


def bootstrap_intervals(predictions: pd.DataFrame, replicates: int = 1000) -> pd.DataFrame:
    rng = np.random.default_rng(BOOT_SEED)
    targets = predictions["target_id"].unique()
    values = {k: [] for k in metrics(predictions["observed_outcome"], predictions["predicted_probability"])}
    by_target = {t: predictions[predictions["target_id"] == t] for t in targets}
    for _ in range(replicates):
        sample = rng.choice(targets, size=len(targets), replace=True)
        frames = [by_target[t] for t in sample]
        boot = pd.concat(frames, ignore_index=True)
        m = metrics(boot["observed_outcome"], boot["predicted_probability"])
        for k, v in m.items():
            values[k].append(v)
    rows = []
    for metric, vals in values.items():
        finite = np.asarray(vals)[np.isfinite(vals)]
        rows.append({"metric": metric, "estimate": metrics(
            predictions["observed_outcome"], predictions["predicted_probability"])[metric],
            "lower_95": float(np.quantile(finite, 0.025)),
            "upper_95": float(np.quantile(finite, 0.975)),
            "replicates": replicates, "resampling_unit": "target"})
    return pd.DataFrame(rows)


def final_model(data: pd.DataFrame, response: str, model: str, interactions: bool) -> tuple[dict, dict, list[str]]:
    cols = CONT_A if model == "A" else CONT_B
    scale = scaling(data, cols)
    x, names = design(data, model, scale, interactions)
    fit = fit_penalized(x, data[response].to_numpy(float), names)
    return fit, scale, names
