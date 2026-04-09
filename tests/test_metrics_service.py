"""Tests for metrics service - PMC calculations."""

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.metrics import DailyMetrics
from app.models.ride import Ride, RideSource
from app.models.user import User
from app.services.metrics_service import get_current_fitness, get_pmc_data, recalculate_from_date


def _make_test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def _make_test_user(db) -> User:
    user = User(
        id="test-user-1",
        email="test@example.com",
        hashed_password="hashed",
        full_name="Test Rider",
        ftp=250,
        weight_kg=75.0,
    )
    db.add(user)
    db.commit()
    return user


def _add_ride(db, user_id: str, ride_date: date, tss: float):
    """Add a ride with a given TSS on a specific date."""
    ride = Ride(
        user_id=user_id,
        source=RideSource.manual,
        title=f"Ride on {ride_date}",
        ride_date=datetime.combine(ride_date, datetime.min.time()).replace(tzinfo=timezone.utc),
        tss=tss,
        duration_seconds=3600,
    )
    db.add(ride)
    db.commit()
    return ride


class TestRecalculateFromDate:
    def test_single_ride_day(self):
        """Single ride day should create a daily_metrics row."""
        db = _make_test_db()
        user = _make_test_user(db)

        today = date.today()
        _add_ride(db, user.id, today, tss=80.0)
        recalculate_from_date(db, user.id, today)

        metrics = db.query(DailyMetrics).filter(
            DailyMetrics.user_id == user.id,
            DailyMetrics.date == today
        ).first()

        assert metrics is not None
        assert metrics.tss == 80.0
        assert metrics.ctl > 0  # Should increase from 0
        assert metrics.atl > 0  # Should increase from 0
        assert metrics.atl > metrics.ctl  # ATL responds faster

    def test_rest_day_decreases_fitness(self):
        """Rest days should decrease CTL and ATL."""
        db = _make_test_db()
        user = _make_test_user(db)

        # Day 1: big ride
        day1 = date.today() - timedelta(days=2)
        _add_ride(db, user.id, day1, tss=100.0)

        # Recalculate from day1 to today (includes 2 rest days)
        recalculate_from_date(db, user.id, day1)

        day1_metrics = db.query(DailyMetrics).filter(
            DailyMetrics.user_id == user.id,
            DailyMetrics.date == day1
        ).first()

        today_metrics = db.query(DailyMetrics).filter(
            DailyMetrics.user_id == user.id,
            DailyMetrics.date == date.today()
        ).first()

        assert today_metrics is not None
        assert today_metrics.ctl < day1_metrics.ctl  # Fitness decreases on rest
        assert today_metrics.atl < day1_metrics.atl  # Fatigue decreases on rest

    def test_consecutive_training_builds_fitness(self):
        """7 days of training should build CTL progressively."""
        db = _make_test_db()
        user = _make_test_user(db)

        base_date = date.today() - timedelta(days=7)
        for i in range(7):
            _add_ride(db, user.id, base_date + timedelta(days=i), tss=70.0)

        recalculate_from_date(db, user.id, base_date)

        day1_metrics = db.query(DailyMetrics).filter(
            DailyMetrics.user_id == user.id,
            DailyMetrics.date == base_date
        ).first()

        day7_metrics = db.query(DailyMetrics).filter(
            DailyMetrics.user_id == user.id,
            DailyMetrics.date == base_date + timedelta(days=6)
        ).first()

        assert day7_metrics.ctl > day1_metrics.ctl  # CTL increasing
        assert day7_metrics.atl > day1_metrics.atl  # ATL increasing

    def test_tsb_is_ctl_minus_atl(self):
        """TSB should always equal CTL - ATL."""
        db = _make_test_db()
        user = _make_test_user(db)

        today = date.today()
        _add_ride(db, user.id, today, tss=100.0)
        recalculate_from_date(db, user.id, today)

        metrics = db.query(DailyMetrics).filter(
            DailyMetrics.user_id == user.id,
            DailyMetrics.date == today
        ).first()

        expected_tsb = metrics.ctl - metrics.atl
        assert abs(metrics.tsb - expected_tsb) < 0.01


class TestGetCurrentFitness:
    def test_no_data_returns_zeros(self):
        db = _make_test_db()
        user = _make_test_user(db)

        fitness = get_current_fitness(db, user.id)
        assert fitness["ctl"] == 0.0
        assert fitness["atl"] == 0.0
        assert fitness["tsb"] == 0.0

    def test_returns_latest_values(self):
        db = _make_test_db()
        user = _make_test_user(db)

        today = date.today()
        _add_ride(db, user.id, today, tss=80.0)
        recalculate_from_date(db, user.id, today)

        fitness = get_current_fitness(db, user.id)
        assert fitness["ctl"] > 0
        assert fitness["atl"] > 0


class TestGetPMCData:
    def test_returns_date_range(self):
        db = _make_test_db()
        user = _make_test_user(db)

        base_date = date.today() - timedelta(days=5)
        for i in range(5):
            _add_ride(db, user.id, base_date + timedelta(days=i), tss=60.0)

        recalculate_from_date(db, user.id, base_date)
        data = get_pmc_data(db, user.id, start_date=base_date)

        assert len(data) >= 5
        # Dates should be in order
        dates = [d.date for d in data]
        assert dates == sorted(dates)
