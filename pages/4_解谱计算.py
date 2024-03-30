import streamlit as st
import tools.interpret as interp
import tools.musts as mst

st.set_page_config(page_title='伽马能谱解析平台', layout='wide')

mst.init_session_state()
mst.interrupt_widget_clean_up()

st.write("enable_interp:", st.session_state.enable_interp)

if st.toggle("输出产额", disabled=not st.session_state.enable_interp):
    st.session_state.output = interp.get_output(st.session_state.std_data, st.session_state.real_data,
                                                st.session_state.real_dept1,
                                                st.session_state.real_dept2)
    st.session_state.have_interpreted = True
