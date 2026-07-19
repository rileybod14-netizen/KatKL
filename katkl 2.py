
import os
import sys
import time
import random
import socket
import shutil
import string
import hashlib
import base64
import threading
import subprocess
import urllib.request

class C:
    PERI = "\033[38;2;178;178;255m"
    PURPLE = "\033[38;2;170;90;255m"
    GRAY = "\033[38;2;150;150;150m"
    RED = "\033[38;2;255;70;70m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

BOX_WIDTH = 58

TAGLINES = [
    "OwO",
    "does anyone read this?",
    "Nya~",
    "are you on Linux, or Termux? Nah, doesn't matter.",
    "haha ur a skid lmao",
    "who was in Paris?",
    "Elliot Alderson would be proud of you",
    "localhost:3000",
]

KATKL_ART = [
    "██╗  ██╗  █████╗  ████████╗ ██╗  ██╗ ██╗     ",
    "██║ ██╔╝ ██╔══██╗ ╚══██╔══╝ ██║ ██╔╝ ██║     ",
    "█████╔╝  ███████║    ██║    █████╔╝  ██║     ",
    "██╔═██╗  ██╔══██║    ██║    ██╔═██╗  ██║     ",
    "██║  ██╗ ██║  ██║    ██║    ██║  ██╗ ███████╗",
    "╚═╝  ╚═╝ ╚═╝  ╚═╝    ╚═╝    ╚═╝  ╚═╝ ╚══════╝",
]

COMMON_PORTS = {
    21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns",
    80: "http", 110: "pop3", 111: "rpcbind", 135: "msrpc",
    139: "netbios-ssn", 143: "imap", 443: "https", 445: "microsoft-ds",
    993: "imaps", 995: "pop3s", 1723: "pptp", 3306: "mysql",
    3389: "rdp", 5900: "vnc", 8080: "http-alt", 8443: "https-alt",
}

STATE = {"scanned": False, "hosts": [], "active_ports": {}}

MORSE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
    '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.', ' ': '/',
}
MORSE_REV = {v: k for k, v in MORSE.items()}

EIGHT_BALL = [
    "It is certain.", "Without a doubt.", "You may rely on it.",
    "Yes, definitely.", "Ask again later.", "Cannot predict now.",
    "Concentrate and ask again.", "Don't count on it.", "My reply is no.",
    "Outlook not so good.", "Very doubtful.", "Signs point to yes.",
]

HACKER_QUOTES = [
    "The quieter you become, the more you are able to hear.",
    "There is no patch for human stupidity.",
    "In a world without walls, who needs windows?",
    "Security is a process, not a product.",
    "Given enough eyeballs, all bugs are shallow.",
    "The only truly secure system is one that is powered off.",
    "Hack the planet.",
]

RANDOM_FACTS = [
    "A group of flamingos is called a flamboyance.",
    "Bananas are berries, but strawberries aren't.",
    "The first computer bug was an actual moth.",
    "Octopuses have three hearts.",
    "Honey never spoils.",
    "The dot over a lowercase i or j is called a tittle.",
]


def clear():
    os.system("clear" if os.name != "nt" else "cls")


def box_line(text="", color=C.PERI, align="center"):
    inner = BOX_WIDTH - 2
    if align == "center":
        text = text.center(inner)
    else:
        text = (" " + text).ljust(inner)
    return f"{C.PURPLE}║{C.RESET}{color}{text}{C.RESET}{C.PURPLE}║{C.RESET}"


def box_top():
    print(f"{C.PURPLE}╔{'═' * (BOX_WIDTH - 2)}╗{C.RESET}")


def box_mid():
    print(f"{C.PURPLE}╠{'═' * (BOX_WIDTH - 2)}╣{C.RESET}")


def box_bottom():
    print(f"{C.PURPLE}╚{'═' * (BOX_WIDTH - 2)}╝{C.RESET}")


def compiling_animation(duration=2.5):
    clear()
    spinner = ["|", "/", "-", "\\"]
    start = time.time()
    i = 0
    while time.time() - start < duration:
        sys.stdout.write(f"\r{C.PERI}Compiling... {spinner[i % len(spinner)]}{C.RESET}")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r" + " " * 30 + "\r")
    clear()


def draw_main_menu():
    clear()
    tagline = random.choice(TAGLINES)
    box_top()
    for line in KATKL_ART:
        print(box_line(line, color=C.PERI + C.BOLD))
    print(box_line(tagline, color=C.GRAY))
    box_mid()
    for opt in [
        "[1] Scan Network",
        "[2] Options",
        "[3] Devices",
        "[4] YouTube Link to ASCII",
        "[5] READ-ME",
        "[6] More Tools",
    ]:
        print(box_line(opt, color=C.PERI, align="left"))
    box_bottom()


def main_menu():
    while True:
        draw_main_menu()
        choice = input(f"\n{C.PERI}kat@kl > {C.RESET}").strip()
        if choice == "1":
            scan_network()
        elif choice == "2":
            options_menu()
        elif choice == "3":
            devices_menu()
        elif choice == "4":
            yt_to_ascii()
        elif choice == "5":
            readme()
        elif choice == "6":
            more_tools_menu()


def run_port_scan(ip, timeout=0.6):
    active = []
    lock = threading.Lock()

    def check(port, name):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
            if s.connect_ex((ip, port)) == 0:
                with lock:
                    active.append((port, name))
        except OSError:
            pass
        finally:
            s.close()

    threads = [threading.Thread(target=check, args=(p, n)) for p, n in COMMON_PORTS.items()]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    active.sort(key=lambda x: x[0])
    return active


def scan_network():
    clear()
    print(f"{C.RED}WARNING:{C.RESET} {C.PURPLE}This scanning tool must only be used on your "
          f"own network LEGALLY. Using this scan on anyone else's network is prohibited. By "
          f"using this, you agree that scanning other people's networks may put you in legal "
          f"trouble.{C.RESET}")
    print()
    print(f"{C.PERI}[Y/N]{C.RESET}")
    while True:
        ans = input(f"{C.PURPLE}> {C.RESET}").strip().lower()
        if ans == "y":
            break
        if ans == "n":
            return

    clear()
    print(f"{C.PURPLE}Enter the network address to scan (e.g. 192.168.0.12):{C.RESET}")
    target = input(f"{C.PURPLE}> {C.RESET}").strip()
    if not target:
        return

    clear()
    print(f"{C.PURPLE}Starting scan on {target} ...{C.RESET}")
    print(f"{C.PURPLE}Host seems up.{C.RESET}")
    print(f"{C.PURPLE}Probing {len(COMMON_PORTS)} common ports...{C.RESET}\n")

    active_ports = run_port_scan(target)
    STATE["active_ports"][target] = active_ports
    STATE["scanned"] = True
    if target not in STATE["hosts"]:
        STATE["hosts"].append(target)

    if active_ports:
        print(f"{C.PURPLE}PORT      SERVICE        STATUS{C.RESET}")
        for port, service in active_ports:
            line = f"{str(port) + '/tcp':<9} {service:<14} active"
            print(f"{C.PURPLE}{line}{C.RESET}")
    else:
        print(f"{C.PURPLE}No active ports found on {target}.{C.RESET}")

    print(f"\n{C.PURPLE}Scan complete. Type 'back' to return to KatKL.{C.RESET}")
    while True:
        cmd = input(f"{C.PURPLE}> {C.RESET}").strip().lower()
        if cmd == "back":
            return


def options_menu():
    while True:
        clear()
        box_top()
        print(box_line("Options", color=C.PERI + C.BOLD))
        box_mid()
        for opt in [
            "[1] Clear saved scan data",
            "[2] Toggle scan speed",
            "[3] About KatKL",
            "[4] Back",
        ]:
            print(box_line(opt, color=C.PERI, align="left"))
        box_bottom()
        choice = input(f"\n{C.PERI}options > {C.RESET}").strip()

        if choice == "1":
            STATE["scanned"] = False
            STATE["hosts"] = []
            STATE["active_ports"] = {}
            print(f"{C.PURPLE}Saved scan data cleared.{C.RESET}")
            time.sleep(1)
        elif choice == "2":
            print(f"{C.PURPLE}Scan speed is fixed for stability in this build.{C.RESET}")
            time.sleep(1.2)
        elif choice == "3":
            clear()
            print(f"{C.PERI}{C.BOLD}KatKL{C.RESET}")
            print(f"{C.PURPLE}A lightweight, Termux-friendly network toolkit for personal, "
                  f"authorized network use.{C.RESET}")
            input(f"\n{C.PERI}Press Enter to return...{C.RESET}")
        elif choice == "4":
            return


def devices_menu():
    clear()
    if not STATE["scanned"]:
        print(f"{C.RED}Network scan info not found. Scan via option 1.{C.RESET}")
        while True:
            cmd = input(f"{C.PURPLE}> {C.RESET}").strip().lower()
            if cmd == "back":
                return
        return

    print(f"{C.PURPLE}Devices found on network:{C.RESET}")
    print(f"{C.GRAY}(For educational purposes only - most useful in a cybersecurity context){C.RESET}\n")

    for host in STATE["hosts"]:
        try:
            name = socket.gethostbyaddr(host)[0]
        except (socket.herror, socket.gaierror, OSError):
            name = "Unknown Device"
        print(f"{C.PURPLE}  {host:<16} -> {name}{C.RESET}")

    print(f"\n{C.PURPLE}Type 'back' to return to KatKL.{C.RESET}")
    while True:
        cmd = input(f"{C.PURPLE}> {C.RESET}").strip().lower()
        if cmd == "back":
            return


def yt_to_ascii():
    clear()
    print(f"{C.PERI}{C.BOLD}YouTube Link to ASCII{C.RESET}")
    print(f"{C.GRAY}Converts the first 20 seconds of a video into a dot-based ASCII animation.{C.RESET}\n")
    url = input(f"{C.PERI}YouTube URL > {C.RESET}").strip()
    if not url:
        return

    if not shutil.which("ffmpeg"):
        print(f"{C.RED}ffmpeg not found. Install it with: pkg install ffmpeg{C.RESET}")
        input(f"{C.PERI}Press Enter to return...{C.RESET}")
        return
    try:
        import yt_dlp
    except ImportError:
        print(f"{C.RED}yt-dlp not found. Install it with: pip install yt-dlp{C.RESET}")
        input(f"{C.PERI}Press Enter to return...{C.RESET}")
        return
    try:
        from PIL import Image
    except ImportError:
        print(f"{C.RED}Pillow not found. Install it with: pip install pillow{C.RESET}")
        input(f"{C.PERI}Press Enter to return...{C.RESET}")
        return

    workdir = "katkl_tmp"
    frames_dir = os.path.join(workdir, "frames")
    video_path = os.path.join(workdir, "clip.mp4")
    if os.path.exists(workdir):
        shutil.rmtree(workdir, ignore_errors=True)
    os.makedirs(frames_dir, exist_ok=True)

    print(f"\n{C.PURPLE}Downloading first 20 seconds of the clip...{C.RESET}")
    ydl_opts = {
        "format": "worst[ext=mp4]/worst",
        "outtmpl": video_path,
        "quiet": True,
        "no_warnings": True,
    }
    try:
        from yt_dlp.utils import download_range_func
        ydl_opts["download_ranges"] = download_range_func(None, [(0, 20)])
        ydl_opts["force_keyframes_at_cuts"] = True
    except ImportError:
        pass

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"{C.RED}Download failed: {e}{C.RESET}")
        shutil.rmtree(workdir, ignore_errors=True)
        input(f"{C.PERI}Press Enter to return...{C.RESET}")
        return

    if not os.path.exists(video_path):
        print(f"{C.RED}Could not locate downloaded file.{C.RESET}")
        shutil.rmtree(workdir, ignore_errors=True)
        input(f"{C.PERI}Press Enter to return...{C.RESET}")
        return

    print(f"{C.PURPLE}Extracting frames...{C.RESET}")
    fps = 10
    width_chars = 80
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", video_path, "-t", "20",
            "-vf", f"fps={fps},scale={width_chars}:-1",
            os.path.join(frames_dir, "frame_%04d.png"),
        ],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    frames = sorted(f for f in os.listdir(frames_dir) if f.endswith(".png"))
    if not frames:
        print(f"{C.RED}No frames extracted.{C.RESET}")
        shutil.rmtree(workdir, ignore_errors=True)
        input(f"{C.PERI}Press Enter to return...{C.RESET}")
        return

    print(f"{C.PURPLE}Rendering {len(frames)} frames as dots... (Ctrl+C to stop early){C.RESET}")
    time.sleep(1.2)

    ascii_frames = []
    for fname in frames:
        img = Image.open(os.path.join(frames_dir, fname)).convert("L")
        w, h = img.size
        pixels = img.load()
        lines = []
        for y in range(0, h, 2):
            line = "".join("." if pixels[x, y] < 128 else " " for x in range(w))
            lines.append(line)
        ascii_frames.append("\n".join(lines))

    try:
        for frame in ascii_frames:
            clear()
            print(f"{C.PERI}{frame}{C.RESET}")
            time.sleep(1 / fps)
    except KeyboardInterrupt:
        pass

    shutil.rmtree(workdir, ignore_errors=True)
    input(f"\n{C.PURPLE}Done! Press Enter to return to KatKL...{C.RESET}")


def gen_password_tool():
    clear()
    print(f"{C.PURPLE}Password Generator{C.RESET}")
    length_in = input(f"{C.PERI}Length (default 16) > {C.RESET}").strip()
    length = int(length_in) if length_in.isdigit() else 16
    chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    pw = "".join(random.choice(chars) for _ in range(max(4, length)))
    print(f"\n{C.PURPLE}Generated password:{C.RESET}")
    print(f"{C.PERI}{pw}{C.RESET}")
    input(f"\n{C.PERI}Press Enter to return...{C.RESET}")


def password_strength_tool():
    clear()
    print(f"{C.PURPLE}Password Strength Checker{C.RESET}")
    pw = input(f"{C.PERI}Enter a password > {C.RESET}")
    score = 0
    if len(pw) >= 8:
        score += 1
    if len(pw) >= 12:
        score += 1
    if any(c.islower() for c in pw):
        score += 1
    if any(c.isupper() for c in pw):
        score += 1
    if any(c.isdigit() for c in pw):
        score += 1
    if any(c in string.punctuation for c in pw):
        score += 1
    labels = {0: "Very Weak", 1: "Very Weak", 2: "Weak", 3: "Okay",
              4: "Good", 5: "Strong", 6: "Very Strong"}
    print(f"\n{C.PURPLE}Strength: {labels[score]} ({score}/6){C.RESET}")
    input(f"\n{C.PERI}Press Enter to return...{C.RESET}")


def hash_text_tool():
    clear()
    print(f"{C.PURPLE}Hash Text{C.RESET}")
    text = input(f"{C.PERI}Enter text > {C.RESET}")
    data = text.encode()
    print(f"\n{C.PURPLE}MD5:    {C.RESET}{C.PERI}{hashlib.md5(data).hexdigest()}{C.RESET}")
    print(f"{C.PURPLE}SHA1:   {C.RESET}{C.PERI}{hashlib.sha1(data).hexdigest()}{C.RESET}")
    print(f"{C.PURPLE}SHA256: {C.RESET}{C.PERI}{hashlib.sha256(data).hexdigest()}{C.RESET}")
    input(f"\n{C.PERI}Press Enter to return...{C.RESET}")


def base64_tool():
    clear()
    print(f"{C.PURPLE}Base64 Encode / Decode{C.RESET}")
    mode = input(f"{C.PERI}(E)ncode or (D)ecode > {C.RESET}").strip().lower()
    text = input(f"{C.PERI}Text > {C.RESET}")
    try:
        if mode == "e":
            result = base64.b64encode(text.encode()).decode()
        else:
            result = base64.b64decode(text.encode()).decode()
        print(f"\n{C.PURPLE}Result:{C.RESET}")
        print(f"{C.PERI}{result}{C.RESET}")
    except Exception as e:
        print(f"\n{C.RED}Error: {e}{C.RESET}")
    input(f"\n{C.PERI}Press Enter to return...{C.RESET}")


def caesar_tool():
    clear()
    print(f"{C.PURPLE}Caesar Cipher{C.RESET}")
    text = input(f"{C.PERI}Text > {C.RESET}")
    shift_in = input(f"{C.PERI}Shift (default 3) > {C.RESET}").strip()
    shift = int(shift_in) if shift_in.lstrip("-").isdigit() else 3
    result = []
    for ch in text:
        if ch.isalpha():
            base_ord = ord('A') if ch.isupper() else ord('a')
            result.append(chr((ord(ch) - base_ord + shift) % 26 + base_ord))
        else:
            result.append(ch)
    print(f"\n{C.PURPLE}Result:{C.RESET}")
    print(f"{C.PERI}{''.join(result)}{C.RESET}")
    input(f"\n{C.PERI}Press Enter to return...{C.RESET}")


def morse_tool():
    clear()
    print(f"{C.PURPLE}Morse Code Translator{C.RESET}")
    mode = input(f"{C.PERI}(E)ncode or (D)ecode > {C.RESET}").strip().lower()
    if mode == "e":
        text = input(f"{C.PERI}Text > {C.RESET}").upper()
        result = " ".join(MORSE.get(c, "?") for c in text)
    else:
        text = input(f"{C.PERI}Morse (space between letters, / for word gap) > {C.RESET}")
        result = "".join(MORSE_REV.get(c, "") for c in text.split(" "))
    print(f"\n{C.PURPLE}Result:{C.RESET}")
    print(f"{C.PERI}{result}{C.RESET}")
    input(f"\n{C.PERI}Press Enter to return...{C.RESET}")


def text_tools_tool():
    clear()
    print(f"{C.PURPLE}Text Reverser / Leetspeak{C.RESET}")
    text = input(f"{C.PERI}Text > {C.RESET}")
    mode = input(f"{C.PERI}(R)everse or (L)eetspeak > {C.RESET}").strip().lower()
    if mode == "r":
        result = text[::-1]
    else:
        leet = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 't': '7', 's': '5',
                 'A': '4', 'E': '3', 'I': '1', 'O': '0', 'T': '7', 'S': '5'}
        result = "".join(leet.get(c, c) for c in text)
    print(f"\n{C.PURPLE}Result:{C.RESET}")
    print(f"{C.PERI}{result}{C.RESET}")
    input(f"\n{C.PERI}Press Enter to return...{C.RESET}")


def coin_flip_tool():
    clear()
    print(f"{C.PURPLE}Coin Flip{C.RESET}\n")
    print(f"{C.PERI}{random.choice(['Heads', 'Tails'])}{C.RESET}")
    input(f"\n{C.PERI}Press Enter to return...{C.RESET}")


def dice_roll_tool():
    clear()
    print(f"{C.PURPLE}Dice Roller{C.RESET}")
    sides_in = input(f"{C.PERI}Sides (default 6) > {C.RESET}").strip()
    sides = int(sides_in) if sides_in.isdigit() else 6
    print(f"\n{C.PERI}You rolled a {random.randint(1, max(1, sides))}{C.RESET}")
    input(f"\n{C.PERI}Press Enter to return...{C.RESET}")


def eight_ball_tool():
    clear()
    print(f"{C.PURPLE}Magic 8-Ball{C.RESET}")
    input(f"{C.PERI}Ask a question and press Enter > {C.RESET}")
    print(f"\n{C.PERI}{random.choice(EIGHT_BALL)}{C.RESET}")
    input(f"\n{C.PERI}Press Enter to return...{C.RESET}")


def random_number_tool():
    clear()
    print(f"{C.PURPLE}Random Number Generator{C.RESET}")
    lo_in = input(f"{C.PERI}Min (default 1) > {C.RESET}").strip()
    hi_in = input(f"{C.PERI}Max (default 100) > {C.RESET}").strip()
    lo = int(lo_in) if lo_in.lstrip("-").isdigit() else 1
    hi = int(hi_in) if hi_in.lstrip("-").isdigit() else 100
    if lo > hi:
        lo, hi = hi, lo
    print(f"\n{C.PERI}{random.randint(lo, hi)}{C.RESET}")
    input(f"\n{C.PERI}Press Enter to return...{C.RESET}")


def hacker_quote_tool():
    clear()
    print(f"{C.PURPLE}Random Hacker Quote{C.RESET}\n")
    print(f"{C.PERI}\"{random.choice(HACKER_QUOTES)}\"{C.RESET}")
    input(f"\n{C.PERI}Press Enter to return...{C.RESET}")


def random_fact_tool():
    clear()
    print(f"{C.PURPLE}Random Fact{C.RESET}\n")
    print(f"{C.PERI}{random.choice(RANDOM_FACTS)}{C.RESET}")
    input(f"\n{C.PERI}Press Enter to return...{C.RESET}")


def public_ip_tool():
    clear()
    print(f"{C.PURPLE}My Public IP{C.RESET}")
    try:
        ip = urllib.request.urlopen("https://api.ipify.org", timeout=5).read().decode()
        print(f"\n{C.PERI}{ip}{C.RESET}")
    except Exception as e:
        print(f"\n{C.RED}Could not fetch public IP: {e}{C.RESET}")
    input(f"\n{C.PERI}Press Enter to return...{C.RESET}")


def local_info_tool():
    clear()
    print(f"{C.PURPLE}Local Device Info{C.RESET}")
    hostname = socket.gethostname()
    local_ip = "Unavailable"
    try:
        local_ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        except OSError:
            pass
        finally:
            s.close()
    print(f"\n{C.PURPLE}Hostname:{C.RESET} {C.PERI}{hostname}{C.RESET}")
    print(f"{C.PURPLE}Local IP:{C.RESET} {C.PERI}{local_ip}{C.RESET}")
    print(f"{C.PURPLE}Python:  {C.RESET} {C.PERI}{sys.version.split()[0]}{C.RESET}")
    input(f"\n{C.PERI}Press Enter to return...{C.RESET}")


def ping_tool():
    clear()
    print(f"{C.PURPLE}Ping a Host{C.RESET}")
    host = input(f"{C.PERI}Host or IP > {C.RESET}").strip()
    if not host:
        return
    if not shutil.which("ping"):
        print(f"\n{C.RED}ping not found. Install it with: pkg install inetutils{C.RESET}")
        input(f"{C.PERI}Press Enter to return...{C.RESET}")
        return
    print(f"\n{C.PURPLE}Pinging {host}...{C.RESET}\n")
    try:
        result = subprocess.run(["ping", "-c", "4", host],
                                 capture_output=True, text=True, timeout=15)
        output = result.stdout or result.stderr
        print(f"{C.PERI}{output}{C.RESET}")
    except Exception as e:
        print(f"{C.RED}Ping failed: {e}{C.RESET}")
    input(f"\n{C.PERI}Press Enter to return...{C.RESET}")


def dns_lookup_tool():
    clear()
    print(f"{C.PURPLE}Domain to IP Lookup{C.RESET}")
    domain = input(f"{C.PERI}Domain > {C.RESET}").strip()
    try:
        ip = socket.gethostbyname(domain)
        print(f"\n{C.PERI}{domain} -> {ip}{C.RESET}")
    except socket.gaierror as e:
        print(f"\n{C.RED}Lookup failed: {e}{C.RESET}")
    input(f"\n{C.PERI}Press Enter to return...{C.RESET}")


def file_hash_tool():
    clear()
    print(f"{C.PURPLE}File Hash Checker{C.RESET}")
    path = input(f"{C.PERI}File path > {C.RESET}").strip()
    if not os.path.isfile(path):
        print(f"\n{C.RED}File not found.{C.RESET}")
        input(f"{C.PERI}Press Enter to return...{C.RESET}")
        return
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    print(f"\n{C.PURPLE}SHA256:{C.RESET}")
    print(f"{C.PERI}{sha256.hexdigest()}{C.RESET}")
    input(f"\n{C.PERI}Press Enter to return...{C.RESET}")


def countdown_tool():
    clear()
    print(f"{C.PURPLE}Countdown Timer{C.RESET}")
    secs_in = input(f"{C.PERI}Seconds > {C.RESET}").strip()
    secs = int(secs_in) if secs_in.isdigit() else 10
    try:
        for remaining in range(secs, 0, -1):
            sys.stdout.write(f"\r{C.PERI}{remaining:>4}s remaining...{C.RESET}")
            sys.stdout.flush()
            time.sleep(1)
        print(f"\n\n{C.PURPLE}Time's up!{C.RESET}")
    except KeyboardInterrupt:
        pass
    input(f"\n{C.PERI}Press Enter to return...{C.RESET}")


def matrix_rain_tool():
    clear()
    cols = shutil.get_terminal_size((60, 20)).columns
    drops = [0] * cols
    chars = "01KATKLZ#$%&"
    print(f"{C.GRAY}Ctrl+C to stop{C.RESET}")
    time.sleep(1)
    try:
        while True:
            line = ""
            for i in range(cols):
                if random.random() < 0.02:
                    drops[i] = 1
                if drops[i] and random.random() < 0.5:
                    line += random.choice([C.PERI, C.PURPLE]) + random.choice(chars) + C.RESET
                else:
                    line += " "
            print(line)
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass


def more_tools_menu():
    tools = [
        ("Password Generator", gen_password_tool),
        ("Password Strength Checker", password_strength_tool),
        ("Hash Text", hash_text_tool),
        ("Base64 Encode/Decode", base64_tool),
        ("Caesar Cipher", caesar_tool),
        ("Morse Code Translator", morse_tool),
        ("Text Reverser / Leetspeak", text_tools_tool),
        ("Coin Flip", coin_flip_tool),
        ("Dice Roller", dice_roll_tool),
        ("Magic 8-Ball", eight_ball_tool),
        ("Random Number Generator", random_number_tool),
        ("Random Hacker Quote", hacker_quote_tool),
        ("Random Fact", random_fact_tool),
        ("My Public IP", public_ip_tool),
        ("Local Device Info", local_info_tool),
        ("Ping a Host", ping_tool),
        ("Domain to IP Lookup", dns_lookup_tool),
        ("File Hash Checker", file_hash_tool),
        ("Countdown Timer", countdown_tool),
        ("Matrix Rain", matrix_rain_tool),
    ]
    while True:
        clear()
        box_top()
        print(box_line("More Tools", color=C.PERI + C.BOLD))
        box_mid()
        for idx, (label, _) in enumerate(tools, start=1):
            print(box_line(f"[{idx}] {label}", color=C.PERI, align="left"))
        print(box_line("[0] Back", color=C.PERI, align="left"))
        box_bottom()
        choice = input(f"\n{C.PERI}more > {C.RESET}").strip()
        if choice == "0":
            return
        if choice.isdigit() and 1 <= int(choice) <= len(tools):
            tools[int(choice) - 1][1]()


def readme():
    clear()
    print(f"{C.PERI}{C.BOLD}KatKL - Multipurpose Cybersecurity Toolkit{C.RESET}\n")
    print(f"{C.PURPLE}KatKL is a Termux toolkit for learning and practicing basic")
    print(f"network reconnaissance on networks you own or are authorized to test.{C.RESET}\n")
    print(f"{C.PURPLE}Features:")
    print(f"  - Local network port scanning")
    print(f"  - Device / host discovery")
    print(f"  - YouTube-to-ASCII dot animation renderer{C.RESET}\n")
    print(f"{C.RED}Only scan networks you own or have explicit permission to test.{C.RESET}")
    print(f"{C.PURPLE}Unauthorized scanning may be illegal where you live.{C.RESET}\n")
    print(f"{C.GRAY}Built for educational and cybersecurity learning purposes.{C.RESET}")
    input(f"\n{C.PERI}Press Enter to return...{C.RESET}")


def main():
    compiling_animation(2.5)
    main_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear()
        print(f"{C.PERI}Exiting KatKL...{C.RESET}")
        sys.exit(0)
