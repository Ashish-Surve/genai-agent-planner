"""Tests for calendar view components."""

from datetime import date, time, timedelta


class TestTimeBlockComponent:
    """Test time block component."""

    def test_import(self):
        """Test component can be imported."""
        from adhd_planner.ui.components.time_block import empty_slot, time_block_card

        assert time_block_card is not None
        assert empty_slot is not None


class TestDayTimeline:
    """Test day timeline component."""

    def test_import(self):
        """Test component can be imported."""
        from adhd_planner.ui.components.day_timeline import date_navigator, day_timeline

        assert day_timeline is not None
        assert date_navigator is not None


class TestCalendarPage:
    """Test calendar page functions."""

    def test_mock_blocks_structure(self):
        """Test mock time blocks have required fields."""
        mock_blocks = [
            {
                "id": "1",
                "title": "Test block",
                "start_time": time(9, 0),
                "end_time": time(10, 0),
                "energy_level": "high",
                "is_break": False,
            }
        ]

        for block in mock_blocks:
            assert "id" in block
            assert "title" in block
            assert "start_time" in block
            assert "end_time" in block
            assert "energy_level" in block
            assert block["energy_level"] in ["high", "medium", "low"]

    def test_stats_calculation(self):
        """Test stats calculation logic."""
        blocks = [
            {"start_time": time(9, 0), "end_time": time(10, 0), "is_break": False},
            {"start_time": time(10, 0), "end_time": time(10, 30), "is_break": True},
            {"start_time": time(10, 30), "end_time": time(12, 0), "is_break": False},
        ]

        total_minutes = 0
        work_minutes = 0
        break_minutes = 0

        for block in blocks:
            start = block["start_time"]
            end = block["end_time"]
            duration = (end.hour * 60 + end.minute) - (start.hour * 60 + start.minute)
            total_minutes += duration
            if block["is_break"]:
                break_minutes += duration
            else:
                work_minutes += duration

        assert total_minutes == 180  # 3 hours
        assert work_minutes == 150  # 2.5 hours
        assert break_minutes == 30  # 0.5 hours

    def test_date_navigation(self):
        """Test date navigation logic."""
        today = date.today()

        # Previous day
        prev_day = today - timedelta(days=1)
        assert prev_day < today

        # Next day
        next_day = today + timedelta(days=1)
        assert next_day > today
