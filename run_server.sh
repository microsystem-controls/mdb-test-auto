#!/bin/bash

SESSION="projects"
WINDOW="mdb_test_auto_server"

# Attempt to kill the window silently
tmux kill-window -t "$SESSION:$WINDOW" 2>/dev/null
tmux new -d -s "$SESSION"
tmux neww -n "$WINDOW" -t "$SESSION:" "cd mdb-test-auto; poetry install; poetry run mdb_tester; $SHELL"
tmux switch-client -t "$SESSION:$WINDOW"
