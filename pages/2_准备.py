import streamlit as st
import tools.prepare as prep
import tools.musts as mst

st.set_page_config(page_title='伽马能谱解析平台', layout='wide')

mst.init_session_state()
mst.interrupt_widget_clean_up()

_f_real = st.file_uploader("请上传实测谱数据文件", type=["las", "xlsx", "xls"])
# 由于在多页面App中离开file_uploader再返回时其会初始化，即_f_real会置为None
# 且不能将file_uploader的key添加到st.session_state中，所以使用_f_real来临时保存其返回值
# 当_f_real不是None时，即重新上传了另一个文件，_f_real更新，则同时更新st.session_state.f_real
if _f_real is not None:
    st.session_state.f_real = _f_real
    mst.reset_session_state()
    prep.transform_f_real(st.session_state.f_real)
st.write("您上传的实测谱文件为：", st.session_state.f_real.name if st.session_state.f_real else None)
st.session_state.enable_transform = st.session_state.f_real is not None

# st.write("st.session_state.enable_transform =", st.session_state.enable_transform)  # 测试用
