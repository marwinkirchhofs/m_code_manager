#!/usr/bin/env bash

# The idea is: Let this script do everything that is actually git, and let 
# python do everything that is not directly git. This includes things like 
# deteriming which branch or commit to fetch from

# constants to make repo timestamp comparisons more readable
REPO_OLDER=0
REPO_UP_TO_DATE=1

############################################################
# UTIL
############################################################
# non-git operations

# https:
# //stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script
SCRIPT_DIR=$(cd -P "$(dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
MCM_DIR=$(dirname "$SCRIPT_DIR")

# get the directory of a codemanager (repo) within m_code_manager
# ARGUMENTS:
# $1 - codemanager
function get_code_manager_dir() {
    echo $MCM_DIR/codemanagers/$1
}

 
############################################################
# GENERIC
############################################################

# update or pull a given submodule
# if the submodule is not there, pull it - with respect to the commit/tag/branch 
# that is passed. If none is passed, pull the default. If the submodule does 
# exist, update it - either to the commit/tag/branch, or to default if none is 
# passed.
# ARGUMENTS:
# - codemanager
# - submodule name
# - (optional) path (aka directory name, in most of the cases)
# - (optional) reference (branch/commit/tag)
function update_submodule() {
    # TODO
    # - check if the submodule is added: `git submodule status | grep`
    # - if the submodule is present
    #     - check for new commits: `check_new_repo`
    #     - `git merge` to integrate the new changes. Why don't you have to 
    #     fetch? Because `check_new_repo` includes a `git remote update`, which 
    #     effectively is `git fetch`, but for all branches that track a remote 
    #     one
    :
}

# self-explanatory: get the timestamp of the commit that a specific repo is 
# currently on
# ARGUMENTS:
# - repo (can be relative path from the working directory)
function get_repo_timestamp() {
    # check current commit timestamp: `git show -s --format=%ct [reference]` (%
    # ct is the placeholder for unix timestamp, should be the easiest one to 
    # compare because it is 32-bit integer). Reference is optional.
    # (-C "$1" simply acts on the current path if $1 is empty)
    echo "$(git show -C "$1" -s --format=%ct)"
}

# works together with get_repo_timestamp, to determine which of two timestamps 
# is the newer one
# ARGUMENTS:
# - first timestamp
# - second timestamp
# RETURNS:
# $REPO_OLDER if $1<$2
# $REPO_UP_TO_DATE otherwise (thus also in case of equality)
function compare_repo_timestamps() {
    if [[ $1 -gt $2 ]]; then
        echo "$REPO_OLDER"
    else
        echo "$REPO_UP_TO_DATE"
    fi
}

# check if there is a new version available for the given repo, with respect to 
# the specified branch/commit/tag (default if none specified)
# ARGUMENTS:
# - repo (full path)
# - (optional) reference (branch/commit/tag)
function check_new_repo() {
    # TODO
    # - get the info for the remote repo (until I maybe find a less explicit 
    # way): `git remote update`
    # - the timestamp is now obtainable from the local index of origin/main -> 
    # pass that to compare_repo_timestamps (alongside with just main) - of 
    # course assuming that main is the reference that you are interested in
    :
}

function get_mcm_timestamp() {
    # determine m_code_manager installation path
    echo $(get_repo_timestamp "$MCM_DIR")
}

# get commit timestamp for a specific codemanager
# ARGUMENTS:
# $1 - codemanager
function get_code_manager_timestamp() {
    echo $(get_repo_timestamp "$(get_code_manager_dir $1)")
}

############################################################
# REPO-SPECIFIC
############################################################

# pull the scripts submodule for the current project
# * add and pull the submodule
#     * TODO: respect the git branch in the mcm config
# * symlink (TODO: or copy) all script assets that belong elsewhere
# ARGUMENTS:
# $1 - codemanager
# $2 - (optional) reference (branche/commit/tag)
function pull_scripts() {
    update_submodule $1 "scripts" "scripts" $2
}

# determine if the scripts repo is older than the currently used version of the 
# respective codemanager
# ARGUMENTS:
# - codemanager
# RETURNS:
# $REPO_OLDER if scripts are older than codemanager
# $REPO_UP_TO_DATE otherwise (thus also in case of equality)
function check_scripts_version() {
    timestamp_code_manager="$(get_code_manager_timestamp $1)"
    timestamp_scripts="$(get_repo_timestamp "scripts")"
    echo "$(compare_repo_timestamps $timestamp_scripts $timestamp_code_manager)"
}


function test() {
    echo $1
    if [[ -z "$1" ]]; then
        echo "here"
    fi
}

test $@
