# P-article parser server

Receives PDFs from the app, parses them with `pdf_to_md_v2.py`, and saves each result in `output/<article name>/`:

- `article.md`: the parsed article
- `images/`: images and tables extracted from it
- a copy of the original PDF

## Setup

Requires Python 3.13.

```sh
cd backend
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Run

```sh
cd backend
.venv/bin/uvicorn server:app --host 127.0.0.1 --port 8000
```

The server has no authentication, so it only listens on this computer. Keep the `127.0.0.1` host.

## Connect the app

**Emulator:** nothing to set up. The app uses `http://10.0.2.2:8000`, which is how an emulator reaches this computer.

**Phone over USB:** forward the port and build the app with the local address:

```sh
adb reverse tcp:8000 tcp:8000
./gradlew installDebug -PparserServerUrl=http://localhost:8000
```

## Test PDF

To put the sample PDF in the Downloads folder of an emulator or connected phone:

```sh
adb push backend/samples/test-article.pdf /sdcard/Download/
```

If it doesn't appear in the file picker, restart the device or open its Files app.
