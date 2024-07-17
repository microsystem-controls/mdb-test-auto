#!/bin/bash

SESSION="projects:"
WINDOW="mdb_test_auto_server"

# Attempt to kill the window silently
tmux kill-window -t "$SESSION$WINDOW" 2>/dev/null

# Start a new window in the session
tmux new-window -n "$WINDOW" -t "$SESSION" "cd mdb-test-auto; poetry run server; $SHELL"
