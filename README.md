## installation

open powershell:

to copy files over to the raspberry pi:

```
./update_pi_directory.ps1 --copy
```

to copy just the frontend files to the raspberry pi:

```
./update_pi_directory.ps1 --copy-frontend
```

to run the server (tmux):

```
./update_pi_directory.ps1 --restart-server
```

## development

tailwind compilation:

```
npm --prefix src/user_interface/tailwindcss run dev
```

automatic reload (frontend):
```
browser-sync start --proxy "http://rasp3a.local:8000" --files "src/**/*.css, src/**/*.js, src/**/*.html"
```
