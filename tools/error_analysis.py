import streamlit as st


@st.cache_data(max_entries=1, show_spinner="正在输出对比图...")
def show_contrast(std_data, well_data, output):
    """
    计算误差分析得出的实测谱并输出对比图
    :param std_data:
    :param well_data:
    :param output:
    :return:err_real:误差分析得出的实测谱
    """
    pass


@st.cache_data(max_entries=1, show_spinner="正在输出误差...")
def show_error(well_data, err_real):
    """
    输出误差
    :param well_data:
    :param err_real:
    :return:
    """
    pass
