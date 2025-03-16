#!/bin/zsh

cd src
for i in {1..1000}
do
        #MODEL=openrouter/deepseek/deepseek-r1
        MODEL=r1
        #MODEL=deepseek
        echo "$i - $(date) ====================================================="
        aider --architect --model $MODEL --subtree-only --read plex.md --read context.txt --yes-always --no-show-model-warnings --weak-model 'openrouter/google/gemini-2.0-flash-001' --message 'if there are errors, work on fixing the errors. if there are no errors, work on cleaning up the code a little bit. If you see that something is not defined or implemented, please work on implementing until there are no errors. The tests need to work as they are right now. Do not edit tests. Do not add tests to the chat. Do not edit the linting rules. Do not run any commands. Do not try to install anything. Do not mock any functionality, actually implement it. Is there any functionality that is not yet implemented? Replace all mocking with actual implementations. Only use small search replace blocks. You can however use many search replace blocks.' **/*py
        sleep 1
done






