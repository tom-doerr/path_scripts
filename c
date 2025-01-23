#!/bin/bash

# Default filters as single string without extra quoting
DEFAULT_FILTERS="+PENDING -bu"

# Handle arguments
if [[ $# -eq 0 ]]; then
    echo "Usage: c [OPTIONS] [FILTERS...] [REPORT_NAME]"
    echo "Options:"
    echo "  -n, --no_default_filters  Disable default filters (+PENDING -bu)"
    exit 1
fi

# Check for no-default-filters flag
NO_DEFAULTS=false
if [[ "$1" == "-n" || "$1" == "--no_default_filters" ]]; then
    NO_DEFAULTS=true
    shift
fi

# Build arguments
ARGS=("--once")
if ! $NO_DEFAULTS; then
    ARGS+=("$DEFAULT_FILTERS")
fi

# Combine remaining arguments into single string and add to ARGS
USER_ARGS="$*"
ARGS+=("$USER_ARGS")

# Pass all arguments as individual quoted elements
"/home/tom/git/scripts/show_tw_tasks.py" "${ARGS[@]}"
