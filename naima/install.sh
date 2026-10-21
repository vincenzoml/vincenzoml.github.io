#!/bin/sh
# Naima's site moved to https://naima-project.github.io/naima/: this runs the installer from there.
set -eu
curl -fsSL https://naima-project.github.io/naima/install.sh | sh
