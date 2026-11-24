# Download the organizer's deployment definition outside the application repository.
$ErrorActionPreference = 'Stop'
$directory = Join-Path $env:LOCALAPPDATA 'VertetifyRegistry'
New-Item -ItemType Directory -Path $directory -Force | Out-Null
$file = Join-Path $directory 'docker-compose.yml'
$revision = 'bd265515804cd969479959b7bb3e0f170e332454'
$url = "https://raw.githubusercontent.com/compellio/DCAP.Web/$revision/docker-compose.yml"
$definition = (Invoke-WebRequest $url -UseBasicParsing).Content.TrimStart([char]0xFEFF)
$definition = $definition.Replace('"6060:8080"', '"127.0.0.1:18660:8080"').Replace('"8545:8545"', '"127.0.0.1:18545:8545"').Replace('"5100:80"', '"127.0.0.1:15100:80"')
if (Test-Path -LiteralPath $file) {
    if ([IO.File]::ReadAllText($file).Trim() -ne $definition.Trim()) {
        throw "Existing external Compose file differs. Review $file before starting."
    }
} else {
    [IO.File]::WriteAllText($file, $definition, [Text.UTF8Encoding]::new($false))
}
docker compose -p vertetify-registry -f $file up -d registry-api
exit $LASTEXITCODE
