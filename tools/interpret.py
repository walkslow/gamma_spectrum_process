import streamlit as st
import lasio


@st.cache_data(max_entries=1, hash_funcs={lasio.las.LASFile: lambda las: tuple(las.data)},
               show_spinner="正在输出产额...")
def get_output(std_data, real_data, dept1, dept2):
    """
    解谱计算，输出铀、钍、钾的产额
    :param std_data:
    :param real_data:
    :param dept1:
    :param dept2:
    :return:output:铀、钍、钾的含量
    """
    pass


