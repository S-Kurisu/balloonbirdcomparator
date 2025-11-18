#https://docs.streamlit.io/develop/
import os
import datetime
import streamlit as st
from PIL import Image
import Plot_Coord
import time

maps_dir = os.path.join(os.path.dirname(__file__), 'Maps/')
st.title("Weather Balloon x Bird Geolocation Comparator")

#dynamic 'live' updating
if 'last_hour' not in st.session_state:
    st.session_state.last_hour = -1

current_hour = datetime.datetime.now().hour

if current_hour != st.session_state.last_hour:
    with st.spinner("Loading Current Hour's Map Data (this may take several minutes)..."):
        # Clear old maps
        if os.path.isdir(maps_dir):
            for f in os.listdir(maps_dir):
                os.remove(os.path.join(maps_dir, f))
        # Generate new maps
        Plot_Coord.plot_coord()

    st.session_state.last_hour = current_hour
    st.success(f"Maps updated for hour {current_hour}")

maps = sorted(os.listdir(maps_dir)) if os.path.isdir(maps_dir) else []

if maps:
    if 'curr' not in st.session_state:
        st.session_state.curr = 0

    #functions for buttons
    def prev_map():
        if st.session_state.curr > 0:
            st.session_state.curr -= 1

    def next_map():
        if st.session_state.curr < len(maps) - 1:
            st.session_state.curr += 1

    #Buttons
    col1, col2 = st.columns(2)
    col1.button("Previous Hour", on_click=next_map)
    col2.button("Next Hour", on_click=prev_map)
    
    img_path = os.path.join(maps_dir, maps[st.session_state.curr])
    st.write(st.session_state.curr)
    st.image(Image.open(img_path))
else:
    st.info("No maps found.")
