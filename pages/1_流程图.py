import streamlit as st
import tools.musts as mst
from streamlit_react_flow import react_flow

st.set_page_config(page_title='伽马能谱解析平台', layout='centered')

mst.init_session_state()
mst.interrupt_widget_clean_up()

flowStyles = {"height": 700, "width": 2000}
elements = [{'id': 1, 'data': {'label': '准备(上传实测谱数据)'}, 'type': 'input', 'position': {'x': 250, 'y': 50}},
            {'id': 2, 'data': {'label': '数据预处理'}, 'position': {'x': 0, 'y': 150},
             'style': {'width': 600, 'height': 150}},
            {'id': 3, 'data': {'label': '解谱计算'}, 'position': {'x': 250, 'y': 350}},
            {'id': 4, 'data': {'label': '反演'}, 'position': {'x': 250, 'y': 450}},
            {'id': 5, 'data': {'label': '剔除异常值'}, 'position': {'x': 50, 'y': 200},
             'style': {'width': 90}, 'parentNode': 2, 'extent': 'parent'},
            {'id': 6, 'data': {'label': '滤波'}, 'position': {'x': 160, 'y': 200},
             'style': {'width': 90}, 'parentNode': 2, 'extent': 'parent'},
            {'id': 7, 'data': {'label': '寻峰'}, 'position': {'x': 270, 'y': 200},
             'style': {'width': 90}, 'parentNode': 2, 'extent': 'parent'},
            {'id': 8, 'data': {'label': '谱漂校正'}, 'position': {'x': 380, 'y': 200},
             'style': {'width': 90}, 'parentNode': 2, 'extent': 'parent'},
            {'id': 9, 'data': {'label': '分辨率校正'}, 'position': {'x': 490, 'y': 200},
             'style': {'width': 90}, 'parentNode': 2, 'extent': 'parent'}
            ]
elements.extend([{"id": f"e{i}-{i + 1}", "source": i, "target": i + 1} for i in range(1, 4)])
elements.extend([{'id': f"e{i}-{i + 1}", "source": i, "target": i + 1} for i in range(5, 9)])

react_flow("flow_chart", elements=elements, flow_styles=flowStyles)
