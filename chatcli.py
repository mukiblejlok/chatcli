#!/usr/bin/env python3
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import openai
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.status import Status
from dotenv import load_dotenv

prompt_style = Style.from_dict({
    '': '#ff0066',
    'pr': '#884444',
})

MODEL = 'gpt-4'
SESSION_START_ID = datetime.now().strftime("%Y%m%d%H%M%S")


def store_messages(messages):
    p = Path(__file__).parent / f".openapi_chat_{SESSION_START_ID}.json"
    p.write_text(json.dumps(messages))
    return None


def cli() -> int:
    console = Console(width=120)
    console.print(f'ChatCLI - OpenAI powered ChatCLI - {MODEL}', style='blue bold', highlight=False)

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    except KeyError:
        console.print('You must set the OPENAI_API_KEY environment variable', style='red')
        return 1

    now_utc = datetime.now(timezone.utc)
    setup = f"""
Help the user by responding to their request, the output should be concise and always written in markdown.
The current date and time is {datetime.now()} {now_utc.astimezone().tzinfo.tzname(now_utc)}.
"""
    messages = [{'role': 'system', 'content': setup}]

    history = Path(__file__).parent / '.openai-prompt-history.txt'
    session = PromptSession(history=FileHistory(str(history)))
    logging.basicConfig()

    while True:
        try:
            store_messages(messages=messages)
            text = session.prompt([("class:pr", "chatcli ➤ ")], auto_suggest=AutoSuggestFromHistory(),
                                  style=prompt_style)
        except (KeyboardInterrupt, EOFError):
            return 0

        if not text:
            continue

        status = Status('[dim]Thinking…[/dim]', console=console)
        status.start()
        messages.append({'role': 'user', 'content': text})

        try:
            response = client.chat.completions.create(model=MODEL, messages=messages, stream=True)
        except KeyboardInterrupt:
            status.stop()
            return 0

        status.stop()
        content = ''
        markdown = Markdown(content)
        try:
            with Live(markdown, refresh_per_second=5, console=console) as live:
                for chunk in response:
                    first_choice = chunk.choices[0]
                    if first_choice.finish_reason is not None:
                        break
                    chunk_text = first_choice.delta.content if first_choice.delta.content else ''
                    content += chunk_text
                    live.update(Markdown(content))
        except KeyboardInterrupt:
            console.print('[dim]Interrupted[/dim]')

        messages.append({'role': 'assistant', 'content': content})


if __name__ == '__main__':
    load_dotenv()
    sys.exit(cli())
