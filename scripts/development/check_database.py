"""Database connectivity verification script (FCD-03 §7.3)."""

import asyncio
import sys
from pathlib import Path

# Add apps/api/src to sys.path so menu_it can be imported
api_src = Path(__file__).resolve().parents[2] / "apps" / "api" / "src"
if str(api_src) not in sys.path:
    sys.path.insert(0, str(api_src))

from sqlalchemy import text
from menu_it.database.engine import engine


async def main() -> None:
    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            print("Database result:", result.scalar_one())
    except Exception as exc:
        print(f"Database connection error: {exc}")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
