def format_rate(rate):
    """
    Formats a decimal rate as a percentage string.
    """
    if rate is None:
        return "N/A"
    return f"{rate * 100:.1f}%"
