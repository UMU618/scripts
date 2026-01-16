Set-PSReadLineKeyHandler -Key "Ctrl+q" -Function MenuComplete

function ll { Get-ChildItem -Force $args }

function gcam { & git commit -am $args }
function gpl { & git pull $args }
function gph { & git push $args }
function grv { & git remote -v }
function gs { & git status }

function wi { & winget install $args }
function ws { & winget search $args }

$env:GO111MODULE = "on"
$env:GOPROXY = "https://goproxy.cn"
