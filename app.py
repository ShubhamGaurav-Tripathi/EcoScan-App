import streamlit as st
import requests
import plotly.graph_objects as go
from PIL import Image
from pyzbar.pyzbar import decode
from fpdf import FPDF
import base64
import time
import json
import math

# --- 1. CONFIGURATION / CONSTANTS ---
PAGE_TITLE = "EcoShop - Sustainable Shopping Assistant"
DEMO_BARCODES_MAP = {
    "Jimjam": "8901063029279",
    "Nutella": "3017620429484",
    "Coca-Cola": "5449000000996",
    "Dairy Milk": "7622201762063",
    "Masala Oats": "8901088068734"
}

# --- 2. CSS STYLES ---
def apply_custom_css():
    st.markdown("""
        <style>
            /* 1. Overall Page & App Container: Ensure no page-level scrolling */
            html, body, .stApp {
                height: 100vh; /* Make it fill the entire viewport height */
                width: 100vw;  /* Make it fill the entire viewport width */
                margin: 0;
                padding: 0;
                overflow: hidden; /* CRUCIAL: Prevents scrollbars on the html/body/main app itself */
                display: flex;
                flex-direction: column; /* Stack children vertically */
            }

            /* Hide Streamlit default header/footer if any, to reclaim space */
            header, footer {
                visibility: hidden;
                height: 0;
                margin: 0;
                padding: 0;
            }

            /* 2. Main Content Block: The area after the title, before the tab content */
            .block-container {
                flex-grow: 1; /* Allow it to take all remaining vertical space within .stApp */
                height: 100%; /* IMPORTANT: It needs a defined height for its flex children */
                max-width: 95vw; /* Keep consistent width constraint */
                overflow: hidden; /* No scrolling for this main block either */
                display: flex;
                flex-direction: column; /* Stack title, tabs, and tab-content area */
                padding-top: 0.5rem; /* Reduced top padding */
            }

            /* Adjust title and tabs to take their space without growing/shrinking */
            h1 {
                margin: 0px; /* Remove default margins */
                flex-shrink: 0;
                padding-bottom: 0.5rem; /* Add some space below title */
            }
            [data-testid="stTabs"] {
                flex-shrink: 0;
                margin-bottom: 0; /* Adjust margin below tabs */
            }

            /* 3. Tab Panel Content: The area inside the selected tab (contains the columns) */
            div[role="tabpanel"] {
                flex-grow: 1; /* Make tab content fill remaining height within block-container */
                height: 100%; /* IMPORTANT: Must have defined height for its column children */
                display: flex; /* Make it a flex container for the columns */
                flex-direction: row; /* Layout columns horizontally */
                overflow: hidden; /* No scrolling for the tab panel itself */
                padding: 0 1rem; /* Adjust horizontal padding */
            }

            /* 4. Streamlit Columns: Ensure columns take full height and are flex containers */
            [data-testid="stColumn"] {
                display: flex;
                flex-direction: column; /* Stack content within columns vertically */
                flex-grow: 1; /* Allow columns to expand to fill horizontal space */
                height: 100%; /* IMPORTANT: Makes column take full height of its tabpanel parent */
                overflow: hidden; /* No scrolling for the column container itself */
            }

            /* 5. CRUCIAL: The actual scrollable content block within the RIGHT column */
            /* This targets the `stVerticalBlock` div, which is the direct parent of your st.elements
               within each column. We want *this* element to scroll if its content overflows. */
            [data-testid="stColumn"]:nth-of-type(2) > div:first-child > [data-testid="stVerticalBlock"] {
                flex-grow: 1; /* Allow this content block to take available vertical space */
                overflow-y: auto; /* FINALLY, make THIS area scrollable */
                padding-right: 1rem; /* Add padding for scrollbar visibility */
                padding-left: 1rem; /* Add some left padding to match general UI */
                min-height: 0; /* Essential for flex-grow to work correctly with overflow:auto */
            }
            /* Adjust padding/margin for `stVerticalBlock` within the left column as well, if needed */
            [data-testid="stColumn"]:nth-of-type(1) > div:first-child > [data-testid="stVerticalBlock"] {
                padding-right: 1rem;
                padding-left: 1rem;
            }


            /* Adjust Plotly charts to fill available space without causing overflow */
            .stPlotlyChart {
                height: auto !important; /* Allow plotly chart to determine its height based on content */
                max-height: 400px; /* Set a maximum height to prevent excessively tall charts */
                min-height: 250px; /* Ensure a minimum size for visibility */
                width: 100% !important; /* Fill parent width */
                margin: 0px !important; /* Remove all default margins around the chart */
                padding: 0px !important; /* Remove all default paddings around the chart */
                border: 1px solid #e0e0e0; /* Add a subtle border to the chart */
                border-radius: 5px; /* Slightly rounded corners for the border */
            }

            /* Adjust margins/padding for various Streamlit elements for a tighter layout */
            .stMarkdown, .stSubheader, .stTextInput, .stFileUploader, .stSelectbox,
            .stButton, .stMetric, .stProgress, .stSuccess, .stInfo, .stWarning, .stError,
            div[data-testid="stHorizontalBlock"] {
                margin-bottom: 0.2rem !important; /* Reduced margin */
                margin-top: 0.2rem !important;    /* Reduced margin */
                padding-top: 0.2rem !important;   /* Reduced padding */
                padding-bottom: 0.2rem !important;/* Reduced padding */
            }

            /* Specific adjustment for subheaders to control space */
            .stSubheader {
                margin-top: 0.5rem !important; /* Slightly more space above subheaders */
                margin-bottom: 0.2rem !important; /* Less space below subheaders */
            }

            /* Specific adjustment for the HR line (st.write("---")) */
            hr {
                margin-top: 0.3rem !important; /* Reduce space above HR */
                margin-bottom: 0.3rem !important; /* Reduce space below HR */
                border-top: 1px solid #eee; /* Lighten HR line if needed */
            }

            /* Adjust spacing for metrics */
            div[data-testid="stMetric"] {
                padding: 0.5rem !important;
                margin-bottom: 0.5rem !important;
            }
        </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE INITIALIZATION ---
def initialize_session_state():
    if 'current_barcode' not in st.session_state:
        st.session_state.current_barcode = None
    if 'manual_barcode_input' not in st.session_state:
        st.session_state.manual_barcode_input = ""
    if 'selected_demo_product' not in st.session_state:
        st.session_state.selected_demo_product = None

# --- 4. CALLBACK FUNCTIONS ---
# Callback functions to update the barcode in session state
def update_barcode_from_manual_input():
    st.session_state.current_barcode = st.session_state.manual_barcode_input
    st.session_state.selected_demo_product = None # Clear demo selection if manually typing

def update_barcode_from_demo_select():
    # Get the barcode from the demo_barcodes_map dictionary using the selected key
    selected_key = st.session_state.selected_demo_product
    if selected_key:
        st.session_state.current_barcode = DEMO_BARCODES_MAP[selected_key]
    st.session_state.manual_barcode_input = "" # Clear manual input if selecting demo

def update_barcode_from_upload(detected_barcode):
    st.session_state.current_barcode = detected_barcode
    # Removed: st.session_state.manual_barcode_input = detected_barcode # This line caused the error
    st.session_state.selected_demo_product = None # Clear other inputs


# --- 5. HELPER FUNCTIONS FOR DATA PROCESSING / PDF GENERATION ---
def _get_carbon_footprint(prod_data):
    carbon_footprint_100g = None
    # 1. Try to get direct 'carbon-footprint_100g'
    if "carbon-footprint_100g" in prod_data:
        try:
            carbon_footprint_100g = float(prod_data["carbon-footprint_100g"])
        except ValueError:
            pass

    # 2. Fallback to ecoscore_data.agribalyse.co2_total if direct field is missing
    if carbon_footprint_100g is None and "ecoscore_data" in prod_data:
        ecoscore_data_obj = prod_data.get("ecoscore_data", {})
        agribalyse_data = ecoscore_data_obj.get("agribalyse", {})
        if "co2_total" in agribalyse_data:
            try:
                # co2_total from Agribalyse is often per kg. Multiply by 100 to get per 100g.
                carbon_footprint_100g = float(agribalyse_data["co2_total"]) * 100
            except ValueError:
                pass
    return carbon_footprint_100g

def _get_eco_grade_details(green_score, ecoscore_grade_char):
    eco_grade_display = ""
    grade_color = "black"
    grade_icon = "❓"

    if ecoscore_grade_char in ['A', 'B', 'C', 'D', 'E']:
        if ecoscore_grade_char == 'A':
            eco_grade_display = "A (Excellent)"
            grade_color = "green"
            grade_icon = "🌳"
        elif ecoscore_grade_char == 'B':
            eco_grade_display = "B (Good)"
            grade_color = "lightgreen"
            grade_icon = "🌿"
        elif ecoscore_grade_char == 'C':
            eco_grade_display = "C (Average)"
            grade_color = "orange"
            grade_icon = "🌱"
        elif ecoscore_grade_char == 'D':
            eco_grade_display = "D (Poor)"
            grade_color = "darkorange"
            grade_icon = "⚠️"
        elif ecoscore_grade_char == 'E':
            eco_grade_display = "E (Dangerous)"
            grade_color = "red"
            grade_icon = "☠️"
    else:
        # Fallback to green_score calculation if ecoscore_grade is not A-E
        if green_score >= 80:
            eco_grade_display = "A (Excellent)"
            grade_color = "green"
            grade_icon = "🌳"
        elif green_score >= 60:
            eco_grade_display = "B (Good)"
            grade_color = "lightgreen"
            grade_icon = "🌿"
        elif green_score >= 40:
            eco_grade_display = "C (Average)"
            grade_color = "orange"
            grade_icon = "🌱"
        elif green_score >= 20:
            eco_grade_display = "D (Poor)"
            grade_color = "darkorange"
            grade_icon = "⚠️"
        else:
            eco_grade_display = "E (Dangerous)"
            grade_color = "red"
            grade_icon = "☠️"
    return eco_grade_display, grade_color, grade_icon

def generate_pdf_bytes(product_name, green_score, barcode, eco_grade_display, carbon_footprint_str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt="EcoScan Sustainability Report", ln=1, align='C')
    pdf.cell(200, 10, txt=f"Product: {product_name}", ln=2)
    pdf.cell(200, 10, txt=f"Barcode: {barcode}", ln=3)
    pdf.cell(200, 10, txt=f"Green Score: {green_score}/100", ln=4)
    pdf.cell(200, 10, txt=f"Eco-Grade: {eco_grade_display}", ln=5)
    # Replace problematic character for PDF output
    safe_carbon_footprint_str = carbon_footprint_str.replace('CO₂e', 'CO2e')
    pdf.cell(200, 10, txt=f"Carbon Footprint: {safe_carbon_footprint_str}", ln=6)
    
    # Return the PDF as bytes
    return pdf.output(dest='S').encode('latin-1')

# --- 6. UI COMPONENT FUNCTIONS ---

def display_tab1_product_info(barcode_to_display):
    report_container = st.empty() # Ensure we have a container to write into

    if barcode_to_display:
        with st.spinner('Fetching product details and generating report...'):
            time.sleep(1) # Simulate network delay or processing time

            res = requests.get(f"https://world.openfoodfacts.org/api/v0/product/{barcode_to_display}.json")

            with report_container.container():
                if res.status_code == 200:
                    data = res.json()
                    if data.get("status") == 1:
                        prod = data["product"]
                        name = prod.get("product_name", "Unknown Product")
                        image = prod.get("image_front_url", "")
                        brand = prod.get("brands", "Unknown Brand")
                        categories = prod.get("categories", "Unknown Category")
                        nutriscore = prod.get("nutriscore_grade", "N/A")

                        # Carbon Emission & EcoScore Logic
                        carbon_footprint_100g = _get_carbon_footprint(prod)
                        display_carbon_footprint = "N/A"
                        if carbon_footprint_100g is not None:
                            display_carbon_footprint = f"{round(carbon_footprint_100g)} g CO₂e / 100g"

                        ecoscore_data_obj = prod.get("ecoscore_data", {})
                        green_score = ecoscore_data_obj.get("score", 0)
                        ecoscore_grade_char = ecoscore_data_obj.get("grade", "u").upper()

                        eco_grade_display, grade_color, grade_icon = _get_eco_grade_details(green_score, ecoscore_grade_char)

                        # Badge + PDF Download side-by-side
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(
                                f"<span style='color: {grade_color}; font-weight: bold;'>{grade_icon} Eco-Grade: {eco_grade_display}</span>",
                                unsafe_allow_html=True
                            )
                        with col2:
                            pdf_bytes = generate_pdf_bytes(name, green_score, barcode_to_display, eco_grade_display, display_carbon_footprint)
                            st.download_button(
                                label="📄 Download PDF",
                                data=pdf_bytes,
                                file_name=f"EcoScan_Report_{barcode_to_display}.pdf",
                                mime="application/pdf",
                                key="download_pdf_button"
                            )

                        # Product image and info side-by-side
                        img_col, info_col = st.columns([1, 3])
                        with img_col:
                            if image:
                                st.image(image, width=120)
                        with info_col:
                            st.markdown(f"### 🏷️ {name}")
                            st.markdown(f"**Brand:** {brand}")
                            st.markdown(f"**Categories:** {categories}")
                            st.markdown(f"**Nutri-Score:** `{nutriscore.upper()}`")
                            st.markdown(f"**Carbon Footprint:** {display_carbon_footprint}")
                            st.metric("♻️ Green Score", f"{green_score}/100")

                        # st.metric("♻️ Green Score", f"{green_score}/100")
                        # st.progress(green_score / 100)

                        # Pie chart breakdown based on Agribalyse data
                        # pie_labels = ["Agriculture", "Processing", "Packaging", "Transportation", "Distribution", "Consumption", "Other/Unknown"]
                        # pie_values = [0, 0, 0, 0, 0, 0, 100]

                        # agribalyse_data = ecoscore_data_obj.get("agribalyse", {})
                        # if agribalyse_data:
                        #     try:
                        #         co2_agri = agribalyse_data.get("co2_agriculture", 0)
                        #         co2_proc = agribalyse_data.get("co2_processing", 0)
                        #         co2_pack = agribalyse_data.get("co2_packaging", 0)
                        #         co2_trans = agribalyse_data.get("co2_transportation", 0)
                        #         co2_dist = agribalyse_data.get("co2_distribution", 0)
                        #         co2_cons = agribalyse_data.get("co2_consumption", 0)
                        #         co2_sum_breakdown = co2_agri + co2_proc + co2_pack + co2_trans + co2_dist + co2_cons

                        #         if co2_sum_breakdown > 0:
                        #             pie_values = [
                        #                 (co2_agri / co2_sum_breakdown) * 100,
                        #                 (co2_proc / co2_sum_breakdown) * 100,
                        #                 (co2_pack / co2_sum_breakdown) * 100,
                        #                 (co2_trans / co2_sum_breakdown) * 100,
                        #                 (co2_dist / co2_sum_breakdown) * 100,
                        #                 (co2_cons / co2_sum_breakdown) * 100,
                        #                 0
                        #             ]
                        #         else:
                        #             pie_values = [0,0,0,0,0,0,100]
                        #     except Exception:
                        #         pass

                        # fig = go.Figure(go.Pie(labels=pie_labels, values=pie_values))
                        # fig.update_layout(height=250, margin=dict(t=0, b=0, l=0, r=0))
                        # st.plotly_chart(fig, use_container_width=True)

                        # Raw Data Copy Feature
                        # st.subheader("📋 Raw Product Data")
                        # json_data_str = json.dumps(data, indent=2)
                        # st.text_area(
                        #     "Copy JSON Data",
                        #     json_data_str,
                        #     height=200,
                        #     key="copy_data_text",
                        #     help="Click the copy icon to copy the full product data in JSON format."
                        # )
                    else:
                        st.error("❌ Product not found.")
                else:
                    st.error("❌ API error.")
    else:
        report_container.info("⬅️ Upload image, pick demo, or enter a barcode to begin.")

def display_tab2_product_comparison(barcode1, barcode2, compare_button):
    comparison_result_placeholder = st.empty()

    if not barcode1 and not barcode2 and not compare_button:
        comparison_result_placeholder.info("Enter barcodes for two products and click 'Compare Carbon Emissions' to see the report.")

    if compare_button:
        with st.spinner('Comparing products...'):
            time.sleep(1.5)

            product1_name = "Product 1"
            product1_carbon = None
            product2_name = "Product 2"
            product2_carbon = None
            messages = []

            # --- Fetch and Extract Carbon Footprint for Product 1 ---
            if barcode1:
                res1 = requests.get(f"https://world.openfoodfacts.org/api/v0/product/{barcode1}.json")
                if res1.status_code == 200:
                    data1 = res1.json()
                    if data1.get("status") == 1:
                        prod1 = data1["product"]
                        product1_name = prod1.get("product_name", f"Product {barcode1}")
                        product1_carbon = _get_carbon_footprint(prod1)
                        if product1_carbon is None:
                            messages.append(f"⚠️ Carbon data not found for {product1_name} (Product 1).")
                        else:
                            product1_carbon = round(product1_carbon)
                    else:
                        messages.append(f"⚠️ Product 1 ({barcode1}) not found in Open Food Facts.")
                else:
                    messages.append(f"❌ API error for Product 1 ({barcode1}).")
            else:
                messages.append("⚠️ Please enter a barcode for Product 1.")

            # --- Fetch and Extract Carbon Footprint for Product 2 ---
            if barcode2:
                res2 = requests.get(f"https://world.openfoodfacts.org/api/v0/product/{barcode2}.json")
                if res2.status_code == 200:
                    data2 = res2.json()
                    if data2.get("status") == 1:
                        prod2 = data2["product"]
                        product2_name = prod2.get("product_name", f"Product {barcode2}")
                        product2_carbon = _get_carbon_footprint(prod2)
                        if product2_carbon is None:
                            messages.append(f"⚠️ Carbon data not found for {product2_name} (Product 2).")
                        else:
                            product2_carbon = round(product2_carbon)
                    else:
                        messages.append(f"⚠️ Product 2 ({barcode2}) not found in Open Food Facts.")
                else:
                    messages.append(f"❌ API error for Product 2 ({barcode2}).")
            else:
                messages.append("⚠️ Please enter a barcode for Product 2.")

            # Write all comparison results and messages to the placeholder
            with comparison_result_placeholder.container():
                st.subheader("📊 Comparison Report")

                if product1_carbon is not None and product2_carbon is not None:
                    if product1_carbon < product2_carbon:
                        st.success(f"**{product1_name}** has lower carbon emissions than {product2_name}. Choose the greener option! 🌳")
                    elif product2_carbon < product1_carbon:
                        st.success(f"**{product2_name}** has lower carbon emissions than {product1_name}. Choose the greener option! 🌳")
                    else:
                        st.info("Both products have similar carbon emissions.")

                    st.write("---")

                    color1 = 'green'
                    color2 = 'darkgreen'
                    if product1_carbon is not None and product2_carbon is not None:
                        if product1_carbon > product2_carbon:
                            color1 = 'red'
                        elif product2_carbon > product1_carbon:
                            color2 = 'red'

                    st.subheader("Carbon Emission Comparison")
                    fig_comp = go.Figure(data=[
                        go.Bar(name=product1_name, x=[product1_name], y=[product1_carbon], marker_color=color1),
                        go.Bar(name=product2_name, x=[product2_name], y=[product2_carbon], marker_color=color2)
                    ])
                    fig_comp.update_layout(
                        barmode='group',
                        title_text='Carbon Emissions Comparison',
                        yaxis_title='Carbon Emission (gCO2e)',
                        height=400
                    )
                    st.plotly_chart(fig_comp, use_container_width=True)
                else:
                    st.info("Enter valid barcodes for both products to see the comparison.")

                for msg in messages:
                    if "⚠️" in msg:
                        st.warning(msg)
                    elif "❌" in msg:
                        st.error(msg)

# --- 7. MAIN APP FUNCTION ---
def main():
    st.title(PAGE_TITLE)
    apply_custom_css()
    initialize_session_state()

    tab1, tab2 = st.tabs(["Current Features", "Product Comparison"])

    with tab1:
        left_col, right_col = st.columns([1, 2])
        with left_col:
            st.subheader("🔍 Scan or Search")
            manual_barcode_input_value = st.text_input(
                "Enter barcode",
                placeholder="Type barcode...",
                key="manual_barcode_input",
                on_change=update_barcode_from_manual_input,
                value=st.session_state.manual_barcode_input
            )

            uploaded_img = st.file_uploader("📷 Upload barcode image", type=["png", "jpg", "jpeg"])
            if uploaded_img:
                img = Image.open(uploaded_img)
                result = decode(img)
                if result:
                    detected_barcode = result[0].data.decode("utf-8")
                    st.success(f"✅ Barcode detected: {detected_barcode}")
                    update_barcode_from_upload(detected_barcode)
                else:
                    st.error("❌ No barcode found in image.")

            # Set default value of selectbox based on current_barcode if it matches a demo product
            initial_demo_index = 0
            if st.session_state.current_barcode:
                for i, (key, value) in enumerate(DEMO_BARCODES_MAP.items()):
                    if value == st.session_state.current_barcode:
                        initial_demo_index = i
                        break

            selected_demo_product_key = st.selectbox(
                "🎯 Try a known product",
                list(DEMO_BARCODES_MAP.keys()),
                index=initial_demo_index,
                key="selected_demo_product",
                on_change=update_barcode_from_demo_select
            )
            if st.session_state.selected_demo_product and st.session_state.current_barcode == DEMO_BARCODES_MAP[st.session_state.selected_demo_product]:
                 st.info(f"Using barcode: {st.session_state.current_barcode}")

        with right_col:
            display_tab1_product_info(st.session_state.current_barcode)

    with tab2:
        left_panel_col, right_panel_col = st.columns([1, 3])
        with left_panel_col:
            st.subheader("📚 Enter Product Barcodes")
            barcode1 = st.text_input("Barcode for Product 1", key="barcode1_comp", placeholder="e.g., 3017620429484", value="3017620429484")
            barcode2 = st.text_input("Barcode for Product 2", key="barcode2_comp", placeholder="e.g., 5449000000996", value="8901058001181")
            compare_button = st.button("Compare Carbon Emissions")

        with right_panel_col:
            display_tab2_product_comparison(barcode1, barcode2, compare_button)

# --- Run the main application ---
if __name__ == "__main__":
    main()
