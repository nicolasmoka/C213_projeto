from Filtragem_dados import filtragem

def chr_from_params(k, tau, theta):
    try:
        return filtragem.calcularCHR((k, tau, theta))
    except Exception:
        Kp = 0.6 * tau / (k * theta)
        Ti = tau
        Td = theta / 2
        return (Kp, Ti, Td)

def itae_from_params(k, tau, theta):
    try:
        return filtragem.calcularITAE((k, tau, theta))
    except Exception:
        Kp = (0.965 / k) * ((theta / tau) ** (-0.85))
        Ti = tau / ((0.796 - 0.147) * (theta / tau))
        Td = tau * 0.308 * ((theta / tau) ** 0.929)
        return (Kp, Ti, Td)
