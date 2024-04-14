import streamlit as st
import tools.error_analysis as err
import tools.musts as mst

st.set_page_config(page_title='伽马能谱解析平台', layout='wide')

mst.init_session_state()
mst.interrupt_widget_clean_up()

st.write("st.session_state.have_interpreted:", st.session_state.have_interpreted)

show_contrast = st.toggle("输出对比图", disabled=not st.session_state.have_interpreted)
container = st.container()
show_error = st.toggle("输出误差", disabled=not show_contrast)
with container:
    if show_contrast:
        st.session_state.err_real = err.show_contrast(st.session_state.std_data, st.session_state.well_data2,
                                                      st.session_state.output)
if show_contrast and show_error:
    err.show_error(st.session_state.well_data2, st.session_state.err_real)
