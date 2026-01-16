"""
核心计算模块：解析表达式、数值积分、绘图、矩阵与复数运算
依赖：sympy, numpy, scipy, matplotlib
"""
import ast
import numpy as np
import sympy as sp
from scipy import integrate
import matplotlib.pyplot as plt

# ===== 表达式评估 =====
def evaluate_expression(expr_str, subs=None):
    """
    评估表达式字符串。返回数值或复数或 SymPy 对象的数值形式。
    subs: 可选 dict，用于替换变量，例如 {'x': 1.23}
    """
    try:
        expr = sp.sympify(expr_str)
    except Exception as e:
        raise ValueError(f"解析表达式失败: {e}")
    if subs:
        try:
            numeric = expr.evalf(subs=subs)
            return complex(numeric) if numeric.is_real is False else float(numeric)
        except Exception:
            # fallback to lambdify
            pass
    # 若表达式包含符号且没有替换，返回表达式的字符串形式
    if expr.free_symbols:
        return expr  # 表示需要变量
    # 无符号，直接数值化
    try:
        val = complex(sp.N(expr))
        # 如果是实数，返回浮点
        if abs(val.imag) < 1e-12:
            return float(val.real)
        return val
    except Exception as e:
        raise ValueError(f"表达式数值化失败: {e}")

# ===== 定积分（数值） =====
def definite_integral(expr_str, var_str, a, b):
    """
    对 expr(var) 在 [a, b] 上做数值积分（使用 scipy.quad）。
    返回 (value, estimated_error)
    """
    try:
        var = sp.symbols(var_str)
        expr = sp.sympify(expr_str)
    except Exception as e:
        raise ValueError(f"解析表达式失败: {e}")
    f = sp.lambdify(var, expr, modules=["numpy", "math"])
    def wrapped(t):
        return np.real_if_close(f(t))
    try:
        val, err = integrate.quad(wrapped, a, b, limit=200)
        return val, err
    except Exception as e:
        raise ValueError(f"积分计算失败: {e}")

# ===== 函数绘图 =====
def plot_function(expr_str, var_str='x', a=-10, b=10, points=400, show=True):
    """
    绘制 y = expr(var) 在区间 [a, b] 上的图形，返回 matplotlib.figure.Figure
    """
    try:
        var = sp.symbols(var_str)
        expr = sp.sympify(expr_str)
    except Exception as e:
        raise ValueError(f"解析表达式失败: {e}")
    f = sp.lambdify(var, expr, modules=["numpy", "math"])
    x = np.linspace(a, b, points)
    try:
        y = f(x)
        y = np.array(y, dtype=np.complex128)
    except Exception as e:
        raise ValueError(f"函数数值化失败: {e}")
    fig, ax = plt.subplots(figsize=(6, 4))
    # 如果有虚部，绘制实部和虚部
    if np.max(np.abs(np.imag(y))) > 1e-12:
        ax.plot(x, np.real(y), label='Re')
        ax.plot(x, np.imag(y), label='Im', linestyle='--')
        ax.legend()
    else:
        ax.plot(x, np.real(y))
    ax.set_xlabel(var_str)
    ax.set_ylabel(f"f({var_str})")
    ax.grid(True)
    if show:
        fig.tight_layout()
    return fig

# ===== 矩阵运算 =====
def parse_matrix(text):
    """
    将文本表示（例如: [[1,2],[3,4]] 或 1,2;3,4）解析为 numpy.array
    """
    text = text.strip()
    # 尝试 python 风格 list 解析
    try:
        obj = ast.literal_eval(text)
        arr = np.array(obj, dtype=np.complex128)
        if arr.ndim != 2:
            raise ValueError("需要二维矩阵")
        return arr
    except Exception:
        # 尝试用分号分行、逗号分列
        try:
            rows = [row.strip() for row in text.split(';') if row.strip()]
            mat = [ [complex(x) for x in row.replace(',', ' ').split()] for row in rows ]
            arr = np.array(mat, dtype=np.complex128)
            return arr
        except Exception as e:
            raise ValueError(f"解析矩阵失败: {e}")

def matrix_add(A_text, B_text):
    A = parse_matrix(A_text); B = parse_matrix(B_text)
    if A.shape != B.shape:
        raise ValueError("矩阵维度不匹配")
    return A + B

def matrix_mul(A_text, B_text):
    A = parse_matrix(A_text); B = parse_matrix(B_text)
    if A.shape[1] != B.shape[0]:
        raise ValueError("矩阵内维度不匹配，无法相乘")
    return A.dot(B)

def matrix_inv(A_text):
    A = parse_matrix(A_text)
    return np.linalg.inv(A)

def matrix_det(A_text):
    A = parse_matrix(A_text)
    return np.linalg.det(A)

def matrix_eig(A_text):
    A = parse_matrix(A_text)
    vals, vecs = np.linalg.eig(A)
    return vals, vecs