$collection = 60289,80683,60288,1210,1204
foreach ($item in $collection) {
    Write-Output "Poggers : $item"
    Start-Process python "./checkEp.py Episode $item false"
}

# Write-Host -NoNewLine 'Press any key to continue...'
# $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')

# Remove-Item -Path './db.json', './db.lock', './logs/checkEp.log'