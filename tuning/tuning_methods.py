import numpy as np
from Filtragem_dados import filtragem

def chr_from_params(k, tau, theta):
    try:
        kp, Ti, Td = filtragem.calcularCHR((k, tau, theta))
        # sanitize
        kp = float(kp) if np.isfinite(kp := kp) else 0.0
        Ti = float(Ti) if np.isfinite(Ti := Ti) else max(1e-6, float(tau))
        Td = float(Td) if np.isfinite(Td := Td) else max(0.0, float(theta)/2)
        return (kp, Ti, Td)
    except Exception:
        try:
            Kp = 0.6 * tau / (k * theta)
        except Exception:
            Kp = 0.0
        Ti = float(tau) if tau is not None else 1.0
        Td = max(0.0, float(theta)/2 if theta is not None else 0.0)
        return (Kp, Ti, Td)

def itae_from_params(k, tau, theta):
    try:
        kp, Ti, Td = filtragem.calcularITAE((k, tau, theta))
        # sanitize outputs
        kp = float(kp) if np.isfinite(kp := kp) else 0.0
        Ti = float(Ti) if np.isfinite(Ti := Ti) else max(1e-6, float(tau))
        Td = float(Td) if np.isfinite(Td := Td) else max(0.0, float(theta)/4)
        # clamp Ti and Td to reasonable ranges relative to process tau to keep integral action meaningful
        tau_val = float(tau) if (tau is not None and np.isfinite(tau)) else 1.0
        min_Ti = max(1e-6, 0.01 * tau_val)
        max_Ti = max(1e-6, 10.0 * tau_val)
        Ti = min(max(Ti, min_Ti), max_Ti)
        min_Td = 0.0
        max_Td = max(0.0, 2.0 * tau_val)
        Td = min(max(Td, min_Td), max_Td)
        return (kp, Ti, Td)
    except Exception:
        try:
            Kp = (0.965 / k) * ((theta / tau) ** (-0.85))
        except Exception:
            Kp = 0.0
        try:
            Ti = (tau) / ((0.796 - 0.147) * (theta / tau))
        except Exception:
            Ti = max(1e-6, float(tau))
        try:
            Td = (tau * 0.308 * ((theta / tau) ** 0.929))
        except Exception:
            Td = max(0.0, float(theta)/4)
        # final sanity
        if not np.isfinite(Kp):
            Kp = 0.0
        if not np.isfinite(Ti) or Ti <= 0:
            Ti = max(1e-6, float(tau))
        if not np.isfinite(Td) or Td < 0:
            Td = max(0.0, float(theta)/4)
        return (float(Kp), float(Ti), float(Td))
