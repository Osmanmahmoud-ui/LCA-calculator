
import streamlit as st
from fpdf import FPDF
import tempfile

# LCA Impact Factors
material_impacts = {
    "ethylene": {"co2": 1.75, "water": 1.2, "energy": 78.0, "acid": 0.015},
    "ammonia": {"co2": 2.38, "water": 1.8, "energy": 38.0, "acid": 0.022},
    "polyethylene": {"co2": 2.1, "water": 0.8, "energy": 85.0, "acid": 0.012},
    "sulfuric_acid": {"co2": 0.35, "water": 0.3, "energy": 2.5, "acid": 0.045},
    "hydrogen": {"co2": 10.4, "water": 1.5, "energy": 55.0, "acid": 0.008}
}

energy_impacts = {
    "natural_gas": {"co2": 0.49, "water": 0.002, "energy": 3.6, "acid": 0.0003},
    "coal": {"co2": 1.02, "water": 0.004, "energy": 3.6, "acid": 0.0012},
    "grid_electricity": {"co2": 0.68, "water": 0.003, "energy": 3.6, "acid": 0.0008},
    "renewables": {"co2": 0.05, "water": 0.001, "energy": 3.6, "acid": 0.0001},
    "solar": {"co2": 0.04, "water": 0.001, "energy": 3.6, "acid": 0.0001},
    "wind": {"co2": 0.03, "water": 0.001, "energy": 3.6, "acid": 0.0001}
}

st.title("🌱 LCA Calculator")
st.subheader("Life Cycle Assessment for Chemical Processes")

material = st.selectbox("Choose Material", list(material_impacts.keys()))
material_amount = st.number_input("Material Amount (kg)", min_value=0.0, max_value=10000.0, step=1.0)

energy_type = st.selectbox("Choose Energy Source", list(energy_impacts.keys()))
energy_amount = st.number_input("Energy Amount (kWh)", min_value=0.0, max_value=10000.0, step=10.0)

if st.button("Calculate Impact"):
    m = material_impacts[material]
    e = energy_impacts[energy_type]

    results = {
        "CO2 Emissions (kg)": round(material_amount * m["co2"] + energy_amount * e["co2"], 2),
        "Water Usage (m³)": round(material_amount * m["water"] + energy_amount * e["water"], 2),
        "Energy Usage (MJ)": round(material_amount * m["energy"] + energy_amount * e["energy"], 2),
        "Acidification (kg SO₂ eq)": round(material_amount * m["acid"] + energy_amount * e["acid"], 2)
    }

    st.success("✅ Results Calculated:")
    for k, v in results.items():
        st.write(f"**{k}:** {v}")

    # PDF Report Generation
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "LCA Calculator Report", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Material: {material} ({material_amount} kg)", ln=True)
    pdf.cell(0, 10, f"Energy: {energy_type} ({energy_amount} kWh)", ln=True)
    pdf.ln(5)
    for k, v in results.items():
        pdf.cell(0, 10, f"{k}: {v}", ln=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        pdf.output(tmpfile.name)
        st.download_button("📄 Download PDF Report", data=open(tmpfile.name, "rb").read(), file_name="LCA_Report.pdf")
