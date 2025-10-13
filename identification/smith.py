import numpy as np
from scipy.signal import savgol_filter
from scipy.interpolate import interp1d
from models.system_model import SystemModel
from utils.metrics import eqm

SAVGOL_WINDOW = 11
SAVGOL_POLYORDER = 3
PADE_ORDER = 20

def _find_first_crossing_time(y, t, target):
    y = np.asarray(y)
    t = np.asarray(t)
    for i in range(1, len(y)):
        if (y[i-1] <= target <= y[i]) or (y[i-1] >= target >= y[i]):
            y0, y1 = y[i-1], y[i]
            t0, t1 = t[i-1], t[i]
            if abs(y1 - y0) < 1e-12:
                return float(t0)
            alpha = (target - y0) / (y1 - y0)
            return float(t0 + alpha * (t1 - t0))
    return None

def smith_identification(t, y, amplitude=1.0, u=None, do_savgol=True, window=SAVGOL_WINDOW, polyorder=SAVGOL_POLYORDER, pade_order=PADE_ORDER):
    """
    Retorna (params, t_model, y_model)
    - params: dict com k,tau,theta,eqm
    - t_model, y_model: tempo e saída simulada do modelo (no mesmo domínio de t_sim usado na simulação).
    """
    t = np.asarray(t).ravel()
    y = np.asarray(y).ravel()
    if t.size == 0 or y.size == 0:
        raise ValueError("t or y empty in smith_identification")

    # smoothing opcional para localizar melhor t1/t2
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
    p1 = 0.283
    p2 = 0.632
    v1 = y0 + p1 * delta
    v2 = y0 + p2 * delta

    t1 = _find_first_crossing_time(y_s, t, v1)
    t2 = _find_first_crossing_time(y_s, t, v2)

    if t1 is None:
        idx1 = (np.abs(y_s - v1)).argmin()
        t1 = float(t[idx1])
    if t2 is None:
        idx2 = (np.abs(y_s - v2)).argmin()
        t2 = float(t[idx2])

    tau = 1.5 * (t2 - t1)
    theta = t2 - tau
    tau = float(max(tau, 1e-6))
    theta = float(max(theta, 0.0))

    # ganho K ajustado pela amplitude do degrau do dataset
    if amplitude == 0 or amplitude is None:
        K = yf - y0
    else:
        K = (yf - y0) / amplitude

    model = SystemModel(K, tau, theta, pade_order=pade_order)
    try:
        # If input u is provided, simulate forced response on same T (preferred)
        if u is not None:
            t_sim, y_sim = model.simulate_forced_response(t, u)
        else:
            # simulate step response on the experimental time grid
            t_sim, y_sim = model.simulate_step_openloop(t)
    except Exception:
        # fallback: return something aligned to t
        t_sim = t
        y_sim = np.interp(t, t, y)

    t_sim = np.asarray(t_sim).astype(float).ravel()
    y_sim = np.asarray(y_sim).astype(float).ravel()

    # agora y_model (y_sim) está no grid t_sim. Para EQM, interpole y_sim em t experimental (t).
    # Interpole o modelo para o grid experimental usando numpy (robusto)
    try:
        t_sim = np.asarray(t_sim).ravel(); y_sim = np.asarray(y_sim).ravel()
        y_hat_on_t = np.interp(t, t_sim, y_sim)
    except Exception:
        y_hat_on_t = np.interp(t, t, y)

    eqm_val = eqm(y, y_hat_on_t)

    params = {"k": float(K), "tau": float(tau), "theta": float(theta), "eqm": float(eqm_val)}
    # retorno: params, t_model (t_sim), y_model (y_sim)
    return params, t_sim, y_sim