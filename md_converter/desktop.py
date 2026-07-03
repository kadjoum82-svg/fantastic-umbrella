from __future__ import annotations

import socket
import threading
import webbrowser

from .webapp.app import create_app


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _lan_ip() -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        try:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
        except OSError:
            return "127.0.0.1"


def main() -> None:
    app = create_app()
    port = _free_port()
    local_url = f"http://127.0.0.1:{port}/"
    lan_url = f"http://{_lan_ip()}:{port}/"

    print("md-converter est prêt.")
    print(f"  Sur cette machine       : {local_url}")
    print(f"  Depuis votre téléphone  : {lan_url}  (même réseau Wi-Fi)")
    print("  Ctrl+C pour quitter.")

    threading.Timer(1.0, lambda: webbrowser.open(local_url)).start()
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
