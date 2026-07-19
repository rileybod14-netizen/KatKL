
import os
import sys
import time
import random
import socket
import shutil
import threading
import subprocess

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
