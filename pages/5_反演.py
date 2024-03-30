import streamlit as st
import tools.invert as inv
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
        st.session_state.inv_real = inv.show_contrast(st.session_state.std_data, st.session_state.real_data,
                                                      st.session_state.output)
if show_contrast and show_error:
    inv.show_error(st.session_state.real_data, st.session_state.inv_real)
