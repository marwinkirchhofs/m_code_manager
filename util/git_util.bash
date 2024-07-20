#!/usr/bin/env bash

# The idea is: Let this script do everything that is actually git, and let 
# python do everything that is not directly git. This includes things like 
# deteriming which branch or commit to fetch from
 
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
    :
}

# self-explanatory: get the timestamp of the commit that a specific repo is 
# currently on
# ARGUMENTS:
# - repo (full path)
function get_repo_timestamp() {
    # TODO
    :
}

# works together with get_repo_timestamp, to determine which of two timestamps 
# is the newer one
# ARGUMENTS:
# - first timestamp
# - second timestamp
function compare_repo_timestamps() {
}

# check if there is a new version available for the given repo, with respect to 
# the specified branch/commit/tag (default if none specified)
# ARGUMENTS:
# - repo (full path)
# - (optional) reference (branch/commit/tag)
function check_new_repo() {
    # TODO
    :
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
function check_scripts_version() {
    # TODO
    :
}


function check_new_scripts

function test() {
    echo $0
    echo $1
    echo $2
}

test $@
