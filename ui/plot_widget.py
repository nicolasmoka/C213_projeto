from pyqtgraph import PlotWidget as PGPlotWidget, PlotItem, ViewBox
import pyqtgraph as pg
from pyqtgraph import mkPen, ScatterPlotItem, InfiniteLine, TextItem
import numpy as np

# Tema claro (global para pyqtgraph)
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class SlowZoomViewBox(ViewBox):
    """
    ViewBox com zoom mais lento para a roda do mouse.
    """
    def __init__(self, zoom_slow_factor=0.02, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zoom_slow_factor = float(zoom_slow_factor)
        self.setMouseEnabled(x=True, y=True)

    def wheelEvent(self, ev, axis=None):
        try:
            delta = ev.angleDelta().y()
        except Exception:
            try:
                delta = ev.delta()
            except Exception:
                delta = 0
        if delta == 0:
            return
        if delta > 0:
            scale = 1.0 - self.zoom_slow_factor
        else:
            scale = 1.0 + self.zoom_slow_factor
        try:
            center = self.mapToView(ev.pos())
            self.scaleBy((scale, scale), center=center)
        except Exception:
            super().wheelEvent(ev, axis)

class PlotWidget(PGPlotWidget):
    def __init__(self, parent=None, title=None, enable_legend=True, zoom_slow_factor=0.2):
        view_box = SlowZoomViewBox(zoom_slow_factor=zoom_slow_factor)
        plot_item = PlotItem(viewBox=view_box)
        super().__init__(parent=parent, plotItem=plot_item)
        if title:
            try:
                self.plotItem.setTitle(title)
            except Exception:
                pass
        try:
            self.plotItem.showGrid(x=True, y=True, alpha=0.3)
        except Exception:
            pass
        self._curves = {}
        self._markers = []
        if enable_legend:
            try:
                self.plotItem.addLegend()
            except Exception:
                pass

    def plot(self, x, y, name=None, pen=None, clear_legend=False, **kwargs):
        """Plota com segurança. Converte x,y para numpy.float arrays."""
        try:
            x = np.asarray(x, dtype=float)
            y = np.asarray(y, dtype=float)
        except Exception:
            x = np.array(list(x), dtype=float)
            y = np.array(list(y), dtype=float)
        if pen is None:
            pen = mkPen(width=2)
        if name is None:
            name = f"curve_{len(self._curves)}"
        if clear_legend:
            self.clear()
        if getattr(self, "plotItem", None) is None:
            return None
        curve = self.plotItem.plot(x=x, y=y, pen=pen, name=name, **kwargs)
        self._curves[name] = curve
        return curve

    def clear(self):
        """Limpa curvas e marcadores."""
        try:
            super().clear()
        except Exception:
            try:
                if self.plotItem is not None:
                    self.plotItem.clear()
            except Exception:
                pass
        self._curves.clear()
        for it in list(self._markers):
            try:
                if getattr(self, "plotItem", None) is not None:
                    self.plotItem.removeItem(it)
            except Exception:
                pass
        self._markers.clear()
        if getattr(self, "plotItem", None) is not None:
            try:
                # re-create legend after clear (avoid duplicates)
                self.plotItem.addLegend()
            except Exception:
                pass

    def add_vline(self, x, label=None, pen=None):
        if getattr(self, "plotItem", None) is None:
            return None
        if pen is None:
            pen = mkPen(color='#ffd700', width=1)
        try:
            vline = InfiniteLine(pos=float(x), angle=90, pen=pen)
            self.plotItem.addItem(vline)
            self._markers.append(vline)
            if label:
                try:
                    vr = self.plotItem.viewRange()
                    ymax = vr[1][1]
                except Exception:
                    ymax = 0
                txt = TextItem(label, anchor=(0.5, 0))
                try:
                    txt.setPos(float(x), ymax)
                except Exception:
                    txt.setPos(float(x), 0)
                self.plotItem.addItem(txt)
                self._markers.append(txt)
            return vline
        except Exception:
            return None

    def add_point(self, x, y, label=None, size=8, brush=None):
        if getattr(self, "plotItem", None) is None:
            return None
        try:
            sp = ScatterPlotItem([float(x)], [float(y)], size=size, brush=brush)
            self.plotItem.addItem(sp)
            self._markers.append(sp)
            if label:
                txt = TextItem(label, anchor=(0, 1))
                txt.setPos(float(x), float(y))
                self.plotItem.addItem(txt)
                self._markers.append(txt)
            return sp
        except Exception:
            return None

    def add_text(self, x, y, label):
        if getattr(self, "plotItem", None) is None:
            return None
        try:
            txt = TextItem(label, anchor=(1, 1))
            txt.setPos(float(x), float(y))
            self.plotItem.addItem(txt)
            self._markers.append(txt)
            return txt
        except Exception:
            return None

    def autoscale(self, margin=0.05):
        if getattr(self, "plotItem", None) is None:
            return
        xs = []; ys = []
        for c in list(self._curves.values()):
            try:
                data = c.getData()
                if data is None:
                    continue
                x = np.asarray(data[0]); y = np.asarray(data[1])
                if x.size == 0 or y.size == 0:
                    continue
                xs.append((float(x.min()), float(x.max()))); ys.append((float(y.min()), float(y.max())))
            except Exception:
                continue
        try:
            if xs:
                xmin = min([a for a,b in xs]); xmax = max([b for a,b in xs])
                dx = (xmax - xmin) * margin if (xmax - xmin) != 0 else 1.0
                self.plotItem.setXRange(xmin - dx, xmax + dx, padding=0)
            if ys:
                ymin = min([a for a,b in ys]); ymax = max([b for a,b in ys])
                dy = (ymax - ymin) * margin if (ymax - ymin) != 0 else 1.0
                self.plotItem.setYRange(ymin - dy, ymax + dy, padding=0)
        except Exception:
            pass