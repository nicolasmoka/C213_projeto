from pyqtgraph import PlotWidget as PGPlotWidget, mkPen, ScatterPlotItem, InfiniteLine, TextItem
import numpy as np

class PlotWidget(PGPlotWidget):
    def __init__(self, parent=None, title=None):
        super().__init__(parent)
        if title:
            self.setTitle(title)
        self.showGrid(x=True, y=True)
        self._curves = {}
        self._markers = []

    def plot(self, x, y, name=None, **kwargs):
        # Use plotItem.plot for robustness
        if name is None:
            name = f'curve_{len(self._curves)}'
        pen = kwargs.pop('pen', mkPen(width=2))
        curve = self.plotItem.plot(x=np.asarray(x), y=np.asarray(y), pen=pen, name=name, **kwargs)
        self._curves[name] = curve
        return curve

    def clear(self):
        super().clear()
        self._curves.clear()
        # remove markers
        for it in self._markers:
            try:
                self.plotItem.removeItem(it)
            except Exception:
                pass
        self._markers.clear()

    # marker helpers
    def add_vline(self, x, label=None, pen=None):
        line = InfiniteLine(pos=x, angle=90, movable=False, pen=pen)
        self.plotItem.addItem(line)
        self._markers.append(line)
        if label:
            txt = TextItem(html=f'<div style="color:white;background:#333;padding:3px;border-radius:3px">{label}</div>', anchor=(0,1))
            txt.setPos(x, self.plotItem.viewRange()[1][1])  
            self.plotItem.addItem(txt)
            self._markers.append(txt)
        return line

    def add_point(self, x, y, label=None, size=8):
        sp = ScatterPlotItem([x], [y], size=size)
        self.plotItem.addItem(sp)
        self._markers.append(sp)
        if label:
            txt = TextItem(html=f'<div style="color:white;background:#333;padding:3px;border-radius:3px">{label}</div>', anchor=(0,1))
            txt.setPos(x, y)
            self.plotItem.addItem(txt)
            self._markers.append(txt)
        return sp
