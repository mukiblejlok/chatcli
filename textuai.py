from textual.app import App, ComposeResult
import asyncio

from textual.app import App, ComposeResult
from textual.widgets import Input, Header, RichLog


class Chat(RichLog):
    pass


class Prompt(Input):
    pass


async def generate_response(text):
    words = text.split()
    while words:
        word = words.pop(0)
        yield word.upper()
        await asyncio.sleep()


class InputApp(App):
    """App to display key events."""

    CSS_PATH = "textuai.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Chat()

        yield Prompt()

    # async def on_input_submitted(self, event: Input.Submitted) -> None:
    #     chat = self.query_one(Chat)
    #     await chat.write(event.value)
    #     event.input.value = "Thinking"
    #     response = await


if __name__ == "__main__":
    app = InputApp()
    app.run()
