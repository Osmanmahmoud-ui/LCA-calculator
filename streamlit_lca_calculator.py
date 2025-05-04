
import streamlit as st

# Data
material_impacts = {
    "ethylene": {"co2": 1.75, "water": 1.2, "energy": 78.0, "acidification": 0.015},
    "ammonia": {"co2": 2.38, "water": 1.8, "energy": 38.0, "acidification": 0.022},
    "polyethylene": {"co2": 2.1, "water": 0.8, "energy": 85.0, "acidification": 0.012},
    "sulfuric_acid": {"co2": 0.35, "water": 0.3, "energy": 2.5, "acidification": 0.045},
    "hydrogen": {"co2": 10.4, "water": 1.5, "energy": 55.0, "acidification": 0.008},
}

energy_impacts = {
    "natural_gas": {"co2": 0.49, "water": 0.002, "energy": 3.6, "acidification": 0.0003},
    "coal": {"co2": 1.02, "water": 0.004, "energy": 3.6, "acidification": 0.0012},
    "grid_electricity": {"co2": 0.68, "water": 0.003, "energy": 3.6, "acidification": 0.0008},
    "renewables": {"co2": 0.05, "water": 0.001, "energy": 3.6, "acidification": 0.0001},
    "solar": {"co2": 0.04, "water": 0.001, "energy": 3.6, "acidification": 0.0001},
    "wind": {"co2": 0.03, "water": 0.001, "energy": 3.6, "acidification": 0.0001},
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

def get_renewable_suggestion(energy_type, current_score):
    suggestions = {
        "coal": ["solar", "wind", "hydropower"],
        "natural_gas": ["biogas", "solar thermal"],
        "grid_electricity": ["solar PV", "wind"],
        "diesel": ["biodiesel", "electric"]
    }
    if current_score < 5 or energy_type in ["renewables", "solar", "wind"]:
        return None
    return suggestions.get(energy_type, ["solar", "wind", "geothermal"])

# Streamlit UI
st.title("🌍 LCA Calculator for Chemical Processes")

material = st.selectbox("Select material", list(material_impacts.keys()))
material_amount = st.number_input("Amount of material used (kg)", min_value=0.0, max_value=10000.0, step=1.0)

energy_type = st.selectbox("Select energy source", list(energy_impacts.keys()))
energy_amount = st.number_input("Amount of energy used (kWh)", min_value=0.0, max_value=10000.0, step=1.0)

if st.button("Calculate LCA"):
    impacts = {}
    for impact_type in ["co2", "water", "energy", "acidification"]:
        mat = material_amount * material_impacts[material][impact_type]
        en = energy_amount * energy_impacts[energy_type][impact_type]
        total = mat + en
        score = get_impact_scale(total, score_ranges[impact_type])
        impacts[impact_type] = {"material": mat, "energy": en, "total": total, "score": score}

    st.subheader("📊 LCA Results")
    for impact, values in impacts.items():
        st.markdown(f"**{impact.upper()} Impact**")
        st.write(f"- From material: {values['material']:.2f}")
        st.write(f"- From energy: {values['energy']:.2f}")
        st.write(f"- TOTAL: {values['total']:.2f}")
        st.write(f"Impact Score: {values['score']} / 10")

    avg_score = sum(v["score"] for v in impacts.values()) / len(impacts)
    st.subheader("🌱 Overall Environmental Impact")
    st.write(f"Average Impact Score: {avg_score:.1f} / 10")
    if avg_score <= 3:
        st.success("This process has relatively LOW environmental impact")
    elif avg_score <= 7:
        st.warning("This process has MODERATE environmental impact")
    else:
        st.error("This process has HIGH environmental impact")

    suggestion_score = get_impact_scale(
        impacts["co2"]["energy"] + impacts["acidification"]["energy"],
        [(2, 1), (5, 3), (10, 5), (20, 7), (50, 9)]
    )
    suggestions = get_renewable_suggestion(energy_type, suggestion_score)
    if suggestions:
        st.subheader("🔄 Sustainability Suggestion")
        st.write(f"Your energy source ({energy_type}) has an environmental score of {suggestion_score}/10.")
        st.write("Consider switching to these renewable sources:")
        for s in suggestions:
            st.write(f"- {s.capitalize()} energy")
        st.info("Switching could reduce your CO₂ emissions by up to 90%!")

    st.caption("Scoring Guide: 1-3 (Low) | 4-7 (Medium) | 8-10 (High)")
