"""
PyQt5 版演示 — 多曲线绘图增强
增强内容：
- 支持多条曲线输入（用分号或换行分隔表达式）
- 自动图例（每条曲线以表达式作为标签）
- 导出保存图像（PNG/SVG/PDF）
- 可切换显示网格与调整采样点数
运行:
    pip install -r requirements-pyqt.txt
    python app_pyqt.py
依赖: PyQt5, matplotlib, numpy, sympy, scipy (core.py 依赖)
"""
import sys
import numpy as np
import sympy as sp
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel, QGroupBox, QFormLayout, QMessageBox,
    QListWidget, QSpinBox, QCheckBox, QFileDialog
)
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from core import evaluate_expression, parse_matrix, matrix_add, matrix_mul, matrix_inv, matrix_det, matrix_eig

# A simple color/style cycle for multiple curves
_STYLE_CYCLE = [
    {'color': 'tab:blue', 'linestyle': '-'},
    {'color': 'tab:orange', 'linestyle': '--'},
    {'color': 'tab:green', 'linestyle': '-.'},
    {'color': 'tab:red', 'linestyle': ':'},
    {'color': 'tab:purple', 'linestyle': '-'},
    {'color': 'tab:brown', 'linestyle': '--'},
]

class CalcMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("xiaowei — PyQt Scientific Calculator (plotting enhanced)")
        self._init_ui()
        self.setMinimumSize(1000, 640)
        self.history = []
        self.memory = 0
        self.last_result = None

    def _init_ui(self):
        central = QWidget()
        main_layout = QHBoxLayout()
        central.setLayout(main_layout)
        self.setCentralWidget(central)

        # style
        self.setStyleSheet("""
            QPushButton { font-size: 13px; padding: 6px; }
            QLineEdit { font-size: 13px; }
            QTextEdit { font-family: monospace; font-size: 13px; }
            QLabel { font-size: 13px; }
        """)

        # Left: expression input / keypad / history (kept simple)
        left_box = QVBoxLayout()
        self.expr_input = QLineEdit()
        self.expr_input.setPlaceholderText("输入表达式，例如: sin(pi/4) + 3")
        self.expr_input.returnPressed.connect(self._on_eval)
        left_box.addWidget(self.expr_input)

        self.result_view = QTextEdit()
        self.result_view.setReadOnly(True)
        left_box.addWidget(self.result_view)

        # minimal keypad (same as before)
        keypad = QGridLayout()
        keys = [
            ('7',0,0),('8',0,1),('9',0,2),('/',0,3),('sin',0,4),
            ('4',1,0),('5',1,1),('6',1,2),('*',1,3),('cos',1,4),
            ('1',2,0),('2',2,1),('3',2,2),('-',2,3),('tan',2,4),
            ('0',3,0),('.',3,1),('(',3,2),(')',3,3),('log',3,4),
            ('^',4,0),('pi',4,1),('e',4,2),('+',4,3),('sqrt',4,4),
        ]
        for t,r,c in keys:
            b = QPushButton(t)
            b.clicked.connect(self._on_key)
            keypad.addWidget(b, r, c)
        left_box.addLayout(keypad)

        ctl_row = QHBoxLayout()
        eval_btn = QPushButton("=")
        eval_btn.clicked.connect(self._on_eval)
        clear_btn = QPushButton("C")
        clear_btn.clicked.connect(self._on_clear)
        ctl_row.addWidget(eval_btn)
        ctl_row.addWidget(clear_btn)
        left_box.addLayout(ctl_row)

        # history list
        left_box.addWidget(QLabel("History"))
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self._on_history_clicked)
        left_box.addWidget(self.history_list, 1)

        main_layout.addLayout(left_box, 2)

        # Right: Plot (top) and Matrix (bottom)
        right_box = QVBoxLayout()

        # Plot group with multi-curve support
        plot_group = QGroupBox("Plot (支持多曲线，分号或换行分隔表达式)")
        plot_layout = QVBoxLayout()
        form = QFormLayout()
        self.plot_expr = QLineEdit("sin(x); cos(x)")
        self.plot_a = QLineEdit("-6.28")
        self.plot_b = QLineEdit("6.28")
        range_row = QHBoxLayout()
        range_row.addWidget(QLabel("from"))
        range_row.addWidget(self.plot_a)
        range_row.addWidget(QLabel("to"))
        range_row.addWidget(self.plot_b)
        self.samples_spin = QSpinBox()
        self.samples_spin.setRange(100, 5000)
        self.samples_spin.setValue(800)
        range_row.addWidget(QLabel("Samples"))
        range_row.addWidget(self.samples_spin)
        self.grid_chk = QCheckBox("Show Grid")
        self.grid_chk.setChecked(True)
        range_row.addWidget(self.grid_chk)
        form.addRow("f(x):", self.plot_expr)
        form.addRow(range_row)
        plot_layout.addLayout(form)

        # matplotlib embedded canvas
        self.fig, self.ax = plt.subplots(figsize=(6,4))
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas)

        plot_btn_row = QHBoxLayout()
        self.plot_btn = QPushButton("Plot")
        self.plot_btn.clicked.connect(self._on_plot)
        self.save_btn = QPushButton("Save Plot")
        self.save_btn.clicked.connect(self._on_save_plot)
        plot_btn_row.addWidget(self.plot_btn)
        plot_btn_row.addWidget(self.save_btn)
        plot_layout.addLayout(plot_btn_row)

        plot_group.setLayout(plot_layout)
        right_box.addWidget(plot_group, 3)

        # Matrix group (unchanged)
        mat_group = QGroupBox("Matrix")
        mat_layout = QVBoxLayout()
        self.ma_edit = QLineEdit("[[1,2],[3,4]]")
        self.mb_edit = QLineEdit("[[5,6],[7,8]]")
        mat_layout.addWidget(QLabel("Matrix A"))
        mat_layout.addWidget(self.ma_edit)
        mat_layout.addWidget(QLabel("Matrix B"))
        mat_layout.addWidget(self.mb_edit)
        mbtn_row = QHBoxLayout()
        for t,k in [('A+B','add'),('A*B','mul'),('inv(A)','inv'),('det(A)','det'),('eig(A)','eig')]:
            b = QPushButton(t)
            b.clicked.connect(self._on_matrix)
            b.setProperty('op', k)
            mbtn_row.addWidget(b)
        mat_layout.addLayout(mbtn_row)
        self.mat_res = QTextEdit(); self.mat_res.setReadOnly(True)
        mat_layout.addWidget(self.mat_res)
        mat_group.setLayout(mat_layout)
        right_box.addWidget(mat_group, 2)

        main_layout.addLayout(right_box, 3)

    # keypad insertion
    def _on_key(self):
        t = self.sender().text()
        if t == '^': t = '**'
        cur = self.expr_input.cursorPosition()
        s = self.expr_input.text()
        new = s[:cur] + t + s[cur:]
        self.expr_input.setText(new)
        self.expr_input.setCursorPosition(cur + len(t))
        self.expr_input.setFocus()

    def _on_eval(self):
        expr = self.expr_input.text().strip()
        if not expr:
            self.result_view.setText("请输入表达式")
            return
        try:
            expr_for_eval = expr.replace('^','**')
            res = evaluate_expression(expr_for_eval)
            self.last_result = res
            self.result_view.setText(str(res))
            self.history.append((expr, res))
            self.history_list.addItem(f"{expr} = {res}")
        except Exception as e:
            self._show_error("Eval 错误", str(e))

    def _on_clear(self):
        self.expr_input.clear()
        self.result_view.clear()

    def _on_history_clicked(self, item):
        txt = item.text()
        if '=' in txt:
            expr = txt.split('=')[0].strip()
            self.expr_input.setText(expr)

    # Plot: supports multiple expressions; expressions separated by ';' or newline
    def _on_plot(self):
        raw = self.plot_expr.text().strip()
        if not raw:
            self._show_error("Plot 错误", "请输入至少一条表达式")
            return
        try:
            a = float(self.plot_a.text())
            b = float(self.plot_b.text())
            if a >= b:
                raise ValueError("a 必须小于 b")
            samples = int(self.samples_spin.value())
        except Exception as e:
            self._show_error("Range error", f"区间或采样参数无效: {e}")
            return

        # split expressions by ; or newline, ignore empty
        exprs = [e.strip() for part in raw.split(';') for e in part.splitlines() for e in [part] if part.strip()]
        # (alternate robust split)
        parts = []
        for chunk in raw.split(';'):
            for line in chunk.splitlines():
                s = line.strip()
                if s:
                    parts.append(s)
        exprs = parts

        xs = np.linspace(a, b, samples)
        self.ax.clear()
        plotted_any = False
        for idx, expr in enumerate(exprs):
            style = _STYLE_CYCLE[idx % len(_STYLE_CYCLE)]
            try:
                x = sp.symbols('x')
                expr_sym = sp.sympify(expr)
                f = sp.lambdify(x, expr_sym, modules=["numpy", "math"])
                ys = f(xs)
                ys = np.array(ys, dtype=np.complex128)
                if np.max(np.abs(np.imag(ys))) > 1e-12:
                    self.ax.plot(xs, np.real(ys), label=f"{expr} (Re)", color=style['color'], linestyle=style['linestyle'])
                    self.ax.plot(xs, np.imag(ys), label=f"{expr} (Im)", color=style['color'], linestyle='--')
                else:
                    self.ax.plot(xs, np.real(ys), label=expr, color=style['color'], linestyle=style['linestyle'])
                plotted_any = True
            except Exception as e:
                # show error for this expression but continue with others
                self._show_message("Plot warning", f"表达式 '{expr}' 绘图失败: {e}")
                continue

        if not plotted_any:
            self._show_error("Plot 错误", "没有有效曲线可绘制")
            return

        if self.grid_chk.isChecked():
            self.ax.grid(True)
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('f(x)')
        self.ax.legend()
        self.canvas.draw_idle()

    def _on_save_plot(self):
        # open file dialog and save current figure
        options = QFileDialog.Options()
        fname, fmt = QFileDialog.getSaveFileName(self, "Save plot", "", "PNG Files (*.png);;SVG Files (*.svg);;PDF Files (*.pdf);;All Files (*)", options=options)
        if not fname:
            return
        try:
            # matplotlib will guess format from extension; ensure directory exists
            self.fig.savefig(fname, bbox_inches='tight', dpi=150)
            self._show_message("Saved", f"Plot saved to: {fname}")
        except Exception as e:
            self._show_error("Save error", str(e))

    def _on_matrix(self):
        op = self.sender().property('op')
        A = self.ma_edit.text().strip()
        B = self.mb_edit.text().strip()
        try:
            if op == 'add':
                res = matrix_add(A, B)
                self.mat_res.setText(str(res))
            elif op == 'mul':
                res = matrix_mul(A, B)
                self.mat_res.setText(str(res))
            elif op == 'inv':
                res = matrix_inv(A)
                self.mat_res.setText(str(res))
            elif op == 'det':
                res = matrix_det(A)
                self.mat_res.setText(str(res))
            elif op == 'eig':
                vals, vecs = matrix_eig(A)
                txt = f"eigenvalues:\n{vals}\neigenvectors:\n{vecs}"
                self.mat_res.setText(txt)
        except Exception as e:
            self._show_error("Matrix 错误", str(e))

    def _show_error(self, title, msg):
        QMessageBox.critical(self, title, str(msg))

    def _show_message(self, title, msg):
        QMessageBox.information(self, title, str(msg))

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont('Arial', 11))
    w = CalcMainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()