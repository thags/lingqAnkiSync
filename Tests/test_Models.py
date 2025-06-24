import sys, os

from LingqAnkiSync.Models.Lingq import Lingq
import pytest


class TestLingqLevelNavigation:
    def test_get_next_level_from_start(self):
        """Test moving from new to recognized."""
        result = Lingq.GetNextLevel("new")
        assert result == "recognized"

    def test_get_next_level_from_middle(self):
        """Test moving from a middle level like familiar to learned."""
        result = Lingq.GetNextLevel("familiar")
        assert result == "learned"

    def test_get_next_level_at_end_returns_none(self):
        """Test that getting next level from known returns None."""
        result = Lingq.GetNextLevel("known")
        assert result is None

    def test_get_prev_level_from_end(self):
        """Test moving from known to learned."""
        result = Lingq.GetPrevLevel("known")
        assert result == "learned"

    def test_get_prev_level_from_middle(self):
        """Test moving from a middle level like recognized to new."""
        result = Lingq.GetPrevLevel("recognized")
        assert result == "new"

    def test_get_prev_level_at_start_returns_none(self):
        """Test that getting previous level from new returns None."""
        result = Lingq.GetPrevLevel("new")
        assert result is None

    def test_get_level_with_invalid_input(self):
        """Test that methods raise an error for an invalid level string."""
        with pytest.raises(ValueError):
            Lingq.GetNextLevel("invalid_level")

        with pytest.raises(ValueError):
            Lingq.GetPrevLevel("invalid_level")


def test_lingq_init():
    """Test Lingq model initialization."""
    lingq = Lingq(
        primaryKey=123,
        word="test",
        translations=["translation1", "translation2"],
        status=1,
        extendedStatus=0,
        tags=["tag1", "tag2"],
        fragment="This is a test sentence.",
        importance=1,
    )

    assert lingq.primaryKey == 123
    assert lingq.word == "test"
    assert lingq.translations == ["translation1", "translation2"]
    assert lingq.status == 1
    assert lingq.extendedStatus == 0
    assert lingq.tags == ["tag1", "tag2"]
    assert lingq.fragment == "This is a test sentence."
    assert lingq.importance == 1


def test_lingq_equality():
    """Test Lingq model equality comparison."""
    lingq1 = Lingq(
        primaryKey=123,
        word="test",
        translations=["translation1"],
        status=1,
        extendedStatus=0,
        tags=["tag1"],
        fragment="test sentence",
        importance=1,
    )

    lingq2 = Lingq(
        primaryKey=123,
        word="test",
        translations=["translation1"],
        status=1,
        extendedStatus=0,
        tags=["tag1"],
        fragment="test sentence",
        importance=1,
    )

    lingq3 = Lingq(
        primaryKey=456,  # Different primary key
        word="test",
        translations=["translation1"],
        status=1,
        extendedStatus=0,
        tags=["tag1"],
        fragment="test sentence",
        importance=1,
    )

    assert lingq1 == lingq2
    assert lingq1 != lingq3
    assert lingq2 != lingq3
