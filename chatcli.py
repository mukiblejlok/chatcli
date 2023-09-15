#!/usr/bin/env python3
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


def cli() -> int:
    console = Console(width=120)
    console.print(f'ChatCLI - OpenAI powered ChatCLI', style='blue bold', highlight=False)

    try:
        openai.api_key = os.environ['OPENAI_API_KEY']
    except KeyError:
        console.print('You must set the OPENAI_API_KEY environment variable', style='red')
        return 1

    now_utc = datetime.now(timezone.utc)
    setup = f"""
Help the user by responding to their request, the output should be concise and always written in markdown.
The current date and time is {datetime.now()} {now_utc.astimezone().tzinfo.tzname(now_utc)}.
"""
    messages = [{'role': 'system', 'content': setup}]

    history = Path().home() / '.openai-prompt-history.txt'
    session = PromptSession(history=FileHistory(str(history)))

    while True:
        try:
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
            response = openai.ChatCompletion.create(model='gpt-4', messages=messages, stream=True)
        except KeyboardInterrupt:
            status.stop()
            return 0

        status.stop()
        content = ''
        markdown = Markdown(content)
        try:
            with Live(markdown, refresh_per_second=15, console=console) as live:
                for chunk in response:
                    if chunk['choices'][0]['finish_reason'] is not None:
                        break
                    chunk_text = chunk['choices'][0]['delta'].get('content', '')
                    content += chunk_text
                    live.update(Markdown(content))
        except KeyboardInterrupt:
            console.print('[dim]Interrupted[/dim]')

        messages.append({'role': 'assistant', 'content': content})


if __name__ == '__main__':
    load_dotenv()
    sys.exit(cli())
