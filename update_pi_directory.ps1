# Define variables
$pscpPath = "C:\Program Files\PuTTY\pscp.exe"
$plinkPath = "C:\Program Files\PuTTY\plink.exe"
$piUser = "pi"
$piHost = "192.168.1.197"
$destDir = "/home/pi/mdb-test-auto/"
$password = "pi"

# Get the current user's home directory
$currentUserName = $env:UserName
$sourceDir = "C:\Users\$currentUserName\mdb-test-auto"

# Remove the directory on the Raspberry Pi if it exists
& $plinkPath -batch -pw $password "$piUser@$piHost" "rm -rf $destDir"

# Copy all files from the current directory to the Raspberry Pi
& $pscpPath -batch -r -pw $password "$sourceDir" "${piUser}@${piHost}:/home/pi/"

# Give permissions and execute server in tmux
& $plinkPath -batch -pw $password "$piUser@$piHost" "chmod a+x ${destDir}run_server.sh && dos2unix ${destDir}run_server.sh && ${destDir}run_server.sh"
