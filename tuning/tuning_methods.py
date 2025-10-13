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
    A = 0.965
    B = -0.85
    C = 0.796
    D = -0.147
    E = 0.308
    F = 0.929
    kp = ((A/k)*((theta/tau)**(B)))
    ti = ((tau)/(C+D*(theta/tau)))
    td = (tau*E*(theta/tau)**F)
    print(ti)
    return (kp, ti, td)