[English](README.md) | 简体中文

# payslate-spike-hybrid-fuzzing

一个小探针：在一个玩具批次检查上写一个最小的 concolic 循环，看它跨过一道“求和相等”的门。目的是在一个小到能把每条路径读完的例子上，先弄清楚 concolic 引擎（SymCC）替我们自动做了什么，再把它接到真正的转换器上。

`concolic.py` 跑一个十字节的玩具检查——一个标记字节、两个三位数字的金额字段，以及一个必须等于两笔之和的三位数字声明合计——它把自己走过的每个分支的条件手工记成一条 Z3 公式，翻转最后一个分支，让 Z3 解出一个走另一条路的输入，再跑一遍。翻转“求和相等”这个分支，正是跨过门的那一步。

```sh
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python3 concolic.py
```

`compare.py` 在同一道门、同一个种子上，把这个循环和随机单字节变异放在一起比，随机数种子固定：

```sh
python3 compare.py
```

结论见 [FINDINGS.zh-CN.md](FINDINGS.zh-CN.md)。

## 关于本仓库

Elsworne、Payslate 和团队成员均为虚构。

本仓库的代码与文档借助 AI 工具编写；记录的输出都来自实际运行。
