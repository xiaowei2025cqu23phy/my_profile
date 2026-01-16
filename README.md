# xiaowei �� Python 科学计算桌面计算器（起始版）

这个项目目标是实现一个“像计算器一样”的 Python 应用，支持：
- 基本与科学数值计算（四则、三角、指数、对数等）
- 定积分数值计算
- 函数绘图（可视化 y = f(x)）
- 矩阵运算（加、乘、求逆、行列式、特征值）
- 复数运算
- 一个便捷的操作面板（按钮式界面，类似实体计算器）

技术栈（起始建议）
- GUI：PySimpleGUI（简单、小巧，易于快速打造面板）
- 数学与符号处理：SymPy
- 数值计算与矩阵：NumPy
- 数值积分：SciPy
- 绘图：Matplotlib

快速开始
1. 克隆或将代码放到项目目录。
2. 创建虚拟环境并安装依赖：
   python -m venv .venv
   source .venv/bin/activate   （Windows: .venv\Scripts\activate）
   pip install -r requirements.txt
3. 运行 GUI：
   python app.py

项目结构（示例）
- README.md
- requirements.txt
- core.py      # 计算核心：解析表达式、积分、绘图、矩阵
- app.py       # GUI 与交互

后续扩展建议
- 用 PyQt / PySide 切换到更强的 UI（更好美观与原生体验）
- 增加历史记录、记忆 M 存储、可编辑表达式栈
- 支持 LaTeX 渲染表达式
- 支持自定义函数与脚本插件
- 增加测试用例与 CI

如果你想我可以：
- 把界面改成基于 PyQt 的更精致版本
- 增加按键映射、键盘支持与主题
- 增加更完善的错误处理与单元测试