from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()

@register.filter(name="clp")
def clp(value):
    """
    Formatea un número como moneda chilena (CLP) con separadores de miles por punto
    y decimales con coma, y antepone el símbolo $.
    Ejemplo: 1234567.89 -> $ 1.234.567,89
    """
    try:
        # Convertir de forma segura a Decimal
        val = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return value

    # Formato US: 1,234,567.89
    s = f"{val:,.2f}"
    # Convertir a formato CL: 1.234.567,89
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"$ {s}"