import pandas as pd
import streamlit as st
import lasio
import chardet
import re
import tools.musts as mst

# 当Excel类型的实测谱数据不包含列名时，默认设置的测井名称
DEFAULT_WELL_NAME = 'W1'
# 由于默认Excel类型的实测谱不包含深度列，默认设置深度的最大值、最小值如下：
DEFAULT_EXCEL_MAX_DEPT = 5000.0
DEFAULT_EXCEL_MIN_DEPT = 1000.0
# 下面的步长是输入深度范围的st.number_input的step参数，是调节深度范围的，与实际的深度步长没有关系
DEFAULT_EXCEL_STEP_DEPT = 1.0
# 下面的步长是Excel文件类型的实测谱数据的步长，是用户指定的，是确定深度范围中的每个深度值的
DEFAULT_FAKE_STEP_DEPT = 0.25


@st.cache_data(max_entries=3, persist=True,
               show_spinner="正在对LAS文件格式的实测谱数据进行格式转换...")
def f_real_to_las(f_real):
    """
    将UploadedFile类型的实测谱数据LAS文件转换为LASFile类型的对象
    :param f_real: 由st.file_uploader上传的实测谱数据LAS文件
    :return:real_data:LASFile类型的实测谱数据
    """
    f_bytes = f_real.getvalue()
    detected_encoding = chardet.detect(f_bytes)["encoding"]
    f_string = f_bytes.decode(detected_encoding)
    real_data = lasio.read(f_string, ignore_header_errors=True, ignore_comments=('#', '"'),
                           read_policy='comma-delimiter', accept_regexp_sub_recommendations=False,
                           dtypes='auto')
    return real_data


def set_las_depths():
    """
    根据LAS文件实测谱数据设置深度范围和步长
    :return:
    """
    if st.session_state.real_data.well.STRT.value > st.session_state.real_data.well.STOP.value:
        min_dept = st.session_state.real_data.well.STOP.value
        max_dept = st.session_state.real_data.well.STRT.value
        step_dept = -st.session_state.real_data.well.STEP.value
    else:
        min_dept = st.session_state.real_data.well.STRT.value
        max_dept = st.session_state.real_data.well.STOP.value
        step_dept = st.session_state.real_data.well.STEP.value
    st.session_state.min_real_dept = min_dept
    st.session_state.max_real_dept = max_dept
    st.session_state.step_real_dept = step_dept


def set_excel_depths(min_dept=DEFAULT_EXCEL_MIN_DEPT, max_dept=DEFAULT_EXCEL_MAX_DEPT,
                     step_real_dept=DEFAULT_EXCEL_STEP_DEPT, step_fake_dept=DEFAULT_FAKE_STEP_DEPT):
    st.session_state.min_real_dept = min_dept
    st.session_state.max_real_dept = max_dept
    st.session_state.step_real_dept = step_real_dept
    st.session_state.step_fake_dept = step_fake_dept


@st.cache_data(max_entries=5)
def has_col_names(f_real):
    """
    判断通过st.file_uploader上传的Excel文件是否包含列名
    我们认为：如果Excel文件的第一行中存在非数字，则该Excel文件有列名
    反之，如果第一行全由数字或者None组成，则无列名
    :param f_real:
    :return:一个元组，第一个元素表示是否含列名，第二个元素表示测井的名称
    """
    first_row = pd.read_excel(f_real, header=None, nrows=1)
    for value in first_row.iloc[0]:
        if value is not None and not isinstance(value, (int, float)):
            well_name = re.sub('\[\d+]$', '', value)
            return True, well_name
    return False, DEFAULT_WELL_NAME


@st.cache_data(max_entries=3, persist=True,
               show_spinner="正在对Excel文件格式的实测谱数据进行格式转换...")
def f_real_to_df(f_real):
    """
    将UploadedFile类型的实测谱数据Excel文件转换为DataFrame类型的对象
    :param f_real: 由st.file_uploader上传的实测谱数据Excel文件
    :return:(real_data, well_name, channel_size):
    """
    if has_col_names(f_real)[0]:
        real_data = pd.read_excel(f_real)
        well_name = has_col_names(f_real)[1]
        channel_size = real_data.shape[1]
        return real_data, well_name, channel_size
    else:
        real_data = pd.read_excel(f_real, header=None)
        channel_size = real_data.shape[1]
        real_data.columns = [f'{DEFAULT_WELL_NAME}[{i + 1}]' for i in range(channel_size)]
        return real_data, DEFAULT_WELL_NAME, channel_size


def transform_f_real(f_real):
    """
    将UploadedFile类型的实测谱数据文件转换为方便处理的类型，
    根据实测谱数据获得深度范围和步长，
    :param f_real: 由st.file_uploader上传的实测谱数据文件
    :return:
    """
    if re.search('\.(las|LAS)$', f_real.name):
        st.session_state.real_data = f_real_to_las(f_real)
        set_las_depths()
    elif re.search('\.(xlsx|xls)$', f_real.name):
        st.session_state.real_data, st.session_state.well_info['name'], st.session_state.well_info[
            'channel_size'] = f_real_to_df(f_real)
        set_excel_depths()
