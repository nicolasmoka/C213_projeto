import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
import pyqtgraph as pg
from Filtragem_dados import filtragem
from scipy.io import loadmat
from tuning_methods import chr_com_overshoot, itae
from pid_simulation import simular_pid

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Controle PID - CHR com Overshoot")

        # === Carregar e filtrar dados ===
        dataset = loadmat('datasets/Dataset_Grupo1_c213.mat')
        entrada = filtragem.filtrar_Entrada(dataset["entrada"])
        salida = filtragem.filtrar_Salida(dataset["salida"])
        tiempo = filtragem.filtrar_Tiempo(dataset["tiempo"])
        dados_filtrados = salida  # já filtrado

        # === Usar parâmetros reais do sistema ===
        parametros = filtragem.filtrar_Parametros_Sistema(dataset["parametros_sistema"])
        k = parametros["k"]
        T = parametros["tau"]
        theta = parametros["theta"]

        # === Sintonia PID ===
        Kp, Ti, Td = chr_com_overshoot(k, T, theta) # se trocar o chr_com_overshoot por itae ele vai retornar o metodo itae 

        # === Simulação da resposta controlada ===
        t_sim, y_sim = simular_pid(Kp, Ti, Td, k, T, theta)

        # === Criar gráfico ===
        plot_widget = pg.PlotWidget()
        self.setCentralWidget(plot_widget)

        # Plotar sinal original
        plot_widget.plot(tiempo, dados_filtrados, pen=pg.mkPen(color='b', width=2), name="Sinal Original")

        # Plotar resposta simulada
        plot_widget.plot(t_sim, y_sim, pen=pg.mkPen(color='r', width=2), name="Resposta PID")

        # Personalização
        plot_widget.setLabel('left', 'Valor')
        plot_widget.setLabel('bottom', 'Tempo (s)')
        plot_widget.showGrid(x=True, y=True)
        plot_widget.addLegend()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1000, 600)
    window.show()
    sys.exit(app.exec_())