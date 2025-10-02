import numpy as np

def eqm(y_true, y_hat):
    y_true = np.asarray(y_true)
    y_hat = np.asarray(y_hat)
    return float(np.mean((y_true - y_hat) ** 2))

def compute_tr(t, y, low=0.1, high=0.9):
    t = np.asarray(t)
    y = np.asarray(y)
    y0 = y[0]; yf = y[-1]
    ylow = y0 + low * (yf - y0)
    yhigh = y0 + high * (yf - y0)
    try:
        idx_low = np.where(y >= ylow)[0][0]
        idx_high = np.where(y >= yhigh)[0][0]
        return float(t[idx_high] - t[idx_low])
    except Exception:
        return None

def compute_mp(y):
    y = np.asarray(y)
    yf = y[-1]
    Mp = (np.max(y) - yf) / abs(yf) if abs(yf) > 1e-9 else None
    return float(Mp) if Mp is not None else None

def compute_ts(t, y, tol=0.02):
    t = np.asarray(t); y = np.asarray(y)
    yf = y[-1]
    lower = yf * (1 - tol); upper = yf * (1 + tol)
    # find last time outside band, ts is next sample time
    idx_out = np.where((y < lower) | (y > upper))[0]
    if idx_out.size == 0:
        return float(t[0])
    last_out = idx_out[-1]
    if last_out + 1 < len(t):
        return float(t[last_out + 1])
    return float(t[-1])

def compute_ess(y):
    y = np.asarray(y)
    return float(y[-1] - y[0])
