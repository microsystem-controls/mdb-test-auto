#!/bin/bash

# Define variables
pscpPath="/usr/bin/scp"
plinkPath="/usr/bin/ssh"
piUser="pi"
piHost="192.168.1.197"
destDir="/home/pi/mdb-test-auto/"
password="pi"

# Get the current script directory
sourceDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [[ " $* " == *" --copy "* ]]; then
    # Check if destination directory exists; create if not
    $plinkPath "$piUser@$piHost" "mkdir -p $destDir"

    # Remove the directory on the Raspberry Pi if it exists
    $plinkPath "$piUser@$piHost" "rm -rf ${destDir}"

    # Copy all files from the current directory to the Raspberry Pi
    $pscpPath -r "$sourceDir/" "$piUser@$piHost:$destDir"
    
    # Give permissions and execute server in tmux
    $plinkPath "$piUser@$piHost" "chmod a+x ${destDir}run_server.sh && dos2unix ${destDir}run_server.sh"
fi

if [[ " $* " == *" --copy-frontend "* ]]; then
    frontend="src/user_interface/"
    frontendDir="${destDir}${frontend}"

    # Check if destination directory exists; create if not
    $plinkPath "$piUser@$piHost" "mkdir -p $frontendDir"

    # Remove the directory on the Raspberry Pi if it exists
    $plinkPath "$piUser@$piHost" "rm -rf ${frontendDir}"

    # Copy all files from the frontend directory to the Raspberry Pi
    $pscpPath -r "$sourceDir/$frontend" "$piUser@$piHost:$frontendDir"
fi

if [[ " $* " == *" --restart-server "* ]]; then
    # Give permissions and execute server in tmux
    $plinkPath "$piUser@$piHost" "${destDir}run_server.sh"
fi

