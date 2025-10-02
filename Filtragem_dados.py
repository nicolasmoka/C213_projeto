import numpy as np
import scipy.io

def _safe_item(x):
    try:
        return x.item()
    except Exception:
        return x
class filtragem:
    @staticmethod
    def filtrar_Configuracao_Experimento(data):
        item = data[0][0]
        valor1 = item[0].item()
        valor2 = item[1].item()
        valor3 = item[2].item()
        texto  = item[3].item()
        return {
            "tiempo_total":valor1,
            "dt": valor2,
            "degrau_tiempo":valor3,
            "descripcion":texto
        }

    @staticmethod
    def filtrar_Parametros_Sistema(data):
        item = data[0][0]
        valores = []
        for elem in item:
            if hasattr(elem, "item"):
                try:
                    valores.append(elem.item())
                except:
                    valores.append(elem[0])
            else:
                valores.append(elem)
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
        variavel_entrada = data[:, 0].tolist()
        degrau_valor_fixo_60 = data[:, 1].tolist()
        return variavel_entrada, degrau_valor_fixo_60

    @staticmethod
    def filtrar_Dados_Saida(data):
        variavel_saida = data[:, 0].tolist()
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

# wrapper de conveniência: retorna dicionário padronizado
def load_mat(path):
    mat = scipy.io.loadmat(path)
    out = {}
    keys = mat.keys()
    if "configuracion_experimento" in mat:
        out["config"] = filtragem.filtrar_Configuracao_Experimento(mat["configuracion_experimento"])
    if "parametros_sistema" in mat:
        out["params"] = filtragem.filtrar_Parametros_Sistema(mat["parametros_sistema"])
    if "dados_entrada" in mat:
        u1, u2 = filtragem.filtrar_Dados_Entrada(mat["dados_entrada"])
        out["dados_entrada"] = {"u": u1, "u_fixed": u2}
    if "dados_saida" in mat:
        y1, y2 = filtragem.filtrar_Dados_Saida(mat["dados_saida"])
        out["dados_saida"] = {"y": y1, "col2": y2}
    if "entrada" in mat:
        out["entrada"] = filtragem.filtrar_Entrada(mat["entrada"])
    if "salida" in mat:
        out["salida"] = filtragem.filtrar_Salida(mat["salida"])
    if "tiempo" in mat:
        out["tiempo"] = filtragem.filtrar_Tiempo(mat["tiempo"])
    # se tempo não existir, tenta criar a partir de config dt
    if "tiempo" not in out and "config" in out:
        dt = out["config"]["dt"]
        n = len(out["dados_saida"]["y"]) if "dados_saida" in out else 1
        out["tiempo"] = [i * dt for i in range(n)]
    # parâmetros do sistema padronizados
    if "params" in out:
        out["K"] = out["params"]["k"]
        out["tau"] = out["params"]["tau"]
        out["theta"] = out["params"]["theta"]
        out["amplitude"] = out["params"].get("amplitude_escalon", out["params"].get("entrada_final", None))
    return out