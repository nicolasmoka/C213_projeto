import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QTabWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QHBoxLayout, QFormLayout, QLineEdit, QComboBox, QFrame
from PyQt5.QtCore import Qt
from ui.plot_widget import PlotWidget
from Filtragem_dados import load_mat
from identification.smith import smith_identification
from tuning.tuning_methods import chr_from_params, itae_from_params
from models.system_model import SystemModel
from utils.metrics import compute_tr, compute_mp, compute_ts, eqm
import numpy as np
from pyqtgraph.exporters import ImageExporter

DEFAULT_DATA_PATH = "datasets"

def _make_right_panel_layout():
    frame = QFrame()
    frame.setFrameShape(QFrame.StyledPanel)
    layout = QVBoxLayout(frame)
    return frame, layout

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Projeto Identificação PID - Grupo 1")
        self.resize(1200, 720)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tab_id = QWidget(); self.tab_pid = QWidget(); self.tab_plots = QWidget()
        self.tabs.addTab(self.tab_id, "Identificação"); self.tabs.addTab(self.tab_pid, "Controle PID"); self.tabs.addTab(self.tab_plots, "Gráficos")

        # --- Identification tab: left plot + right panel ---
        id_left_layout = QVBoxLayout()
        self.plot_id = PlotWidget(title="Entrada / Saída (experimental)")
        id_left_layout.addWidget(self.plot_id)

        right_frame, right_layout = _make_right_panel_layout()
        # controls
        self.btn_load = QPushButton("Escolher Arquivo (.mat)")
        self.lbl_status = QLabel("Nenhum arquivo carregado")
        right_layout.addWidget(self.btn_load); right_layout.addWidget(self.lbl_status)
        # identification button
        self.btn_identify = QPushButton("Identificação (Smith)")
        right_layout.addWidget(self.btn_identify)

        form = QFormLayout()
        self.k_field = QLineEdit(); self.tau_field = QLineEdit(); self.theta_field = QLineEdit(); self.eqm_field = QLineEdit()
        for w in (self.k_field, self.tau_field, self.theta_field, self.eqm_field):
            w.setReadOnly(True)
        form.addRow("K:", self.k_field); form.addRow("τ:", self.tau_field); form.addRow("θ:", self.theta_field); form.addRow("EQM:", self.eqm_field)
        right_layout.addLayout(form)
        self.btn_export_id = QPushButton("Exportar Gráfico")
        right_layout.addWidget(self.btn_export_id)
        right_layout.addStretch()

        # assemble identification tab layout
        id_hbox = QHBoxLayout()
        id_hbox.addLayout(id_left_layout, 3)
        id_hbox.addWidget(right_frame, 1)
        self.tab_id.setLayout(id_hbox)

        # --- PID tab ---
        pid_left_layout = QVBoxLayout()
        self.plot_pid = PlotWidget(title="Resposta do Controle PID")
        pid_left_layout.addWidget(self.plot_pid)

        right_frame_pid, right_layout_pid = _make_right_panel_layout()
        self.mode_combo = QComboBox(); self.mode_combo.addItems(["Método", "Manual"])
        self.method_combo = QComboBox(); self.method_combo.addItems(["CHR","ITAE"])
        self.kp_input = QLineEdit("0.0"); self.ti_input = QLineEdit("0.0"); self.td_input = QLineEdit("0.0")
        self.sp_input = QLineEdit("20")  # setpoint default shows in your screenshot
        right_layout_pid.addWidget(QLabel("Seleção de Sintonia:"))
        right_layout_pid.addWidget(self.mode_combo)
        right_layout_pid.addWidget(QLabel("Método (se Método):"))
        right_layout_pid.addWidget(self.method_combo)
        pid_form = QFormLayout()
        pid_form.addRow("Kp:", self.kp_input); pid_form.addRow("Ti:", self.ti_input); pid_form.addRow("Td:", self.td_input)
        pid_form.addRow("SP:", self.sp_input)
        right_layout_pid.addLayout(pid_form)
        self.btn_tune = QPushButton("Sintonizar e Simular")
        self.btn_export_pid = QPushButton("Exportar Gráfico")
        right_layout_pid.addWidget(self.btn_tune); right_layout_pid.addWidget(self.btn_export_pid)
        right_layout_pid.addStretch()
        pid_hbox = QHBoxLayout()
        pid_hbox.addLayout(pid_left_layout, 3)
        pid_hbox.addWidget(right_frame_pid, 1)
        self.tab_pid.setLayout(pid_hbox)

        # --- Compare / Graphics tab (reuse plot_compare) ---
        plots_layout = QVBoxLayout()
        self.plot_compare = PlotWidget(title="Comparação: Aberta x Fechada")
        plots_layout.addWidget(self.plot_compare)
        self.tab_plots.setLayout(plots_layout)

        # state
        self.current_data = None
        self.ident_params = None

        # connections
        self.btn_load.clicked.connect(self.load_file)
        self.btn_identify.clicked.connect(self.run_identification)
        self.btn_tune.clicked.connect(self.run_tune)
        self.btn_export_id.clicked.connect(lambda: self._export_plot(self.plot_id))
        self.btn_export_pid.clicked.connect(lambda: self._export_plot(self.plot_pid))
        self.mode_combo.currentTextChanged.connect(self._update_mode_fields)
        self._update_mode_fields(self.mode_combo.currentText())

    def load_file(self):
        start_path = DEFAULT_DATA_PATH if os.path.isdir(DEFAULT_DATA_PATH) else "."
        fname, _ = QFileDialog.getOpenFileName(self, "Escolher .mat", start_path, "MAT files (*.mat)")
        if not fname:
            return
        try:
            self.current_data = load_mat(fname)
            self.lbl_status.setText(os.path.basename(fname))
            # plot entrada e saida
            t = np.asarray(self.current_data.get("tiempo"))
            if "salida" in self.current_data:
                y = np.asarray(self.current_data["salida"])
            else:
                y = np.asarray(self.current_data["dados_saida"]["y"])
            # entrada preferencialmente entrada else dados_entrada.u_fixed
            if "entrada" in self.current_data:
                u = np.asarray(self.current_data["entrada"])
            else:
                u = np.asarray(self.current_data["dados_entrada"]["u_fixed"])
            # draw
            self.plot_id.clear()
            self.plot_id.plot(t, u, name="Entrada (u)")
            self.plot_id.plot(t, y, name="Saída (y)")
            # auto-identify immediately
            self.run_identification()
        except Exception as e:
            self.lbl_status.setText("Erro ao carregar: " + str(e))

    def run_identification(self):
        if not self.current_data:
            self.lbl_status.setText("Carregue um .mat primeiro")
            return
        t = np.asarray(self.current_data.get("tiempo"))
        if "salida" in self.current_data:
            y = np.asarray(self.current_data["salida"])
        else:
            y = np.asarray(self.current_data["dados_saida"]["y"])
        amplitude = self.current_data.get("amplitude", None) or self.current_data.get("params",{}).get("amplitude_escalon", 1.0)
        params, t_model, y_hat = smith_identification(t, y, amplitude=amplitude)
        self.ident_params = params
        self.k_field.setText(f"{params['k']:.6g}")
        self.tau_field.setText(f"{params['tau']:.6g}")
        self.theta_field.setText(f"{params['theta']:.6g}")
        self.eqm_field.setText(f"{params['eqm']:.6g}")
        # update compare and id plots
        self.plot_compare.clear()
        model = SystemModel(params["k"], params["tau"], params["theta"], pade_order=10)
        t_sim, y_sim = model.simulate_step_openloop(t)
        self.plot_compare.plot(t_sim, y_sim, name="Modelo Aberto (Smith)")
        self.plot_compare.plot(t, y, name="Saída Experimental")
        # mark key points (on experiment)
        # compute metrics on open-loop experimental signal
        try:
            # use utils functions for tr/mp/ts but those expect closed-loop; we'll compute approximate markers from y_hat or y
            tr = compute_tr(t, y_hat)  # time of rise from model
            # mark on compare plot if found
            if tr:
                self.plot_compare.add_vline(tr, label=f"tr={tr:.2f}s")
        except Exception:
            pass

    def _update_mode_fields(self, mode_text):
        is_method = (mode_text == "Método")
        self.method_combo.setEnabled(is_method)
        self.kp_input.setReadOnly(is_method)
        self.ti_input.setReadOnly(is_method)
        self.td_input.setReadOnly(is_method)

    def run_tune(self):
        if self.mode_combo.currentText() == "Método":
            if not self.ident_params:
                self.lbl_status.setText("Identifique o sistema primeiro")
                return
            method = self.method_combo.currentText()
            k = self.ident_params["k"]; tau = self.ident_params["tau"]; theta = self.ident_params["theta"]
            if method == "CHR":
                kp, ti, td = chr_from_params(k, tau, theta)
            else:
                kp, ti, td = itae_from_params(k, tau, theta)
            self.kp_input.setText(f"{kp:.6g}"); self.ti_input.setText(f"{ti:.6g}"); self.td_input.setText(f"{td:.6g}")
            self.kp_input.setReadOnly(True); self.ti_input.setReadOnly(True); self.td_input.setReadOnly(True)
        else:
            try:
                kp = float(self.kp_input.text()); ti = float(self.ti_input.text()); td = float(self.td_input.text())
            except Exception:
                self.lbl_status.setText("Insira valores numéricos no modo Manual")
                return

        # get final values (either method-set or manual)
        kp = float(self.kp_input.text()); ti = float(self.ti_input.text()); td = float(self.td_input.text())
        if self.current_data and "tiempo" in self.current_data:
            T = np.asarray(self.current_data["tiempo"])
        else:
            T = np.linspace(0, 150, 500)
        params = self.ident_params or {"k":1.0,"tau":1.0,"theta":0.0}
        model = SystemModel(params["k"], params["tau"], params["theta"], pade_order=10)
        t_cl, y_cl = model.simulate_step_closedloop(kp, ti, td, T)
        # plot
        self.plot_pid.clear()
        self.plot_pid.plot(t_cl, y_cl, name=f"Fechada (PID)")
        # compute metrics and add markers
        tr = compute_tr(t_cl, y_cl)
        mp = compute_mp(y_cl)
        ts = compute_ts(t_cl, y_cl)
        # mark tr, mp, ts
        if tr:
            self.plot_pid.add_vline(tr, label=f"tr={tr:.2f}s")
        if mp is not None and y_cl is not None:
            idx_peak = np.argmax(y_cl)
            self.plot_pid.add_point(t_cl[idx_peak], y_cl[idx_peak], label=f"Mp={mp*100:.2f}%")
        if ts:
            self.plot_pid.add_vline(ts, label=f"ts={ts:.2f}s")
        self.lbl_status.setText(f"Sintonizado. tr={tr}, Mp={mp}, ts={ts}")

    def _export_plot(self, plot_widget):
        exporter = ImageExporter(plot_widget.plotItem)
        fname, _ = QFileDialog.getSaveFileName(self, "Salvar figura", DEFAULT_DATA_PATH, "PNG Files (*.png)")
        if not fname:
            return
        if not fname.lower().endswith(".png"):
            fname += ".png"
        exporter.parameters()['width'] = 1200
        exporter.export(fname)
        self.lbl_status.setText(f"Figura salva: {fname}")