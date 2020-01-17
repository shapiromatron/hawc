#!/bin/bash

# Create the session to be used
tmux new-session -d -s hawc

# split the window
tmux split-window -v
tmux split-window -h
tmux select-pane -t 0
tmux split-window -h

# Run commands
tmux send-keys -t 0 "cd project && source ../venv/bin/activate" enter
tmux send-keys -t 1 "cd project && source ../venv/bin/activate && python manage.py shell" enter
tmux send-keys -t 2 "cd project && source ../venv/bin/activate && python manage.py runserver" enter
tmux send-keys -t 3 "npm --prefix ./frontend run start" enter

# attach to shell
tmux select-pane -t 0
tmux attach-session
