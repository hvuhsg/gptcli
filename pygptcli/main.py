import sys
import openai
import shelve
from pathlib import Path

from colorama import Fore, Style


db_dirpath = Path.home() / Path(".pygptcli")
if not db_dirpath.is_dir():
    db_dirpath.mkdir()

db_filepath = str((db_dirpath / Path("settings.db")).absolute())
db_file = shelve.open(db_filepath, writeback=True)


def main():
    if len(sys.argv) == 1:
        print("Get help with the --help or -h flags.")
        exit(1)

    if sys.argv[1] in ["--help", "-h"]:
        help_message()
        return

    if sys.argv[1] == "--configure":
        configure()
        return

    if sys.argv[1] == "--show-vars":
        show_vars()
        return

    request()


def help_message():
    print("This tool is built to communicate with OpenAI GPT3 from the terminal.")
    print("The usage is simple, just pass the prompt as argument to this tool.")
    print("Before starting to send requests you must configure your api key, to configure valuables you can use the --configure command")
    print("The --configure command accept 2 arguments, KEY and VALUE")
    print("The available variables are:")
    print("\topenaikey -> The API Key to use when calling OpenAI API (required)")
    print("\tmax_tokens -> Max number of words in the response default to 300 (optional)")
    print("\ttemperature -> The model temperature default to 0.8 (optional)")
    print("To see all of the current configuration, use the --show-vars command")


def show_vars():
    print("Showing current configuration")
    for k, v in db_file.items():
        print(f"{k} -> {v}")


def request():
    prompt = ' '.join(sys.argv[1:])
    answer = ""

    print(Fore.YELLOW + '-'*10, f"Prompt: {prompt}", '-'*10 + Style.RESET_ALL, end="\n\n")
    print("\t\t", end="")

    for text in get_response_iter(prompt):
        if not answer and text in [" ", "\t", "\n"]:
            continue

        answer += text
        text = text.replace("\n", "\n\t\t")
        print(text, end="")

    print(Style.DIM + '\n\n' + '-'*10, "DONE", '-'*10 + Style.RESET_ALL)


def configure():
    if len(sys.argv) != 4:
        print("ERROR: expecting 2 arguments after --configure, for example:\n")
        print("     pygptcli --configure openaikey <YOUR_KEY>\n")
        exit(0)

    key = sys.argv[2]
    value = sys.argv[3]

    save_key(key, value)
    print(Fore.GREEN, f"Key '{key}' saved successfully" + Style.RESET_ALL)


def get_response_iter(prompt: str) -> iter:
    openai.api_key = get_key("openaikey")
    if not openai.api_key:
        print(Fore.RED + "ERROR: openai key not configured")
        print("You can use the nex command to configure it:\n")
        print("     pygptcli --configure openaikey <YOUR_KEY>\n")
        print("You can find your key here -> https://platform.openai.com/account/api-keys" + Style.RESET_ALL)
        return

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=int(get_key("max_tokens", 300)),
        n=1,
        stop=None,
        temperature=get_key("temperature", 0.8),
        stream=True,
    )

    # Process response as a stream
    for chunk in response:
        text = chunk['choices'][0]["text"]
        yield text


def save_key(key: str, value):
    db_file[key] = value


def get_key(key: str, default=None):
    return db_file.get(key, default)
