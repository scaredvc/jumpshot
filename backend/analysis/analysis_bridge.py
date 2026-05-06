import os
import subprocess


DEFAULT_REFERENCE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "nba_reference.txt",
)


def _is_truthy(value):
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def is_demo_mode():
    return _is_truthy(os.environ.get("DEMO_MODE", "true"))


def _load_reference_sections(reference_path):
    with open(reference_path, "r", encoding="utf-8") as handle:
        content = handle.read().strip()

    sections = {}
    current_player = None
    current_lines = []

    for line in content.splitlines():
        if line.startswith("## "):
            if current_player and current_lines:
                sections[current_player] = "\n".join(current_lines).strip()
            current_player = line[3:].strip()
            current_lines = []
            continue
        current_lines.append(line)

    if current_player and current_lines:
        sections[current_player] = "\n".join(current_lines).strip()

    return sections


def get_local_nba_player_analysis(player_name, reference_path=DEFAULT_REFERENCE_FILE):
    if not os.path.exists(reference_path):
        raise FileNotFoundError(
            f"NBA reference file not found at {reference_path}."
        )

    sections = _load_reference_sections(reference_path)
    if player_name not in sections:
        available_players = ", ".join(sorted(sections)) or "none"
        raise KeyError(
            f"No local NBA reference found for {player_name}. "
            f"Available players: {available_players}."
        )

    return sections[player_name]


def _run_scraper(player_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join("yt webscraper puppeteer", "index.js")
    node_source = (
        f"const getPlayerAnalysis = require('./{script_path}');"
        "async function run() {"
        f"  const analysis = await getPlayerAnalysis('{player_name}');"
        "  if (typeof analysis === 'string') {"
        "    console.log(analysis);"
        "  } else {"
        "    console.log(JSON.stringify(analysis));"
        "  }"
        "}"
        "run().catch((error) => {"
        "  console.error(error.message);"
        "  process.exit(1);"
        "});"
    )

    result = subprocess.run(
        ["node", "-e", node_source],
        capture_output=True,
        text=True,
        cwd=script_dir,
        check=False,
    )

    if result.returncode != 0:
        stderr = result.stderr.strip() or "Unknown scraper failure"
        raise RuntimeError(stderr)

    stdout = result.stdout.strip()
    if not stdout:
        raise RuntimeError("Scraper returned no analysis text.")

    return stdout


def get_nba_player_analysis(player_name):
    if is_demo_mode():
        return get_local_nba_player_analysis(player_name)

    try:
        return _run_scraper(player_name)
    except Exception:
        if os.path.exists(DEFAULT_REFERENCE_FILE):
            return get_local_nba_player_analysis(player_name)
        raise
