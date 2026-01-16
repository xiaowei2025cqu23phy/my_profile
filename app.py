"""
简单的 PySimpleGUI 应用：按钮式操作面板，支持表达式求值、定积分、函数绘图与矩阵操作（演示）
运行：python app.py
"""
import io
import PySimpleGUI as sg
from core import evaluate_expression, definite_integral, plot_function, parse_matrix, matrix_add, matrix_mul, matrix_inv, matrix_det, matrix_eig
import matplotlib.pyplot as plt

# 布局
sg.theme('LightBlue')

left_col = [
    [sg.Input(key='-EXPR-', size=(28,1)), sg.Button('Eval', key='-EVAL-')],
    [sg.Multiline(key='-RESULT-', size=(40,6), disabled=True)],
    [sg.Text('积分: f(x)'), sg.Input('sin(x)', key='-INT_EXPR-', size=(18,1)), sg.Text('变量'), sg.Input('x', key='-INT_VAR-', size=(4,1))],
    [sg.Text('从'), sg.Input('-3.14', key='-INT_A-', size=(8,1)), sg.Text('到'), sg.Input('3.14', key='-INT_B-', size=(8,1)), sg.Button('Integrate', key='-INT-')],
    [sg.Text('_'*40)],
    [sg.Text('绘图: f(x)'), sg.Input('sin(x)', key='-PLOT_EXPR-', size=(18,1)), sg.Text('x from'), sg.Input('-6.28', key='-PLOT_A-', size=(6,1)), sg.Text('to'), sg.Input('6.28', key='-PLOT_B-', size=(6,1)), sg.Button('Plot', key='-PLOT-')],
]

right_col = [
    [sg.Frame('矩阵运算 (支持 Python 列表语法)', [
        [sg.Text('矩阵 A'), sg.Input('[[1,2],[3,4]]', key='-MA-', size=(30,1))],
        [sg.Text('矩阵 B'), sg.Input('[[5,6],[7,8]]', key='-MB-', size=(30,1))],
        [sg.Button('A + B', key='-MADD-'), sg.Button('A * B', key='-MMUL-'), sg.Button('inv(A)', key='-MINV-')],
        [sg.Button('det(A)', key='-MDET-'), sg.Button('eig(A)', key='-MEIG-')],
        [sg.Multiline(key='-MRES-', size=(40,8), disabled=True)]
    ])]
]

layout = [
    [sg.Column(left_col), sg.VerticalSeparator(), sg.Column(right_col)],
    [sg.Button('Exit')]
]

window = sg.Window('xiaowei Scientific Calculator (demo)', layout, finalize=True)

# 事件循环
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break

    try:
        if event == '-EVAL-':
            expr = values['-EXPR-'].strip()
            if not expr:
                window['-RESULT-'].update('请输入表达式')
                continue
            res = evaluate_expression(expr)
            window['-RESULT-'].update(str(res))

        if event == '-INT-':
            expr = values['-INT_EXPR-'].strip()
            var = values['-INT_VAR-'].strip() or 'x'
            a = float(values['-INT_A-'])
            b = float(values['-INT_B-'])
            val, err = definite_integral(expr, var, a, b)
            window['-RESULT-'].update(f"Integral [{a},{b}] = {val}  (err ~ {err})")

        if event == '-PLOT-':
            expr = values['-PLOT_EXPR-'].strip()
            a = float(values['-PLOT_A-'])
            b = float(values['-PLOT_B-'])
            fig = plot_function(expr, 'x', a, b, show=True)
            # 在新窗口显示 matplotlib 图形
            fig.show()

        # 矩阵操作事件
        if event == '-MADD-':
            A = values['-MA-']; B = values['-MB-']
            res = matrix_add(A, B)
            window['-MRES-'].update(str(res))

        if event == '-MMUL-':
            A = values['-MA-']; B = values['-MB-']
            res = matrix_mul(A, B)
            window['-MRES-'].update(str(res))

        if event == '-MINV-':
            A = values['-MA-']
            res = matrix_inv(A)
            window['-MRES-'].update(str(res))

        if event == '-MDET-':
            A = values['-MA-']
            res = matrix_det(A)
            window['-MRES-'].update(str(res))

        if event == '-MEIG-':
            A = values['-MA-']
            vals, vecs = matrix_eig(A)
            txt = f"eigenvalues:\n{vals}\neigenvectors:\n{vecs}"
            window['-MRES-'].update(txt)

    except Exception as e:
        window['-RESULT-'].update(f"错误: {e}")

window.close()