import numpy as np
from scipy.signal import savgol_filter
from scipy.interpolate import interp1d
from models.system_model import SystemModel
from utils.metrics import eqm

SAVGOL_WINDOW = 11
SAVGOL_POLYORDER = 3
PADE_ORDER = 10

def _find_first_crossing_time(y, t, target):
    """
    Encontra a primeira vez em que y cruza 'target'.
    Faz interpolação linear entre amostras (i-1,i).
    Retorna time float; se não encontrado, retorna None.
    """
    y = np.asarray(y)
    t = np.asarray(t)
    # procura primeiro i tal que y[i] >= target
    for i in range(1, len(y)):
        if (y[i-1] <= target <= y[i]) or (y[i-1] >= target >= y[i]):
            y0, y1 = y[i-1], y[i]
            t0, t1 = t[i-1], t[i]
            if abs(y1 - y0) < 1e-12:
                return float(t0)
            alpha = (target - y0) / (y1 - y0)
            return float(t0 + alpha * (t1 - t0))
    return None

def smith_identification(t, y, amplitude=1.0, do_savgol=True, window=SAVGOL_WINDOW, polyorder=SAVGOL_POLYORDER, pade_order=PADE_ORDER):
    t = np.asarray(t)
    y = np.asarray(y)
    # smoothing
    if do_savgol and len(y) >= 5:
        w = window
        if w >= len(y):
            w = len(y) - 1 if (len(y)-1) % 2 == 1 else len(y)-2
        if w % 2 == 0:
            w += 1
        if w < 3:
            w = 3
        try:
            y_s = savgol_filter(y, w, polyorder)
        except Exception:
            y_s = y.copy()
    else:
        y_s = y.copy()

    y0 = float(y_s[0]); yf = float(y_s[-1])
    delta = yf - y0
    # percentis Smith (PDF)
    p1 = 0.283
    p2 = 0.632
    v1 = y0 + p1 * delta
    v2 = y0 + p2 * delta

    t1 = _find_first_crossing_time(y_s, t, v1)
    t2 = _find_first_crossing_time(y_s, t, v2)

    # fallbacks
    if t1 is None:
        # nearest index
        idx1 = (np.abs(y_s - v1)).argmin()
        t1 = float(t[idx1])
    if t2 is None:
        idx2 = (np.abs(y_s - v2)).argmin()
        t2 = float(t[idx2])

    tau = 1.5 * (t2 - t1)
    theta = t2 - tau
    if amplitude == 0:
        K = yf - y0
    else:
        K = (yf - y0) / amplitude

    # simulate open-loop model using plant with pade
    model = SystemModel(K, tau, theta, pade_order=pade_order)
    try:
        t_sim, y_sim = model.simulate_step_openloop(t)
    except Exception:
        # fallback: use linspace
        t_sim = t
        y_sim = np.interp(t_sim, t, y)  # fallback approximate

    # ensure float arrays
    t_sim = np.asarray(t_sim).astype(float)
    y_sim = np.asarray(y_sim).astype(float)

    # interpolate model to experimental t (safe usage of interp1d):
    f_sim = interp1d(t_sim, y_sim, bounds_error=False, fill_value=(y_sim[0], y_sim[-1]))
    y_hat = f_sim(t)

    eqm_val = eqm(y, y_hat)

    params = {"k": float(K), "tau": float(tau), "theta": float(theta), "eqm": float(eqm_val)}
    return params, t, y_hat
