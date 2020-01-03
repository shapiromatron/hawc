#!/bin/bash

# Create the session to be used
tmux new-session -d -s hawc-hero-new

# split the window
tmux split-window -v
tmux split-window -h
tmux select-pane -t 0
tmux split-window -h

# Run commands
tmux send-keys -t 0 "source venv/bin/activate" enter
tmux send-keys -t 1 "source venv/bin/activate && manage.py shell" enter
tmux send-keys -t 2 "source venv/bin/activate && manage.py runserver 8200" enter
tmux send-keys -t 3 "cd hawc && npm start" enter

# attach to shell
tmux select-pane -t 0
tmux attach-session
