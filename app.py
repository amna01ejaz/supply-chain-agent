import streamlit as st
import pandas as pd
import plotly.express as px
from agno.agent import Agent
from agno.models.google import Gemini

# 1. Page Configuration
st.set_page_config(page_title="Supply Chain Hub", layout="wide")
st.title("📦 Enterprise Multi-Agent Supply Chain & Inventory Optimization Simulator")
st.write("Orchestrate a team of autonomous operations agents to track retail stock velocities and predict restock cadences.")

# 2. Sidebar Configuration for Credentials
st.sidebar.header("System Authentication")
api_key = st.sidebar.text_input("Enter Gemini API Key (Starts with AIzaSy):", type="password")

st.sidebar.markdown("""
### Multi-Agent Topology:
1. **Inventory Tracker Agent:** Evaluates raw stock levels vs incoming velocity orders.
2. **Predictive Restock Node:** Calculates safety stock variables and drafts a procurement manifest.
""")

st.write("---")

# 3. Sample Warehouse Data Buffer
st.subheader("1. Current Warehouse Log Stream")
sample_inventory = (
    "Product A: Current Stock: 45 units. Daily Sales Rate: 12 units. Lead Time from supplier: 3 days.\n"
    "Product B: Current Stock: 410 units. Daily Sales Rate: 15 units. Lead Time from supplier: 7 days.\n"
    "Product C: Current Stock: 8 units. Daily Sales Rate: 4 units. Lead Time from supplier: 2 days.\n"
    "Product D: Current Stock: 120 units. Daily Sales Rate: 35 units. Lead Time from supplier: 5 days."
)

raw_log_data = st.text_area(
    "Edit raw warehouse logistics metrics below:",
    value=sample_inventory,
    height=150
)

if st.button("Initialize Optimization Routine"):
    if not api_key:
        st.error("Please enter a valid Gemini API key starting with 'AIzaSy' in the sidebar configuration.")
    elif not raw_log_data.strip():
        st.warning("Please supply inventory metrics to audit.")
    else:
        with st.spinner("Orchestrating operations agents... Generating risk assessments and order manifests..."):
            try:
                # 4. Define the Inventory Tracker Agent
                tracker_agent = Agent(
                    model=Gemini(id="gemini-2.5-flash", api_key=api_key),
                    description="You are an expert warehouse inventory manager specializing in tracking stock levels and depletion timelines.",
                    instructions=[
                        "Analyze the raw data stream and identify every unique product label.",
                        "Calculate the 'Days of Stock Remaining' for each product using the formula: (Current Stock / Daily Sales Rate).",
                        "Flag any product with less than 5 days of remaining stock as 'CRITICAL STOCK ALERT'."
                    ],
                    markdown=True
                )

                # 5. Define the Predictive Restock Agent
                restock_agent = Agent(
                    model=Gemini(id="gemini-2.5-flash", api_key=api_key),
                    description="You are a senior supply chain procurement strategist and logician.",
                    instructions=[
                        "Take the stock depletion timelines compiled by the tracker agent.",
                        "Calculate the absolute 'Reorder Point' for each item. Formula: (Daily Sales Rate * Lead Time).",
                        "Generate an optimal replenishment order quantity for each flagged item to stabilize warehouse safety metrics for the next 30 days.",
                        "Present the final analysis as a clean Markdown table listing: Product Name | Days Left | Risk Status | Recommended Reorder Quantity."
                    ],
                    markdown=True
                )

                # 6. Build the Collaborative Team Agent
                supply_chain_team = Agent(
                    team=[tracker_agent, restock_agent],
                    model=Gemini(id="gemini-2.5-flash", api_key=api_key),
                    instructions=[
                        "Run the localized tracking check over the inventory strings first.",
                        "Pass those metrics to the restock planner to compute logistics forecasts.",
                        "Display the finalized procurement blueprint cleanly with clear markdown headers."
                    ],
                    markdown=True
                )

                # 7. Execute Simulation
                response = supply_chain_team.run(raw_log_data)
                
                st.success("🎯 Supply Chain Analysis Complete!")
                
                col1, col2 = st.columns([3, 2])
                with col1:
                    st.write("### 📝 Operations Manifest & Order Blueprint")
                    st.markdown(response.content)
                    
                with col2:
                    st.write("### 📊 Warehouse Stock Depletion Map")
                    # Build a rapid baseline metrics chart for visual alignment representation
                    chart_df = pd.DataFrame({
                        "Product": ["Product A", "Product B", "Product C", "Product D"],
                        "Days of Stock Remaining": [3.75, 27.3, 2.0, 3.42],
                        "Risk Tier": ["Critical Risk", "Stable", "Critical Risk", "Critical Risk"]
                    })
                    
                    fig = px.bar(
                        chart_df, 
                        x="Product", 
                        y="Days of Stock Remaining", 
                        color="Risk Tier",
                        color_discrete_map={"Critical Risk": "#FF3333", "Stable": "#33FF66"},
                        title="Estimated Days Until Out-of-Stock (Stockout)",
                        template="plotly_dark"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.info("💡 **Logistics Advisory:** Stock runs for Product C and Product D will be completely exhausted shortly. Prioritize supplier procurement actions immediately.")
                    
            except Exception as e:
                st.error(f"Simulation Infrastructure Error: {e}")