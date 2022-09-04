from importlib.resources import files

from textual.app import App
from textual.reactive import Reactive
from textual.widgets import Footer, Placeholder
from textual.widget import Widget
from rich.panel import Panel
from rich.panel import Text

from not_nintendogs import data


class Hover(Widget):
    mouse_over = Reactive(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dog_text = files(data).joinpath("doggo.txt").read_text()
        self.mouse_over = False

    def render(self) -> Panel:
        return Panel(
            Text.from_ansi(self.dog_text),
            title="This is a doggo",
        )

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False


class MainApp(App):
    show_bar = Reactive(False)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bar = None

    async def on_load(self) -> None:
        """Bind keys here."""
        await self.bind("b", "toggle_sidebar", "Toggle sidebar")
        await self.bind("q", "quit", "Quit")

    def watch_show_bar(self, show_bar: bool) -> None:
        """Called when show_bar changes."""
        self.bar.animate("layout_offset_x", 0 if show_bar else -40)

    def action_toggle_sidebar(self) -> None:
        """Called when user hits 'b' key."""
        self.show_bar = not self.show_bar

    async def on_mount(self) -> None:
        """Layout here."""
        footer = Footer()
        self.bar = Placeholder(name="left")

        await self.view.dock(footer, edge="bottom")
        await self.view.dock(Hover(), edge="top")
        await self.view.dock(self.bar, edge="left", size=40, z=1)

        self.bar.layout_offset_x = -40


if __name__ == "__main__":
    MainApp.run()
