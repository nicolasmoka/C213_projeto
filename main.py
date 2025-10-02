import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
import pyqtgraph as pg
from Filtragem_dados import filtragem
from scipy.io import loadmat

#Importaçao do dataset .mat
dataset = loadmat('datasets/Dataset_Grupo1_c213.mat')

#Extração das variáveis do dicionário retornado pelo loadmat 
configurcao_experimento = dataset["configuracion_experimento"]
parametros_sistema = dataset["parametros_sistema"]
dados_entrada = dataset["dados_entrada"]
dados_saida = dataset["dados_saida"]
entrada = dataset["entrada"]
salida = dataset["salida"]
tiempo = dataset ["tiempo"]
# Sua lista de dados (resumida só como exemplo — use a completa que você mandou)
dados = filtragem.filtrar_Salida(salida)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gráfico com PyQt5 + PyQtGraph")

        # cria um widget de plotagem
        plot_widget = pg.PlotWidget()
        self.setCentralWidget(plot_widget)

        # eixo X (índices da lista)
        x = list(range(len(dados)))

        # plota os dados
        plot_widget.plot(x, dados, pen=pg.mkPen(color='b', width=2), name="Sinal")

        # personalização
        plot_widget.setLabel('left', 'Valor')
        plot_widget.setLabel('bottom', 'Índice')
        plot_widget.showGrid(x=True, y=True)
        plot_widget.addLegend()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 500)
    window.show()
    sys.exit(app.exec_())
