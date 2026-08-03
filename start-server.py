#!/usr/bin/env python3

import http.server
import socket
import socketserver
import threading
import os
import sys

# Configurazioni
HOST = ""            # ascolta su tutte le interfacce
PORT = 8000          # cambia se vuoi una porta diversa
SITE_DIR = "site"    # cartella da servire (creala se non esiste)

class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Serve i file dalla directory SITE_DIR se esiste
        super().__init__(*args, directory=(SITE_DIR if os.path.isdir(SITE_DIR) else None), **kwargs)

    def log_message(self, format, *args):
        # Opzionale: puoi stampare i log qui
        pass

def find_local_ip():
    # Cerca l'IP locale usato per la rete senza dover aprire interfacce manualmente
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = "127.0.0.1"
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        pass
    finally:
        s.close()
    return ip

def ensure_site_dir():
    if not os.path.isdir(SITE_DIR):
        os.makedirs(SITE_DIR, exist_ok=True)
        index_path = os.path.join(SITE_DIR, "index.html")
        with open(index_path, "w") as f:
            f.write(
                "<html><body><h1>Sito locale in esecuzione</h1>"
                "<p>Questo è un sito statico servito da Python.</p>"
                "</body></html>"
            )

def main():
    ensure_site_dir()

    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()

    local_ip = find_local_ip()
    print(f"Sito locale in esecuzione su http://{local_ip}:{PORT}/ (servendo la cartella: {SITE_DIR})")
    print("Per fermare, digita 'stop' e premi Invio (o premi Ctrl+C).")

    try:
        while True:
            cmd = input()
            if cmd.strip().lower() in ("stop", "quit", "exit", "end"):
                break
    except KeyboardInterrupt:
        pass

    print("Spegnimento in corso...")
    httpd.shutdown()
    httpd.server_close()
    server_thread.join()
    print("Server arrestato.")

if __name__ == "__main__":
    main()