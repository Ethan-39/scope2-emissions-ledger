# Scope 2 Emissions Ledger｜范围二排放台账

一个标准库 Python 教学项目：创建小型合成用电活动台账，并对同一批活动数据分别按 location-based（基于位置）和 market-based（基于市场）口径计算 Scope 2 排放量，输出逐行明细和汇总。

## 运行

需要 Python 3.10 或以上版本，在项目目录运行：

```powershell
python scope2_emissions_ledger.py
python scope2_emissions_ledger.py --seed 7
python -m unittest discover -s tests -v
```

运行后生成 `data/electricity_activity.csv`、`results/line_items.csv` 和 `results/report.json`。同一个随机种子会生成相同活动数据；改变种子只改变合成用电量。

## 计算内容

活动表以设施和季度为粒度，记录 kWh 与两个示例排放因子。每条活动分别计算：`排放量（kg CO2e）= 用电量（kWh）× 排放因子（kg CO2e/kWh）`。结果按核算方法与设施汇总，并给出两种方法总量差异。

location-based 与 market-based 是两种不同数据口径，不应混为同一因子：前者示意电网平均排放信息，后者示意与供应商或合同工具相关的排放信息。真实核算涉及因子来源、期间、地区、合同凭证与适用规则；本项目没有验证这些内容。

## 术语备注

- **Scope 2（范围二）**：组织购买或取得的电力、蒸汽、供热或制冷所关联的间接排放类别。本示例仅演示购电。
- **Location-based**：使用电网区域平均排放信息表达用电相关排放的计算口径。
- **Market-based**：使用供应商或合同相关信息表达用电相关排放的计算口径。
- **排放因子**：把活动数据（如 kWh）换算为排放量的系数。
- **CO2e**：二氧化碳当量；现实数据还需说明纳入的温室气体和核算方法。

## 数据边界

全部用电量为固定种子的合成示例。所有因子均是占位数字，不对应任何国家、地区、电网、供应商、能源属性凭证或报告年度。项目不会判断凭证质量、剩余组合或方法适用性，不构成合规意见、审计证据或可披露的组织盘查结果；真实用途必须替换并留存可核验来源。
