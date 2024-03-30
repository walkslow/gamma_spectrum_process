import streamlit as st
import pandas as pd
# import re
import tools.musts as mst

st.set_page_config(page_title='伽马能谱解析平台', layout='wide')

mst.init_session_state()
mst.interrupt_widget_clean_up()
st.session_state.std_data = pd.read_excel("K、Th、U标准谱数据.xlsx")

# with open('intro.svg', 'r', encoding='utf-8') as f:
#     svg_content = f.read()
# svg_content = re.search(r'<svg.*?</svg>', svg_content, re.DOTALL).group()
# st.write("svg_content的类型：", type(svg_content))
# st.write(svg_content)
# st.image(svg_content)
# st.write(svg_content,unsafe_allow_html=True)
st.image("intro.png")