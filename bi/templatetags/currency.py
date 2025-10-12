from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()

@register.filter(name="clp")
def clp(value):
    """
    Formatea un número como moneda chilena (CLP) sin decimales,
    con separador de miles por punto y antepone el símbolo $.
    Ejemplo: 1234567 -> $ 1.234.567
    """
    try:
        # Convertir de forma segura a Decimal
        val = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return value

    # Formato CLP sin decimales
    s = f"{val:,.0f}"       # 1,234,567
    s = s.replace(",", ".")  # 1.234.567
    return f"$ {s}"