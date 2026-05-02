from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automage_agents.agents.renderer import write_rendered_agent
from automage_agents.config.loader import load_user_profile_toml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render AutoMage-2 agents.md from a user TOML profile.")
    parser.add_argument("--user", required=True, help="Path to user profile TOML file.")
    parser.add_argument("--output", required=True, help="Path to rendered agents.md output.")
    parser.add_argument("--template", default=None, help="Optional template name: staff/line_worker/manager/executive/base.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    user_profile = load_user_profile_toml(args.user)
    output_path = write_rendered_agent(user_profile, Path(args.output), args.template)
    print(f"Rendered agent template: {output_path}")


if __name__ == "__main__":
    main()
