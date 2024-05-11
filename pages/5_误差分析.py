import math
import time

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import tools.error_analysis as err
import tools.musts as mst

st.set_page_config(page_title='伽马能谱解析平台', layout='wide')

mst.init_session_state()
mst.interrupt_widget_clean_up()

# st.write("st.session_state.have_interpreted:", st.session_state.have_interpreted)

show_contrast = st.toggle("输出对比图", disabled=not st.session_state.have_interpreted, key="tog_contrast")
container = st.container(height=400)
show_error = st.toggle("输出误差", disabled=not show_contrast, key="tog_error")
with container:
    if show_contrast:
        st.session_state.err_real = err.show_contrast(st.session_state.std_data, st.session_state.well_data2,
                                                      st.session_state.output, start_interp=1, depth_counts=-1)
if show_contrast and show_error:
    err.show_error(st.session_state.well_data2, st.session_state.err_real)

# # 下面是测试
# # 该函数用于显示标准谱数据及图像
# def show_std(title, scale_type='linear'):
#     std_data_chart = pd.DataFrame(st.session_state.std_data)
#     std_data_chart.insert(0, 'channel', range(1, len(std_data_chart) + 1))
#     with st.expander(f'{title}标准谱具体数据表'):
#         st.write(std_data_chart.T)
#     std_data_chart = std_data_chart.loc[:, ['channel', 'K', 'Th', 'U']].melt(id_vars=['channel'], var_name='element',
#                                                                              value_name='counts')
#     chart = alt.Chart(std_data_chart).mark_line().encode(
#         x='channel:N',
#         y=alt.Y('counts', scale=alt.Scale(type=scale_type)),
#         color='element',
#     ).properties(
#         # title=f'{scale_type}轴下{title}标准谱图像',
#         width=1000,  # 设置图表宽度为600像素
#         height=400  # 设置图表高度为50像素
#     )
#     st.altair_chart(chart)
#
#
# # 未处理的标准谱
# st.session_state.std_data = pd.read_excel("K、Th、U标准谱数据.xlsx")
# show_std("未处理的", scale_type='symlog')
#
# # 对标准谱进行分辨率校正
# D0 = 0.00015
# D1 = 0.0001
# D2 = 0.05
# channel_size = len(st.session_state.std_data)
# for i in range(channel_size):
#     # 将小于0的能量值视为0
#     if st.session_state.std_data.iloc[i, 0] < 0:
#         st.session_state.std_data.iloc[i, 0] = 0
#     # else:
#     #     st.session_state.std_data.iloc[i, 0] *= 1e-2
# D = np.zeros(channel_size)
# for i in range(channel_size):
#     D[i] = D0 + D1 * st.session_state.std_data.iloc[i, 0] + (D2 * st.session_state.std_data.iloc[i, 0]) ** 2
# # st.write("D:")
# # D_chart_data = pd.DataFrame(D.T, columns=['value'])
# # D_chart_data.insert(0, 'channel', range(1, channel_size + 1))
# # st.write(D_chart_data.T)
# # D_chart = alt.Chart(D_chart_data).mark_line().encode(
# #     x='channel:N',
# #     y=alt.Y('value'),  # scale=alt.Scale(type='log')
# # ).properties(
# #     title='D的数据图像',
# #     width=1000,  # 设置图表宽度为600像素
# #     height=400  # 设置图表高度为50像素
# # )
# # st.altair_chart(D_chart)
#
# # 求correct256x256矩阵
# correct = np.zeros((channel_size, channel_size))
# for i in range(channel_size):
#     for j in range(channel_size):
#         correct[i, j] = 1 / (math.sqrt(2 * math.pi) * D[i]) * math.exp(
#             -(st.session_state.std_data.iloc[j, 0] - st.session_state.std_data.iloc[i, 0]) ** 2 / (2 * D[i] ** 2))
# # # 显示256x256矩阵
# # with st.expander("256x256矩阵数据："):
# #     st.write("256x256矩阵：", correct)
# # # correct_chart = alt.Chart()
# # correct_chart_data = pd.DataFrame(correct[0, :].T, columns=['counts'])
# # correct_chart_data.insert(0, 'channel', range(1, len(correct_chart_data) + 1))
# # correct_chart = alt.Chart(correct_chart_data).mark_line().encode(
# #     x='channel:N',
# #     y=alt.Y('counts'),  # scale=alt.Scale(type='log')
# # ).properties(
# #     # title='256x256矩阵的每一行数据图像',
# #     width=1000,  # 设置图表宽度为600像素
# #     height=400  # 设置图表高度为50像素
# # )
# # # st.altair_chart(correct_chart)
# # # time.sleep(1)
# # # empty_space = st.empty()
# # for i in range(0, 256):
# #     correct_chart_data = pd.DataFrame(correct[i, :].T, columns=['counts'])
# #     correct_chart_data.insert(0, 'channel', range(1, len(correct_chart_data) + 1))
# #     correct_chart += alt.Chart(correct_chart_data).mark_line().encode(
# #         x='channel:N',
# #         y=alt.Y('counts'),  # scale=alt.Scale(type='log')
# #         # color=alt.value(f'#{i:06x}')
# #     ).properties(
# #         # title=f"256x256矩阵的每一行数据图像",
# #         width=1000,  # 设置图表宽度为600像素
# #         height=400  # 设置图表高度为50像素
# #     )
# #     # with empty_space:
# #     #     st.altair_chart(correct_chart)
# #     #     time.sleep(0.05)
# # # correct_chart = correct_chart1 + correct_chart2
# # st.altair_chart(correct_chart)
#
# # 分辨率校正
# raw_std_data = st.session_state.std_data.iloc[:, 1:].copy()
# st.session_state.std_data.iloc[:, 1:] = correct.dot(st.session_state.std_data.iloc[:, 1:])
# show_std("分辨率校正后未归一化的", scale_type='symlog')
#
# # 对标准谱进行归一化
# for label in st.session_state.std_data.iloc[:, 1:].columns:
#     sum_counts = sum(st.session_state.std_data[label])
#     raw_sum_counts = sum(raw_std_data[label])
#     st.session_state.std_data[label] = st.session_state.std_data[label] / sum_counts * raw_sum_counts
# show_std("分辨率校正后且归一化的", scale_type='symlog')
