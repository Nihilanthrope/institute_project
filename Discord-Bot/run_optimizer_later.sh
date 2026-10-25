#!/usr/bin/env bash
cd /home/nihilanthrope/github/Discord-Bot || exit 1
sleep 600
.venv/bin/python optimize_server.py > /tmp/rupzha-optimizer.log 2>&1
nohup .venv/bin/python -u bot.py > /tmp/rupzha-bot.log 2>&1 &
