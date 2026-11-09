#!/bin/bash
# fetch issue JSON (read-only) for each number
cd "$(dirname "$0")"; mkdir -p raw
for n in "$@"; do
  gh issue view $n -R zen-browser/desktop --json number,title,body,state,stateReason,closedAt,labels,comments,author,createdAt,url > raw/$n.json 2>raw/$n.err || echo "fail $n"
done
