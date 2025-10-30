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
    Musisz pobrać kluczowe pliki z oryginalnego repozytorium [**Gezine/Y2JB**](https://github.com/Gezine/Y2JB) i umieścić je we właściwych miejscach. Wszystkie pliki muszą znajdować się w jednym katalogu.

    | Plik / Katalog | Źródło (Gezine/Y2JB) |
    | :--- | :--- |
    | **`run_server.py`** | Twój zmodyfikowany skrypt serwera. |
    | **`payload_sender.py`** | Pobierz ten plik z repozytorium. |
    | **`payloads/`** | Utwórz katalog. |
    | **`payloads/helloworld.js`** | Pobierz ten plik (lub inny `.js` payload). |

### 2. Edycja konfiguracji

Jeśli zmienisz nazwy lub ścieżki plików, lub chcesz zmienić domyślny język, edytuj następujące linie na początku pliku **`run_server.py`**:

```python
PAYLOAD_SENDER_PATH = "payload_sender.py" 
PAYLOAD_FILE = "payloads/helloworld.js" 
SCAN_PORT = 50000 
SCAN_TIMEOUT = 1
DEFAULT_LANG = 'en'  # Zmień na 'pl' jeśli ma być domyślny
SUPPORTED_LANGS = ['pl', 'en']





# 🎮 PS5 Payload Sender (Y2JB Integration)

A Python/Flask server designed to send JavaScript payloads to your PlayStation 5 console after launching **Y2JB**. The server is accessible from your PC, phone, or tablet on your local network.

### 1. Requirements and Installation

You must have **Python 3** and the **Flask** library installed.

1.  **Flask Installation:**
    Open your terminal (or Command Prompt/PowerShell) and use the following command to install the required packages:
    ```bash
    pip install Flask
    ```

2.  **Required Files and Structure:**
    You must download essential files from the original [**Gezine/Y2JB**](https://github.com/Gezine/Y2JB) repository and place them correctly. All files must reside within the same main project folder.

    | File / Directory | Source (Gezine/Y2JB) |
    | :--- | :--- |
    | **`run_server.py`** | Your modified server script. |
    | **`payload_sender.py`** | Download this file from the repository. |
    | **`payloads/`** | Create this directory. |
    | **`payloads/helloworld.js`** | Download this file (or any other `.js` payload). |

### 2. Configuration Editing

If you change file names, paths, or want to modify the default language, edit the following lines at the beginning of the **`run_server.py`** file:

```python
PAYLOAD_SENDER_PATH = "payload_sender.py" 
PAYLOAD_FILE = "payloads/helloworld.js" 
SCAN_PORT = 50000 
SCAN_TIMEOUT = 1
DEFAULT_LANG = 'en'  # Change to 'pl' for Polish default
SUPPORTED_LANGS = ['pl', 'en']
