import numpy as np

def eqm(y_true, y_hat):
    y_true = np.asarray(y_true).ravel()
    y_hat = np.asarray(y_hat).ravel()
    if y_true.shape != y_hat.shape:
        xp = np.linspace(0, 1, num=len(y_hat))
        x = np.linspace(0, 1, num=len(y_true))
        y_hat = np.interp(x, xp, y_hat)
    return float(np.mean((y_true - y_hat) ** 2))

def compute_tr(t, y, low=0.1, high=0.9, sp=None):
    """
    Compute rise time between fractions low and high.
    If sp (setpoint) is provided, the final value is assumed to be sp.
    Otherwise the steady value is estimated as the mean of the last 5% of samples.
    """
    t = np.asarray(t).ravel()
    y = np.asarray(y).ravel()
    if len(t) < 2 or len(y) < 2:
        return None
    y0 = float(y[0])
    if sp is None:
        yf = float(np.mean(y[-max(1, int(0.05*len(y))):]))
    else:
        yf = float(sp)
    ylow = y0 + low * (yf - y0)
    yhigh = y0 + high * (yf - y0)
    try:
        idx_low = np.where(y >= ylow)[0][0]
        idx_high = np.where(y >= yhigh)[0][0]
        return float(t[idx_high] - t[idx_low])
    except Exception:
        return None

def compute_mp(y, sp=None):
    """
    Compute maximum overshoot as a fraction (e.g. 0.1 == 10%).
    If sp is provided, Mp is computed relative to sp; otherwise relative to estimated steady value.
    """
    y = np.asarray(y).ravel()
    if y.size == 0:
        return None
    if sp is None:
        yf = float(np.mean(y[-max(1, int(0.05*len(y))):]))
    else:
        yf = float(sp)
    if abs(yf) < 1e-9:
        return None
    Mp = (np.max(y) - yf) / abs(yf)
    return float(Mp)

def compute_ts(t, y, tol=0.02, sp=None):
    """
    Compute settling time as the first time the response remains within tol (fraction) of final value.
    If sp is provided, the final value is assumed to be sp.
    """
    t = np.asarray(t).ravel()
    y = np.asarray(y).ravel()
    if y.size == 0:
        return None
    if sp is None:
        yf = float(np.mean(y[-max(1, int(0.05*len(y))):]))
    else:
        yf = float(sp)
    lower = yf * (1 - tol); upper = yf * (1 + tol)
    idx_out = np.where((y < lower) | (y > upper))[0]
    if idx_out.size == 0:
        return float(t[0])
    last_out = int(idx_out[-1])
    if last_out + 1 < len(t):
        return float(t[last_out + 1])
    return float(t[-1])

def compute_ess(y, sp=None):
    """
    Erro em regime permanente.
    Se sp fornecido (setpoint real), compute ess = SP - steady_value.
    Senão, fallback para y[-1] - y[0].
    """
    y = np.asarray(y).ravel()
    if y.size == 0:
        return 0.0
    steady = float(np.mean(y[-max(1, int(0.05*len(y))):]))
    if sp is None:
        return float(steady - float(y[0]))
    return float(sp - steady)
