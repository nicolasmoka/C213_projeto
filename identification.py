def identificar_sundaresan(tempo, saida):
    VF = saida[-1]
    t1 = tempo[next(i for i, y in enumerate(saida) if y >= 0.353 * VF)]
    t2 = tempo[next(i for i, y in enumerate(saida) if y >= 0.853 * VF)]
    T = (t2 - t1) / 2
    theta = 1.3 * t1 - 0.29 * t2
    return T, theta