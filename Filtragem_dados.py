import matplotlib.pyplot as plt
import control as ctrl
from scipy.io import loadmat
import numpy as np

# Importação do dataset .mat
dataset = loadmat('datasets/Dataset_Grupo1_c213.mat')

# Extração das variáveis do dicionário retornado pelo loadmat
configuracao_experimento = dataset["configuracion_experimento"]
parametros_sistema = dataset["parametros_sistema"]
dados_entrada = dataset["dados_entrada"]
dados_saida = dataset["dados_saida"]
entrada = dataset["entrada"]
salida = dataset["salida"]
tiempo = dataset["tiempo"]

class filtragem:

    @staticmethod
    def filtrar_Configuracao_Experimento(data):
        item = data[0][0]
        dict = {
            "tiempo_total": item[0].item(),
            "dt": item[1].item(),
            "degrau_tiempo": item[2].item(),
            "descripcion": item[3].item()
        }
        return dict

    @staticmethod
    def filtrar_Parametros_Sistema(data):
        item = data[0][0]
        valores = []
        for elem in item:
            try:
                valores.append(elem.item())
            except:
                valores.append(elem[0])
        return {
            "k": valores[0],
            "tau": valores[1],
            "theta": valores[2],
            "ruido": valores[3],
            "entrada_inicial": valores[4],
            "entrada_final": valores[5],
            "temp_inicial": valores[6],
            "amplitude_escalon": valores[7],
            "valor_final_teorico": valores[8],
            "valor_final_real": valores[9],
            "error_simulacion": valores[10],
            "descripcion": valores[11]
        }

    @staticmethod
    def filtrar_Dados_Entrada(data):
        return data[:, 0].tolist(), data[:, 1].tolist()

    @staticmethod
    def filtrar_Dados_Saida(data):
        return data[:, 0].tolist(), data[:, 1].tolist()

    @staticmethod
    def filtrar_Entrada(data):
        return data.flatten().tolist()

    @staticmethod
    def filtrar_Salida(data):
        return data.flatten().tolist()

    @staticmethod
    def filtrar_Tiempo(data):
        return data.flatten().tolist()

    @staticmethod
    def parametrosSistema(data):
        return data["k"], data["tau"], data["theta"]

    @staticmethod
    def calcularCHR(data):
        k, T, theta = data
        Kp = (0.6 * T) / (k * theta)
        Ti = T
        Td = theta / 2
        return Kp, Ti, Td

    @staticmethod
    def calcularITAE(data):
        k, T, theta = data
        Kp = (0.965 / k) * ((theta / T) ** -0.85)
        Ti = T / ((0.796 - 0.147) * (theta / T))
        Td = T * 0.308 * ((theta / T) ** 0.929)
        return Kp, Ti, Td

# Teste visual simples
print("Configuração do Experimento:")
print(filtragem.filtrar_Configuracao_Experimento(configuracao_experimento))
print("-" * 80)

print("Parâmetros do Sistema:")
print(filtragem.filtrar_Parametros_Sistema(parametros_sistema))
print("-" * 80)

print("Dados de Entrada:")
print(filtragem.filtrar_Dados_Entrada(dados_entrada))
print("-" * 80)

print("Dados de Saída:")
print(filtragem.filtrar_Dados_Saida(dados_saida))
print("-" * 80)

print("Entrada:")
print(filtragem.filtrar_Entrada(entrada))
print("-" * 80)

print("Saída:")
print(filtragem.filtrar_Salida(salida))
print("-" * 80)

print("Tempo:")
print(filtragem.filtrar_Tiempo(tiempo))
print("-" * 80)

# Plot simples do sinal filtrado
dados = filtragem.filtrar_Salida(salida)
x = range(len(dados))

plt.figure(figsize=(12, 6))
plt.plot(x, dados, label="Sinal")
plt.xlabel("Índice")
plt.ylabel("Valor")
plt.title("Plot da Lista de Valores")
plt.legend()
plt.grid(True)
plt.show()