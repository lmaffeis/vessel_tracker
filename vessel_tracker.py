import asyncio
import websockets
import json
import streamlit as st
import pandas as pd
from datetime import datetime, timezone

async def connect_ais_stream(mmsi_filter, bounding_box):

    async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
        subscribe_message = {
            "APIKey": "cf26a3af737fd17145d3032ab887022b00b1a7d1",
            "BoundingBoxes": [[[-bounding_box, -bounding_box], [bounding_box, bounding_box]]],
            "FiltersShipMMSI": [mmsi_filter]
        }

        subscribe_message_json = json.dumps(subscribe_message)
        await websocket.send(subscribe_message_json)

        async for message_json in websocket:
            message = json.loads(message_json)
            message_type = message["MessageType"]

            if message_type == "PositionReport":
                ais_message = message['Message']['PositionReport']
                return ais_message['Latitude'], ais_message['Longitude']

def main():
    st.title("Vessel Location Tracker")

    mmsi_filter = st.text_input("Enter Vessel MMSI:", "")

    bounding_box_options = list(range(10, 100, 10))
    selected_bounding_box = st.selectbox("Select BoundingBox Size:", bounding_box_options)

    if st.button("Track Boat"):
        latitude, longitude = asyncio.run(connect_ais_stream(mmsi_filter, selected_bounding_box))

        rounded_latitude = round(latitude, 5)
        rounded_longitude = round(longitude, 5)

        st.write(f"Latitude: {rounded_latitude}")
        st.write(f"Longitude: {rounded_longitude}")

        # Create a DataFrame with the location data
        data = {'LATITUDE': [latitude], 'LONGITUDE': [longitude]}
        df = pd.DataFrame(data)

        st.write("Vessel Location:")
        st.map(df)

if __name__ == "__main__":
    main()
