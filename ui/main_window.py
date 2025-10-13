import os
import numpy as np
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel,
    QHBoxLayout, QFormLayout, QLineEdit, QComboBox, QFrame
)
from PyQt5.QtCore import Qt
from pyqtgraph import mkPen
from ui.plot_widget import PlotWidget
from Filtragem_dados import load_mat
from identification.smith import smith_identification
from tuning.tuning_methods import chr_from_params, itae_from_params
from models.system_model import SystemModel
from utils.metrics import compute_tr, compute_mp, compute_ts, eqm as eqm_func
from pyqtgraph.exporters import ImageExporter

DEFAULT_DATA_PATH = "datasets"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Projeto Prático C213 - Identificação e Sintonia PID")
        self.resize(1200, 720)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tab_id = QWidget()
        self.tab_pid = QWidget()
        self.tab_inicio = QWidget()
        # ordem: Inicio, Identificação, Controle PID
        self.tabs.addTab(self.tab_inicio, "Início")
        self.tabs.addTab(self.tab_id, "Identificação")
        self.tabs.addTab(self.tab_pid, "Controle PID")

        # estado
        self.current_data = None
        self.ident_params = None
        self.current_t = None
        self.current_u = None
        self.current_y = None

        # Aba Início (apresentação)
        inicio_layout = QVBoxLayout()
        title = QLabel("Projeto Prático C213 - Identificação e Sintonia PID")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 16px;")
        inicio_layout.addWidget(title)

        info = QLabel(
            "Grupo 1 — Ferramenta de identificação (Smith) e sintonia PID.\n\n"
            "Ferramentas: PyQt5, PyQtGraph, control, NumPy, SciPy.\n\n"
            "Carregue um dataset na aba Identificação para começar."
        )
        info.setAlignment(Qt.AlignCenter)
        info.setWordWrap(True)
        inicio_layout.addWidget(info)
        self.tab_inicio.setLayout(inicio_layout)

        # --- Aba Identificação ---
        left_id = QVBoxLayout()
        # único plot na aba de identificação
        self.plot_id = PlotWidget(title="Saída / Modelo / Degrau", enable_legend=True, zoom_slow_factor=0.02)
        left_id.addWidget(self.plot_id)

        # direita com botões/info
        right_frame = QFrame(); right_frame.setFrameShape(QFrame.StyledPanel)
        right_layout = QVBoxLayout(right_frame)

        self.btn_load = QPushButton("Escolher Arquivo (.mat)")
        right_layout.addWidget(self.btn_load)
        self.lbl_filename = QLabel("Selecione um dataset.")
        right_layout.addWidget(self.lbl_filename)
        # botão Identificação removido (identificação é automática ao carregar)

        form = QFormLayout()
        self.k_field = QLineEdit(); self.tau_field = QLineEdit(); self.theta_field = QLineEdit(); self.eqm_field = QLineEdit()
        for w in (self.k_field, self.tau_field, self.theta_field, self.eqm_field):
            w.setReadOnly(True); w.setFixedWidth(160)
        form.addRow("K:", self.k_field); form.addRow("τ:", self.tau_field); form.addRow("θ:", self.theta_field); form.addRow("EQM:", self.eqm_field)
        right_layout.addLayout(form)

        self.btn_export_id = QPushButton("Exportar Gráfico")
        self.btn_reset_id = QPushButton("Reset")
        right_layout.addWidget(self.btn_export_id); right_layout.addWidget(self.btn_reset_id)
        right_layout.addStretch()

        h_id = QHBoxLayout()
        h_id.addLayout(left_id, 3)
        h_id.addWidget(right_frame, 1)
        self.tab_id.setLayout(h_id)

        # --- Aba PID ---
        left_pid = QVBoxLayout()
        self.plot_pid = PlotWidget(title="Resposta do Controle PID", enable_legend=True, zoom_slow_factor=0.02)
        left_pid.addWidget(self.plot_pid)

        right_frame_pid = QFrame(); right_frame_pid.setFrameShape(QFrame.StyledPanel)
        right_layout_pid = QVBoxLayout(right_frame_pid)

        right_layout_pid.addWidget(QLabel("Seleção de Sintonia:"))
        self.mode_combo = QComboBox(); self.mode_combo.addItems(["Método", "Manual"])
        right_layout_pid.addWidget(self.mode_combo)
        right_layout_pid.addWidget(QLabel("Método (se Método):"))
        self.method_combo = QComboBox(); self.method_combo.addItems(["CHR", "ITAE"])
        right_layout_pid.addWidget(self.method_combo)

        pid_form = QFormLayout()
        self.kp_input = QLineEdit("0.0000"); self.ti_input = QLineEdit("0.0000"); self.td_input = QLineEdit("0.0000"); self.lambda_input = QLineEdit("0.0000")
        # SP field (vai ser preenchido ao carregar dataset)
        self.sp_input = QLineEdit("0.0000")
        # metric fields (read-only)
        self.tr_field = QLineEdit("0.0000"); self.ts_field = QLineEdit("0.0000"); self.mp_field = QLineEdit("0.0000")
        for w in (self.tr_field, self.ts_field, self.mp_field):
            w.setReadOnly(True); w.setFixedWidth(120)

        pid_form.addRow("Kp:", self.kp_input); pid_form.addRow("Ti:", self.ti_input); pid_form.addRow("Td:", self.td_input); pid_form.addRow("λ:", self.lambda_input)
        pid_form.addRow("SP:", self.sp_input)
        pid_form.addRow("tr:", self.tr_field); pid_form.addRow("ts:", self.ts_field); pid_form.addRow("Mp:", self.mp_field)
        right_layout_pid.addLayout(pid_form)

        self.btn_tune = QPushButton("Sintonizar e Simular")
        self.btn_export_pid = QPushButton("Exportar Gráfico")
        self.btn_reset_pid = QPushButton("Reset")
        right_layout_pid.addWidget(self.btn_tune); right_layout_pid.addWidget(self.btn_export_pid); right_layout_pid.addWidget(self.btn_reset_pid)
        right_layout_pid.addStretch()

        h_pid = QHBoxLayout()
        h_pid.addLayout(left_pid, 3)
        h_pid.addWidget(right_frame_pid, 1)
        self.tab_pid.setLayout(h_pid)

        # conexões
        self.btn_load.clicked.connect(self.load_file)
        # botão identificar removido: sem conexão
        self.btn_export_id.clicked.connect(lambda: self._export_plot(self.plot_id))
        self.btn_export_pid.clicked.connect(lambda: self._export_plot(self.plot_pid))
        self.btn_tune.clicked.connect(self.run_tune)
        self.btn_reset_id.clicked.connect(self.reset_identification)
        self.btn_reset_pid.clicked.connect(self.reset_pid)
        self.mode_combo.currentTextChanged.connect(self._update_mode_fields)
        self.method_combo.currentTextChanged.connect(self._update_method_fields)
        self._update_mode_fields(self.mode_combo.currentText())
        self._update_method_fields(self.method_combo.currentText())

    # --- funções ---
    def load_file(self):
        start_path = DEFAULT_DATA_PATH if os.path.isdir(DEFAULT_DATA_PATH) else "."
        fname, _ = QFileDialog.getOpenFileName(self, "Escolher .mat", start_path, "MAT files (*.mat)")
        if not fname:
            return
        try:
            self.current_data = load_mat(fname)
            self.lbl_filename.setText(os.path.basename(fname))

            # extrai vetores do dataset
            t = np.asarray(self.current_data.get("tiempo"))
            y = np.asarray(self.current_data.get("salida") if "salida" in self.current_data else self.current_data["dados_saida"]["y"])
            u = np.asarray(self.current_data.get("entrada") if "entrada" in self.current_data else self.current_data["dados_entrada"]["u_fixed"])

            self.current_t = t
            self.current_u = u
            self.current_y = y

            # define SP padrão a partir do dataset (amplitude do degrau)
            dataset_amp = None
            if isinstance(self.current_data, dict):
                dataset_amp = self.current_data.get('amplitude', None)
                if dataset_amp is None and 'params' in self.current_data:
                    try:
                        dataset_amp = float(self.current_data['params'].get('amplitude_escalon'))
                    except Exception:
                        dataset_amp = None
            if dataset_amp is None:
                try:
                    dataset_amp = float(np.mean(u))
                except Exception:
                    dataset_amp = 1.0

            # set SP UI para o valor do dataset (4 decimais)
            try:
                self.sp_input.setText(f"{float(dataset_amp):.4f}")
            except Exception:
                self.sp_input.setText("0.0000")

            # plota: degrau (u), saída experimental (y) — identificação será chamada automaticamente
            self.plot_id.clear()
            self.plot_id.plot(t, u, name="Degrau (u)", pen=mkPen(color='#1f77b4', width=1.2))
            self.plot_id.plot(t, y, name="Saída Experimental (y)", pen=mkPen(color='#111111', width=1.6))
            self.plot_id.autoscale()

            # executa identificação automaticamente
            self.run_identification()
        except Exception as e:
            self.lbl_filename.setText("Erro ao carregar: " + str(e))

    def run_identification(self):
            if not self.current_data:
                self.lbl_filename.setText("Carregue um .mat primeiro")
                return

            t = np.asarray(self.current_data.get("tiempo"))
            y = np.asarray(self.current_data.get("salida") if "salida" in self.current_data else self.current_data["dados_saida"]["y"])
            amplitude = self.current_data.get("amplitude", self.current_data.get("params",{}).get("amplitude_escalon", 1.0))

            # smith_identification agora retorna params, t_model, y_model
            params, t_model, y_model = smith_identification(t, y, amplitude=amplitude)
            self.ident_params = params

            # preenche campos identificacao
            self.k_field.setText(f"{params['k']:.4f}")
            self.tau_field.setText(f"{params['tau']:.4f}")
            self.theta_field.setText(f"{params['theta']:.4f}")

            # interpola y_model (modelo) para o grid experimental t para cálculo de EQM
            try:
                t_model = np.asarray(t_model).ravel()
                y_model = np.asarray(y_model).ravel()
                if np.array_equal(t_model, np.asarray(t).ravel()):
                    y_hat_on_t = y_model
                else:
                    y_hat_on_t = np.interp(np.asarray(t).ravel(), t_model, y_model)
                from utils.metrics import eqm as mse_func
                eqm_val = float(mse_func(np.asarray(y).ravel(), y_hat_on_t))
            except Exception:
                eqm_val = float(params.get('eqm', np.nan)) if isinstance(params, dict) else float(np.nan)

            self.eqm_field.setText(f"{eqm_val:.4f}")
            try:
                if isinstance(self.ident_params, dict):
                    self.ident_params['eqm'] = eqm_val
            except Exception:
                pass

            # Replot único gráfico: degrau (u), saída experimental (y) e modelo smith (ŷ)
            try:
                u = np.asarray(self.current_u) if hasattr(self, 'current_u') and self.current_u is not None else np.ones_like(t)
            except Exception:
                u = np.ones_like(t)

            self.plot_id.clear()
            self.plot_id.plot(t, u, name="Degrau (u)", pen=mkPen(color='red', width=1.2))
            self.plot_id.plot(t, y, name="Saída Experimental (y)", pen=mkPen(color='#111111', width=1.6))

            # plot model using t_model / y_model (o modelo pode ter sido simulado em t_model)
            try:
                self.plot_id.plot(t_model, y_model, name="Modelo Smith (ŷ)", pen=mkPen(color='green', width=2))
            except Exception:
                # se falhar, tente interpolar para t e plotar
                try:
                    y_hat_on_t = np.interp(np.asarray(t).ravel(), t_model, y_model)
                    self.plot_id.plot(t, y_hat_on_t, name="Modelo Smith (ŷ)", pen=mkPen(color='orange', width=2, style=Qt.DashLine))
                except Exception:
                    pass

            # marca t1,t2 aproximados a partir da saída experimental (para visual)
            try:
                y_s = y
                y0 = float(y_s[0]); yf = float(y_s[-1]); delta = yf - y0
                v1 = y0 + 0.283 * delta; v2 = y0 + 0.632 * delta
                idx1 = int(np.argmin(np.abs(y - v1)))
                idx2 = int(np.argmin(np.abs(y - v2)))
                t1 = float(t[idx1]); t2 = float(t[idx2])
                self.plot_id.add_vline(t1, label=f"t1={t1:.2f}s")
                self.plot_id.add_vline(t2, label=f"t2={t2:.2f}s")
            except Exception:
                pass

            self.plot_id.autoscale()
            self.tabs.setCurrentWidget(self.tab_id)


    def _update_mode_fields(self, mode_text):
        is_method = (mode_text == "Método")
        self.method_combo.setEnabled(is_method)
        self.kp_input.setReadOnly(is_method)
        self.ti_input.setReadOnly(is_method)
        self.td_input.setReadOnly(is_method)
        self._update_method_fields(self.method_combo.currentText())

    def _Update_method_fields_case_insensitive(self, method_text):
        return self._update_method_fields(method_text)

    def _update_method_fields(self, method_text):
        if str(method_text).upper() == "IMC":
            self.lambda_input.setReadOnly(False)
        else:
            self.lambda_input.setReadOnly(True)
            self.lambda_input.setText("0.0000")

    def run_tune(self):
        # decide valores kp, ti, td (método ou manual)
        if self.mode_combo.currentText() == "Método":
            if not self.ident_params:
                self.lbl_filename.setText("Identifique primeiro.")
                return
            method = self.method_combo.currentText()
            k = self.ident_params["k"]; tau = self.ident_params["tau"]; theta = self.ident_params["theta"]
            if method == "CHR":
                kp, ti, td = chr_from_params(k, tau, theta)
            elif method == "ITAE":
                kp, ti, td = itae_from_params(k, tau, theta)
            else:
                kp = ti = td = 0.0
            self.kp_input.setText(f"{kp:.4f}"); self.ti_input.setText(f"{ti:.4f}"); self.td_input.setText(f"{td:.4f}")
            self.kp_input.setReadOnly(True); self.ti_input.setReadOnly(True); self.td_input.setReadOnly(True)
        else:
            try:
                kp = float(self.kp_input.text()); ti = float(self.ti_input.text()); td = float(self.td_input.text())
            except Exception:
                self.lbl_filename.setText("Insira valores numéricos válidos no modo Manual")
                return

        # garante floats
        try:
            kp = float(self.kp_input.text()); ti = float(self.ti_input.text()); td = float(self.td_input.text())
        except Exception:
            kp = ti = td = 0.0

        # define vetor de tempo T
        if self.current_data and "tiempo" in self.current_data:
            T = np.asarray(self.current_data["tiempo"])
        else:
            T = np.linspace(0, 150, 500)

        params = self.ident_params or {"k":1.0,"tau":1.0,"theta":0.0}
        model = SystemModel(params["k"], params["tau"], params["theta"], pade_order=10)

        # decide sinal de entrada U com base no SP (UI) ou no dataset
        U = None
        try:
            sp_val_user = float(self.sp_input.text())
        except Exception:
            sp_val_user = None

        # amplitude dataset
        dataset_amp = None
        if self.current_data is not None:
            dataset_amp = self.current_data.get('amplitude', None)
            if dataset_amp is None and 'params' in self.current_data:
                try:
                    dataset_amp = float(self.current_data['params'].get('amplitude_escalon'))
                except Exception:
                    dataset_amp = None
        if dataset_amp is None and hasattr(self, 'current_u') and self.current_u is not None:
            try:
                dataset_amp = float(np.mean(np.asarray(self.current_u)))
            except Exception:
                dataset_amp = None

        # regra: se usuário forneceu SP e ele difere do dataset_amp → usar SP constante
        if sp_val_user is not None and dataset_amp is not None and (abs(sp_val_user - float(dataset_amp)) > 1e-6):
            U = np.ones_like(T, dtype=float) * float(sp_val_user)
        elif sp_val_user is not None and dataset_amp is None:
            U = np.ones_like(T, dtype=float) * float(sp_val_user)
        else:
            # usa sinal do dataset (interpolado para grid T se necessário)
            if hasattr(self, 'current_u') and self.current_u is not None:
                cu = np.asarray(self.current_u, dtype=float)
                if cu.shape == T.shape:
                    U = cu
                else:
                    try:
                        U = np.interp(T, np.linspace(T.min(), T.max(), num=cu.size), cu)
                    except Exception:
                        U = np.ones_like(T, dtype=float) * (float(dataset_amp) if dataset_amp is not None else 1.0)
            else:
                U = np.ones_like(T, dtype=float) * (float(dataset_amp) if dataset_amp is not None else 1.0)

        # simulação
        try:
            t_cl, y_cl = model.simulate_step_closedloop(kp, ti, td, T, U=U)
        except TypeError:
            try:
                t_cl, y_cl = model.simulate_step_closedloop(kp, ti, td, T)
            except Exception:
                t_cl = T; y_cl = np.zeros_like(T)
        except Exception:
            t_cl = T; y_cl = np.zeros_like(T)

        t_cl = np.asarray(t_cl); y_cl = np.asarray(y_cl)

        # plot no PID plot (apenas)
        self.plot_pid.clear()
        self.plot_pid.plot(t_cl, y_cl, name="Fechada (PID)", pen=mkPen(color='#333333', width=1.6))
        self.plot_pid.autoscale()

        # métricas (tr, mp, ts)
        tr = compute_tr(t_cl, y_cl) or 0.0
        mp = compute_mp(y_cl) or 0.0
        ts = compute_ts(t_cl, y_cl) or 0.0
        self.tr_field.setText(f"{tr:.4f}")
        self.ts_field.setText(f"{ts:.4f}")
        self.mp_field.setText(f"{mp:.4f}")

        # marcadores robustos
        try:
            if tr and tr > 0:
                self.plot_pid.add_vline(tr, label=f"tr={tr:.2f}s")
        except Exception:
            pass
        try:
            if (y_cl is not None) and (len(y_cl) > 0):
                idx_peak = int(np.argmax(y_cl))
                if 0 <= idx_peak < len(t_cl):
                    self.plot_pid.add_point(t_cl[idx_peak], y_cl[idx_peak], label=f"Mp={mp*100:.2f}%")
        except Exception:
            pass
        try:
            if ts and ts > 0:
                self.plot_pid.add_vline(ts, label=f"ts={ts:.2f}s")
        except Exception:
            pass

    def reset_identification(self):
        self.plot_id.clear()
        self.k_field.setText(""); self.tau_field.setText(""); self.theta_field.setText(""); self.eqm_field.setText("")
        self.lbl_filename.setText("Selecione um dataset.")
        self.current_data = None; self.ident_params = None
        self.current_t = None; self.current_u = None; self.current_y = None
        try:
            self.sp_input.setText("0.0000")
        except Exception:
            pass

    def reset_pid(self):
        self.plot_pid.clear()
        self.kp_input.setText("0.0000"); self.ti_input.setText("0.0000"); self.td_input.setText("0.0000")
        self.kp_input.setReadOnly(False); self.ti_input.setReadOnly(False); self.td_input.setReadOnly(False)
        self.tr_field.setText("0.0000"); self.ts_field.setText("0.0000"); self.mp_field.setText("0.0000")
        try:
            self.sp_input.setText("0.0000")
        except Exception:
            pass

    def _export_plot(self, plot_widget):
        try:
            exporter = ImageExporter(plot_widget.plotItem)
            fname, _ = QFileDialog.getSaveFileName(self, "Salvar figura", DEFAULT_DATA_PATH, "PNG Files (*.png)")
            if not fname:
                return
            if not fname.lower().endswith(".png"):
                fname += ".png"
            exporter.parameters()['width'] = 1600
            exporter.export(fname)
            self.lbl_filename.setText(f"Figura salva: {os.path.basename(fname)}")
        except Exception as e:
            self.lbl_filename.setText(f"Erro ao exportar: {e}")
