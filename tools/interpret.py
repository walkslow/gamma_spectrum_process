import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from scipy.optimize import least_squares


def residuals(element_contents, std_data, real_data):
    """
    由标准谱乘元素含量得到拟合的实测谱，返回与真实实测谱的残差
    :param element_contents: K、U、Th的元素含量，单位分别为 %(百分比)、ppm(百万分之一)、ppm，1_D array格式
    :param std_data: 标准谱数据
    :param real_data: 某一深度点的实测谱数据
    :return:
    """
    # 先对element_contents校正单位
    element_contents[0] = element_contents[0] * 1e-2
    element_contents[1:] = element_contents[1:] * 1e-6
    # st.write("转换单位之后的element_contents为：",element_contents)
    element_contents = element_contents.reshape((-1, 1))  # 将element_contents转置为列向量
    predict_data = std_data.dot(element_contents).flatten()
    result = predict_data - real_data
    return result


@st.cache_data(max_entries=3, persist=True, show_spinner="正在解谱...")
def get_element_contents(initial_guess, std_data, real_data):
    """
    使用最小二乘法求得使残差平方和最小的元素含量
    :param initial_guess: 对K、U、Th的含量的初始猜测值，单位分别为 %(百分比)、ppm(百万分之一)、ppm
    :param std_data: 标准谱数据
    :param real_data: 某一深度点的实测谱数据
    :return:
    """
    result = least_squares(residuals, initial_guess, args=(std_data, real_data))
    return result.x


@st.cache_data(max_entries=1, show_spinner="正在计算产额...")
def get_output(std_data, well_data, initial_guess):
    """
    解谱计算，输出所有深度点的K、U、Th的产额
    :param std_data:标准谱数据
    :param well_data:所有深度点的实测谱数据
    :param initial_guess: 对K、U、Th的含量的初始猜测值，单位分别为 %(百分比)、ppm(百万分之一)、ppm
    :return:output:所有深度点K、U、Th的含量,第一列为深度
    """
    data = well_data.iloc[:, 1:]  # 去除了深度列的谱数据
    output = np.zeros((len(data), 4))  # 保存每一个深度点的K、U、Th的含量，初始化为0
    output[:, 0] = well_data.iloc[:, 0]  # output的第一列为深度列
    for row_index, row in data.iterrows():
        output[row_index, 1:] = get_element_contents(initial_guess, std_data, row)
    return output


@st.cache_data(max_entries=1, show_spinner="正在显示产额图...")
def show_output(output):
    """
    显示所有深度点的K、U、Th的含量图
    :param output:
    :return:
    """
    data = []
    charts = []
    for i in range(3):
        data.append(pd.DataFrame({
            'depth': output[:, 0],
            'contents': output[:, i + 1]
        }))
    point_selection = alt.selection_point(
        on='mouseover',
        nearest=True,
        fields=['depth', 'contents'],
        empty='none'
    )
    # 添加K的产额图
    charts.append(alt.Chart(data[0]).mark_line().encode(
        x=alt.X('depth:N', axis=None),
        y=alt.Y('contents:Q', axis=alt.Axis(title='K(%)')),
        color=alt.Color(value="blue"),
    ))
    # 添加U的产额图
    charts.append(alt.Chart(data[1]).mark_line().encode(
        x=alt.X('depth:N', axis=None),
        y=alt.Y('contents:Q', axis=alt.Axis(title='U(ppm)')),
        color=alt.Color(value="black"),
    ))
    # 添加Th的产额图
    charts.append(alt.Chart(data[2]).mark_line().encode(
        x='depth:N',
        y=alt.Y('contents:Q', axis=alt.Axis(title='Th(ppm)')),
        color=alt.Color(value="red"),
    ))
    # 对于每个子图都相同的操作
    for i in range(3):
        charts[i] = charts[i].properties(
            width=600,  # 设置图表宽度为600像素
            height=80  # 设置图表高度为50像素
        )
        points = charts[i].mark_point().encode(
            opacity=alt.condition(point_selection, alt.value(1), alt.value(0))
        ).add_params(point_selection)
        charts[i] = (charts[i] + points).interactive()
    combined_chart = alt.vconcat(*charts, spacing=0).resolve_scale(y='independent')
    combined_chart.title = alt.TitleParams("不同深度的K、U、Th含量图", anchor='middle')
    # combined_chart.configure_legend(title=None)
    # 在Streamlit中显示图表
    st.altair_chart(combined_chart)
