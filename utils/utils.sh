#!/bin/bash

# Function to extract parent directory name from a path
get_parent_dir() {
    local path="$1"
    local parent_dir="${path%/*}"
    echo "$parent_dir"
}
