"""Tests for ride service - FIT parsing and ride creation."""

from datetime import date, datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.formulas import normalized_power, training_stress_score, intensity_factor
from app.models.base import Base
from app.models.ride import Ride, RideData
from app.models.user import User
from app.services.ride_service import create_ride_from_recording


def _make_test_db():
    """Create an in-memory SQLite database with all tables."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def _make_test_user(db) -> User:
    """Create a test user with FTP set."""
    user = User(
        id="test-user-1",
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test Rider",
        ftp=250,
        weight_kg=75.0,
        max_hr=185,
    )
    db.add(user)
    db.commit()
    return user


class TestCreateRideFromRecording:
    def test_creates_ride_with_metrics(self):
        """In-app recording should create a ride with NP/IF/TSS."""
        db = _make_test_db()
        user = _make_test_user(db)

        # Simulate 10 minutes of steady riding at 200W
        data_points = [
            {"elapsed_seconds": i, "power": 200, "heart_rate": 145, "cadence": 90}
            for i in range(600)
        ]

        ride = create_ride_from_recording(
            db, user, "Test Ride", datetime.now(timezone.utc), data_points
        )

        assert ride.id is not None
        assert ride.source == "in_app"
        assert ride.title == "Test Ride"
        assert ride.duration_seconds == 600
        assert ride.average_power == 200.0
        assert ride.normalized_power is not None
        assert ride.average_hr == 145
        assert ride.average_cadence == 90
        assert ride.ftp_at_time == 250
        assert ride.tss is not None
        assert ride.intensity_factor is not None

        # Check data points were inserted
        count = db.query(RideData).filter(RideData.ride_id == ride.id).count()
        assert count == 600

    def test_ride_without_ftp(self):
        """Ride without FTP should still be created, just without IF/TSS."""
        db = _make_test_db()
        user = User(
            id="no-ftp-user",
            email="noftp@example.com",
            hashed_password="hashed",
            full_name="No FTP",
        )
        db.add(user)
        db.commit()

        data_points = [
            {"elapsed_seconds": i, "power": 200}
            for i in range(60)
        ]

        ride = create_ride_from_recording(
            db, user, "No FTP Ride", datetime.now(timezone.utc), data_points
        )

        assert ride.id is not None
        assert ride.tss is None
        assert ride.intensity_factor is None

    def test_variable_power_np_higher_than_avg(self):
        """Variable power should produce NP higher than average."""
        db = _make_test_db()
        user = _make_test_user(db)

        # 60s blocks of 100W and 300W for 4 minutes
        data_points = []
        for i in range(240):
            block = (i // 60) % 2
            power = 100 if block == 0 else 300
            data_points.append({"elapsed_seconds": i, "power": power})

        ride = create_ride_from_recording(
            db, user, "Variable Ride", datetime.now(timezone.utc), data_points
        )

        assert ride.normalized_power > ride.average_power

    def test_links_workout(self):
        """Should link ride to workout if provided."""
        db = _make_test_db()
        user = _make_test_user(db)

        data_points = [{"elapsed_seconds": i, "power": 200} for i in range(60)]
        ride = create_ride_from_recording(
            db, user, "Linked Ride", datetime.now(timezone.utc),
            data_points, workout_id="workout-123"
        )

        assert ride.workout_id == "workout-123"


class TestMetricsCalculation:
    def test_np_matches_formula(self):
        """Ride NP should match the formula module's calculation."""
        power_data = [200] * 120  # 2 min steady
        expected_np = normalized_power(power_data)

        db = _make_test_db()
        user = _make_test_user(db)

        data_points = [{"elapsed_seconds": i, "power": 200} for i in range(120)]
        ride = create_ride_from_recording(
            db, user, "NP Check", datetime.now(timezone.utc), data_points
        )

        assert abs(ride.normalized_power - expected_np) < 0.1

    def test_tss_one_hour_at_ftp(self):
        """1 hour at FTP should produce ~100 TSS."""
        db = _make_test_db()
        user = _make_test_user(db)

        # 1 hour at FTP (250W)
        data_points = [{"elapsed_seconds": i, "power": 250} for i in range(3600)]
        ride = create_ride_from_recording(
            db, user, "FTP Hour", datetime.now(timezone.utc), data_points
        )

        # TSS should be approximately 100 for 1 hour at FTP
        assert ride.tss is not None
        assert abs(ride.tss - 100.0) < 2.0
