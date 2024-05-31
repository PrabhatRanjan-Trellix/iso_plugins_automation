#!/bin/bash

# Function to extract parent directory name from a path
get_parent_dir() {
    "${string%/*}"
}
