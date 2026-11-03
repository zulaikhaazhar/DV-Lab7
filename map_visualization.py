
import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Interactive World Map",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Interactive Map Visualization Examples")

st.markdown(
    """
    <div style="
        font-size: 18px;
        font-weight: 600;
        color: #4A90A4;
        margin-top: -10px;
        margin-bottom: 5px;
    ">
        Prepared by: Zulaikha Mohd Azhar
    </div>
    """,
    unsafe_allow_html=True
)

st.write(
    "Explore world geographical data through "
    "different map visualization techniques."
)

st.caption("TFB3133 / TEB3133 – Data Visualization | Lab 7")

# ==========================================
# 2. LOAD NATURAL EARTH DATASET
# ==========================================

@st.cache_data
def load_data():

    file_path = (
        "ne_110m_admin_0_countries/"
        "ne_110m_admin_0_countries.shp"
    )

    gdf = gpd.read_file(file_path)

    # Detect country name column
    if "name" in gdf.columns:
        country_col = "name"
    elif "NAME" in gdf.columns:
        country_col = "NAME"
    elif "ADMIN" in gdf.columns:
        country_col = "ADMIN"
    else:
        raise ValueError(
            "Country name column not found in dataset."
        )

    # Add simulated population if unavailable
    if "pop_est" not in gdf.columns:
        np.random.seed(0)
        gdf["pop_est"] = np.random.randint(
            1000000, 1000000000, size=len(gdf)
        )

    return gdf, country_col


# ==========================================
# 3. LOAD DATA
# ==========================================

try:
    gdf, country_col = load_data()

except Exception as e:
    st.error(f"Unable to load map dataset: {e}")
    st.stop()


# ==========================================
# 4. SIDEBAR NAVIGATION
# ==========================================

st.sidebar.title("🌍 Map Controls")

st.sidebar.header("Choose a Map Type")

map_type = st.sidebar.radio(
    "Select Map Type",
    [
        "Map Cosmetics",
        "Map Visual Hierarchy",
        "Choropleth Map",
        "Geo Projection"
    ]
)

# ==========================================
# 7. CALCULATE POPULATION DENSITY
# ==========================================

def calculate_density(data):

    # Project to an equal-area coordinate system
    # before calculating geographical area.
    projected = data.to_crs("EPSG:6933")

    area_km2 = projected.geometry.area / 1000000

    density = (
        projected["pop_est"] / area_km2
    ).replace([np.inf, -np.inf], np.nan)

    return density.fillna(0)

# ==========================================
# 5. MAP COSMETICS
# ==========================================

if map_type == "Map Cosmetics":

    st.header("1. Map Cosmetics")

    st.write(
        "Customize the appearance of the world map "
        "using different colors and backgrounds."
    )

    map_color = st.selectbox(
        "Choose Map Color",
        ["skyblue", "lightgreen", "orange", "lightcoral"]
    )

    background_color = st.selectbox(
        "Choose Background Color",
        ["lightgrey", "white", "lightyellow", "lightblue"]
    )

    fig, ax = plt.subplots(figsize=(12, 7))

    gdf.plot(
        ax=ax,
        color=map_color,
        edgecolor="black",
        linewidth=0.5
    )

    ax.set_title(
        "Styled World Map",
        fontsize=16,
        fontweight="bold"
    )

    ax.set_facecolor(background_color)

    ax.set_axis_off()

    st.pyplot(fig)
    plt.close(fig)

    st.success(
        "Map cosmetics successfully customized!"
    )


# ==========================================
# 6. MAP VISUAL HIERARCHY
# ==========================================

elif map_type == "Map Visual Hierarchy":

    st.header("2. Map Visual Hierarchy")

    st.write(
        "Select countries to highlight in red. "
        "Other countries will remain sky blue."
    )

    default_countries = [
        "Brazil", "India", "China",
        "Australia", "South Africa", "Russia"
    ]

    available_countries = gdf[country_col].dropna().tolist()

    default_countries = [
        country for country in default_countries
        if country in available_countries
    ]

    highlighted_countries = st.multiselect(
        "Select Countries to Highlight",
        available_countries,
        default=default_countries
    )

    # Assign colors
    gdf_visual = gdf.copy()

    gdf_visual["color"] = gdf_visual[
        country_col
    ].apply(
        lambda x: "red"
        if x in highlighted_countries
        else "skyblue"
    )

    fig, ax = plt.subplots(figsize=(12, 7))

    gdf_visual.plot(
        ax=ax,
        color=gdf_visual["color"],
        edgecolor="black",
        linewidth=0.5
    )

    ax.set_title(
        "World Map with Highlighted Countries",
        fontsize=15,
        fontweight="bold"
    )

    ax.set_axis_off()

    st.pyplot(fig)
    plt.close(fig)

    st.write(
        f"Number of highlighted countries: "
        f"{len(highlighted_countries)}"
    )



# ==========================================
# 8. CHOROPLETH MAP
# ==========================================

elif map_type == "Choropleth Map":

    st.header("3. Choropleth Map")

    st.write(
        "Visualize population density using "
        "different color schemes and log transformation."
    )

    color_choice = st.selectbox(
        "Choose Color Scheme",
        ["OrRd", "YlGn", "Blues", "Purples", "Greens"],
        index=0
    )

    use_log_scale = st.checkbox(
        "Use Log Transformation",
        value=True
    )

    gdf_choro = gdf.copy()

    gdf_choro["pop_density"] = calculate_density(
        gdf_choro
    )

    if use_log_scale:
        gdf_choro["pop_density"] = np.log1p(
            gdf_choro["pop_density"]
        )

    fig, ax = plt.subplots(figsize=(12, 7))

    gdf_choro.plot(
        column="pop_density",
        cmap=color_choice,
        edgecolor="black",
        linewidth=0.3,
        legend=True,
        ax=ax,
        missing_kwds={
            "color": "lightgrey",
            "label": "No data"
        }
    )

    ax.set_title(
        f"Population Density by Country "
        f"(Color Scheme: {color_choice})",
        fontsize=15,
        fontweight="bold"
    )

    ax.set_axis_off()

    st.pyplot(fig)
    plt.close(fig)

    if use_log_scale:
        st.info(
            "Log transformation is enabled. "
            "This helps reduce the effect of extremely "
            "large population density values."
        )
    else:
        st.info(
            "Log transformation is disabled. "
            "The original population density values "
            "are displayed."
        )


# ==========================================
# 9. GEO PROJECTION
# ==========================================

elif map_type == "Geo Projection":

    st.header("4. Geo Projection")

    st.write(
        "Explore how different geographical "
        "projections affect the appearance of the world map."
    )

    projection_options = {
        "WGS 84 (Original)": "EPSG:4326",
        "Web Mercator": "EPSG:3857",
        "Mollweide": "ESRI:54009",
        "Equal Earth": "EPSG:8857"
    }

    proj_choice = st.selectbox(
        "Select a Projection",
        list(projection_options.keys())
    )

    color_choice = st.selectbox(
        "Choose Color Scheme",
        ["OrRd", "YlGn", "Blues", "Purples", "Greens"]
    )

    use_log_scale = st.checkbox(
        "Use Log Transformation for Population Density",
        value=True
    )

    gdf_proj = gdf.copy()

    gdf_proj["pop_density"] = calculate_density(
        gdf_proj
    )

    if use_log_scale:
        gdf_proj["pop_density"] = np.log1p(
            gdf_proj["pop_density"]
        )

    try:

        gdf_proj = gdf_proj.to_crs(
            projection_options[proj_choice]
        )

        fig, ax = plt.subplots(figsize=(12, 7))

        gdf_proj.plot(
            column="pop_density",
            cmap=color_choice,
            edgecolor="black",
            linewidth=0.3,
            legend=True,
            ax=ax
        )

        ax.set_title(
            f"World Map in {proj_choice} Projection",
            fontsize=15,
            fontweight="bold"
        )

        ax.set_axis_off()

        st.pyplot(fig)
        plt.close(fig)

        st.success(
            f"Currently displaying: {proj_choice}"
        )

    except Exception as e:
        st.error(
            f"Unable to apply this projection: {e}"
        )


# ==========================================
# 10. LAB 7 REFLECTION REPORT
# ==========================================

st.divider()

st.header("📝 Lab 7 Reflection Report")

st.markdown("""
### 1. Introduction

This lab focuses on creating interactive geographical
visualizations using Streamlit, GeoPandas, Matplotlib,
and NumPy. The Natural Earth dataset was used to display
countries around the world and explore different
mapping techniques.

### 2. Map Cosmetics

The first experiment involved customizing the map's
appearance by changing country colors, border colors,
and background colors. These changes improved the
visual presentation of the map and demonstrated how
map cosmetics can make geographical information
more visually appealing and easier to understand.

### 3. Map Visual Hierarchy

The second experiment highlighted selected countries
in red while keeping the remaining countries in sky
blue. This created a visual hierarchy that made the
selected countries stand out immediately. The
experiment demonstrated how contrasting colors
can direct the audience's attention towards important
geographical areas.

### 4. Choropleth Map

The third experiment visualized population density
using different color schemes, including OrRd, YlGn,
Blues, Purples, and Greens. I also experimented with
logarithmic transformation. This transformation helps
reduce the impact of extremely large values and makes
differences in population density easier to visualize.

### 5. Geo Projection

The final experiment explored different geographical
projections, including WGS 84, Web Mercator,
Mollweide, and Equal Earth. Each projection changes
the appearance and representation of the world map.
This demonstrated that selecting an appropriate
projection is important because geographical
projections can introduce different distortions.

### 6. Conclusion

Overall, this lab improved my understanding of
geographical data visualization and how different
visualization techniques communicate information.
I learned how map cosmetics, visual hierarchy,
choropleth maps, and geographical projections can
affect the interpretation of geographical data.
Combining these techniques with Streamlit also
allows users to explore and customize visualizations
interactively.

Note: If the Natural Earth dataset does not contain
population estimates, the application generates
random sample values. Therefore, the resulting
population density visualization should not be
interpreted as actual population statistics.
""")

st.caption(
    "TFB3133 / TEB3133 Data Visualization - Lab 7"
)
