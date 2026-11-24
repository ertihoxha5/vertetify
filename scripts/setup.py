"""Create the ignored local environment once. Keep existing settings on retries."""
from pathlib import Path
from secrets import token_urlsafe

root = Path(__file__).resolve().parents[1]
template = (root / ".env.example").read_text()
try:
    with (root / ".env").open("x", encoding="utf-8") as file:
        file.write(template.replace("POSTGRES_PASSWORD=\n", f"POSTGRES_PASSWORD={token_urlsafe(32)}\n"))
except FileExistsError:
    print("Existing .env retained.")
else:
    print("Local .env created.")
