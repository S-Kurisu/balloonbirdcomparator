#https://docs.streamlit.io/develop/
# app.py
import os
import datetime
import streamlit as st
from PIL import Image
import Plot_Coord
import time

# Directories
maps_dir = os.path.join(os.path.dirname(__file__), 'Maps/')

st.title("Weather Balloon x Bird Geolocation Comparator")

if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.datetime.now()

# Update maps once per hour
if 'last_hour' not in st.session_state:
    st.session_state.last_hour = -1

hour = datetime.datetime.now().hour
if hour != st.session_state.last_hour:
    if os.path.isdir(maps_dir):
        for f in os.listdir(maps_dir):
            os.remove(os.path.join(maps_dir, f))
    with st.spinner("Loading Map Data (this may take several minutes)..."):
        Plot_Coord.plot_coord()
    st.session_state.last_hour = hour
    st.success(f"Maps updated for hour {hour}")

maps = os.listdir(maps_dir) if os.path.isdir(maps_dir) else []
if maps:
    if 'curr' not in st.session_state:
        st.session_state.curr = 0

    def prev_map():
        if st.session_state.curr > 0:
            st.session_state.curr -= 1

    def next_map():
        if st.session_state.curr < len(maps) - 1:
            st.session_state.curr += 1

    #buttons
    col1, col2 = st.columns(2)
    col1.button("Back 1 Hour", on_click=next_map)
    col2.button("Forward 1 Hour", on_click=prev_map)

    # Display current map
    img_path = os.path.join(maps_dir, maps[st.session_state.curr])
    st.image(Image.open(img_path))
else:
    st.info("No maps found.")

now = datetime.datetime.now()
if (now - st.session_state.last_refresh).seconds >= 60:
    st.session_state.last_refresh = now
    st.experimental_rerun()
