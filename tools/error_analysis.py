import math
import pandas as pd
import streamlit as st
import numpy as np
import altair as alt


@st.cache_data(max_entries=1, show_spinner="正在输出对比图...")
def show_contrast(std_data, well_data, output, *, start_interp=1, depth_counts=-1):
    """
    计算误差分析得出的实测谱并输出对比图
    :param std_data:256x4 dataframe
    :param well_data:第一列为深度，第2到257列为相应能道计数值
    :param output:第一列为深度，2到4列为K、U、Th的含量
    :param start_interp: 开始显示对比图的能道数，默认为1
    :param depth_counts: 显示的深度个数，即子图个数，默认为-1，表示将所有深度的对比图都显示出来
    :return:err_real:误差分析得出的实测谱，与well_data格式相同，都是dataframe
    """
    channel_size = well_data.shape[1] - 1
    depth_size = len(well_data) if depth_counts == -1 or depth_counts > len(well_data) else depth_counts
    std_counts = std_data.loc[:, ['K', 'U', 'Th']].to_numpy()
    err_real = np.zeros(well_data.shape)
    err_real[:, 1:] = output[:, 1:].dot(std_counts.T)  # 计数值
    err_real[:, 0] = well_data.iloc[:, 0]  # 深度列
    err_real = pd.DataFrame(err_real, columns=well_data.columns)
    data = {
        'depth': np.repeat(well_data.iloc[:depth_size, 0], (channel_size - start_interp + 1) * 2),
        'channel': np.tile(range(start_interp, channel_size + 1), depth_size * 2),
        'counts': pd.concat(
            [pd.concat([well_data.iloc[i, start_interp:], err_real.iloc[i, start_interp:]], axis=0) for i in
             range(depth_size)],
            axis=0).to_numpy(),
        'name': np.tile(np.repeat(['before', 'after'], channel_size - start_interp + 1), depth_size)
    }
    df = pd.DataFrame(data)
    chart = alt.Chart(df).mark_line().encode(
        x='channel:N',
        y=alt.Y('counts:Q', axis=alt.Axis(title='', orient='right', values=[]), scale=alt.Scale(type='symlog')),
        # color='name:N',
        # strokeDash=alt.condition(
        #     alt.datum.name == 'before',  # test predicate
        #     alt.value([]),  # if_true: value when the condition is true
        #     alt.value([3, 3])
        # )
        color=alt.Color('name:N', legend=alt.Legend(title='Status'),
                        scale=alt.Scale(domain=['before', 'after'], range=['blue', 'red'])),
        strokeDash=alt.StrokeDash('name:N', legend=alt.Legend(title='Status'),
                                  scale=alt.Scale(domain=['before', 'after'], range=[[0], [3, 3]])),
    ).properties(
        width=600,  # 设置图表宽度为600像素
        height=50  # 设置图表高度为50像素
    ).facet(
        row='depth:N',  # 使用行面来区分不同的深度
    )
    # 使用选择器反应太慢了
    # point_selection = alt.selection_point(
    #     on='mouseover',
    #     nearest=True,
    #     fields=['channel', 'counts', 'name'],
    #     empty='none'
    # )
    # points = chart.mark_point().encode(
    #     opacity=alt.condition(point_selection, alt.value(1), alt.value(0))
    # ).add_params(point_selection)
    # chart = (chart + points).interactive()
    # chart = chart.facet(
    #     row='depth:N',  # 使用行面来区分不同的深度
    # )
    chart.title = alt.TitleParams("对比图", anchor='middle')
    st.altair_chart(chart)
    return err_real


@st.cache_data(max_entries=1, show_spinner="正在输出误差...")
def show_error(well_data, err_real):
    """
    输出误差，即||well_data-err_data||的2-范数
    :param well_data:
    :param err_real:
    :return:
    """
    channel_size = well_data.shape[1] - 1
    depth_size = len(well_data)
    err = np.zeros((2, depth_size))
    err[0, :] = well_data.iloc[:, 0]
    for i in range(depth_size):
        temp = 0
        for j in range(1, channel_size + 1):
            temp += (well_data.iloc[i, j] - err_real.iloc[i, j]) ** 2
        temp = math.sqrt(temp)
        err[1, i] = temp
    err = pd.DataFrame(err.T, columns=['深度', '2-范数'])
    st.dataframe(err.T)
    return err
