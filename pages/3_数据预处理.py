import streamlit as st
import tools.preprocess as prepro
import tools.musts as mst
import re

st.set_page_config(page_title='伽马能谱解析平台', layout='wide')

mst.init_session_state()
mst.interrupt_widget_clean_up()

st.write("enable_transform=", st.session_state.enable_transform)
st.session_state.enable_choose = st.session_state.enable_transform

if st.session_state.f_real is not None and re.search('\.(las|LAS)$', st.session_state.f_real.name):
    st.subheader("-选择探测器")
    if st.session_state.enable_choose:
        wells_info = prepro.get_wells_info(st.session_state.real_data)
        if st.session_state.select_well is None:
            st.session_state.select_well = list(wells_info.keys())[0]
        st.session_state.well_info['name'] = st.selectbox("请选择您想处理的探测器", options=wells_info.keys(),
                                                          key='select_well')
        st.session_state.well_info['channel_size'] = wells_info[st.session_state.well_info['name']]

    st.divider()

st.subheader("-选择深度范围并输出原始谱图")
with st.form("dept_form"):
    dept1, dept2, step = st.columns([2, 2, 1])
    submitted = st.form_submit_button("确认提交深度范围", on_click=prepro.set_submitted_true,
                                      disabled=not st.session_state.enable_choose)
    # 当首次点击form_submit_button或者之后修改深度范围后再次点击form_submit_button时，更新well_data
    if submitted:
        st.session_state.well_data = prepro.get_well_data(st.session_state.real_data,
                                                          st.session_state.well_info['name'],
                                                          st.session_state.well_info['channel_size'],
                                                          st.session_state.real_dept1,
                                                          st.session_state.real_dept2)
        # 当well_data确认之后，初始化预处理过程中的数据well_data2为well_data
        st.session_state.well_data2 = st.session_state.well_data.copy()
        mst.reset_preprocess_state()
    # 初始化时不显示谱图，在不改变实测谱数据文件的条件下初次提交深度范围后，下面条件永真，显示数据在相应深度范围的谱图
    if st.session_state.submitted:
        with st.expander("原始谱图在相应深度范围的具体数据表"):
            st.container(height=200).write(st.session_state.well_data)
        prepro.show_raw_spectrum(st.session_state.well_data,
                                 st.session_state.well_info['name'],
                                 st.session_state.well_info['channel_size'])
        prepro.show_raw_gr(st.session_state.real_data)
        st.session_state.enable_prepro = True
    else:
        st.session_state.enable_prepro = False

with dept1:
    if st.session_state.real_dept1 is None:
        st.session_state.real_dept1 = st.session_state.max_real_dept
    st.number_input("请选择起始深度：", min_value=st.session_state.min_real_dept,
                    max_value=st.session_state.max_real_dept,
                    step=st.session_state.step_real_dept,
                    key="real_dept1",
                    disabled=not st.session_state.enable_choose)

with dept2:
    st.number_input("请选择结束深度：", min_value=st.session_state.min_real_dept,
                    max_value=st.session_state.max_real_dept,
                    step=st.session_state.step_real_dept,
                    key="real_dept2",
                    disabled=not st.session_state.enable_choose)

if st.session_state.f_real is not None and re.search('\.(xlsx|xls)$', st.session_state.f_real.name):
    with step:
        st.number_input("请设置深度步长：", min_value=0.0, max_value=1.0, step=0.25, key="step_fake_dept",
                        disabled=not st.session_state.enable_choose)

st.divider()

st.subheader("-预处理并输出预处理后的谱图")
# 分别表示剔除异常值、滤波、寻峰、谱漂校正、分辨率校正
removing, filtering, peak_detect, drift_correct, resolution_correct = st.columns(5)
graph_space = st.container(height=400)  # 在预处理过程中展示谱图

with removing:
    st.checkbox("异常值检测与处理", key='removing', disabled=not st.session_state.enable_prepro,
                on_change=prepro.prepro_func,
                args=[prepro.removing, not st.session_state.removing, st.session_state.well_data2, 5, 99])
with filtering:
    st.checkbox("滤波", key='filtering', disabled=not st.session_state.removing, on_change=prepro.prepro_func,
                args=[prepro.filtering, not st.session_state.filtering, st.session_state.well_data2, 5, 2])
with peak_detect:
    st.checkbox("寻峰", key='peak_detect', disabled=not st.session_state.filtering, on_change=prepro.prepro_func,
                args=[prepro.peak_detect, not st.session_state.peak_detect, st.session_state.well_data2])
with drift_correct:
    st.checkbox("谱漂校正", key='drift_correct', disabled=not st.session_state.peak_detect,
                on_change=prepro.prepro_func,
                args=[prepro.drift_correct, not st.session_state.drift_correct, st.session_state.std_peaks,
                      st.session_state.peaks, st.session_state.well_data2])
with resolution_correct:
    st.checkbox("分辨率校正", key='resolution_correct', disabled=not st.session_state.drift_correct,
                on_change=prepro.prepro_func,
                args=[prepro.resolution_correct, not st.session_state.resolution_correct, st.session_state.std_data,
                      st.session_state.well_data2])
with graph_space:
    if st.session_state.removing:
        with st.expander("预处理过程中的谱图在相应深度范围的具体数据表"):
            st.container(height=200).write(st.session_state.well_data2)
        with st.expander("峰位数据"):
            cols = st.columns(2)
            with cols[0]:
                st.write("实测谱峰位peaks:", st.session_state.peaks)
            with cols[1]:
                st.write("标准谱峰位std_peaks:", st.session_state.std_peaks)
        prepro.show_after_spectrum(st.session_state.well_data2, st.session_state.well_info['name'],
                                   st.session_state.well_info['channel_size'])

st.session_state.enable_interp = (st.session_state.removing and st.session_state.filtering
                                  and st.session_state.peak_detect and st.session_state.drift_correct
                                  and st.session_state.resolution_correct)
