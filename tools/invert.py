import streamlit as st
import lasio


@st.cache_data(max_entries=1, hash_funcs={lasio.las.LASFile: lambda las: tuple(las.data)},
               show_spinner="正在输出对比图...")
def show_contrast(std_data, real_data, output):
    """
    计算反演得出的实测谱并输出对比图
    :param std_data:
    :param real_data:
    :param output:
    :return:inv_real:反演得出的实测谱
    """
    pass


@st.cache_data(max_entries=1, hash_funcs={lasio.las.LASFile: lambda las: tuple(las.data)},
               show_spinner="正在输出误差...")
def show_error(real_data, inv_real):
    """
    输出误差
    :param real_data:
    :param inv_real:
    :return:
    """
    pass
