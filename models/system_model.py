import numpy as np
import control as ctrl

PADE_ORDER_DEFAULT = 10

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

    def simulate_step_closedloop(self, Kp, Ti, Td, T):
        # PID in parallel form implemented as numerator [Kp*Td, Kp, Kp/Ti], denominator [1,0]
        pid = ctrl.tf([Kp * Td, Kp, Kp / Ti], [1, 0])
        plant = self.tf_with_delay()
        ol = ctrl.series(pid, plant)
        cl = ctrl.feedback(ol, 1)
        t, y = ctrl.step_response(cl, T)
        return t, np.asarray(y)
