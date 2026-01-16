"""
PyQt5 版演示：更像实体计算器的面板 + 绘图/矩阵面板
运行:
    pip install -r requirements-pyqt.txt
    python app_pyqt.py
依赖: PyQt5, matplotlib, numpy, sympy, scipy (core.py 依赖)
"""
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel, QGroupBox, QFormLayout, QMessageBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from core import evaluate_expression, definite_integral, plot_function, parse_matrix, matrix_add, matrix_mul, matrix_inv, matrix_det, matrix_eig

class CalcMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("xiaowei — PyQt Scientific Calculator (demo)")
        self._init_ui()
        self.setMinimumSize(900, 600)

    def _init_ui(self):
        central = QWidget()
        main_layout = QHBoxLayout()
        central.setLayout(main_layout)
        self.setCentralWidget(central)

        # 左侧: 显示 + 数字键盘 + 科学函数
        left_box = QVBoxLayout()
        self.expr_input = QLineEdit()
        self.expr_input.setPlaceholderText("输入表达式，例如: sin(pi/4) + 3")
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

        # 控制按钮
        eval_btn = QPushButton("Eval")
        eval_btn.clicked.connect(self._on_eval)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._on_clear)
        left_box.addLayout(keypad)
        ctl_row = QHBoxLayout()
        ctl_row.addWidget(eval_btn)
        ctl_row.addWidget(clear_btn)
        left_box.addLayout(ctl_row)

        main_layout.addLayout(left_box, 2)

        # 右侧: tabs (Plot 和 Matrix)
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

        # matplotlib canvas
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

    # slot: keypad buttons
    def _on_key(self):
        sender = self.sender()
        t = sender.text()
        # replace ^ with ** for python
        if t == '^':
            t = '**'
        # insert at cursor
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
            # some users use ^ for power; accept ** as well
            expr = expr.replace('^','**')
            res = evaluate_expression(expr)
            self.result_view.setText(str(res))
        except Exception as e:
            self._show_error("Eval 错误", str(e))

    def _on_clear(self):
        self.expr_input.clear()
        self.result_view.clear()

    def _on_plot(self):
        expr = self.plot_expr.text().strip()
        try:
            a = float(self.plot_a.text())
            b = float(self.plot_b.text())
        except Exception:
            self._show_error("Range error", "请输入有效的区间 a, b")
            return
        try:
            # use core.plot_function to get a matplotlib.figure
            fig = plot_function(expr, 'x', a, b, show=False)
            # clear existing axes and draw new figure into our canvas
            self.fig.clf()