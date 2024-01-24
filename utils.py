import streamlit as st
import geopandas as gpd
import folium
from folium.plugins import Draw
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import base64
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle



# Database connection parameters
db_params = {
    'user': 'postgres',
    'password': 'Admin',
    'host': 'localhost',
    'port': '5432',
    'database': 'airquality'
}
# Create a database engine
engine = create_engine(f'postgresql+psycopg2://{db_params["user"]}:{db_params["password"]}@{db_params["host"]}:{db_params["port"]}/{db_params["database"]}')
# Load GeoDataFrame using the engine
node = gpd.read_postgis("SELECT * FROM airqualitydata", engine, geom_col='geometry')
def main():
    st.set_page_config(layout="wide")  # Set the page layout to wide
    st.markdown(
        """
    <style>
        div[data-testid="column"]:nth-of-type(1) {
            border: 1px solid red;
            padding: 0;
            margin: 0;
        }

        div[data-testid="column"]:nth-of-type(2) {
            border: 1px solid blue;
            text-align: center;
            padding: 0;
            margin: 0;
        }

        div[data-testid="column"]:nth-of-type(3) {
            border: 1px solid red;
            text-align: center;
            padding: 0;
            margin: 0;
        }
    </style>

        """,unsafe_allow_html=True
    )
    # Create two columns with custom widths
    sidebar,MapArea, Equation = st.columns([2,6, 2])
    # Column 1 content with three headings
    with sidebar:
    # Sidebar content
        st.image("logo.png", width=250)
        st.title("Filters")
        # Get unique values for the selected column
        filter_datevalues = ['All'] + list(node['Datetime'].unique())  # Add 'All' to the list
        filter_Date = st.selectbox(f"Filter Date ['Datetime']", filter_datevalues)
        # Get unique values for the selected column
    # Dropdown filter for "performance," "pm10," "sound," "humidity," and "deviceid"
        filter_columns = st.selectbox("Filter by Column", ["Performance", "PM10", "O3", "PM2.5", "NO2","sound"])
        # Get unique values for the selected column
        filter_values = ['All'] + list(node[filter_columns].unique())  # Add 'All' to the list
        # Dropdown for specific values in the selected column
        filter_selected_value = st.selectbox(f"Filter by {filter_columns}", filter_values)
        # Apply filters to the GeoDataFrame
        if filter_selected_value == 'All':
            filtered_node = node
        else:
            filtered_node = node[node[filter_columns] == filter_selected_value]
        # Export button to download data in CSV format 
        if st.button("Export Data",use_container_width=True):
            csv_data = filtered_node.to_csv(index=False)
            b64 = base64.b64encode(csv_data.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="filtered_data.csv">Download CSV</a>'
            st.markdown(href, unsafe_allow_html=True)
    with MapArea:
        m = folium.Map(location=[filtered_node['geometry'].centroid.y.mean(), filtered_node['geometry'].centroid.x.mean()], zoom_start=10)
 #       m = folium.Map(location=map_center, zoom_start=10)
        # Define color ranges based on the selected filter column
        color_range_symbol = {
            'Performance': [(1200, 12000, '#ff5050'),(800, 1200, '#ff5050'), (400, 800, '#f0e641'), (200, 400, '#50cdaa'),(0, 200, '#50f0e6')],
            'PM10': [(100, 10000,'#960032'),(51, 100, '#ff5050'), (36, 50, '#f0e641'),  (21, 35, '#50cdaa'),  (0, 20, '#50f0e6'), ],
            'O3': [(400,40000, '#960032'),(240,400, '#960032'),(181, 240, '#ff5050'),(121, 180, '#f0e641'),(61, 120, '#50cdaa'),(0, 60, '#50f0e6')],
            'PM2.5': [(100, 10000, '#960032'),(50,100, '#960032') ,(25, 50, '#ff5050'),(20, 25, '#f0e641'),(10, 20, '#50cdaa'),(0, 10, '#50f0e6')],
            'NO2': [(200, 20000, '#960032'), (100, 200, '#ff5050'),(40, 100, '#f0e641'), (20, 40, '#50cdaa'), (0, 20, '#50f0e6')],
            'sound': [(100, 10000,'#960032'),(51, 100, '#ff5050'), (36, 50, '#f0e641'),  (21, 35, '#50cdaa'),  (0, 20, '#50f0e6') ],
        }
        # Add the Esri World Imagery basemap
        Imagery = folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
            name='World Imagery'
        )
        Imagery.add_to(m)
        # Create a MarkerCluster to group markers
        marker_cluster = MarkerCluster(name="Nodes").add_to(m)
        # Iterate through the GeoDataFrame and add features with popups
        for idx, row in filtered_node.iterrows():
            value = row[filter_columns]
            popup_html = f'<b>Performance:</b> {row["Performance"]}<br>'
            popup_html += f'<b>NO2:</b> {row["NO2"]}<br>'
            popup_html += f'<b>O3:</b> {row["O3"]}<br>'
            popup_html += f'<b>PM 2.5:</b> {row["PM2.5"]}<br>'
            popup_html += f'<b>PM 10:</b> {row["PM10"]}<br>'
            popup_html += f'<b>co2:</b> {row["co2"]}<br>'
            popup_html += f'<b>health:</b> {row["health"]}<br>'
            popup_html += f'<b>humidity:</b> {row["humidity"]}<br>'
            popup_html += f'<b>humidity_abs:</b> {row["humidity_abs"]}<br>'
            popup_html += f'<b>Measure Time:</b> {row["measuretime"]}<br>'
            popup_html += f'<b>Pressure:</b> {row["pressure"]}<br>'
            popup_html += f'<b>PM1:</b> {row["PM1"]}<br>'
            popup_html += f'<b>Sound:</b> {row["sound"]}<br>'
            popup_html += f'<b>sound_max:</b> {row["sound_max"]}<br>'
            popup_html += f'<b>temperature:</b> {row["temperature"]}<br>'
            popup_html += f'<b>timestamp:</b> {row["timestamp"]}<br>'
            popup_html += f'<b>tvoc:</b> {row["tvoc"]}<br>'
            popup_html += f'<b>uptime:</b> {row["uptime"]}<br>'
            popup_html += f'<b>latitude:</b> {row["latitude"]}<br>'
            popup_html += f'<b>longitude:</b> {row["longitude"]}<br>'
            # Get color based on the filter column value and color ranges
            color = None
            try:
                numeric_value = float(value)
                for color_range in color_range_symbol.get(filter_columns, []):
                    if color_range[0] <= numeric_value < color_range[1]:
                        color = color_range[2]
                        break
            except ValueError:
                # Handle the case where the value is not a valid number
                color = 'gray'
            # Use a default color if no match found
            if color is None:
                color = 'gray'
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=8,
                color='none',
                fill_color=color,
                fill_opacity=1.0,
                popup=folium.Popup(popup_html, max_width=300),
            ).add_to(marker_cluster)
        # Draw widget on the map
        Draw().add_to(m)
        # Fullscreen and Geocoder plugins
        folium.plugins.Fullscreen(position="topright", title="Expand me", title_cancel="Exit me", force_separate_button=True).add_to(m)
        folium.plugins.Geocoder(position="topright", collapsed=True).add_to(m)
        # Add LayerControl to the map
        folium.LayerControl().add_to(m)
        # Display the map using st_folium
        folium_static(m, width=800, height=550)
        legend_data = [
            ('Very Good', '#50f0e6'),
            ('Good', '#50cdaa'),
            ('Moderate', '#f0e641'),
            ('Bad', '#ff5050'),
            ('Very Bad', '#960032')
        ]
        fig, ax = plt.subplots(figsize=(10, 1))
        ax.set_axis_off()
        box_size = 0.0
        rectangles = [
            patches.Rectangle((0.1 + i * 0.2, 0.35), box_size, box_size/2, color=color, label=label)
            for i, (label, color) in enumerate(legend_data)
        ]
        for rect in rectangles:
            ax.add_patch(rect)
        ax.legend(loc='center', bbox_to_anchor=(0.5, 0.5), ncol=len(legend_data), prop={'size': 10}, frameon=False)
        st.pyplot(fig)
      # Graph Code
        datetime_values = node['Datetime']  # Assuming 'Datetime' is the correct column name
        filter_columns = filtered_node[filter_columns]  # Use the dynamic column selected by the user
        # Define color ranges based on the selected filter column
        color_range_dict = {
            'Performance': [(1200, float(filter_columns.max()) + 1, '#960032'), (800, 1200, '#ff5050'), (400, 800, '#f0e641'), (200, 400, '#50cdaa'), (0, 200, '#50f0e6')],
            'PM10': [(100, float(filter_columns.max()) + 1,'#960032'),(51, 100, '#ff5050'), (36, 50, '#f0e641'),  (21, 35, '#50cdaa'),  (0, 20, '#50f0e6'), ],
            'O3': [(400, float(filter_columns.max()) + 1, '#960032'),(240,400, '#960032'),(181, 240, '#ff5050'),(121, 180, '#f0e641'),(61, 120, '#50cdaa'),(0, 60, '#50f0e6')],
            'PM2.5': [(100, float(filter_columns.max()) + 1, '#960032'),(50,100, '#960032') ,(25, 50, '#ff5050'),(20, 25, '#f0e641'),(10, 20, '#50cdaa'),(0, 10, '#50f0e6')],
            'NO2': [(200, float(filter_columns.max()) + 1, '#960032'), (100, 200, '#ff5050'),(40, 100, '#f0e641'), (20, 40, '#50cdaa'), (0, 20, '#50f0e6')],
        }
        color_ranges = color_range_dict.get(filter_columns.name, [])  # Get the color ranges based on the selected filter column
        # Create shapes for each color range
        shapes = []
        for color_range in color_ranges:
            shapes.append(dict(
                type='rect',
                xref='paper',
                yref='y',
                x0=0,
                x1=1,
                y0=color_range[0],
                y1=color_range[1],
                fillcolor=color_range[2],
                opacity=0.9,
                layer='below',
                line=dict(width=0),
            ))
        # Create a trace (line chart)
        trace = go.Scatter(x=datetime_values, y=filter_columns, mode='lines', name='Line Chart', line=dict(color='black'))
        # Create a layout with shapes
        layout = go.Layout(
            title=f'Line Chart with Background Color Classification ({filter_columns.name})',
            xaxis=dict(title='Datetime'),
            yaxis=dict(title=filter_columns.name),  # Use the column name as the y-axis title
            shapes=shapes
        )
        # Create a figure
        fig = go.Figure(data=[trace], layout=layout)
        # Show the figure
        st.plotly_chart(fig)
  # Column 2 content with two paragraphs
    with Equation:
                     # Classification function

        st.write(f"**Filter Column:** {filter_columns.name}")
        st.write(f"**Air quality Value:** {filter_selected_value}")

        def classify_air_quality(value):
            try:
                numeric_value = float(value)
                if 0 <= numeric_value <= 20:
                    return "Very Good"
                elif 21 <= numeric_value <= 40:
                    return "Good"
                elif 41 <= numeric_value <= 100:
                    return "Moderate"
                elif 101 <= numeric_value <= 200:
                    return "Poor"
                else:
                    return "Very Poor"
            except ValueError:
                return "      "
        # Classify and display the class
        class_value = classify_air_quality(filter_selected_value)
        st.write(f"**Air quality Index:** {class_value}")
if __name__ == '__main__':
    main()
