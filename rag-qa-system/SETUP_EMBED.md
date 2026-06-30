# Python Embedded Portable Setup Guide

You only need to do this **once** before distributing the project.  
After setup, classmates just double-click `start.bat`.

---

## Step 1: Download Python Embeddable

Go to: https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip

> Use Python 3.11.9 (stable, widely compatible).  
> If your classmates use 32-bit Windows, download `python-3.11.9-embed-win32.zip` instead.

---

## Step 2: Extract to Project

Extract the zip directly into:

```
rag-qa-system\python-embed\
```

The result should look like:

```
rag-qa-system\python-embed\
    python.exe
    python311._pth
    python311.zip
    ...
```

---

## Step 3: Edit `python311._pth` (CRITICAL)

Open `python-embed\python311._pth` with Notepad.

**Original content:**
```
python311.zip
.
# Uncomment to run site.main() automatically
#import site
```

**Change it to:**
```
python311.zip
.
Lib\site-packages
import site
```

> `import site` enables site-packages (required for pip-installed libs).  
> `Lib\site-packages` ensures pip can install packages to the correct location.

---

## Step 4: Download `get-pip.py`

Download from: https://bootstrap.pypa.io/get-pip.py

Save it **directly into** `rag-qa-system\python-embed\`:

```
rag-qa-system\python-embed\
    python.exe
    python311._pth
    get-pip.py          <-- put here
    ...
```

---

## Step 5: Install pip for Embedded Python

Open CMD in `rag-qa-system\` and run:

```bat
.\python-embed\python.exe .\python-embed\get-pip.py
```

Wait for pip to install. Then verify:

```bat
.\python-embed\python.exe -m pip --version
```

> Once pip is installed, you can delete `get-pip.py` or keep it for re-setup.

---

## Step 6: Verify Everything Works

```bat
.\python-embed\python.exe -m pip install --only-binary :all: -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
.\python-embed\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload
```

If both succeed, you're good to go. Give the whole folder to your classmates.

---

## Directory After Full Setup

```
rag-qa-system/
    python-embed/
        python.exe
        python311._pth       (edited: import site + Lib\site-packages)
        Scripts/
            pip.exe
        Lib\site-packages/   (populated after pip install)
    .venv/                   (NOT used anymore - can delete)
    start.bat
    requirements.txt
    .env
    app/
    data/
```

> The old `.venv/` directory is no longer needed. The embedded Python inside `python-embed/` replaces it entirely.

---

## Why This Works On Any Windows PC

| Problem | Without Embed | With Embed |
|---------|-------------|-----------|
| No Python installed | Fails | Works - Python is included |
| Wrong Python version | Fails | Works - version is pinned |
| PATH not configured | Fails | Works - all paths hardcoded |
| System Python polluted by other projects | Unpredictable | Works - fully isolated |
| pip install fails (no C++ compiler) | Fails | `--only-binary :all:` avoids all compilation |