# Setup Guide
Make sure [uv](https://docs.astral.sh/uv/getting-started/installation/) is installed on your system. You can check by running this comment:

```bash
# Linux/MacOS
uv --verison
```
```ps1
# Windows
uv --version
```

Then, run the project:

> [!NOTE]
> Project requires **[Python 3.11](https://www.python.org/downloads/)** to be able
> to run **[PyGame](https://www.pygame.org/news)** since they didn't support
> latest Python version yet at the time we working on the assignment.

```bash
# Linux/MacOS
uv sync --frozen --no-cache
uv run ./main.py
```
```ps1
# Windows
uv sync --frozen --no-cache
uv run .\main.py
```
