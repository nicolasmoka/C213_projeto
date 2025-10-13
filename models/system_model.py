import numpy as np
import control as ctrl

PADE_ORDER_DEFAULT = 20

class SystemModel:
    def __init__(self, K=1.0, tau=1.0, theta=0.0, pade_order=PADE_ORDER_DEFAULT):
        self.K = float(K)
        self.tau = float(tau)
        self.theta = float(theta)
        self.pade_order = int(pade_order)
        self.tf = ctrl.tf([self.K], [self.tau, 1.0])

    def tf_with_delay(self):
        if self.theta and self.pade_order > 0:
            num, den = ctrl.pade(self.theta, self.pade_order)
            pade_tf = ctrl.tf(num, den)
            return ctrl.series(self.tf, pade_tf)
        return self.tf

    def simulate_step_openloop(self, T):
        plant = self.tf_with_delay()
        t, y = ctrl.step_response(plant, T)
        return t, np.asarray(y)

    def simulate_forced_response(self, T, U):
        """Simula resposta forçada (open-loop) da planta para o sinal de entrada U.

        T: tempo (array)
        U: sinal de entrada (array com mesmo tamanho de T)
        Retorna (t_sim, y_sim)
        """
        plant = self.tf_with_delay()
        T = np.asarray(T)
        U = np.asarray(U, dtype=float)
        # if sizes differ, interpolate U to T
        if U.shape != T.shape:
            try:
                U = np.interp(T, np.linspace(T.min(), T.max(), num=U.size), U)
            except Exception:
                U = np.ones_like(T, dtype=float) * float(np.mean(U))
        try:
            t_sim, y_sim = ctrl.forced_response(plant, T=T, U=U)[:2]
        except Exception:
            resp = ctrl.forced_response(plant, T=T, U=U)
            t_sim, y_sim = resp[0], resp[1]
        return np.asarray(t_sim, dtype=float).ravel(), np.asarray(y_sim, dtype=float).ravel()

    def simulate_step_closedloop(self, Kp, Ti, Td, T, U=None, step_amplitude=1.0):
        """
        Simula resposta em malha fechada.
        - Se U for fornecido (mesmo tamanho de T), usa forced_response(sys, T, U)
        - Caso contrário, gera um degrau unitário * step_amplitude
        Retorna (t_sim, y_sim) numpy arrays.
        """
        # cria PID e planta (com possível atraso via pade)
        # guard against Ti being zero
        #Ti_safe = float(Ti) if (Ti is not None and np.isfinite(Ti) and Ti != 0) else 1e-6
        pid = ctrl.tf([Kp * Td, Kp, Kp / Ti], [1, 0])
        plant = self.tf_with_delay()
        ol = ctrl.series(pid, plant)
        cl = ctrl.feedback(ol, 1)

        # prepara sinal de entrada U
        T = np.asarray(T)
        if U is None:
            U = np.ones_like(T, dtype=float) * float(step_amplitude)
        else:
            U = np.asarray(U, dtype=float)
            # se U tiver tamanho diferente, tenta interpolar para grid T
            if U.shape != T.shape:
                U = np.interp(T, np.linspace(T.min(), T.max(), num=U.size), U)

        # usa forced_response para simular com o sinal U
        try:
            T_sim, Y_sim = ctrl.forced_response(cl, T=T, U=U)[:2]
        except Exception:
            # fallback para versões/instâncias do control que retornam 3-tupla ou se algo falhar
            resp = ctrl.forced_response(cl, T=T, U=U)
            T_sim, Y_sim = resp[0], resp[1]

        return [T_sim,Y_sim]

