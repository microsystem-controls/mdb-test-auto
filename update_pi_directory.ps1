# Define variables
$pscpPath = "C:\Program Files\PuTTY\pscp.exe"
$plinkPath = "C:\Program Files\PuTTY\plink.exe"
$piUser = "pi"
$piHost = "192.168.1.197"
$destDir = "/home/pi/mdb-test-auto/"
$password = "pi"

if ($args -contains "--copy"){
    # Get the current user's home directory
    $sourceDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition

    # Check if destination directory exists; create if not
    & $plinkPath -batch -pw $password "$piUser@$piHost" "mkdir -p $destDir"

    # Remove the directory on the Raspberry Pi if it exists
    & $plinkPath -batch -pw $password "$piUser@$piHost" "rm -rf ${destDir}*"

    # Copy all files from the current directory to the Raspberry Pi
    & $pscpPath -batch -r -pw $password "$sourceDir\*" "${piUser}@${piHost}:${destDir}"
    
    # Give permissions and execute server in tmux
    & $plinkPath -batch -pw $password "$piUser@$piHost" "chmod a+x ${destDir}run_server.sh && dos2unix ${destDir}run_server.sh"
}

if ($args -contains "--copy-frontend"){
    $frontend = "src/user_interface/"
    $frontendDir = "${destDir}${frontend}"

    # Get the current user's home directory
    $sourceDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition

    # Check if destination directory exists; create if not
    & $plinkPath -batch -pw $password "$piUser@$piHost" "mkdir -p $frontendDir"

    # Remove the directory on the Raspberry Pi if it exists
    & $plinkPath -batch -pw $password "$piUser@$piHost" "rm -rf ${frontendDir}*"

    # Copy all files from the current directory to the Raspberry Pi
    & $pscpPath -batch -r -pw $password "$sourceDir\$frontend*" "${piUser}@${piHost}:${frontendDir}"
}

if ($args -contains "--restart-server"){
    # Give permissions and execute server in tmux
    & $plinkPath -batch -pw $password "$piUser@$piHost" "${destDir}run_server.sh"
}
