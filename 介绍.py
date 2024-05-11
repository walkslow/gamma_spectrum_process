import numpy as np
import streamlit as st
import pandas as pd
# import re
import tools.musts as mst

st.set_page_config(page_title='伽马能谱解析平台', layout='wide')

mst.init_session_state()
mst.interrupt_widget_clean_up()

# st.write("std_data的形状：", st.session_state.std_data.shape)
# st.write("std_data:", st.session_state.std_data)
# st.session_state.std_peaks = np.array([112, 134, 197])  # K、U、Th在标准谱中的峰位

# with open('intro.svg', 'r', encoding='utf-8') as f:
#     svg_content = f.read()
# svg_content = re.search(r'<svg.*?</svg>', svg_content, re.DOTALL).group()
# st.write("svg_content的类型：", type(svg_content))
# st.write(svg_content)
# st.image(svg_content)
# st.write(svg_content,unsafe_allow_html=True)
st.image("intro.png")
st.markdown("伽马能谱测井是按照不同能量范围记录自然伽马射线强度的一种测井方法。"
            "地层放出的伽马射线大多数由钾、钍、铀衰变而来，通过处理伽马能谱类测井数据，可以得出地层中钾、钍、铀的含量。"
            "这对于研究地层特性、识别生油层和油气勘探开发等具有重要的指导意义。"
            "由于测井环境的复杂多变和测井仪器的自身缺陷等原因，对伽马能谱类测井数据的后期处理一直是整个测井过程中的重点与难点。"
            "本平台采用 KNN 算法对测井数据进行异常值检测与处理，利用 Savitzky-Golay 滤波器消除噪声与统计涨落，采用高斯拟合法寻峰，"
            "使用多项式拟合进行谱漂校正，最后使用最小二乘法进行解谱分析，得出钾、钍、铀在各个深度地层中的含量。")
