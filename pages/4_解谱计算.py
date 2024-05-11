import streamlit as st
import numpy as np
import pandas as pd
import tools.interpret as interp
import tools.musts as mst

st.set_page_config(page_title='伽马能谱解析平台', layout='wide')

mst.init_session_state()
mst.interrupt_widget_clean_up()

# st.session_state.enable_interp = True  # 测试用
# st.write("enable_interp:", st.session_state.enable_interp)

if st.toggle("输出产额", disabled=not st.session_state.enable_interp, key='tog_interp'):
    st.session_state.output = interp.get_output(st.session_state.std_data, st.session_state.well_data2,
                                                np.array([0, 0, 0], dtype=np.float64), start_interp=97)
    with st.expander("不同深度的K、U、Th具体含量表"):
        st.container(height=200).write(
            pd.DataFrame(st.session_state.output, columns=['Depth', 'K', 'U', 'Th']))
    with st.container(height=400):
        interp.show_output(st.session_state.output)
    st.session_state.have_interpreted = True
