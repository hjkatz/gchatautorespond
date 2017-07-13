#!/bin/bash

#### LIBRARY FUNCTIONS ####
# echos out with color, e.g.
#   color_echo red "My Error"
#   color_echo yellow "My Warning"
#   color_echo green "My Success"
function color_echo () {
    case $1 in
     red)
          color=31
          ;;
     green)
          color=32
          ;;
     yellow)
          color=33
          ;;
     *)
          color=$1
          ;;
    esac

    # remove $1
    shift

    echo -e "\033[1;${color}m$@\033[0m"
}

# begin reading from the keyboard
function turn_on_keyboard () {
    # save stdin to fd 6
    exec 6<&1

    # set stdin to /dev/tty
    exec </dev/tty

    # because we're about to read something...I guess
    flush_stdin
}

# stop reading from the keyboard
function turn_off_keyboard () {
    # restore stdin from fd 6 and close fd 6
    exec 1<&6 6>&-
}

# [see: https://superuser.com/questions/276531/clear-stdin-before-reading]
function flush_stdin() {
    while read -e -t 0.1 ; do : ; done
}


# asks the user for input in the form of a [y/n] question
# the result is stored in the variable $ANSWER
function ask () {
    question="$1"

    # manually run color echo without a newline
    echo -e -n "\033[1;33m$question [y/n]: \033[0m"

    turn_on_keyboard
    read -n 1 ANSWER
    turn_off_keyboard

    # add the missing newline
    echo ""

    # loop until the user responds with a y or n
    while [[ $ANSWER != y ]] && [[ $ANSWER != n ]] ; do
        # manually run color echo without a newline
        echo -e -n "\033[1;33m[y/n]: \033[0m"

        turn_on_keyboard
        read -n 1 ANSWER
        turn_off_keyboard

        # add the missing newline
        echo ""
    done
}

# asks the user for input in the form of a [y/n] question
# the result is stored in the variable $ANSWER
function ask_with_timeout () {
    timeout="$1"
    default="$2"
    question="$3"

    # manually run color echo without a newline
    color_echo yellow "$question [y/n]"
    echo -e -n "\033[1;33mAssuming \"$default\" in $timeout secs: \033[0m"

    turn_on_keyboard
    read -t $timeout -n 1 ANSWER
    turn_off_keyboard

    # add the missing newline
    echo ""

    if [[ $? != 0 ]] ; then
        # timeout occurred
        ANSWER="$default"
    else
        # loop until the user responds with a y or n
        while [[ $ANSWER != y ]] && [[ $ANSWER != n ]] ; do
            # manually run color echo without a newline
            echo -e -n "\033[1;33m[y/n]: \033[0m"

            turn_on_keyboard
            read -n 1 ANSWER
            turn_off_keyboard

            # add the missing newline
            echo ""
        done
    fi
}

# Shortcut for echoing red and exiting
function die () {
    color_echo red "$@"
    exit -1
}

# this script MUST be run as root
if [[ ! "$USER" == "root" ]] ||  [ ! "$(id -u)" == 0 ] ; then
    die "You must run this script as root."
fi

#### USAGE ####
function usage () {
    message="$@"
    prog_name=`basename "$0"`

    echo "$prog_name [--email <email@neadwerx.com>] [--msg <message|filepath>]"
    echo "This script is used to install the gchat auto-repond bot."
    echo ""
    echo "Flags:"
    echo "       --email <email>           : the email of the user to auth and setup with."
    echo "       --msg <message|filepath>  : the string message or filepath to your message."
    die $message
}

#### GETOPTS ####

automate="false"

#!/bin/bash
while [ ! $# -eq 0 ] ; do
    case "$1" in
        --help | -h)
            usage
            ;;
        --email)
            shift
            email="$1"
            ;;
        --msg)
            shift
            msg="$1"
            ;;
    esac
    shift
done

# required args
[[ -z $email ]] && die "Missing required email!"
[[ -z $msg ]] && die "Missing required msg!"

#### VARIABLES ####
install_dir="/usr/share/gchatautorespond"
template_dir="$install_dir/templated"
systemd_services_path="/usr/lib/systemd/system"
service_name="gchatautorespond.service"
DIR="$(readlink -f $(dirname "$0"))"

#### MAIN PROGRAM ####

if ! [[ -f "$DIR/$email.oauth_credentials" ]] ; then
    color_echo yellow "Performing first time oauth setup..."
    $DIR/standalone_bot.py auth
fi

if ! [[ -d $install_dir ]] ; then
    color_echo yellow "Linking directory $install_dir to $DIR..."
    ln -s $DIR $install_dir
fi

color_echo yellow "Customizing service files..."
mkdir -p $DIR/templated/
cp -f $DIR/systemd/* $DIR/templated/
perl -p -i -e "s{\{\{email\}\}}{$email}" $DIR/templated/*
perl -p -i -e "s{\{\{msg\}\}}{$msg}" $DIR/templated/*

color_echo yellow "Copying over systemd service files..."
cp -f $DIR/templated/* $systemd_services_path/

color_echo yellow "Reloading systemd daemons..."
systemctl daemon-reload || die "Failed to reload systemctl daemons! Check journalctl for more information."

color_echo yellow "Restarting $service_name..."
systemctl restart $service_name || die "Failed to restart $service_name! Check journalctl for more information."

color_echo green "All done!"
