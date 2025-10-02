
import matplotlib.pyplot as plt
import control as ctrl
from scipy.io import loadmat
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
    
    @staticmethod
    def parametrosSistema(data):
        k = data["k"]
        tau = data["tau"]
        theta = data["theta"]
        return (k,tau,theta)
    
    @staticmethod
    def calcularCHR(data):
        k,T,theta = data
        kp = (0.6*(T))/(k*theta)
        Ti = T
        Td = theta/2
        return (kp,Ti,Td)

    @staticmethod
    def calcularITAE(data):
        k,T,theta = data
        kp = (0.965/k)*((theta/T)**(-0.85))
        Ti = T/((0.796-0.147)*(theta/T))
        Td = T * 0.308 * ((theta/T)**(0.929))
        return (kp,Ti,Td)

print("Configuração do Experimento:")
print(filtragem.filtrar_Configuracao_Experimento(configurcao_experimento))
print("-" * 80)

print("Parâmetros do Sistema:")
print(filtragem.filtrar_Parametros_Sistema(parametros_sistema))

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

dados = filtragem.filtrar_Salida(salida)
x = range(len(dados))

# plotar
plt.figure(figsize=(12, 6))
plt.plot(x, dados, label="Sinal")
plt.xlabel("Índice")
plt.ylabel("Valor")
plt.title("Plot da Lista de Valores")
plt.legend()
plt.grid(True)
plt.show()


'''
dic = filtragem.filtrar_Parametros_Sistema(parametros_sistema)
K,tau,theta  = filtragem.parametrosSistema(dic)

Kp, Ti, Td = filtragem.calcularCHR([K,tau,theta])

sys = ctrl.tf([K], [tau, 1])

# Aproximação de Padé para o atraso
num, den = ctrl.pade(theta, 20)
sys_pade = ctrl.tf(num, den)
sys_atraso = ctrl.series(sys, sys_pade)

# ---- PID COM VALORES FIXOS ----

PID = ctrl.tf([Kp*Td, Kp, Kp/Ti], [1, 0])

# Sistema em malha fechada
Cs = ctrl.series(PID, sys_atraso)
T = np.linspace(0, 150, 500)   # usa seu vetor fixo de tempo
t, y = ctrl.step_response(ctrl.feedback(Cs), T)

# Plota com amplitude escalada
amplitude = 60.0
plt.figure(figsize=(6,4))
plt.plot(t, y*amplitude, label='PID')
plt.title('Sistema com Controle PID (valores fixos)')
plt.xlabel('Tempo (s)')
plt.ylabel('Amplitude')
plt.grid(True)
plt.legend()
plt.show()

# Informações do sistema
infos_PID = ctrl.step_info(ctrl.feedback(Cs))
print('Parâmetros do Sistema Controlado:')
print(f'  - Tempo de subida: {infos_PID.get("RiseTime"):.2f} s')
print(f'  - Overshoot: {infos_PID.get("Overshoot"):.2f} %')
'''