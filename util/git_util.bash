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
REPO_OLDER="old"
REPO_UP_TO_DATE="up-to-date"


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
# 
# If reference is specified and causes the submodule HEAD to change, those 
# changes are NOT committed to the parent repo by design choice. The user needs 
# to decide themselves when to commit the changes, or if they maybe just want to 
# try something out with a different reference of a subrepo without committing 
# anything, because they might go back to the previous state.
#
# ARGUMENTS:
# - submodule name
# - path (aka directory name, in most of the cases)
# - remote repo
# - (optional) reference (branch/commit/tag)
function update_submodule() {
    submodule=$1
    path=$2
    remote_repo=$3
    reference=$4

    # check for existence (and add submodule if it is not registered yet)
    git submodule status | grep $submodule
    if [[ $? -ne 0 ]]; then
        git submodule add $remote_repo $path
    fi

    # check the remote url, and update if different from $remote_repo
    current_url=$(git -C $path remote get-url origin)
    if [[ ! "$current_url" == "$remote_repo" ]]; then
        # difference between the two versions: The first one (commented out) 
        # only acts on the submodule, bit leaves .gitmodules untouched. The 
        # second one changes both .gitmodules and the submodule itself.
        # Yes, you can recover from the first one by updating to the .gitmodules 
        # url - you can not recover from the second one (from within the repo).  
        # But every url is either generated from default naming conventions, or 
        # user-specified in the mcm version config file. Therefore, they are 
        # always available to reset, unless the user messes it up, in which case 
        # it's their problem.
#         git -C $path remote set-url origin $remote_repo $current_url
        git submodule set-url $path $remote_repo
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

# just initialize a git repo
function init() {
    git init
}

# reset a submodule to the reference that the current parent repo points to for 
# the submodule
# ARGUMENTS:
# - repo/path
# - overwrite   (if passed: overwrite; if not passed: don't overwrite)
function reset_submodule() {
    path=$1
    overwrite=$2
    if [[ ! -z $overwrite ]]; then
        # -f is needed such that manual changes to the subrepo get overwritten 
        # (otherwise the command just fails if there are changes to the subrepo)
        arg_force="-f"
    else
        arg_force=""
    fi

    # there is a more "radical" method to this:
    # `git submodule deinit -f $path && git submodule update --init`
    #https://stackoverflow.com/questions/10906554/how-do-i-revert-my-changes-to-a-git-submodule
    # we first stick to this method and see if it causes any problems.
    git submodule update --checkout $arg_force $path
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
    # "origin/$reference". Reason: If reference is a branch, then you have to 
    # use the origin version, because a potential local copy of the branch is 
    # not forwarded yet. If reference is a commit or tag, then 
    # "origin/$reference" will just fail, which is fine. In that case, plain 
    # reference is what you want.

    # use 'origin' as the hard-coded name for the remote repo
    # reference is a remote branch
    git -C "$path" show-ref --exists refs/remotes/origin/$reference 1>/dev/null 2>&1
    if [[ $? -eq 0 ]]; then
        timestamp=$(git -C "$path" show -s --format=%ct origin/$reference)
        echo $timestamp
        return 0
    fi

    # reference is a local branch without a remote
    git -C "$path" show-ref --exists refs/heads/$reference 1>/dev/null 2>&1
    if [[ $? -eq 0 ]]; then
        timestamp=$(git -C "$path" show -s --format=%ct $reference)
        echo $timestamp
        return 0
    fi

    # reference is a tag
    git -C "$path" show-ref --tags $reference 1>/dev/null 2>&1
    if [[ $? -eq 0 ]]; then
        timestamp=$(git -C "$path" show -s --format=%ct $reference)
        echo $timestamp
        return 0
    fi

    # reference has to be a commit (otherwise it doesn't exist)
    timestamp=$(git -C "$path" show -s --format=%ct $reference)
    if [[ $? -eq 0 ]]; then
        echo $timestamp
        return 0
    fi

    return 1
}

# determine which of two timestamps is the newer one
# ARGUMENTS:
# - first timestamp
# - second timestamp
# RETURNS:
# $REPO_OLDER if $1<$2
# $REPO_UP_TO_DATE otherwise (thus also in case of equality)
function compare_repo_timestamps() {
    if [[ $1 -lt $2 ]]; then
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
function check_repo_new_commit() {
    path=$1
    reference=$2
    [[ -z "$reference" ]] && reference="origin"
    # - get the info for the remote repo (until I maybe find a less explicit 
    # way): `git remote update`
    # - the timestamp is now obtainable from the local index of origin/main -> 
    # pass that to compare_repo_timestamps (alongside with just main) - of 
    # course assuming that main is the reference that you are interested in
    git -C "$1" remote update
    timestamp_local=$(get_repo_timestamp $path)
    timestamp_remote=$(get_repo_timestamp $path $reference)

    echo "$(compare_repo_timestamps $timestamp_local $timestamp_remote)"
}

function get_mcm_timestamp() {
    # determine m_code_manager installation path
    echo $(get_repo_timestamp "$MCM_DIR")
}

# get commit timestamp for a specific codemanager implementation
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
#
# why does this function need to get the remote repo as an argument (from python) 
# instead of deriving the correct url from the codemanager and naming convention?  
# Two reasons:
# 1. Leave full control over things like naming conventions to the python 
# environment - if conventions change, you only have to change them there
# 2. It is planned to give the user the possibility to use their own fork of 
# scripts and point to that, instead of the standard one. Python has that info 
# because it reads the mcm version config file, the bash script does not have 
# that info. So hard-coded url could be straight-up wrong.
#
# ARGUMENTS:
# $1 - codemanager
# $2 - (optional) reference (branche/commit/tag)
# $3 - remote repo
function pull_scripts() {
    codemanager=$1
    reference=$2
    remote=$3
    update_submodule "scripts" $reference $remote
}

# determine if the scripts repo is older than the currently used version of the 
# respective codemanager
# ARGUMENTS:
# - codemanager
# RETURNS:
# $REPO_OLDER if scripts are older than codemanager
# $REPO_UP_TO_DATE otherwise (thus also in case of equality)
function check_scripts_version() {
    codemanager=$1
    timestamp_code_manager="$(get_code_manager_timestamp $codemanager)"
    timestamp_scripts="$(get_repo_timestamp "scripts")"
    echo "$(compare_repo_timestamps $timestamp_scripts $timestamp_code_manager)"
}

function test() {
    for arg in $@; do
        echo $arg
    done
#     if [[ -z "$1" ]]; then
#         echo "here"
#     fi
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
