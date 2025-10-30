from flask import Flask, render_template_string, request, jsonify
import threading
import time
import os
import sys
import ipaddress

APP = Flask(__name__)

PAYLOAD_SENDER_PATH = "payload_sender.py"
PAYLOAD_FILE = "payloads/helloworld.js"
SCAN_PORT = 50000
SCAN_TIMEOUT = 1
DEFAULT_LANG = 'en'
SUPPORTED_LANGS = ['pl', 'en']

LANG = {
    'pl': {
        'title': 'Ps5 Payload sender Y2JB',
        'h1': 'PS5 Payload Sender',
        'subtitle': 'Payload sender - Y2JB Integration',
        'settings': 'Konfiguracja',
        'payload': 'Plik payload',
        'target_port': 'Port docelowy',
        'network_auto': 'Wykryta sieć',
        'actions': 'Akcje',
        'manual_ip': 'Adres IP',
        'placeholder_ip': 'np. {base}.22',
        'btn_scan': 'Automatyczne skanowanie',
        'btn_send': 'Wyślij payload',
        'status': 'Status operacji',
        'status_waiting': 'Gotowy do pracy',
        'status_running': 'Przetwarzanie...',
        'status_success': '✅ Zakończono pomyślnie',
        'status_error': '❌ Wystąpił błąd',
        'alert_ip_missing': 'Wprowadź adres IP!',
        'alert_task_error': 'Błąd uruchamiania:',
        'log_start_scan': '🔍 Skanowanie sieci {base}.* (port {port}, timeout: {timeout}s)\n',
        'log_found_ip': '✅ Wykryto otwarty port {port} na {host}\n',
        'log_scan_end_found': '✅ Znaleziono cel: {host}\n',
        'log_scan_end_not_found': '❌ Nie znaleziono otwartego portu\n',
        'log_try_send': '📦 Wysyłanie \'{file}\' → {host}:{port}\n',
        'log_success_sent': '✅ Wysłano {bytes} bajtów do {host}\n',
        'log_err_file_not_found': '❌ Nie znaleziono pliku: {file}\n',
        'log_err_conn_refused': '❌ Połączenie odrzucone przez {host}:{port}\n',
        'log_err_no_port': '❌ Brak otwartego portu - uruchom Y2JB na PS5\n',
        'log_err_mode_ip': '❌ Nieprawidłowy adres IP\n',
        'log_err_critical': '❌ Błąd krytyczny: {e}\n',
        'using_payload_sender': '🔧 Używam payload_sender.py\n',
        'payload_sender_not_found': '⚠️  Nie znaleziono payload_sender.py\n'
    },
    'en': {
        'title': 'Ps5 Payload sender Y2JB',
        'h1': 'PS5 Payload Sender',
        'subtitle': 'Payload sender - Y2JB Integration',
        'settings': 'Configuration',
        'payload': 'Payload file',
        'target_port': 'Target port',
        'network_auto': 'Detected network',
        'actions': 'Actions',
        'manual_ip': 'IP Address',
        'placeholder_ip': 'e.g., {base}.22',
        'btn_scan': 'Auto scan',
        'btn_send': 'Send payload',
        'status': 'Operation status',
        'status_waiting': 'Ready',
        'status_running': 'Processing...',
        'status_success': '✅ Completed successfully',
        'status_error': '❌ Error occurred',
        'alert_ip_missing': 'Enter IP address!',
        'alert_task_error': 'Startup error:',
        'log_start_scan': '🔍 Scanning network {base}.* (port {port}, timeout: {timeout}s)\n',
        'log_found_ip': '✅ Found open port {port} on {host}\n',
        'log_scan_end_found': '✅ Target found: {host}\n',
        'log_scan_end_not_found': '❌ No open port found\n',
        'log_try_send': '📦 Sending \'{file}\' → {host}:{port}\n',
        'log_success_sent': '✅ Sent {bytes} bytes to {host}\n',
        'log_err_file_not_found': '❌ File not found: {file}\n',
        'log_err_conn_refused': '❌ Connection refused by {host}:{port}\n',
        'log_err_no_port': '❌ No open port - start Y2JB on PS5\n',
        'log_err_mode_ip': '❌ Invalid IP address\n',
        'log_err_critical': '❌ Critical error: {e}\n',
        'using_payload_sender': '🔧 Using payload_sender.py\n',
        'payload_sender_not_found': '⚠️  payload_sender.py not found\n'
    }
}

def get_local_network_base():
    """Auto-detect local network subnet"""
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        base = '.'.join(local_ip.split('.')[:3])
        return base
    except Exception as e:
        print(f"[!] Auto-detect error: {e} - fallback to 192.168.1")
        return "192.168.1"

NETWORK_BASE = get_local_network_base()
STATUS = {
    "running": False,
    "output": "",
    "code": None,
    "lang": DEFAULT_LANG
}

if not os.path.isfile(PAYLOAD_FILE):
    print(f"[WARN] File {PAYLOAD_FILE} doesn't exist! Create: mkdir -p payloads/")

if not os.path.isfile(PAYLOAD_SENDER_PATH):
    print(f"[WARN] {PAYLOAD_SENDER_PATH} not found!")

def is_valid_ip(ip):
    """Validate IP address format"""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def check_port(host, port, timeout):
    """Check if port is open on host"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        sock.close()
        return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def scan_network(L):
    """Scan subnet for open SCAN_PORT"""
    global STATUS
    detected_ip = None
    STATUS["output"] += L['log_start_scan'].format(base=NETWORK_BASE, port=SCAN_PORT, timeout=SCAN_TIMEOUT)

    threads = []
    found_event = threading.Event()

    def worker(ip_suffix):
        nonlocal detected_ip
        host = f"{NETWORK_BASE}.{ip_suffix}"

        if found_event.is_set():
            return

        if check_port(host, SCAN_PORT, SCAN_TIMEOUT):
            if not found_event.is_set():
                detected_ip = host
                found_event.set()
                STATUS["output"] += L['log_found_ip'].format(port=SCAN_PORT, host=host)

    for i in range(1, 255):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join(timeout=SCAN_TIMEOUT + 0.5)

    if detected_ip:
        STATUS["output"] += L['log_scan_end_found'].format(host=detected_ip)
    else:
        STATUS["output"] += L['log_scan_end_not_found']

    return detected_ip

def send_payload(file_path, host, port, L):
    """Send payload using payload_sender.py"""
    global STATUS
    STATUS["output"] += L['log_try_send'].format(file=file_path, host=host, port=port)

    try:
        if not os.path.isfile(file_path):
            STATUS["output"] += L['log_err_file_not_found'].format(file=file_path)
            STATUS["code"] = 1
            return False

        if not os.path.isfile(PAYLOAD_SENDER_PATH):
            STATUS["output"] += L['payload_sender_not_found']
            STATUS["code"] = 1
            return False

        STATUS["output"] += L['using_payload_sender']

        # Call payload_sender.py: python payload_sender.py <host> <port> <file>
        import subprocess
        result = subprocess.run(
            [sys.executable, PAYLOAD_SENDER_PATH, host, str(port), file_path],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            # Get file size
            with open(file_path, 'rb') as f:
                payload_size = len(f.read())

            if result.stdout:
                STATUS["output"] += result.stdout

            STATUS["output"] += L['log_success_sent'].format(bytes=payload_size, host=host)
            STATUS["code"] = 0
            return True
        else:
            if result.stderr:
                STATUS["output"] += f"❌ Error: {result.stderr}\n"
            STATUS["code"] = 4
            return False

    except subprocess.TimeoutExpired:
        STATUS["output"] += L['log_err_conn_refused'].format(host=host, port=port)
        STATUS["code"] = 3
        return False
    except FileNotFoundError:
        STATUS["output"] += L['log_err_file_not_found'].format(file=file_path)
        STATUS["code"] = 1
        return False
    except Exception as e:
        STATUS["output"] += L['log_err_critical'].format(e=str(e))
        STATUS["code"] = 4
        return False

def run_task(mode, ip_host=None, lang_code=DEFAULT_LANG):
    """Main task runner for scan or send operations"""
    global STATUS
    L = LANG.get(lang_code, LANG[DEFAULT_LANG])

    STATUS["running"] = True
    STATUS["output"] = ""
    STATUS["code"] = None
    STATUS["lang"] = lang_code

    try:
        if mode == 'scan':
            detected_ip = scan_network(L)
            if detected_ip:
                send_payload(PAYLOAD_FILE, detected_ip, SCAN_PORT, L)
            else:
                STATUS["output"] += L['log_err_no_port']
                STATUS["code"] = 5
        elif mode == 'send' and ip_host and is_valid_ip(ip_host):
            send_payload(PAYLOAD_FILE, ip_host, SCAN_PORT, L)
        else:
            STATUS["output"] += L['log_err_mode_ip']
            STATUS["code"] = 6
    except Exception as e:
        STATUS["output"] += L['log_err_critical'].format(e=str(e))
        STATUS["code"] = 99

    STATUS["running"] = False

HTML_TEMPLATE = """
<!doctype html>
<html lang="{{ L.lang }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ L['title'] }}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #0a0e27;
            color: #e4e8f0;
            min-height: 100vh;
            padding: 15px;
            position: relative;
            overflow-x: hidden;
        }

        .bg-animation {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            overflow: hidden;
        }

        .bg-animation::before {
            content: '';
            position: absolute;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.15) 0%, transparent 50%),
                        radial-gradient(circle at 80% 80%, rgba(138, 43, 226, 0.15) 0%, transparent 50%),
                        radial-gradient(circle at 40% 90%, rgba(72, 61, 139, 0.15) 0%, transparent 50%);
            animation: bgMove 20s ease infinite;
        }

        @keyframes bgMove {
            0%, 100% { transform: translate(0, 0) rotate(0deg); }
            33% { transform: translate(-5%, -5%) rotate(120deg); }
            66% { transform: translate(5%, 5%) rotate(240deg); }
        }

        .particle {
            position: fixed;
            width: 3px;
            height: 3px;
            background: rgba(138, 43, 226, 0.5);
            border-radius: 50%;
            animation: float 15s infinite;
            z-index: -1;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0) translateX(0); opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { transform: translateY(-100vh) translateX(100px); opacity: 0; }
        }

        .container {
            max-width: 1000px;
            margin: 0 auto;
            position: relative;
            z-index: 1;
        }

        .lang-switch {
            position: fixed;
            top: 15px;
            right: 15px;
            background: rgba(26, 31, 58, 0.8);
            backdrop-filter: blur(10px);
            padding: 8px 16px;
            border-radius: 20px;
            border: 1px solid rgba(138, 43, 226, 0.3);
            display: flex;
            gap: 10px;
            align-items: center;
            z-index: 1000;
            font-size: 0.85rem;
        }

        .lang-switch a {
            color: #a0aec0;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
            padding: 4px 8px;
            border-radius: 8px;
        }

        .lang-switch a:hover {
            color: #667eea;
            background: rgba(102, 126, 234, 0.1);
        }

        .lang-switch span {
            color: rgba(255,255,255,0.2);
            font-size: 0.7rem;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 40px 25px;
            background: rgba(26, 31, 58, 0.4);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            border: 1px solid rgba(138, 43, 226, 0.3);
            box-shadow: 0 15px 50px rgba(138, 43, 226, 0.2);
            position: relative;
            overflow: hidden;
            animation: slideDown 0.8s cubic-bezier(0.16, 1, 0.3, 1);
        }

        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .header h1 {
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: titlePulse 3s ease-in-out infinite;
        }

        @keyframes titlePulse {
            0%, 100% { filter: brightness(1); }
            50% { filter: brightness(1.2); }
        }

        .header p {
            font-size: 1rem;
            opacity: 0.7;
            font-weight: 300;
        }

        .card {
            background: rgba(26, 31, 58, 0.4);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(138, 43, 226, 0.3);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            animation: fadeInUp 0.8s ease-out backwards;
        }

        .card:nth-child(2) { animation-delay: 0.1s; }
        .card:nth-child(3) { animation-delay: 0.2s; }
        .card:nth-child(4) { animation-delay: 0.3s; }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .card:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 45px rgba(138, 43, 226, 0.3);
            border-color: rgba(138, 43, 226, 0.5);
        }

        .card h3 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.3rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .card h3::before {
            content: '';
            width: 3px;
            height: 20px;
            background: linear-gradient(180deg, #667eea, #764ba2);
            border-radius: 2px;
        }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }

        .info-item {
            background: rgba(102, 126, 234, 0.05);
            padding: 16px;
            border-radius: 10px;
            border: 1px solid rgba(102, 126, 234, 0.2);
            transition: all 0.3s ease;
        }

        .info-item:hover {
            background: rgba(102, 126, 234, 0.1);
            transform: translateY(-2px);
        }

        .info-item label {
            display: block;
            font-size: 0.8rem;
            color: #9ca3af;
            margin-bottom: 6px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .info-item .value {
            font-size: 1.1rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .input-group {
            margin-bottom: 20px;
        }

        .input-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #9ca3af;
            font-size: 0.9rem;
        }

        input[type=text] {
            width: 100%;
            padding: 14px 16px;
            border: 2px solid rgba(102, 126, 234, 0.3);
            border-radius: 10px;
            background: rgba(26, 31, 58, 0.6);
            color: #e4e8f0;
            font-size: 1rem;
            transition: all 0.3s ease;
            font-family: 'Inter', sans-serif;
        }

        input[type=text]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .button-group {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }

        button {
            padding: 16px 24px;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: 'Inter', sans-serif;
            position: relative;
            overflow: hidden;
        }

        button::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }

        button:hover::before {
            width: 300px;
            height: 300px;
        }

        #scan_btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }

        #scan_btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 35px rgba(102, 126, 234, 0.5);
        }

        #send_btn {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            box-shadow: 0 8px 25px rgba(245, 87, 108, 0.4);
        }

        #send_btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 35px rgba(245, 87, 108, 0.5);
        }

        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none !important;
        }

        .console {
            background: #0d1117;
            color: #58a6ff;
            padding: 20px;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            white-space: pre-wrap;
            height: 350px;
            overflow-y: auto;
            border-radius: 10px;
            border: 1px solid rgba(88, 166, 255, 0.2);
            box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.5);
        }

        .console::-webkit-scrollbar {
            width: 8px;
        }

        .console::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.2);
        }

        .console::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, #667eea, #764ba2);
            border-radius: 10px;
        }

        #status_indicator {
            padding: 14px 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            font-weight: 600;
            text-align: center;
            transition: all 0.3s ease;
        }

        .status-waiting {
            background: rgba(102, 126, 234, 0.2);
            color: #667eea;
            border: 1px solid rgba(102, 126, 234, 0.3);
        }

        .status-running {
            background: rgba(251, 191, 36, 0.2);
            color: #fbbf24;
            border: 1px solid rgba(251, 191, 36, 0.3);
            animation: statusPulse 2s ease-in-out infinite;
        }

        @keyframes statusPulse {
            0%, 100% { box-shadow: 0 0 15px rgba(251, 191, 36, 0.2); }
            50% { box-shadow: 0 0 30px rgba(251, 191, 36, 0.4); }
        }

        .status-success {
            background: rgba(34, 197, 94, 0.2);
            color: #22c55e;
            border: 1px solid rgba(34, 197, 94, 0.3);
            animation: successPulse 0.5s ease-out;
        }

        @keyframes successPulse {
            0% { transform: scale(0.95); }
            50% { transform: scale(1.03); }
            100% { transform: scale(1); }
        }

        .status-error {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.3);
            animation: errorShake 0.4s ease-out;
        }

        @keyframes errorShake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-8px); }
            75% { transform: translateX(8px); }
        }

        .spinner {
            display: inline-block;
            width: 14px;
            height: 14px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-top-color: white;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin-left: 8px;
            vertical-align: middle;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
            body {
                padding: 10px;
            }

            .header {
                padding: 30px 20px;
                margin-bottom: 20px;
            }

            .header h1 {
                font-size: 2rem;
            }

            .header p {
                font-size: 0.9rem;
            }

            .card {
                padding: 20px;
            }

            .lang-switch {
                top: 10px;
                right: 10px;
                padding: 6px 12px;
                font-size: 0.75rem;
            }

            .button-group {
                grid-template-columns: 1fr;
            }

            .info-grid {
                grid-template-columns: 1fr;
            }

            .console {
                height: 250px;
                font-size: 0.8rem;
            }
        }
    </style>
</head>
<body>
    <div class="bg-animation"></div>

    <div class="particle" style="left: 10%; animation-delay: 0s;"></div>
    <div class="particle" style="left: 25%; animation-delay: 2s;"></div>
    <div class="particle" style="left: 40%; animation-delay: 4s;"></div>
    <div class="particle" style="left: 55%; animation-delay: 1s;"></div>
    <div class="particle" style="left: 70%; animation-delay: 3s;"></div>
    <div class="particle" style="left: 85%; animation-delay: 5s;"></div>

    <div class="lang-switch">
        <a href="?lang=pl">🇵🇱 PL</a>
        <span>|</span>
        <a href="?lang=en">🇬🇧 EN</a>
    </div>

    <div class="container">
        <div class="header">
            <h1>{{ L['h1'] }}</h1>
            <p>{{ L['subtitle'] }}</p>
        </div>

        <div class="card">
            <h3>⚙️ {{ L['settings'] }}</h3>
            <div class="info-grid">
                <div class="info-item">
                    <label>{{ L['payload'] }}</label>
                    <div class="value">{{ payload_file }}</div>
                </div>
                <div class="info-item">
                    <label>{{ L['target_port'] }}</label>
                    <div class="value">{{ scan_port }}</div>
                </div>
                <div class="info-item">
                    <label>{{ L['network_auto'] }}</label>
                    <div class="value">{{ network_base }}.*</div>
                </div>
            </div>
        </div>

        <div class="card">
            <h3>🎮 {{ L['actions'] }}</h3>

            <div class="input-group">
                <label for="ip_host">{{ L['manual_ip'] }}</label>
                <input type="text" id="ip_host" placeholder="{{ L['placeholder_ip'].format(base=network_base) }}">
            </div>

            <div class="button-group">
                <button onclick="startTask('scan')" id="scan_btn">
                    🔍 {{ L['btn_scan'] }}
                </button>

                <button onclick="startTask('send')" id="send_btn">
                    ▶️ {{ L['btn_send'] }}
                </button>
            </div>
        </div>

        <div class="card">
            <h3>📊 {{ L['status'] }}</h3>
            <div id="status_indicator" class="status-waiting">{{ L['status_waiting'] }}</div>
            <div class="console" id="output"></div>
        </div>
    </div>

    <script>
        const L = {{ L | tojson }};
        const outputDiv = document.getElementById('output');
        const statusDiv = document.getElementById('status_indicator');
        const scanBtn = document.getElementById('scan_btn');
        const sendBtn = document.getElementById('send_btn');
        let isRunning = false;
        let statusInterval = null;

        function updateStatus() {
            if (!isRunning && statusInterval !== null) {
                clearInterval(statusInterval);
                statusInterval = null;
                return;
            }

            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    outputDiv.textContent = data.output;
                    outputDiv.scrollTop = outputDiv.scrollHeight;

                    if (data.running) {
                        statusDiv.innerHTML = L['status_running'] + ' <span class="spinner"></span>';
                        statusDiv.className = 'status-running';
                    } else if (data.code !== null) {
                        isRunning = false;
                        if (data.code === 0) {
                            statusDiv.textContent = L['status_success'];
                            statusDiv.className = 'status-success';
                        } else {
                            statusDiv.textContent = L['status_error'];
                            statusDiv.className = 'status-error';
                        }
                        scanBtn.disabled = false;
                        sendBtn.disabled = false;
                    }
                })
                .catch(error => {
                    console.error('Status fetch error:', error);
                    statusDiv.textContent = L['alert_task_error'];
                    statusDiv.className = 'status-error';
                    isRunning = false;
                    scanBtn.disabled = false;
                    sendBtn.disabled = false;
                });
        }

        function startTask(mode) {
            if (isRunning) return;

            let ip = '';
            if (mode === 'send') {
                ip = document.getElementById('ip_host').value.trim();
                if (!ip) {
                    alert(L['alert_ip_missing']);
                    return;
                }
            }

            isRunning = true;
            scanBtn.disabled = true;
            sendBtn.disabled = true;
            statusDiv.innerHTML = L['status_running'] + ' <span class="spinner"></span>';
            statusDiv.className = 'status-running';
            outputDiv.textContent = '';

            fetch('/run_task', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mode: mode, ip: ip, lang: L.lang })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (statusInterval === null) {
                        statusInterval = setInterval(updateStatus, 1000);
                    }
                } else {
                    alert(L['alert_task_error'] + ' ' + data.message);
                    isRunning = false;
                    scanBtn.disabled = false;
                    sendBtn.disabled = false;
                    statusDiv.className = 'status-error';
                }
            })
            .catch(error => {
                console.error('Task start error:', error);
                alert('Critical server error');
                isRunning = false;
                scanBtn.disabled = false;
                sendBtn.disabled = false;
                statusDiv.className = 'status-error';
            });
        }

        document.getElementById('ip_host').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                startTask('send');
            }
        });
    </script>
</body>
</html>
"""

@APP.route('/')
def index():
    """Main page with interface"""
    lang_code = request.args.get('lang', DEFAULT_LANG)
    if lang_code not in SUPPORTED_LANGS:
        lang_code = DEFAULT_LANG
        
    L = LANG[lang_code].copy()
    L['lang'] = lang_code
    
    return render_template_string(HTML_TEMPLATE, 
        payload_file=PAYLOAD_FILE, 
        scan_port=SCAN_PORT, 
        network_base=NETWORK_BASE,
        L=L
    )

@APP.route('/run_task', methods=['POST'])
def handle_run_task():
    """Endpoint for starting scan or send task"""
    data = request.json
    mode = data.get('mode')
    ip = data.get('ip')
    lang_code = data.get('lang', DEFAULT_LANG)
    
    threading.Thread(target=run_task, args=(mode, ip, lang_code)).start()
    
    return jsonify({"success": True, "message": "Task started"})

@APP.route('/status')
def get_status():
    """Endpoint for status polling (AJAX)"""
    return jsonify(STATUS)

if __name__ == '__main__':
    # Flask runs only the main thread, the server logic runs in the main thread
    # The scan/send operation is run in a separate thread (run_task)
    print("----------------------------------------------------------")
    print(f"Server started on http://127.0.0.1:5000 (Network base: {NETWORK_BASE})")
    print(f"Target payload: {PAYLOAD_FILE}")
    print(f"Target port: {SCAN_PORT}")
    print("----------------------------------------------------------")
    APP.run(debug=False, host='0.0.0.0')
