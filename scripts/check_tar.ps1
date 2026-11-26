param([Parameter(Mandatory=$true)][string]$TarId)
# Read-only independent verification of the immutable diploma profile (REST v1).
$ErrorActionPreference = 'Stop'
if ($TarId -cnotmatch '^urn:tar:eip155\.31337:(?:0x)?([0-9a-fA-F]{40})$') { throw 'Expected a local chain 31337 TAR ID.' }
$contract = '0x' + $Matches[1]
$composeFile = Join-Path $env:LOCALAPPDATA 'VertetifyRegistry/docker-compose.yml'
function Invoke-Cast([string[]]$Arguments) {
    $result = docker compose -p vertetify-registry -f $composeFile exec -T ethereum cast @Arguments --rpc-url http://127.0.0.1:8545
    if ($LASTEXITCODE -ne 0) { throw 'Local contract read failed.' }
    return ($result | Out-String).Trim()
}
if ((Invoke-Cast @('chain-id')) -ne '31337') { throw 'Unexpected chain.' }
$block = Invoke-Cast @('block-number')
$count = Invoke-Cast @('call',$contract,'totalVersions()(uint256)','--block',$block)
if ($count -ne '1') { throw 'Expected exactly one version for an immutable Vertetify record.' }
$chain = Invoke-Cast @('call',$contract,'getChecksum(uint256)(bytes32)','0','--block',$block)
$program = @"
import hashlib, json, sys
from urllib.request import urlopen
import rfc8785
ref = sys.argv[1]
base = "http://registry-api:8080/api/v1/TAR"
with urlopen(base + "/version/" + ref + ":1", timeout=8) as response:
    historical = json.load(response)
with urlopen(base + "/" + ref, timeout=8) as response:
    latest = json.load(response)
for r in (latest, historical):
    if r["id"] != ref or type(r["version"]) is not int or r["version"] != 1:
        raise ValueError("Unexpected TAR identity or version")
    digest = "0x" + hashlib.sha256(rfc8785.dumps(r["data"])).hexdigest()
    if not digest == r["checksum"].lower() == sys.argv[2].lower():
        raise ValueError("Checksum mismatch")
print(json.dumps(dict(tar=ref,version=1,contract_slot=0,block=sys.argv[3],jcs_sha256=digest,registry_checksum=historical["checksum"].lower(),contract_checksum=sys.argv[2].lower(),match=True)))
"@
$program | docker compose exec -T web python - $TarId $chain $block
if ($LASTEXITCODE -ne 0) { throw 'TAR comparison failed.' }
