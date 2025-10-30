# PS5-Payload-Sender-Y2JB-
The PS5 Payload Sender (Y2JB) is a Python automation tool (Flask/CLI) for remote payload delivery to PS5 consoles. It scans the local network on port 50000 (Y2JB listener) in Full Auto mode or handles manual sends.

# 🎮 PS5 Payload Sender (Integracja Y2JB)

Serwer w Pythonie/Flask do wysyłania payloadów do konsoli PlayStation 5 po uruchomieniu **Y2JB**. Serwer jest dostępny z Twojego komputera, telefonu lub tabletu w sieci lokalnej.

### 1. Wymagania i instalacja

Musisz mieć zainstalowany **Python 3** oraz bibliotekę **Flask**.

1.  **Instalacja Flask:**
    Otwórz terminal (lub Wiersz polecenia/PowerShell) i zainstaluj wymagane pakiety:
    ```bash
    pip install Flask
    ```

2.  **Wymagane Pliki i Struktura:**
    Musisz pobrać kluczowe pliki z oryginalnego repozytorium **Gezine/Y2JB** i umieścić je we właściwych miejscach. Wszystkie pliki muszą znajdować się w jednym katalogu.

    | Plik / Katalog | Źródło (Gezine/Y2JB) |
    | :--- | :--- |
    | **`run_server.py`** | Twój zmodyfikowany skrypt serwera. |
    | **`payload_sender.py`** | Pobierz ten plik. |
    | **`payloads/`** | Utwórz katalog. |
    | **`payloads/helloworld.js`** | Pobierz ten plik (lub inny `.js`). |

### 2. Edycja konfiguracji

Jeśli zmienisz nazwy lub ścieżki plików, możesz je edytować na początku pliku **`run_server.py`**:

```python
PAYLOAD_SENDER_PATH = "payload_sender.py" 
PAYLOAD_FILE = "payloads/helloworld.js" 
SCAN_PORT = 50000 # Port nasłuchu na PS5
