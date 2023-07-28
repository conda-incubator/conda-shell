# Check if any arguments were passed
if ($args.Length -eq 0) {
    Write-Host "No arguments provided. Exiting..."
    Exit
}

# Concatenate all arguments into a single string
$arguments = $args -join ' '

# Evaluate the concatenated arguments
Invoke-Expression -Command $arguments

# Open a new PowerShell instance
Start-Process powershell