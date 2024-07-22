#!/usr/bin/env bash

# Script purely meant as a git functionality helper to m_code_manager, invoked 
# by git_util.py.
# The idea is: Let this script do everything that is actually git, and let 
# python do everything that is not directly git. On the python side, this 
# includes things like deteriming which branch or commit to fetch from.
#
# Then why is this a bash script after all, and not python? Because I really did 
# not want to mess with GitPython, after briefly looking at it, and also this 
# way I'm learning to work with the proper git commands for managing submodules.  
# Plus it makes this script maintainable, because everyone knows how to use git, 
# and noone knows how to use GitPython. And it keeps a clean interface between 
# bash and python, as opposed to for example calling every git command from 
# separate inline python subprocess calls. The python script is written such 
# that there is exactly one function calling this script and passing all the 
# information of what it is supposed to do, so if the interfacing fails, you at 
# least know where to start.
#
# generally, the functions in this script assume to be executed from a project's 
# top-level directory. They are likely to fail otherwise.
#
# also, there really is not a lot of error-catching in the functions. They are 
# (being) developed to work in their intended way, from within the correct 
# working directory etc, and I almost guarantee they don't do what you want (if 
# they do anything) if used differently.

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
# * if the submodule is not there, pull it - with respect to the 
# commit/tag/branch that is passed. If none is passed, pull the default.
# * If the submodule does exist, update it - either to the commit/tag/branch, or 
# to default if none is passed.
# ARGUMENTS:
# - codemanager
# - submodule name
# - (optional) reference (branch/commit/tag)
# - (optional) remote repo
# - (optional) path (aka directory name, in most of the cases) - will be equal 
# to 'submodule name' if not passed
function update_submodule() {
    code_manager=$1
    submodule=$2
    reference=$3
    remote_repo=$5

    if [[ ! -z "$4" ]]; then
        path=$4
    else
        path=$submodule
    fi

    # check for existence (and add submodule if it is not registered yet)
    git submodule status | grep $submodule
    if [[ $? -ne 0 ]]; then
        git submodule add $remote_repo $path
    fi

    # update or checkout subrepo
    if [[ -z "$reference" ]]; then
        # if no reference is passed, just update the subrepo to whatever 
        # .gitmodules says, standard git
        git submodule update --init $path
    else
        # TODO: make the fetch optional, but in the general case (aka if it 
        # hasn't been done before) you need it
        git -C $path fetch
        git -C $path checkout $reference
    fi
}

# self-explanatory: get the timestamp of the commit that a specific repo is 
# currently on
# ARGUMENTS:
# $1 - repo (can be relative path from the working directory)
# $2 - (optional) reference - leave empty if you want the timestamp of the 
# current head
function get_repo_timestamp() {
    path=$1
    reference=$2
    # check current commit timestamp: `git show -s --format=%ct [reference]` (%
    # ct is the placeholder for unix timestamp, should be the easiest one to 
    # compare because it is 32-bit integer). Reference is optional (command 
    # refers to the current head if $reference is empty).
    # (-C "$1" simply acts on the current path if $1 is empty)

    # try two times: First the the plain reference, and second time with 
    # "origin/$reference". Reason: If reference is a commit or tag, then plain 
    # works. But if it is a branch, you either need a local version for it to 
    # work, or you need to address the remote one at origin. I could either 
    # always make local branches, but as long as you don't want to actually work 
    # on the data, there's no point in doing that, timestamp and data you can 
    # also get from the remote branch. And I couldn't find a good way to 
    # determine whether a reference is a branch or something else, don't know 
    # how git does it, but currently I'm ok with just trying twice.
    timestamp=$(git -C "$path" show -s --format=%ct $reference)
    if [[ $? -eq 0 ]]; then
        echo $timestamp
        return 0
    fi

    # use 'origin' as the hard-coded name for the remote repo
    timestamp=$(git -C "$path" show -s --format=%ct origin/$reference)
    if [[ $? -eq 0 ]]; then
        echo $timestamp
        return 0
    else
        return 1
    fi
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
# the specified branch/commit/tag (default if none specified). ATTENTION: The 
# function compares to the local repo's current head, regardless of the 
# specified reference. The reference specification is only used for the 
# comparison to remote.
# ARGUMENTS:
# $1 - repo (can be relative path from the working directory)
# $2 - (optional) reference (branch/commit/tag)
function check_new_repo() {
    path=$1
    reference=$2
    # - get the info for the remote repo (until I maybe find a less explicit 
    # way): `git remote update`
    # - the timestamp is now obtainable from the local index of origin/main -> 
    # pass that to compare_repo_timestamps (alongside with just main) - of 
    # course assuming that main is the reference that you are interested in
    git -C "$1" remote update
    timestamp_local=$(get_repo_timestamp $path)
    timestamp_remote=$(get_repo_timestamp $path $reference)
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
    codemanager=$1
    reference=$2
    # TODO: argument order
    update_submodule $codemanager "scripts" "scripts" $reference
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
    echo $@
    if [[ -z "$1" ]]; then
        echo "here"
    fi
}


############################################################
# EXECUTION
############################################################
# - interpret the first argument as a function name
# - then call that function and pass it the remaining arguments (achieved by the 
# shift, which drops the first argument after it was saved to `fun`)

fun=$1
shift
$fun $@
