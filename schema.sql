CREATE TABLE athletes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ftp FLOAT DEFAULT 308.0
            );
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE rides (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ride_id TEXT UNIQUE,
                start_time DATETIME,
                duration_sec INTEGER,
                distance_km FLOAT,
                avg_power FLOAT,
                avg_hr FLOAT,
                avg_cadence FLOAT,
                max_power FLOAT,
                max_hr FLOAT,
                max_cadence FLOAT,
                total_work_kj FLOAT,
                tss FLOAT,
                normalized_power FLOAT,
                left_right_balance TEXT,
                power_zone_times JSON
            , hr_zone_times JSON);
