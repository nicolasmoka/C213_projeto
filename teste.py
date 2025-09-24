import numpy as np
import matplotlib.pyplot as plt
import control as ctrl

# -------------------------------
# Parâmetros da planta (1ª ordem com atraso)
# -------------------------------
K = 1       # ganho da planta
T = 5       # constante de tempo
L = 2       # tempo morto

# Função de transferência da planta sem atraso
G = ctrl.tf([K], [T, 1])

# Aproximação de Padé para o atraso
num_pade, den_pade = ctrl.pade(L, 1)
G_pade = ctrl.series(ctrl.tf(num_pade, den_pade), G)

# -------------------------------
# MÉTODO CHR (com ultrapassagem)
# -------------------------------
Kp_chr = 0.6 * T / (K * L)
Ti_chr = T
Td_chr = 0.5 * L

# Controlador PID - CHR
num_chr = [Kp_chr * Td_chr, Kp_chr, Kp_chr / Ti_chr]
den_chr = [1, 0]
C_chr = ctrl.tf(num_chr, den_chr)

# -------------------------------
# MÉTODO ITAE (1ª ordem com atraso)
# -------------------------------
Kp_itae = 0.586 * (T / (K * L))
Ti_itae = L / (1.03 - 0.165 * (L / T))
Td_itae = 0.308 * L * ((L / T) ** 0.929)

# Controlador PID - ITAE
num_itae = [Kp_itae * Td_itae, Kp_itae, Kp_itae / Ti_itae]
den_itae = [1, 0]
C_itae = ctrl.tf(num_itae, den_itae)

# -------------------------------
# Impressão dos controladores
# -------------------------------
print("✅ Controlador CHR:")
print(C_chr)

print("\n✅ Controlador ITAE:")
print(C_itae)

# -------------------------------
# Simulação da resposta ao degrau
# -------------------------------
# Malha fechada CHR
sys_chr = ctrl.feedback(ctrl.series(C_chr, G_pade), 1)
t1, y1 = ctrl.step_response(sys_chr)

# Malha fechada ITAE
sys_itae = ctrl.feedback(ctrl.series(C_itae, G_pade), 1)
t2, y2 = ctrl.step_response(sys_itae)

# -------------------------------
# Plotagem dos gráficos
# -------------------------------
plt.figure(figsize=(10, 6))
plt.plot(t1, y1, label='CHR (com ultrapassagem)', linestyle='--')
plt.plot(t2, y2, label='ITAE', linestyle='-')
plt.title('Resposta ao Degrau - Controladores PID')
plt.xlabel('Tempo (s)')
plt.ylabel('Saída')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()