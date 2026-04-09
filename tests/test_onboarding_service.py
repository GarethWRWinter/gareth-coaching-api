"""Tests for onboarding quiz and goal event services."""

from datetime import date, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.onboarding import GoalEvent, OnboardingResponse
from app.models.user import User
from app.services.onboarding_service import (
    create_goal,
    delete_goal,
    get_goal,
    get_goals,
    get_onboarding_response,
    get_onboarding_status,
    submit_quiz,
    update_goal,
    _infer_experience_level,
)


def _make_test_db():
    """Create an in-memory SQLite database with all tables."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def _make_test_user(db, user_id="test-user-1") -> User:
    """Create a test user."""
    user = User(
        id=user_id,
        email=f"{user_id}@example.com",
        hashed_password="hashed",
        full_name="Test Rider",
        ftp=250,
        weight_kg=75.0,
    )
    db.add(user)
    db.commit()
    return user


class TestSubmitQuiz:
    def test_basic_submission(self):
        """Should save quiz answers and mark completed."""
        db = _make_test_db()
        user = _make_test_user(db)

        response = submit_quiz(
            db, user.id,
            primary_goal="build_fitness",
            secondary_goals=["improve_ftp", "learn_skills"],
            current_weekly_volume_hours=8.0,
            years_cycling=3,
            indoor_outdoor_preference="both",
        )

        assert response.id is not None
        assert response.primary_goal == "build_fitness"
        assert response.secondary_goals == ["improve_ftp", "learn_skills"]
        assert response.current_weekly_volume_hours == 8.0
        assert response.years_cycling == 3
        assert response.indoor_outdoor_preference == "both"
        assert response.completed_at is not None

    def test_replaces_existing_response(self):
        """Re-submitting quiz should replace the old response."""
        db = _make_test_db()
        user = _make_test_user(db)

        submit_quiz(db, user.id, primary_goal="build_fitness")
        response2 = submit_quiz(db, user.id, primary_goal="race")

        assert response2.primary_goal == "race"
        # Should only have one response
        count = db.query(OnboardingResponse).filter(
            OnboardingResponse.user_id == user.id
        ).count()
        assert count == 1

    def test_invalid_primary_goal_raises(self):
        """Invalid primary goal should raise ValueError."""
        db = _make_test_db()
        user = _make_test_user(db)

        try:
            submit_quiz(db, user.id, primary_goal="invalid_goal")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_infers_experience_level(self):
        """Should set experience level on user if not already set."""
        db = _make_test_db()
        user = _make_test_user(db)
        assert user.experience_level is None

        submit_quiz(
            db, user.id,
            primary_goal="build_fitness",
            years_cycling=5,
            current_weekly_volume_hours=12,
        )

        db.refresh(user)
        assert user.experience_level == "elite"

    def test_does_not_overwrite_existing_experience_level(self):
        """Should not overwrite experience level if already set."""
        db = _make_test_db()
        user = _make_test_user(db)
        user.experience_level = "advanced"
        db.commit()

        submit_quiz(
            db, user.id,
            primary_goal="build_fitness",
            years_cycling=0,
            current_weekly_volume_hours=1,
        )

        db.refresh(user)
        assert user.experience_level == "advanced"

    def test_updates_weekly_hours_on_profile(self):
        """Should update user's weekly_hours_available from quiz."""
        db = _make_test_db()
        user = _make_test_user(db)
        assert user.weekly_hours_available is None

        submit_quiz(
            db, user.id,
            primary_goal="build_fitness",
            current_weekly_volume_hours=10.5,
        )

        db.refresh(user)
        assert user.weekly_hours_available == 10.5


class TestOnboardingStatus:
    def test_not_completed(self):
        """Status should show not completed for new user."""
        db = _make_test_db()
        user = _make_test_user(db)

        status = get_onboarding_status(db, user.id)
        assert status["completed"] is False
        assert status["completed_at"] is None

    def test_completed(self):
        """Status should show completed after quiz submission."""
        db = _make_test_db()
        user = _make_test_user(db)

        submit_quiz(db, user.id, primary_goal="target_event")
        status = get_onboarding_status(db, user.id)

        assert status["completed"] is True
        assert status["completed_at"] is not None
        assert status["primary_goal"] == "target_event"


class TestGetOnboardingResponse:
    def test_returns_none_if_not_completed(self):
        """Should return None if no quiz submitted."""
        db = _make_test_db()
        user = _make_test_user(db)

        result = get_onboarding_response(db, user.id)
        assert result is None

    def test_returns_full_response(self):
        """Should return full response after quiz."""
        db = _make_test_db()
        user = _make_test_user(db)

        submit_quiz(
            db, user.id,
            primary_goal="improve_ftp",
            years_cycling=2,
        )

        result = get_onboarding_response(db, user.id)
        assert result is not None
        assert result.primary_goal == "improve_ftp"
        assert result.years_cycling == 2


class TestGoalCRUD:
    def test_create_goal(self):
        """Should create a goal event."""
        db = _make_test_db()
        user = _make_test_user(db)
        future_date = date.today() + timedelta(days=90)

        goal = create_goal(
            db, user.id,
            event_name="Gran Fondo",
            event_date=future_date,
            event_type="gran_fondo",
            priority="a_race",
            target_duration_minutes=240,
            notes="Big event!",
        )

        assert goal.id is not None
        assert goal.event_name == "Gran Fondo"
        assert goal.event_date == future_date
        assert goal.event_type == "gran_fondo"
        assert goal.priority == "a_race"
        assert goal.target_duration_minutes == 240
        assert goal.notes == "Big event!"

    def test_create_goal_invalid_type(self):
        """Invalid event type should raise ValueError."""
        db = _make_test_db()
        user = _make_test_user(db)

        try:
            create_goal(
                db, user.id,
                event_name="Race",
                event_date=date.today(),
                event_type="invalid_type",
                priority="a_race",
            )
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

    def test_list_goals_ordered_by_date(self):
        """Goals should be returned ordered by event date."""
        db = _make_test_db()
        user = _make_test_user(db)

        d1 = date.today() + timedelta(days=30)
        d2 = date.today() + timedelta(days=10)
        d3 = date.today() + timedelta(days=60)

        create_goal(db, user.id, "Later Race", d1, "road_race", "b_race")
        create_goal(db, user.id, "Soon Race", d2, "crit", "a_race")
        create_goal(db, user.id, "Far Race", d3, "time_trial", "c_race")

        goals = get_goals(db, user.id)
        assert len(goals) == 3
        assert goals[0].event_name == "Soon Race"
        assert goals[1].event_name == "Later Race"
        assert goals[2].event_name == "Far Race"

    def test_get_goal_by_id(self):
        """Should retrieve a specific goal by ID."""
        db = _make_test_db()
        user = _make_test_user(db)

        goal = create_goal(
            db, user.id, "My Race", date.today(), "road_race", "a_race"
        )

        fetched = get_goal(db, goal.id, user.id)
        assert fetched is not None
        assert fetched.event_name == "My Race"

    def test_get_goal_wrong_user(self):
        """Should not return goals belonging to another user."""
        db = _make_test_db()
        user1 = _make_test_user(db, "user-1")
        user2 = _make_test_user(db, "user-2")

        goal = create_goal(
            db, user1.id, "User1 Race", date.today(), "crit", "a_race"
        )

        result = get_goal(db, goal.id, user2.id)
        assert result is None

    def test_update_goal(self):
        """Should update goal fields."""
        db = _make_test_db()
        user = _make_test_user(db)

        goal = create_goal(
            db, user.id, "Old Name", date.today(), "road_race", "b_race"
        )

        updated = update_goal(db, goal, {
            "event_name": "New Name",
            "priority": "a_race",
        })

        assert updated.event_name == "New Name"
        assert updated.priority == "a_race"
        assert updated.event_type == "road_race"  # unchanged

    def test_delete_goal(self):
        """Should delete a goal event."""
        db = _make_test_db()
        user = _make_test_user(db)

        goal = create_goal(
            db, user.id, "Delete Me", date.today(), "gravel", "c_race"
        )
        goal_id = goal.id

        delete_goal(db, goal)

        result = get_goal(db, goal_id, user.id)
        assert result is None

    def test_multiple_users_isolated(self):
        """Each user should only see their own goals."""
        db = _make_test_db()
        user1 = _make_test_user(db, "user-1")
        user2 = _make_test_user(db, "user-2")

        create_goal(db, user1.id, "User1 Race", date.today(), "road_race", "a_race")
        create_goal(db, user2.id, "User2 Race", date.today(), "crit", "b_race")

        goals1 = get_goals(db, user1.id)
        goals2 = get_goals(db, user2.id)

        assert len(goals1) == 1
        assert goals1[0].event_name == "User1 Race"
        assert len(goals2) == 1
        assert goals2[0].event_name == "User2 Race"


class TestInferExperienceLevel:
    def test_beginner(self):
        assert _infer_experience_level(0, 2) == "beginner"

    def test_intermediate(self):
        assert _infer_experience_level(2, 5) == "intermediate"

    def test_advanced(self):
        assert _infer_experience_level(4, 10) == "advanced"

    def test_elite(self):
        assert _infer_experience_level(6, 15) == "elite"

    def test_none_values(self):
        assert _infer_experience_level(None, None) == "beginner"
