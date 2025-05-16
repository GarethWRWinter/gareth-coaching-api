def sanitize_fit_data(data):
    """
    Extracts clean second-by-second power, HR, cadence etc.
    from a parsed FIT file's 'record' messages.
    """
    clean = []
    for record in data.get_messages("record"):
        entry = {}
        for field in record:
            entry[field.name] = field.value
        clean.append(entry)
    return clean
