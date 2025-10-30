# PS5-Payload-Sender-Y2JB-
The PS5 Payload Sender (Y2JB) is a Python automation tool (Flask/CLI) for remote payload delivery to PS5 consoles. It scans the local network on port 50000 (Y2JB listener) in Full Auto mode or handles manual sends.

# 💻 PS5 Payload Sender (Integracja Y2JB)

The PS5 Payload Sender (Y2JB) to narzędzie automatyzujące w Pythonie (Flask/CLI) do zdalnego wysyłania payloadów do konsoli PS5. Skanuje sieć lokalną na porcie 50000 (nasłuch Y2JB) lub obsługuje ręczne wysyłki.

---

### 1. Wymagania i instalacja

Musisz mieć zainstalowany **Python 3** oraz bibliotekę **Flask**.

1.  **Instalacja Flask:**
    Otwórz terminal (lub Wiersz polecenia/PowerShell) i zainstaluj wymagane pakiety:
    ```bash
    pip install Flask
     ```
     jeżeli nie działa to pierwsze to używamy tego:
    ```bash
    python -m pip install Flask
    ```

2.  **Wymagane Pliki i Struktura:**
    Pobierz kluczowe pliki z oryginalnego repozytorium [**Gezine/Y2JB**](https://github.com/Gezine/Y2JB) i umieść je we właściwych miejscach. Wszystkie pliki muszą znajdować się w jednym katalogu.

    | Plik / Katalog | Źródło (Gezine/Y2JB) |
    | :--- | :--- |
    | **`run_server.py`** | Twój zmodyfikowany skrypt serwera. |
    | **`payload_sender.py`** | Pobierz ten plik z repozytorium. |
    | **`payloads/`** | Utwórz katalog. |
    | **`payloads/helloworld.js`** | Pobierz ten plik (lub inny `.js` payload). |

---

### 2. Edycja konfiguracji

Jeśli zmienisz nazwy lub ścieżki plików, lub chcesz zmienić domyślny język, edytuj następujące linie na początku pliku **`run_server.py`**:

```python
PAYLOAD_SENDER_PATH = "payload_sender.py" 
PAYLOAD_FILE = "payloads/helloworld.js" 
SCAN_PORT = 50000 
SCAN_TIMEOUT = 1
DEFAULT_LANG = 'en'  # Zmień na 'pl' jeśli ma być domyślny
SUPPORTED_LANGS = ['pl', 'en']
```

Otwórz Terminal: Użyj PowerShell, Wiersza Polecenia lub Terminala systemowego.

Przejdź do Katalogu Projektu:

```Bash
cd C:\ścieżka\do\folderu\z\plikami
```
Uruchom Skrypt: Użyj głównego pliku run_server.py:

```Bash
python run_server.py
```

<img width="602" height="709" alt="obraz" src="https://github.com/user-attachments/assets/5babf6f7-4997-4aba-9089-8b342340a904" />





# 💻 PS5 Payload Sender (Y2JB Integration)

The PS5 Payload Sender (Y2JB) is a Python automation tool (Flask/CLI) for remote payload delivery to PS5 consoles. It scans the local network on port 50000 (Y2JB listener) in Full Auto mode or handles manual sends.

---

### 1. Requirements and Installation

You must have **Python 3** and the **Flask** library installed.

1.  **Flask Installation:**
    Open your terminal (or Command Prompt/PowerShell) and use the following command to install the required packages:
    ```bash
    pip install Flask
    ```
    If the command above returns an error (`pip is not recognized`), use the alternative method:
    ```bash
    python -m pip install Flask
    ```

2.  **Required Files and Structure:**
    You must download essential files from the original [**Gezine/Y2JB**](https://github.com/Gezine/Y2JB) repository and place them correctly. All files must reside within the same main project folder.

    | File / Directory | Source (Gezine/Y2JB) |
    | :--- | :--- |
    | **`run_server.py`** | Your modified server script. |
    | **`payload_sender.py`** | Download this file from the repository. |
    | **`payloads/`** | Create this directory. |
    | **`payloads/helloworld.js`** | Download this file. |

---

### 2. Configuration Editing

If you change file names, paths, or want to modify the default language, edit the following lines at the beginning of the **`run_server.py`** file:

```python
PAYLOAD_SENDER_PATH = "payload_sender.py" 
PAYLOAD_FILE = "payloads/helloworld.js" 
SCAN_PORT = 50000 
SCAN_TIMEOUT = 1
DEFAULT_LANG = 'en'  # Change to 'pl' for Polish default
SUPPORTED_LANGS = ['pl', 'en']
```


Open Terminal: Use PowerShell, Command Prompt, or your system Terminal.

Navigate to Project Directory:

```bash
cd C:\path\to\your\files\folder
```

Run the Script: Use the main file run_server.py:
```bash
python run_server.py
```
<img width="604" height="704" alt="obraz" src="https://github.com/user-attachments/assets/9aa66263-837d-4831-b1a8-5a49f2cff63b" />

