import sys, os

from lingqAnkiSync.Models.Lingq import Lingq
import pytest


class TestLingqLevelNavigation:
    def test_get_next_level_from_start(self):
        """Test moving from new to recognized."""
        result = Lingq.get_next_level("new")
        assert result == "recognized"

    def test_get_next_level_from_middle(self):
        """Test moving from a middle level like familiar to learned."""
        result = Lingq.get_next_level("familiar")
        assert result == "learned"

    def test_get_next_level_at_end_returns_none(self):
        """Test that getting next level from known returns None."""
        result = Lingq.get_next_level("known")
        assert result is None

    def test_get_prev_level_from_end(self):
        """Test moving from known to learned."""
        result = Lingq.get_prev_level("known")
        assert result == "learned"

    def test_get_prev_level_from_middle(self):
        """Test moving from a middle level like recognized to new."""
        result = Lingq.get_prev_level("recognized")
        assert result == "new"

    def test_get_prev_level_at_start_returns_none(self):
        """Test that getting previous level from new returns None."""
        result = Lingq.get_prev_level("new")
        assert result is None

    def test_get_level_with_invalid_input(self):
        """Test that methods raise an error for an invalid level string."""
        with pytest.raises(ValueError):
            Lingq.get_next_level("invalid_level")

        with pytest.raises(ValueError):
            Lingq.get_prev_level("invalid_level")
