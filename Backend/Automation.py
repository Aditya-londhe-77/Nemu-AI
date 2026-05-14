from AppOpener import close, open as appopen # type: ignore
from webbrowser import open as webopen
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard # type: ignore
import asyncio
import os


env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
Username = env_vars.get("Username", "User")

# Define HTML classes to scrape
classes = ["Z0cb0rf", "hgKElc", "LTKooSYITrcY", "Z0LCW", "gsrt wb_b FzwWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta", 
           "iTz6cF", "OSr0Rd LTKOO", "VL7dq", "webanswers-webanswers_table__webanswers-table", "dDoNo ikb4Bb gsrt", "sXLa0e", 
           "LWfK8e", "V0F4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]


useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

client = Groq(api_key=GroqAPIKey)


professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask."
]
messages = []
SystemChatBot = [{"role": "system", "content": f"Hello, I am {Username}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}]


def GoogleSearch(Topic):
    """Open Google search results in the default browser."""
    url = f"https://www.google.com/search?q={Topic}"
    webbrowser.open(url)
    print(f"[green]Opened Google Search for:[/green] {Topic}")
    return True


def Content(Topic):
    def OpenNotepad(File):
        subprocess.Popen(["notepad.exe", File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": prompt})
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic = Topic.replace("content", "", 1).strip()
    ContentByAI = ContentWriterAI(Topic)

    filename = rf"Data\{Topic.lower().replace(' ', '')}.txt"
    os.makedirs("Data", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as file:
        file.write(ContentByAI)

    OpenNotepad(filename)
    return True


def YouTubeSearch(Topic):
    url = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(url)
    return True


def PlayYoutube(query):
    return YouTubeSearch(query)

def OpenApp(app, sess=requests.session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links]

        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers)
            return response.text if response.status_code == 200 else None

        html = search_google(app)
        if html:
            links = extract_links(html)
            if links:
                webopen(links[0])
        return True

def CloseApp(app):
    if "chrome" in app:
        return False
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        return False


def System(command):
    def mute(): keyboard.press_and_release("volume mute")
    def unmute(): keyboard.press_and_release("volume mute")
    def volume_up(): keyboard.press_and_release("volume up")
    def volume_down(): keyboard.press_and_release("volume down")

    commands = {
        "mute": mute,
        "unmute": unmute,
        "volume up": volume_up,
        "volume down": volume_down
    }

    action = commands.get(command.lower())
    if action:
        action()
        return True
    return False


async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        cmd = command.strip()
        cmd_lower = cmd.lower()

        if cmd_lower.startswith("open ") and not cmd_lower.startswith("open file") and "open it" not in cmd_lower:
            funcs.append(asyncio.to_thread(OpenApp, cmd[5:].strip()))

        elif cmd_lower.startswith("close "):
            funcs.append(asyncio.to_thread(CloseApp, cmd[6:].strip()))

        elif cmd_lower.startswith("play "):
            funcs.append(asyncio.to_thread(PlayYoutube, cmd[5:].strip()))

        elif "content" in cmd_lower:
            topic = cmd.replace("content", "", 1).strip()
            funcs.append(asyncio.to_thread(Content, topic))

        elif cmd_lower.startswith("google search "):
            funcs.append(asyncio.to_thread(GoogleSearch, cmd[14:].strip()))

        elif cmd_lower.startswith("youtube search "):
            funcs.append(asyncio.to_thread(YouTubeSearch, cmd[15:].strip()))

        elif cmd_lower.startswith("system "):
            funcs.append(asyncio.to_thread(System, cmd[7:].strip()))

        else:
            print(f"[red]No function found for command:[/red] {cmd}")

    results = await asyncio.gather(*funcs)

    for result in results:
        yield result


async def Automation(commands: list[str]):
    async for _ in TranslateAndExecute(commands):
        pass
    return True


if __name__ == "__main__":
    commands = [
       
        "play phonk music on youtube "
    ]
    asyncio.run(Automation(commands))
