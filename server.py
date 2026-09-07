import http.server
import socketserver
import json
import os
import uuid
import datetime

PORT = 8081
DATA_FILE = "incidencias.json"


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/incidencias"):
            self.send_json(self.load_data())
            return
        super().do_GET()

    def do_POST(self):
        if self.path == "/api/incidencias":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                text = body.decode("utf-8")
            except UnicodeDecodeError:
                text = body.decode("latin-1")
            try:
                inc = json.loads(text)
            except json.JSONDecodeError:
                self.send_json({"ok": False, "error": "Datos inválidos"}, 400)
                return

            inc["id"] = uuid.uuid4().hex
            inc["creado"] = datetime.datetime.now().isoformat()

            data = self.load_data()
            data.append(inc)
            self.save_data(data)

            self.send_json({"ok": True, "incidencia": inc})
            return

        self.send_error(405)

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return []
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

    def save_data(self, data):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def send_json(self, obj, status=200):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)


with socketserver.ThreadingTCPServer(("", PORT), Handler) as httpd:
    print("Servidor de tipificación corriendo en: http://localhost:" + str(PORT))
    print("Abre la app en http://localhost:" + str(PORT) + "/index.html")
    httpd.serve_forever()