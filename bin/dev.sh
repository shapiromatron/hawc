#!/bin/bash

# Create the session to be used
tmux new-session -d -s hawc

# split the window
tmux split-window -v
tmux split-window -h
tmux select-pane -t 0
tmux split-window -h

# Run commands
tmux send-keys -t 0 "workon hawc && cd project" enter
tmux send-keys -t 1 "workon hawc && cd project && python manage.py shell" enter
tmux send-keys -t 2 "workon hawc && cd project && python manage.py runserver 8000" enter
tmux send-keys -t 3 "workon hawc && cd project && npm start" enter

# attach to shell
tmux select-pane -t 0
tmux attach-session
