from scipy.io import loadmat
import pandas as pd
import numpy as np

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

# Classe que agrupa funções de filtragem dos dados
class filtragem:

    @staticmethod
    def filtrar_Configuracao_Experimento(data):
        item = data[0][0]
        valor1 = item[0].item()   # 150 (int)
        valor2 = item[1].item()   # 0.5 (float)
        valor3 = item[2].item()   # 0 (int)
        texto  = item[3].item()   # string "Escalón desde 0% - Alineamiento Smith perfecto"

        dict = {
            "tiempo_total":valor1,
            "dt": valor2,
            "degrau_tiempo":valor3,
            "descripcion":texto
        }

        return dict

    @staticmethod
    def filtrar_Parametros_Sistema(data):
        item = data[0][0]
        valores = []
        for elem in item:
            if hasattr(elem, "item"):  # Se for array numérico
                try:
                    valores.append(elem.item())
                except:
                    valores.append(elem[0])  # Caso seja array de string
            else:
                valores.append(elem)

        dicionario = {
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
            "descripcion": valores[11]  # pega a string, ignora o array duplicado
        }

        return dicionario

    @staticmethod
    def filtrar_Dados_Entrada(data):
        variavel_entrada = data[:, 0].tolist()  # valor crescente de +0.5 coluna 1
        degrau_valor_fixo_60 = data[:, 1].tolist() # valor fixo d e60 coluna 2
        return variavel_entrada, degrau_valor_fixo_60

    @staticmethod
    def filtrar_Dados_Saida(data):
        variavel_saida = data[:, 0].tolist() # valor crescente de +0.5
        coluna2 = data[:, 1].tolist()
        return variavel_saida, coluna2

    @staticmethod
    def filtrar_Entrada(data):
        entrada = data[0,:].tolist()
        return entrada
    
    @staticmethod
    def filtrar_Salida(data):
        salida = data[0,:].tolist()
        return salida
    
    @staticmethod
    def filtrar_Tiempo(data):
        tiempo = data[0,:].tolist()
        return tiempo

print("Configuração do Experimento:")
print(filtragem.filtrar_Configuracao_Experimento(configurcao_experimento))
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