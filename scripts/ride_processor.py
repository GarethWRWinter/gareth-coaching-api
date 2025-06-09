def process_latest_fit_file(access_token):
    file_name, local_path = get_latest_fit_file_from_dropbox(access_token)
    if not file_name or not local_path:
        return None

    fitfile = fitparse.FitFile(local_path)
    records = []
    for record in fitfile.get_messages("record"):
        record_data = {}
        for field in record:
            record_data[field.name] = field.value
        records.append(record_data)

    df = pd.DataFrame(records)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    print(f"[INFO] Using FTP (Functional Threshold Power): {FTP} watts")
    metrics = calculate_ride_metrics(df, FTP)

    ride_data = {
        "ride_id": file_name,
        "start_time": df["timestamp"].min().to_pydatetime() if "timestamp" in df.columns else datetime.utcnow(),
        "duration_sec": metrics["duration_seconds"],
        "distance_km": metrics.get("distance_km", 0),
        "avg_power": metrics["average_power"],
        "max_power": metrics["max_power"],
        "tss": metrics["tss"],
        "total_work_kj": metrics.get("total_work_kj", 0),
        "power_zone_times": metrics["zones"],
    }

    # Convert NumPy floats to native floats
    for k, v in ride_data.items():
        if isinstance(v, np.generic):
            ride_data[k] = float(v)

    store_ride(ride_data)

    # Return ride_data as the summary for API response
    return ride_data
