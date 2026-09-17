# This is inteneded for the Trackpulse server, it may not work on other systems.
# run with bash scripts/update.sh

#!/usr/bin/env bash

set -euo pipefail

repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$repo_dir"
git pull --ff-only
sudo systemctl restart trackpulse.service

echo "TrackPulse updated and service restarted."