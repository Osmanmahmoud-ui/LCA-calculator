
import streamlit as st
from fpdf import FPDF
import datetime

# البيانات
material_impacts = {
    "ammonia": {"co2": 2.38, "water": 1.8, "energy": 38.0, "acidification": 0.022},
}
energy_impacts = {
    "natural_gas": {"co2": 0.49, "water": 0.002, "energy": 3.6, "acidification": 0.0003},
}
score_ranges = {
    "co2": [(10, 1), (25, 3), (50, 5), (100, 7), (500, 9)],
    "water": [(5, 1), (20, 3), (50, 5), (100, 7), (200, 9)],
    "energy": [(100, 1), (500, 3), (1000, 5), (2000, 7), (5000, 9)],
    "acidification": [(0.01, 1), (0.05, 3), (0.1, 5), (0.5, 7), (1.0, 9)],
}

def get_impact_scale(value, ranges):
    for i, (threshold, _) in enumerate(ranges):
        if value <= threshold:
            return min(10, i + 1)
    return 10

def generate_pdf(material, material_amount, energy_type, energy_amount, impacts, avg_score, energy_score, suggestions):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "LCA Environmental Impact Report", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Input Summary:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Material: {material} | Amount: {material_amount} kg", ln=True)
    pdf.cell(0, 10, f"Energy Source: {energy_type} | Amount: {energy_amount} kWh", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Impact Results:", ln=True)
    pdf.set_font("Arial", '', 12)
    for impact, vals in impacts.items():
        line = f"{impact.capitalize()} Impact: Material = {vals['material']:.2f}, Energy = {vals['energy']:.2f}, Total = {vals['total']:.2f} {vals['unit']}, Score = {vals['score']}/10"
        pdf.multi_cell(0, 8, line)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Overall Assessment:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Average Impact Score: {avg_score:.1f}/10", ln=True)
    pdf.cell(0, 10, f"Impact Level: {'LOW' if avg_score <= 3 else 'MODERATE' if avg_score <= 7 else 'HIGH'}", ln=True)
    pdf.ln(10)

    if suggestions:
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Renewable Energy Suggestions:", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Current energy impact score: {energy_score}/10", ln=True)
        pdf.multi_cell(0, 10, f"Consider switching to: {', '.join(suggestions).title()} to reduce CO2 emissions by up to 90%.")
        pdf.ln(10)

    return pdf.output(dest='S').encode('latin-1')


# واجهة Streamlit
st.title("LCA Calculator with PDF Report")

material = st.selectbox("Select material", list(material_impacts.keys()))
material_amount = st.number_input("Material amount (kg)", 0.0, 10000.0, step=1.0)
energy_type = st.selectbox("Select energy source", list(energy_impacts.keys()))
energy_amount = st.number_input("Energy amount (kWh)", 0.0, 10000.0, step=1.0)

if st.button("Calculate LCA"):
    impacts = {}
    for impact_type in ["co2", "water", "energy", "acidification"]:
        mat = material_amount * material_impacts[material][impact_type]
        en = energy_amount * energy_impacts[energy_type][impact_type]
        total = mat + en
        unit = {
            "co2": "kg CO2-eq",
            "water": "m³",
            "energy": "MJ",
            "acidification": "kg SO2-eq"
        }[impact_type]
        score = get_impact_scale(total, score_ranges[impact_type])
        impacts[impact_type] = {"material": mat, "energy": en, "total": total, "score": score, "unit": unit}

    avg_score = sum(v["score"] for v in impacts.values()) / len(impacts)
    energy_score = get_impact_scale(impacts["co2"]["energy"] + impacts["acidification"]["energy"], [(2, 1), (5, 3), (10, 5), (20, 7), (50, 9)])
    suggestions = ["solar", "wind"]

    st.subheader("📊 Results")
    st.write(f"**Material Used:** {material_amount} kg of {material}")
    st.write(f"**Energy Used:** {energy_amount} kWh of {energy_type}")
    for impact, vals in impacts.items():
        st.markdown(f"**{impact.capitalize()} Impact**")
        st.write(f"- From material: {vals['material']:.2f} {vals['unit']}")
        st.write(f"- From energy: {vals['energy']:.2f} {vals['unit']}")
        st.write(f"- Total: {vals['total']:.2f} {vals['unit']}")
        st.write(f"- Score: {vals['score']}/10 {'★'*vals['score']} {'☆'*(10 - vals['score'])}")

    st.success(f"Average Score: {avg_score:.1f}/10")

    # عرض زر تحميل PDF بعد عرض النتائج
    pdf_bytes = generate_pdf(material, material_amount, energy_type, energy_amount, impacts, avg_score, energy_score, suggestions)
    st.download_button("📄 Download PDF Report", data=pdf_bytes, file_name="lca_report.pdf", mime="application/pdf")
