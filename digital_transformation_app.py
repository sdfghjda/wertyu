import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots

# 设置页面标题
st.set_page_config(page_title="企业数字化转型指数查询系统", layout="wide")

# 应用标题
st.title("企业数字化转型指数查询系统")

# 读取数据
@st.cache_data

def load_data():
    file_path = '两版合并后的年报数据_完整版.xlsx'
    df = pd.read_excel(file_path)
    return df

# 加载数据
df = load_data()

# 创建左侧查询面板
with st.sidebar:
    st.header("查询面板")
    st.write("请选择以下参数进行查询")
    
    # 股票代码查询
    stock_codes = sorted(df['股票代码'].unique())
    selected_stock = st.selectbox("股票代码", stock_codes)
    
    # 年份查询
    min_year = int(df['年份'].min())
    max_year = int(df['年份'].max())
    selected_year = st.selectbox("年份", sorted(df['年份'].unique()))
    
    # 查询按钮
    if st.button("查询"):
        st.session_state['query_executed'] = True

# 确保会话状态存在
if 'query_executed' not in st.session_state:
    st.session_state['query_executed'] = False

# 过滤数据
filtered_data = df[(df['股票代码'] == selected_stock)]
selected_year_data = df[(df['股票代码'] == selected_stock) & (df['年份'] == selected_year)]

# 按照年份排序
filtered_data = filtered_data.sort_values('年份')

# 获取企业名称
company_name = filtered_data['企业名称'].iloc[0] if not filtered_data.empty else "未知企业"

# 第一部分：统计概览
st.header("统计概览")

# 创建统计卡片
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("总记录数", len(df))

with col2:
    st.metric("企业数量", df['股票代码'].nunique())

with col3:
    st.metric("年份范围", f"{int(df['年份'].min())}-{int(df['年份'].max())}")

with col4:
    avg_index = df['数字化转型指数'].mean()
    st.metric("平均指数", f"{avg_index:.2f}")

with col5:
    max_index = df['数字化转型指数'].max()
    st.metric("最高指数", f"{max_index:.2f}")

with col6:
    min_index = df['数字化转型指数'].min()
    st.metric("最低指数", f"{min_index:.2f}")

# 第二部分：数据概览
st.header("数据概览")

# 显示数据结构信息
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("数据预览")
    st.dataframe(df.sample(10), use_container_width=True)

with col2:
    st.subheader("数据结构")
    st.write(f"行数: {len(df)}")
    st.write(f"列数: {len(df.columns)}")
    st.subheader("主要列名")
    for col in df.columns:
        st.write(f"- {col}")

# 第三部分：数字化转型指数分布
st.header("数字化转型指数分布")

# 创建分布图表
col1, col2 = st.columns(2)

with col1:
    # 整体分布直方图
    fig_hist = px.histogram(
        df,
        x='数字化转型指数',
        nbins=50,
        title='数字化转型指数整体分布',
        labels={'数字化转型指数': '数字化转型指数', 'count': '企业数量'}
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    # 技术维度与应用维度散点图
    fig_scatter = px.scatter(
        df,
        x='技术维度',
        y='应用维度',
        color='数字化转型指数',
        hover_data=['股票代码', '企业名称', '年份'],
        title='技术维度 vs 应用维度',
        labels={'技术维度': '技术维度', '应用维度': '应用维度'}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# 第四部分：数字化转型指数详细统计
st.header("数字化转型指数详细统计")

# 计算详细统计信息
detailed_stats = {
    "平均值": filtered_data['数字化转型指数'].mean(),
    "中位数": filtered_data['数字化转型指数'].median(),
    "最大值": filtered_data['数字化转型指数'].max(),
    "最小值": filtered_data['数字化转型指数'].min(),
    "标准差": filtered_data['数字化转型指数'].std(),
    "25%分位数": filtered_data['数字化转型指数'].quantile(0.25),
    "75%分位数": filtered_data['数字化转型指数'].quantile(0.75)
}

# 显示详细统计
col1, col2, col3, col4 = st.columns(4)

for i, (key, value) in enumerate(detailed_stats.items()):
    if i % 4 == 0:
        with col1:
            st.metric(key, f"{value:.2f}" if not np.isnan(value) else "N/A")
    elif i % 4 == 1:
        with col2:
            st.metric(key, f"{value:.2f}" if not np.isnan(value) else "N/A")
    elif i % 4 == 2:
        with col3:
            st.metric(key, f"{value:.2f}" if not np.isnan(value) else "N/A")
    else:
        with col4:
            st.metric(key, f"{value:.2f}" if not np.isnan(value) else "N/A")

# 第五部分：数字化转型指数折线图
st.header("数字化转型指数趋势")

if not filtered_data.empty:
    # 创建多指标折线图
    fig_line = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 添加数字化转型指数
    fig_line.add_trace(
        go.Scatter(x=filtered_data['年份'], y=filtered_data['数字化转型指数'], 
                  name="数字化转型指数", line=dict(color="#1f77b4", width=3)),
        secondary_y=False,
    )
    
    # 添加技术维度
    fig_line.add_trace(
        go.Scatter(x=filtered_data['年份'], y=filtered_data['技术维度'], 
                  name="技术维度", line=dict(color="#ff7f0e", width=2, dash="dash")),
        secondary_y=False,
    )
    
    # 添加应用维度
    fig_line.add_trace(
        go.Scatter(x=filtered_data['年份'], y=filtered_data['应用维度'], 
                  name="应用维度", line=dict(color="#2ca02c", width=2, dash="dot")),
        secondary_y=False,
    )
    
    # 更新布局
    fig_line.update_layout(
        title=f"{company_name} ({selected_stock}) 数字化转型指数趋势",
        xaxis_title="年份",
        yaxis_title="指数值",
        legend_title="指标类型",
        hovermode="x unified"
    )
    
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.write("没有找到相关数据")

# 第六部分：详细数据统计
st.header("详细数据统计")

# 显示查询结果的详细数据
if not selected_year_data.empty:
    st.subheader(f"{company_name} ({selected_stock}) - {selected_year} 年详细数据")
    
    # 创建详细数据表格
    detail_df = selected_year_data[['股票代码', '企业名称', '年份', '人工智能词频数', '大数据词频数', '云计算词频数', 
                                   '区块链词频数', '数字技术运用词频数', '技术维度', '应用维度', '数字化转型指数']]
    st.dataframe(detail_df, use_container_width=True)
    
    # 显示词频数统计
    st.subheader("词频数统计")
    
    # 创建词频数图表
    word_freq_data = {
        "类别": ['人工智能', '大数据', '云计算', '区块链', '数字技术运用'],
        "词频数": [
            selected_year_data['人工智能词频数'].iloc[0],
            selected_year_data['大数据词频数'].iloc[0],
            selected_year_data['云计算词频数'].iloc[0],
            selected_year_data['区块链词频数'].iloc[0],
            selected_year_data['数字技术运用词频数'].iloc[0]
        ]
    }
    
    fig_bar = px.bar(
        word_freq_data,
        x='类别',
        y='词频数',
        title="数字技术词频数统计",
        labels={'类别': '技术类别', '词频数': '出现次数'}
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.write("未找到该年份的详细数据")

# 添加数据说明
st.header("数据说明")
st.markdown("""\n
### 指标解释
- **数字化转型指数**: 综合反映企业数字化转型程度的指数
- **技术维度**: 反映企业在数字化技术方面的投入和应用
- **应用维度**: 反映企业在数字化应用方面的效果和影响
- **人工智能词频数**: 年报中提及人工智能相关词汇的次数
- **大数据词频数**: 年报中提及大数据相关词汇的次数
- **云计算词频数**: 年报中提及云计算相关词汇的次数
- **区块链词频数**: 年报中提及区块链相关词汇的次数
- **数字技术运用词频数**: 年报中提及数字技术运用相关词汇的次数

### 数据来源
数据来自企业年报中相关关键词的词频统计和分析。
""")