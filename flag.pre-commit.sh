#!/bin/bash

# https://www.ittybittyapps.com/blog/2013-09-03-git-pre-push/

# If the following text is found anywhere in the source for HEAD, we will prevent committing
dont_commit_flag="DO NOT PUSH"

flag_found=`git grep --color "$dont_push_flag" HEAD`
if [ -n "$flag_found" ]
then
    # Display which commit the first occurrence of the flag was found and exit failure
    commit=`git log --pretty=format:'%Cred%h%Creset' -S "$dont_commit_flag" | tail -n1`
    echo "Found $flag_found, first occurrence was in $commit, not committing"
    exit 1
fi
exit 0