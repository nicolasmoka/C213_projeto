"""Static Matplotlib-based PlotWidget

Replaces the previous pyqtgraph interactive widget with a static
Matplotlib FigureCanvas that preserves a small subset of the old API
used by the app:

- plot(x, y, name=None, pen=None, clear_legend=False)
- clear()
- add_vline(x, label=None, pen=None)
- add_point(x, y, label=None, size=8, brush=None)
- add_text(x, y, label)
- autoscale(margin=0.05)

This keeps the rest of the application code unchanged while providing
static, non-interactive plots that are rendered once when drawn.
"""

from PyQt5.QtWidgets import QSizePolicy
import importlib
FigureCanvas = None
for mod_name in ("matplotlib.backends.backend_qtagg", "matplotlib.backends.backend_qt5agg", "matplotlib.backends.backend_qt4agg"):
    try:
        mod = importlib.import_module(mod_name)
        FigureCanvas = getattr(mod, "FigureCanvasQTAgg", None) or getattr(mod, "FigureCanvas", None)
        if FigureCanvas is not None:
            break
    except Exception:
        continue
if FigureCanvas is None:
    raise ImportError("Could not import a Qt FigureCanvas from Matplotlib backends")
from matplotlib.figure import Figure
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import numpy as np


class PlotWidget(FigureCanvas):
    def __init__(self, parent=None, title=None, enable_legend=True, zoom_slow_factor=None):
        fig = Figure(figsize=(5, 4), dpi=100)
        super().__init__(fig)
        self.setParent(parent)
        self.figure = fig
        self.ax = fig.add_subplot(111)
        self._curves = {}  # name -> Line2D
        self._markers = []
        self._enable_legend = bool(enable_legend)
        if title:
            try:
                self.ax.set_title(title)
            except Exception:
                pass
        # white background
        self.figure.patch.set_facecolor('white')
        self.ax.set_facecolor('white')
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()

    def plot(self, x, y, name=None, pen=None, clear_legend=False, **kwargs):
        """Plot x,y on the static Matplotlib axes.

        name: optional curve name used for legend management.
        pen: ignored (kept for API compatibility). Use kwargs for color/linestyle.
        """
        try:
            x = np.asarray(x, dtype=float)
            y = np.asarray(y, dtype=float)
        except Exception:
            x = np.array(list(x), dtype=float)
            y = np.array(list(y), dtype=float)
        if name is None:
            name = f"curve_{len(self._curves)}"
        if clear_legend:
            self.clear()
        # remove existing curve with same name
        if name in self._curves:
            ln = self._curves.pop(name)
            try:
                ln.remove()
            except Exception:
                pass
        # accept color and linewidth from kwargs to mimic pen
        color = kwargs.pop('color', None)
        linewidth = kwargs.pop('linewidth', 2)
        line, = self.ax.plot(x, y, label=name if self._enable_legend else None, color=color, linewidth=linewidth, **kwargs)
        self._curves[name] = line
        if self._enable_legend:
            try:
                # only create legend if there are labeled artists
                handles, labels = self.ax.get_legend_handles_labels()
                if any([lab for lab in labels if not str(lab).startswith('_') and str(lab) != '']):
                    self.ax.legend()
            except Exception:
                pass
        self.draw_idle()
        return line

    def clear(self):
        try:
            self.ax.cla()
        except Exception:
            pass
        self._curves.clear()
        # clear markers list
        self._markers.clear()
        if self._enable_legend:
            try:
                leg = self.ax.get_legend()
                if leg is not None:
                    leg.remove()
            except Exception:
                pass
        self.draw_idle()

    def add_vline(self, x, label=None, pen=None):
        try:
            vline = self.ax.axvline(x=float(x), color='#ffd700', linewidth=1)
            self._markers.append(vline)
            if label:
                # place label at top
                ymax = self.ax.get_ylim()[1]
                txt = self.ax.text(float(x), ymax, str(label), ha='center', va='bottom')
                self._markers.append(txt)
            self.draw_idle()
            return vline
        except Exception:
            return None

    def add_point(self, x, y, label=None, size=8, brush=None):
        try:
            sc = self.ax.scatter([float(x)], [float(y)], s=float(size)**2, c=[brush if brush is not None else 'C0'])
            self._markers.append(sc)
            if label:
                txt = self.ax.text(float(x), float(y), str(label), ha='left', va='bottom')
                self._markers.append(txt)
            self.draw_idle()
            return sc
        except Exception:
            return None

    def add_text(self, x, y, label):
        try:
            txt = self.ax.text(float(x), float(y), str(label), ha='right', va='top')
            self._markers.append(txt)
            self.draw_idle()
            return txt
        except Exception:
            return None

    def autoscale(self, margin=0.05):
        # autoscale based on existing curves
        try:
            self.ax.relim()
            self.ax.autoscale_view()
            # apply margin
            xmin, xmax = self.ax.get_xlim()
            ymin, ymax = self.ax.get_ylim()
            dx = (xmax - xmin) * margin if (xmax - xmin) != 0 else 1.0
            dy = (ymax - ymin) * margin if (ymax - ymin) != 0 else 1.0
            self.ax.set_xlim(xmin - dx, xmax + dx)
            self.ax.set_ylim(ymin - dy, ymax + dy)
            self.draw_idle()
        except Exception:
            pass
