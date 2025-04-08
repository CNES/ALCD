#!/bin/bash

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Error: You must specify a McCabe threshold and a directory to analyze."
    echo "Usage: $0 <threshold> <directory>"
    exit 1
fi

threshold=$1
directory=$2

if [ ! -d "$directory" ]; then
    echo "Error: The directory '$directory' does not exist."
    exit 1
fi

all_files_ok=true
for file in $(find "$directory" -name "*.py"); do
    echo "Analyzing $file ..."
    output=$(python -m mccabe --min "$threshold" "$file")

    if [ -n "$output" ]; then
        echo "Error: McCabe complexity too high in $file"
        echo "$output"
        all_files_ok=false
    fi
done

if $all_files_ok; then
    echo "✅ All files have McCabe scores less than or equal to $threshold. ✅"
else
    echo "❌ Some files have a complexity higher than $threshold ❌"
    exit 1
fi

exit 0
