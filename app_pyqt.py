"""
PyQt5 版演示：更像实体计算器的面板 + 绘图/矩阵面板
增强：改进嵌入绘图、键盘支持、历史和内存键、样式美化
运行:
    pip install -r requirements-pyqt.txt
    python app_pyqt.py
依赖: PyQt5, matplotlib, numpy, sympy, scipy (core.py 依赖)
"""
import sys
import numpy as np
import sympy as sp
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel, QGroupBox, QFormLayout, QMessageBox,
    QListWidget, QShortcut
)
from PyQt5.QtGui import QFont, QKeySequence
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from core import evaluate_expression, parse_matrix, matrix_add, matrix_mul, matrix_inv, matrix_det, matrix_eig

class CalcMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("xiaowei — PyQt Scientific Calculator (enhanced)")
        self._init_ui()
        self.setMinimumSize(980, 620)
        self.history = []  # list of (expr, result)
        self.memory = 0    # memory register (numeric or complex)
        self.last_result = None

    def _init_ui(self):
        central = QWidget()
        main_layout = QHBoxLayout()
        central.setLayout(main_layout)
        self.setCentralWidget(central)

        # 全局样式
        self.setStyleSheet("""
            QPushButton { font-size: 14px; padding: 6px; }
            QLineEdit { font-size: 14px; }
            QTextEdit { font-family: monospace; font-size: 13px; }
        """
        )

        # 左侧: 显示 + 数字键盘 + 科学函数
        left_box = QVBoxLayout()
        self.expr_input = QLineEdit()
        self.expr_input.setPlaceholderText("输入表达式，例如: sin(pi/4) + 3")
        self.expr_input.returnPressed.connect(self._on_eval)  # Enter 键评估
        left_box.addWidget(self.expr_input)

        self.result_view = QTextEdit()
        self.result_view.setReadOnly(True)
        left_box.addWidget(self.result_view)

        # 键盘区域
        keypad = QGridLayout()
        buttons = [
            ('7',0,0),('8',0,1),('9',0,2),('/',0,3),('sin',0,4),
            ('4',1,0),('5',1,1),('6',1,2),('*',1,3),('cos',1,4),
            ('1',2,0),('2',2,1),('3',2,2),('-',2,3),('tan',2,4),
            ('0',3,0),('.',3,1),('(',3,2),(')',3,3),('log',3,4),
            ('^',4,0),('pi',4,1),('e',4,2),('+',4,3),('sqrt',4,4),
        ]
        for text,r,c in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(self._on_key)
            keypad.addWidget(btn, r, c)

        # 控制按钮和内存键
        eval_btn = QPushButton("=")
        eval_btn.setToolTip('Evaluate (Enter)')
        eval_btn.clicked.connect(self._on_eval)
        clear_btn = QPushButton("C")
        clear_btn.setToolTip('Clear (Esc)')
        clear_btn.clicked.connect(self._on_clear)

        mplus = QPushButton('M+')
        mplus.clicked.connect(self._on_m_plus)
        mminus = QPushButton('M-')
        mminus.clicked.connect(self._on_m_minus)
        mr = QPushButton('MR')
        mr.clicked.connect(self._on_mr)
        mc = QPushButton('MC')
        mc.clicked.connect(self._on_mc)

        left_box.addLayout(keypad)
        ctl_row = QHBoxLayout()
        ctl_row.addWidget(eval_btn)
        ctl_row.addWidget(clear_btn)
        ctl_row.addWidget(mplus)
        ctl_row.addWidget(mminus)
        ctl_row.addWidget(mr)
        ctl_row.addWidget(mc)
        left_box.addLayout(ctl_row)

        # 历史列表
        hist_label = QLabel('History')
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self._on_history_clicked)
        left_box.addWidget(hist_label)
        left_box.addWidget(self.history_list, 1)

        main_layout.addLayout(left_box, 2)

        # 右侧: Plot 和 Matrix
        right_box = QVBoxLayout()

        # Plot group
        plot_group = QGroupBox("Plot")
        plot_layout = QVBoxLayout()
        form = QFormLayout()
        self.plot_expr = QLineEdit("sin(x)")
        self.plot_a = QLineEdit("-6.28")
        self.plot_b = QLineEdit("6.28")
        form.addRow("f(x):", self.plot_expr)
        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("from"))
        range_layout.addWidget(self.plot_a)
        range_layout.addWidget(QLabel("to"))
        range_layout.addWidget(self.plot_b)
        form.addRow(range_layout)
        plot_layout.addLayout(form)

        # matplotlib canvas (single figure reused)
        self.fig, self.ax = plt.subplots(figsize=(5,3))
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas)

        plot_btn = QPushButton("Plot")
        plot_btn.clicked.connect(self._on_plot)
        plot_layout.addWidget(plot_btn)
        plot_group.setLayout(plot_layout)
        right_box.addWidget(plot_group)

        # Matrix group
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
        right_box.addWidget(mat_group)

        main_layout.addLayout(right_box, 3)

        # 快捷键: Esc 清空, Ctrl+H 清除历史
        QShortcut(QKeySequence('Esc'), self, activated=self._on_clear)
        QShortcut(QKeySequence('Ctrl+H'), self, activated=self._clear_history)

    # slot: keypad buttons
    def _on_key(self):
        sender = self.sender()
        t = sender.text()
        # replace ^ with ** for python
        if t == '^':
            t = '**'
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
            # 显示
            self.result_view.setText(str(res))
            # 追加历史
            self.history.append((expr, res))
            self.history_list.addItem(f"{expr} = {res}")
        except Exception as e:
            self._show_error("Eval 错误", str(e))

    def _on_clear(self):
        self.expr_input.clear()
        self.result_view.clear()

    # Memory operations
    def _on_m_plus(self):
        if self.last_result is None:
            return
        try:
            self.memory = complex(self.memory) + complex(self.last_result)
        except Exception:
            # ignore if not numeric
            pass
        self._show_message('Memory', f'Memory = {self.memory}')

    def _on_m_minus(self):
        if self.last_result is None:
            return
        try:
            self.memory = complex(self.memory) - complex(self.last_result)
        except Exception:
            pass
        self._show_message('Memory', f'Memory = {self.memory}')

    def _on_mr(self):
        # recall
        self.expr_input.insert(str(self.memory))

    def _on_mc(self):
        self.memory = 0
        self._show_message('Memory', 'Memory cleared')

    def _on_history_clicked(self, item):
        # 点击历史条目时，将表达式放入输入框
        txt = item.text()
        if '=' in txt:
            expr = txt.split('=')[0].strip()
            self.expr_input.setText(expr)

    def _clear_history(self):
        self.history = []
        self.history_list.clear()

    def _on_plot(self):
        expr = self.plot_expr.text().strip()
        try:
            a = float(self.plot_a.text())
            b = float(self.plot_b.text())
        except Exception:
            self._show_error("Range error", "请输入有效的区间 a, b")
            return
        if a >= b:
            self._show_error("Range error", "确保 a < b")
            return
        try:
            # 使用 sympy 将表达式转换为数值函数并在当前 Axes 上绘图
            x = sp.symbols('x')
            expr_sym = sp.sympify(expr)
            f = sp.lambdify(x, expr_sym, modules=["numpy", "math"])
            xs = np.linspace(a, b, 800)
            ys = f(xs)
            ys = np.array(ys, dtype=np.complex128)
            self.ax.clear()
            if np.max(np.abs(np.imag(ys))) > 1e-12:
                self.ax.plot(xs, np.real(ys), label='Re')
                self.ax.plot(xs, np.imag(ys), label='Im', linestyle='--')
                self.ax.legend()
            else:
                self.ax.plot(xs, np.real(ys))
            self.ax.set_xlabel('x')
            self.ax.set_ylabel(f'f(x)')
            self.ax.grid(True)
            self.canvas.draw_idle()
        except Exception as e:
            self._show_error("Plot 错误", str(e))

    def _on_matrix(self):
        sender = self.sender()
        op = sender.property('op')
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
        QMessageBox.critical(self, title, msg)

    def _show_message(self, title, msg):
        QMessageBox.information(self, title, msg)


def main():
    app = QApplication(sys.argv)
    # 更好看的默认字体
    app.setFont(QFont('Arial', 11))
    w = CalcMainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()