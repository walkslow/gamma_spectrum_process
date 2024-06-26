import math

import pandas as pd
import streamlit as st
import lasio
import re
import numpy as np
import altair as alt
from pyod.models.knn import KNN
from scipy.signal import savgol_filter
from tools.tools_findpeak import get_peak


@st.cache_data(max_entries=3, hash_funcs={lasio.las.LASFile: lambda las: tuple(las.keys())})
def get_wells_info(real_data):
    """
    根据实测谱数据得到各个井的名称和能道数，返回包含所有井的名称和能道数的字典
    :param real_data:
    :return:well_info{}:键为井名称，值为能道数
    """
    wells_info = {}
    for name in real_data.keys():
        match_object = re.search('\[\d+]$', name)
        if match_object:
            well_name = name[:match_object.start()]
            if well_name not in wells_info.keys():
                wells_info[well_name] = 1
            else:
                wells_info[well_name] += 1
    return wells_info


def set_submitted_true():
    """
    将选择深度范围的表单form的form_submitted_button的状态置为True,
    其初始状态为False,一次点击以后都为True，方便展示之前选择的谱图
    """
    st.session_state.submitted = True


@st.cache_data(max_entries=5)
def get_sample_size(dept1, dept2, step):
    """
    根据深度范围和步长求得合并采样点个数
    :return:
    """
    if dept1 is not None and dept2 is not None and step is not None:
        return round(abs(dept1 - dept2) / step) + 1


@st.cache_data(max_entries=3)
def generate_list(x, step, y):
    """
    生成一个列表，第一个元素为x，步长为-step，最后一个元素大于等于y
    :param x: 大值
    :param step: 正值
    :param y: 小值
    :return:result：List
    """
    result = []
    current_value = x
    while current_value >= y:
        result.append(current_value)
        current_value -= step
    return result


@st.cache_data(max_entries=5, persist=True, hash_funcs={lasio.las.LASFile: lambda las: tuple(las.data)},
               show_spinner="正在获取对应深度范围的数据")
def get_well_data(real_data, well_name, channel_size, dept1, dept2):
    """
    从完整的实测谱数据中提取相应深度的数据
    :param real_data:
    :param well_name:
    :param channel_size:
    :param dept1:大深度
    :param dept2:小深度
    :return:well_data:pd.DataFrame格式,带深度depth列
    """
    if dept1 < dept2:
        temp = dept1
        dept1 = dept2
        dept2 = temp
    if re.search('\.(las|LAS)$', st.session_state.f_real.name):
        col_start = f'{well_name}[1]'
        col_end = f'{well_name}[{channel_size}]'
        old_index = real_data.keys()[0]  # 因为LAS文件将第一个key作为数据部分的索引名称，一般为DEPT
        df1 = real_data.df()
        if df1.index[0] > df1.index[1]:  # 说明df1按深度递减的顺序索引
            data1 = df1.loc[dept1:dept2, col_start:col_end]
        else:
            data1 = df1.loc[dept2:dept1, col_start:col_end]
        df2 = data1.reset_index()  # 重置索引为自然索引，原来的深度索引变成第一列数据
        data2 = df2.loc[(dept2 <= df2[old_index]) & (df2[old_index] <= dept1), old_index]  # 深度列
    elif re.search('\.(xlsx|xls)$', st.session_state.f_real.name):
        dept_list = generate_list(dept1, st.session_state.step_fake_dept, dept2)
        dept_list = dept_list[:len(real_data)] if len(dept_list) > len(real_data) else dept_list  # 不包含第len(real_data)列
        data1 = real_data.loc[:len(dept_list) - 1]  # 包含第len(dept_list) - 1 行
        data2 = pd.DataFrame(dept_list, columns=['DEPT'])

    # 由于data1和data2的索引可能不同，一个是深度索引，一个是自然索引，且自然索引可能不是从0开始，所以需要重置自然索引并丢弃原来的索引再合并
    well_data = pd.concat([data2.reset_index(drop=True), data1.reset_index(drop=True)], axis=1)
    return well_data


def get_spectrum(well_data, well_channel_size, *, depth_counts=-1):
    """
    获得要展示的altair谱图的chart图表对象
    :param well_data: 谱图数据
    :param well_channel_size: 能道数
    :param depth_counts: 要展示的深度点个数，默认-1表示well_data的所有深度点
    :return:
    """
    # st.write("get_spectrum函数里面的well_data是：",well_data)
    if depth_counts == -1 or depth_counts > len(well_data):
        depth_counts = len(well_data)
    selected_data = well_data.iloc[:depth_counts, 1:]
    data = {
        'depth': np.repeat(well_data.iloc[:depth_counts, 0], well_channel_size),
        'channel': np.tile(range(1, well_channel_size + 1), len(selected_data)),
        'counts': pd.concat([selected_data.iloc[i] for i in range(len(selected_data))], axis=0).to_numpy()
    }
    df = pd.DataFrame(data)
    # st.write("get_spectrum函数里面图表原data是：", df)
    # 创建图表
    chart = alt.Chart(df).mark_line().encode(
        x=alt.X('channel:N', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('counts:Q', axis=alt.Axis(title='', orient='right', values=[]), scale=alt.Scale(type='symlog'))
    ).properties(
        width=600,  # 设置图表宽度为600像素
        height=50  # 设置图表高度为50像素
    ).facet(
        row='depth:N',  # 使用行面来区分不同的深度
    )
    return chart


@st.cache_data(max_entries=5, persist=True, show_spinner="正在显示原始谱图...")
def show_raw_spectrum(well_data, well_name, well_channel_size):
    """
    井名和深度范围确定后，展示原始谱图
    :param well_data:为pd.DataFrame
    :param well_name:
    :param well_channel_size:
    """
    # st.write("show_raw_spectrum函数里面的well_data为：",well_data)
    chart = get_spectrum(well_data, well_channel_size)
    chart.title = alt.TitleParams(f"{well_name}在不同深度的原始谱图", anchor='middle')
    with st.container(height=300):
        st.altair_chart(chart)


@st.cache_data(max_entries=5, persist=True, hash_funcs={lasio.las.LASFile: lambda las: tuple(las.data)},
               show_spinner="正在显示原始GR谱图...")
def show_raw_gr(real_data):
    """
    显示实测谱在所有深度的GR等数据
    :param real_data:
    :return:
    """
    if re.search('\.(las|LAS)$', st.session_state.f_real.name):
        names = ["GR", "CALI", "RDEP", "RHOB", "NPHI", "DTC", "SP", "GRTO", "GRTC", "URAN", "THOR", "POTA"]
        exist_names = []
        for name in names:
            if name in real_data.keys():
                exist_names.append(name)
        if exist_names:
            dept_counts = get_sample_size(st.session_state.max_real_dept, st.session_state.min_real_dept,
                                          st.session_state.step_real_dept)
            real_df = real_data.df()
            data = {
                'name': np.repeat(exist_names, dept_counts),
                'depth': np.tile(real_df.index.to_numpy(), len(exist_names)),
                'counts': pd.concat([real_df[name] for name in exist_names], axis=0).to_numpy()
            }
            df = pd.DataFrame(data)
            # 创建图表
            chart = alt.Chart(df).mark_line().encode(
                x='depth:Q',
                y=alt.Y('counts:Q', axis=alt.Axis(title='', orient='right', values=[])),  # y轴为 counts，并不显示标题和刻度
                color='name:N'
            ).properties(
                width=600,  # 设置图表宽度为600像素
                height=50  # 设置图表高度为50像素
            ).facet(
                row='name:N',  # 使用行面来区分不同的深度
            )
            with st.container(height=300):
                st.altair_chart(chart)


@st.cache_data(max_entries=1, show_spinner="正在进行异常值检测与处理...")
def removing(well_data, k, q):
    """
    预处理之异常值检测与处理，将异常值替换为左右正常值的平均值
    :param well_data: 确认了深度范围的原始谱图数据，DataFrame格式
    :param k:KNN算法的参数，即邻居的数量
    :param q:用于确定阈值，表示异常值的异常分数高于百分之q的异常分数
    :return:well_data
    """
    well_data.clip(lower=0, inplace=True)  # 将小于0的值置为0
    knn = KNN(n_neighbors=k)
    data = well_data.iloc[:, 1:]  # 去除了深度列的谱数据
    outliers_index = [None] * len(data)  # 列表元素为数组，保存每一行的异常值的列索引，列索引从1开始，因为第0列为深度列
    for row_index, row in data.iterrows():
        knn.fit(list(enumerate(row, 1)))
        # 获取异常分数
        scores = knn.decision_scores_
        # 确定阈值
        threshold = np.percentile(scores, q)
        # 标记异常值的列索引
        outliers_index[row_index] = np.where(scores > threshold)[0] + 1
        # well_data.iloc[row_index, np.where(scores > threshold)[0]+1] = 0
        # 异常值处理，将异常值转换为左右正常数据的平均值
        for i in outliers_index[row_index]:
            left_index = i - 1
            right_index = i + 1
            while left_index in outliers_index[row_index] and left_index > 0:
                left_index = left_index - 1
            while right_index in outliers_index[row_index] and right_index < well_data.shape[1]:
                right_index = right_index + 1
            left_value = well_data.iloc[row_index, left_index] if left_index != 0 else 0
            right_value = well_data.iloc[row_index, right_index] if right_index != well_data.shape[1] else 0
            well_data.iloc[row_index, i] = (left_value + right_value) / 2
    # st.write(outliers_index)
    return well_data


@st.cache_data(max_entries=1, show_spinner="正在滤波...")
def filtering(well_data, window_length, polyorder):
    """
    预处理之滤波，使用Savitzky-Golay滤波器
    :param well_data:
    :param window_length:窗口长度，为奇数
    :param polyorder:拟合的多项式阶数
    :return:
    """
    data = well_data.iloc[:, 1:]  # 去除了深度列的谱数据
    # 对每一行使用Savitzky-Golay滤波器
    for row_index, row in data.iterrows():
        well_data.iloc[row_index, 1:] = savgol_filter(row.to_numpy(), window_length, polyorder)
    return well_data


@st.cache_data(max_entries=1, show_spinner="正在寻峰...")
def peak_detect(well_data):
    """
    预处理之寻峰，寻峰之前先将不同深度点按一定权重叠加
    :param well_data:
    :return:(well_data,peaks):well_data为将不同深度点按一定权重叠加后的数据，
    peaks为每一个深度点的峰位，每个深度点都有3个峰位，分别为K、U、Th，如果没有寻到峰，则置None
    """
    well_data.clip(lower=0, inplace=True)  # 将小于0的值置为0
    data = well_data.iloc[:, 1:]  # 去除了深度列的谱数据
    max_index = len(data) - 1
    # 深度点前后5个叠加深度点的权重，其本身权重为1
    weight = [0.98, 0.955, 0.9, 0.85, 0.775]
    for row_index, row in data.iterrows():
        for i, w in enumerate(weight, 1):
            if row_index - i >= 0:
                well_data.iloc[row_index, 1:] += data.iloc[row_index - i, :] * w
            if row_index + i <= max_index:
                well_data.iloc[row_index, 1:] += data.iloc[row_index + i, :] * w
    # 寻峰
    data = well_data.iloc[:, 1:]  # 去除了深度列的谱数据
    m = 20  # 寻峰范围
    peaks = np.zeros((len(data), 3))  # 峰位初始化为0
    for row_index, row in data.iterrows():
        for i in range(len(st.session_state.std_peaks)):
            peak = get_peak(row.copy(), (st.session_state.std_peaks[i] - m, st.session_state.std_peaks[i] + m))[2]
            # 注意，下面未寻到的峰位 置为None会被解释为np.nan
            peaks[row_index, i] = peak if 0 < peak < st.session_state.well_info["channel_size"] else np.nan
    return well_data, peaks


@st.cache_data(max_entries=1, show_spinner="正在进行谱漂校正...")
def drift_correct(std_peaks, real_peaks, well_data):
    """
    预处理之谱漂校正，选择K和Th的峰位对实测谱进行谱漂校正
    :param std_peaks:标准谱峰位
    :param real_peaks:实测谱峰位
    :param well_data:
    :return:
    """
    data = well_data.iloc[:, 1:]  # 去除了深度列的谱数据
    channel_size = data.shape[1]
    for row_index, row in data.iterrows():
        # 保存实测谱寻到的峰的索引
        real_peak_indices = []
        for i, peak in enumerate(real_peaks[row_index, :], 0):
            if not np.isnan(peak):
                real_peak_indices.append(i)
        # 当实测谱没有寻到峰或只寻到一个峰时，我们不进行谱漂校正
        # if len(real_peak_indices) <= 1:
        #     continue
        # 当K和Th峰未寻到时，我们不进行谱漂校正
        if not (0 in real_peak_indices and 2 in real_peak_indices):
            continue
        # numpy数组不能使用列表进行索引，所以将real_peak_indices先转换为numpy数组
        # real_peak_indices = np.array(real_peak_indices)
        # K峰和Th峰的索引分别为0和2
        real_peak_indices = np.array([0, 2])
        # st.write("real_peak_indices:",real_peak_indices)
        # st.write("std_peaks[real_peak_indices]:", std_peaks[real_peak_indices])
        # st.write("real_peaks[row_index, real_peak_indices]:", real_peaks[row_index, real_peak_indices])
        param = np.polyfit(std_peaks[real_peak_indices], real_peaks[row_index, real_peak_indices], 1)  # 拟合系数
        # st.write("拟合系数：", param)
        func = np.poly1d(param)  # 拟合函数
        new_spectrum = np.zeros(channel_size)  # 保存每个深度点谱漂校正之后的计数值
        for i in range(channel_size):
            channel_left = func(i)  # 谱漂校正之前的低能道址
            channel_right = func(i + 1)  # 谱漂校正之前的高能道址
            left_bond = 0 if channel_left < 0 else channel_left
            left_bond = channel_size - 1 if left_bond > channel_size - 1 else left_bond
            right_bond = channel_size - 1 if channel_right > channel_size - 1 else channel_right
            right_bond = 0 if right_bond < 0 else right_bond
            left_int = int(left_bond)
            right_int = int(right_bond)
            value1 = (1 - (left_bond - left_int)) * row[left_int]
            value2 = (right_bond - right_int) * row[right_int]
            value3 = 0
            if right_int - left_int > 1:
                value3 = sum(row[j] for j in range(left_int + 1, right_int))
            elif right_int - left_int == 1:
                value3 = 0
            elif right_int - left_int == 0:
                value3 = -row[left_int]
            new_spectrum[i] = value1 + value2 + value3
        well_data.iloc[row_index, 1:] = new_spectrum
    return well_data


@st.cache_data(max_entries=1, show_spinner="正在进行分辨率校正...")
def resolution_correct(std_data, well_data):
    """
    预处理之分辨率校正，对标准谱进行分辨率校正，然后对标准谱和实测谱进行归一化处理
    :param std_data:
    :param well_data:
    :return:
    """
    # 对标准谱进行分辨率校正
    D0 = 0.00015
    D1 = 0.0001
    D2 = 0.05
    channel_size = len(std_data)
    for i in range(channel_size):
        # 将小于0的能量值视为0
        if std_data.iloc[i, 0] < 0:
            std_data.iloc[i, 0] = 0
        # else:
        #     st.session_state.std_data.iloc[i, 0] *= 1e-2
    D = np.zeros(channel_size)
    for i in range(channel_size):
        D[i] = D0 + D1 * std_data.iloc[i, 0] + (D2 * std_data.iloc[i, 0]) ** 2
    correct = np.zeros((channel_size, channel_size))
    for i in range(channel_size):
        for j in range(channel_size):
            correct[i, j] = 1 / (math.sqrt(2 * math.pi) * D[i]) * math.exp(
                -(std_data.iloc[j, 0] - std_data.iloc[i, 0]) ** 2 / (2 * D[i] ** 2))
    # st.write("256x256矩阵：", correct)
    raw_std_data = std_data.iloc[:, 1:].copy()
    std_data.iloc[:, 1:] = correct.dot(std_data.iloc[:, 1:])
    # 对标准谱进行归一化
    for label in std_data.iloc[:, 1:].columns:
        sum_counts = sum(std_data[label])
        raw_sum_counts = sum(raw_std_data[label])
        std_data[label] = std_data[label] / sum_counts * raw_sum_counts
    # 对实测谱进行归一化
    well_data.clip(lower=0, inplace=True)  # 将小于0的值置为0
    # for row_index, row in well_data.iloc[:, 1:].iterrows():
    #     sum_counts = sum(row)
    #     row /= sum_counts
    #     well_data.iloc[row_index, 1:] = row
    return std_data, well_data


def prepro_func(func, checked, *args, **kwargs):
    """
    当checked为True时，执行func函数
    :param func:
    :param checked:
    """
    if checked:
        result = func(*args, **kwargs)
        func_name = func.__name__
        if func_name == 'peak_detect':
            st.session_state.well_data2, st.session_state.peaks = result
        elif func_name == 'resolution_correct':
            st.session_state.std_data, st.session_state.well_data2 = result
        else:
            st.session_state.well_data2 = result


@st.cache_data(max_entries=5, persist=True, show_spinner="正在显示处理后的谱图...")
def show_after_spectrum(well_data, well_name, well_channel_size, *, depth_counts=-1):
    """
    展示预处理过程中的谱图变化
    :param well_data:
    :param well_name:
    :param well_channel_size:
    :param depth_counts: 显示的深度点个数，默认为-1，表示将well_data的所有深度点的谱图都显示出来
    :return:
    """
    chart = get_spectrum(well_data, well_channel_size, depth_counts=depth_counts)
    if st.session_state.resolution_correct:
        chart.title = alt.TitleParams(f"{well_name}分辨率校正后的谱图", anchor='middle')
    elif st.session_state.drift_correct:
        chart.title = alt.TitleParams(f"{well_name}谱漂校正后的谱图", anchor='middle')
    elif st.session_state.peak_detect:
        chart.title = alt.TitleParams(f"{well_name}寻峰后的谱图", anchor='middle')
    elif st.session_state.filtering:
        chart.title = alt.TitleParams(f"{well_name}滤波后的谱图", anchor='middle')
    elif st.session_state.removing:
        chart.title = alt.TitleParams(f"{well_name}异常值处理后的谱图", anchor='middle')
    st.altair_chart(chart)
