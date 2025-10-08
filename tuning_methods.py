def chr_sem_overshoot(k, T, theta):
    Kp = 0.6 * T / (k * theta)
    Ti = T
    Td = theta / 2
    return Kp, Ti, Td

def chr_com_overshoot(k, T, theta):
    Kp = 0.95 * T / (k * theta)
    Ti = 1.357 * T
    Td = 0.473 * theta
    return Kp, Ti, Td

def itae(k, T, theta):
    A = 0.965
    B = -0.85
    C = 0.796
    D = -0.147
    E = 0.308
    F = 0.929

    Kp = A / (k * (theta / T) ** B)
    Ti = T * (C + D * (theta / T))
    Td = F * theta * E * T / (T + theta)
    return Kp, Ti, Td