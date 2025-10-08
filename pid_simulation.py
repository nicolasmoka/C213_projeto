import control as ctrl
import numpy as np

def simular_pid(Kp, Ti, Td, k, T, theta, tempo_final=100):
    # === Planta sem atraso ===
    Gp = ctrl.tf([k], [T, 1])

    # === Aproximação de Padé para o atraso ===
    num_pade, den_pade = ctrl.pade(theta, 1)  # ordem 1 para simplicidade
    atraso = ctrl.tf(num_pade, den_pade)

    # === Planta com atraso ===
    Gp_atrasada = ctrl.series(Gp, atraso)

    # === Controlador PID ===
    Gc = ctrl.tf([Kp * Td, Kp, Kp / Ti], [1, 0])

    # === Sistema em malha fechada ===
    sistema = ctrl.feedback(ctrl.series(Gc, Gp_atrasada), 1)

    # === Simulação da resposta ao degrau ===
    t = np.linspace(0, tempo_final, 1000)
    t, y = ctrl.step_response(sistema, T=t)
    return t, y