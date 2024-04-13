import streamlit as st
import numpy as np


def init_session_state():
    # 保存标准谱数据
    if "std_data" not in st.session_state:
        st.session_state.std_data = None
    if "std_peaks" not in st.session_state:
        st.session_state.std_peaks = None
    # 表示实测谱文件是否已经被上传
    if "enable_transform" not in st.session_state:
        st.session_state.enable_transform = None
    # 存储UploadedFile格式的实测谱文件
    if "f_real" not in st.session_state:
        st.session_state.f_real = None
    if "real_data" not in st.session_state:
        st.session_state.real_data = None
    if 'min_real_dept' not in st.session_state:
        st.session_state.min_real_dept = None
    if 'max_real_dept' not in st.session_state:
        st.session_state.max_real_dept = None
    if 'step_real_dept' not in st.session_state:
        st.session_state.step_real_dept = None
    # 对于像Excel文件这种没有深度列的实测谱数据，深度步长由用户指定，即step_fake_dept
    if 'step_fake_dept' not in st.session_state:
        st.session_state.step_fake_dept = None
    if "enable_choose" not in st.session_state:
        st.session_state.enable_choose = None
    if "enable_prepro" not in st.session_state:
        st.session_state.enable_prepro = False
    if "well_info" not in st.session_state:
        st.session_state.well_info = {}
    if "select_well" not in st.session_state:
        st.session_state.select_well = None
    if "real_dept1" not in st.session_state:
        st.session_state.real_dept1 = None
    if "real_dept2" not in st.session_state:
        st.session_state.real_dept2 = None
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    # 探测器和深度范围确定后，保存选择处理的数据
    if "well_data" not in st.session_state:
        st.session_state.well_data = None
    # 预处理过程中的数据，由于要与well_data进行比较，所以重新定义一个变量
    if "well_data2" not in st.session_state:
        st.session_state.well_data2 = None
    if "removing" not in st.session_state:
        st.session_state.removing = False
    if "filtering" not in st.session_state:
        st.session_state.filtering = False
    if "peak_detect" not in st.session_state:
        st.session_state.peak_detect = False
    # 保存每个深度点的三个峰位
    if "peaks" not in st.session_state:
        st.session_state.peaks = None
    if "drift_correct" not in st.session_state:
        st.session_state.drift_correct = False
    if "resolution_correct" not in st.session_state:
        st.session_state.resolution_correct = False
    if "enable_interp" not in st.session_state:
        st.session_state.enable_interp = None
    if "output" not in st.session_state:
        st.session_state.output = None
    if "have_interpreted" not in st.session_state:
        st.session_state.have_interpreted = False
    # 反演得出的实测谱
    if "inv_real" not in st.session_state:
        st.session_state.inv_real = None


def interrupt_widget_clean_up():
    st.session_state.select_well = st.session_state.select_well
    st.session_state.real_dept1 = st.session_state.real_dept1
    st.session_state.real_dept2 = st.session_state.real_dept2
    st.session_state.step_fake_dept = st.session_state.step_fake_dept
    st.session_state.removing = st.session_state.removing
    st.session_state.filtering = st.session_state.filtering
    st.session_state.peak_detect = st.session_state.peak_detect
    st.session_state.drift_correct = st.session_state.drift_correct
    st.session_state.resolution_correct = st.session_state.resolution_correct


def reset_session_state():
    """
    当上传了一个新的实测谱文件之后，重置部分session_state
    """
    st.session_state.enable_choose = None
    st.session_state.enable_prepro = False
    st.session_state.well_info = {}
    st.session_state.select_well = None
    st.session_state.real_dept1 = None
    st.session_state.real_dept2 = None
    st.session_state.step_fake_dept = None
    st.session_state.submitted = False
    st.session_state.well_data = None
    st.session_state.well_data2 = None
    st.session_state.removing = False
    st.session_state.filtering = False
    st.session_state.peak_detect = False
    st.session_state.peaks = None
    st.session_state.drift_correct = False
    st.session_state.resolution_correct = False
    st.session_state.enable_interp = None
    st.session_state.output = None
    st.session_state.have_interpreted = False
    st.session_state.inv_real = None


def reset_preprocess_state():
    """
    当修改深度范围后再次点击form_submit_button时，将预处理及之后过程中的部分session_state重置
    """
    st.session_state.removing = False
    st.session_state.filtering = False
    st.session_state.peak_detect = False
    # 各个深度点的3个峰位，初始化为0
    st.session_state.peaks = np.zeros((len(st.session_state.well_data), 3))
    st.session_state.drift_correct = False
    st.session_state.resolution_correct = False
    st.session_state.enable_interp = None
    st.session_state.output = None
    st.session_state.have_interpreted = False
    st.session_state.inv_real = None


def show_session_state():
    for item in st.session_state.items():
        st.write(item)
