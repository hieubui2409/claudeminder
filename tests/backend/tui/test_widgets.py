"""Tests for TUI widgets."""

from __future__ import annotations

import pytest
from textual.app import App, ComposeResult

from backend.tui.widgets.usage_display import UsageDisplay


class TestUsageDisplayWidget:
    """Tests for UsageDisplay widget."""

    @pytest.mark.asyncio
    async def test_initial_state(self):
        """Test initial widget state."""

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield UsageDisplay()

        async with TestApp().run_test() as pilot:
            widget = pilot.app.query_one(UsageDisplay)
            assert widget.five_hour_usage == 0.0
            assert widget.seven_day_usage is None
            assert widget.extra_usage is None

    @pytest.mark.asyncio
    async def test_update_five_hour_usage(self):
        """Test updating five hour usage."""

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield UsageDisplay()

        async with TestApp().run_test() as pilot:
            widget = pilot.app.query_one(UsageDisplay)
            widget.five_hour_usage = 50.0
            await pilot.pause()

            assert widget.five_hour_usage == 50.0

    @pytest.mark.asyncio
    async def test_update_all_usage(self):
        """Test updating all usage values."""

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield UsageDisplay()

        async with TestApp().run_test() as pilot:
            widget = pilot.app.query_one(UsageDisplay)
            widget.update_usage(
                five_hour=45.0,
                seven_day=30.0,
                extra=10.0,
            )
            await pilot.pause()

            assert widget.five_hour_usage == 45.0
            assert widget.seven_day_usage == 30.0
            assert widget.extra_usage == 10.0


class TestProgressBar:
    """Tests for progress bar rendering."""

    @pytest.mark.asyncio
    async def test_green_color_under_75(self):
        """Test progress bar is green under 75%."""

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield UsageDisplay()

        async with TestApp().run_test() as pilot:
            widget = pilot.app.query_one(UsageDisplay)
            bar = widget._progress_bar(50.0)
            assert "green" in bar

    @pytest.mark.asyncio
    async def test_yellow_color_at_75(self):
        """Test progress bar is yellow at 75%."""

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield UsageDisplay()

        async with TestApp().run_test() as pilot:
            widget = pilot.app.query_one(UsageDisplay)
            bar = widget._progress_bar(80.0)
            assert "yellow" in bar

    @pytest.mark.asyncio
    async def test_red_color_at_90(self):
        """Test progress bar is red at 90%."""

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield UsageDisplay()

        async with TestApp().run_test() as pilot:
            widget = pilot.app.query_one(UsageDisplay)
            bar = widget._progress_bar(95.0)
            assert "red" in bar

    @pytest.mark.asyncio
    async def test_bar_width(self):
        """Test progress bar respects width."""

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield UsageDisplay()

        async with TestApp().run_test() as pilot:
            widget = pilot.app.query_one(UsageDisplay)
            bar = widget._progress_bar(50.0, width=20)
            # Bar should have 10 filled + 10 empty chars
            assert "█" * 10 in bar
            assert "░" * 10 in bar

    @pytest.mark.asyncio
    async def test_bar_caps_at_100(self):
        """Test progress bar caps at 100%."""

        class TestApp(App):
            def compose(self) -> ComposeResult:
                yield UsageDisplay()

        async with TestApp().run_test() as pilot:
            widget = pilot.app.query_one(UsageDisplay)
            bar = widget._progress_bar(150.0, width=10)
            # Should be fully filled
            assert "█" * 10 in bar
