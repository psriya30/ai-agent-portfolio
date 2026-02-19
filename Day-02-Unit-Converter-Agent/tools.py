# tools.py
from smolagents import tool

@tool
def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """
    Convert a numeric value from one unit to another.

    Args:
        value: The number to convert (e.g., 5).
        from_unit: The input unit. Supported: km, m, cm, mm, mile, kg, g, lb, c, f
        to_unit: The output unit. Supported: km, m, cm, mm, mile, kg, g, lb, c, f

    Returns:
        Converted value as a string, or an error message if units are unsupported.
    """
    fu = from_unit.strip().lower()
    tu = to_unit.strip().lower()

    # ---- Length conversions (base: meters) ----
    length_to_m = {
        "mm": 0.001,
        "cm": 0.01,
        "m": 1.0,
        "km": 1000.0,
        "mile": 1609.344,
    }

    # ---- Weight conversions (base: kilograms) ----
    weight_to_kg = {
        "g": 0.001,
        "kg": 1.0,
        "lb": 0.45359237,
    }

    # ---- Temperature conversions ----
    def c_to_f(c: float) -> float:
        return (c * 9/5) + 32

    def f_to_c(f: float) -> float:
        return (f - 32) * 5/9

    # Length
    if fu in length_to_m and tu in length_to_m:
        meters = value * length_to_m[fu]
        out = meters / length_to_m[tu]
        return f"{out:.4f} {tu}"

    # Weight
    if fu in weight_to_kg and tu in weight_to_kg:
        kg = value * weight_to_kg[fu]
        out = kg / weight_to_kg[tu]
        return f"{out:.4f} {tu}"

    # Temperature
    if fu == "c" and tu == "f":
        return f"{c_to_f(value):.2f} f"
    if fu == "f" and tu == "c":
        return f"{f_to_c(value):.2f} c"

    return (
        "Error: Unsupported conversion. Supported units: "
        "Length(km,m,cm,mm,mile), Weight(kg,g,lb), Temp(c,f)."
    )
