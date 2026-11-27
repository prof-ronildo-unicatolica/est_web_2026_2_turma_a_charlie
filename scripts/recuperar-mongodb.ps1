$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $root ".env"

if (-not (Test-Path $envFile)) {
    throw "Arquivo .env não encontrado na raiz do projeto."
}

$lines = Get-Content $envFile
$passwordLine = $lines | Where-Object { $_ -match '^\s*MONGO_ADMIN_PASSWORD\s*=' } | Select-Object -First 1
if (-not $passwordLine) {
    throw "MONGO_ADMIN_PASSWORD não foi encontrado no .env."
}

$password = ($passwordLine -replace '^\s*MONGO_ADMIN_PASSWORD\s*=\s*', '').Trim().Trim('"').Trim("'")
if ([string]::IsNullOrWhiteSpace($password)) {
    throw "MONGO_ADMIN_PASSWORD está vazio no .env."
}

Write-Host "Parando temporariamente API, worker e MongoDB (os volumes serão preservados)..."
docker compose stop core-service audit-worker mongodb
if ($LASTEXITCODE -ne 0) { throw "Falha ao parar os serviços." }

$tempContainer = $null
try {
    Write-Host "Iniciando MongoDB temporariamente sem autenticação, usando o mesmo volume..."
    $tempContainer = (docker compose run -d --no-deps --entrypoint mongod mongodb --dbpath /data/db --bind_ip_all --noauth).Trim()
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($tempContainer)) {
        throw "Não foi possível iniciar o MongoDB temporário."
    }

    Start-Sleep -Seconds 5
    Write-Host ""
    Write-Host "No shell do MongoDB, execute exatamente este bloco:"
    Write-Host 'const adminDb = db.getSiblingDB("admin");'
    Write-Host 'if (adminDb.getUser("admin")) {'
    Write-Host '  adminDb.updateUser("admin", { pwd: passwordPrompt() });'
    Write-Host '} else {'
    Write-Host '  adminDb.createUser({ user: "admin", pwd: passwordPrompt(), roles: [{ role: "root", db: "admin" }] });'
    Write-Host '}'
    Write-Host ""
    Write-Host "Digite a mesma senha definida em MONGO_ADMIN_PASSWORD no .env."
    docker exec -it $tempContainer mongosh --quiet
    if ($LASTEXITCODE -ne 0) { throw "O shell do MongoDB terminou com erro." }

    $encodedPassword = [System.Uri]::EscapeDataString($password)
    $mongoUrl = "mongodb://admin:$encodedPassword@mongodb:27017/?authSource=admin"
    $newLines = @()
    $urlUpdated = $false
    foreach ($line in $lines) {
        if ($line -match '^\s*MONGODB_URL\s*=') {
            $newLines += "MONGODB_URL=$mongoUrl"
            $urlUpdated = $true
        } else {
            $newLines += $line
        }
    }
    if (-not $urlUpdated) { $newLines += "MONGODB_URL=$mongoUrl" }
    [System.IO.File]::WriteAllLines($envFile, $newLines, [System.Text.UTF8Encoding]::new($false))

    Write-Host "Credenciais atualizadas no .env. Reiniciando serviços..."
}
finally {
    if ($tempContainer) {
        docker stop $tempContainer | Out-Null
        docker rm $tempContainer | Out-Null
    }
}

docker compose up -d mongodb
if ($LASTEXITCODE -ne 0) { throw "Falha ao iniciar MongoDB." }

$healthy = $false
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 2
    $health = docker inspect --format '{{.State.Health.Status}}' hotel-mongo 2>$null
    if ($health -eq "healthy") { $healthy = $true; break }
}
if (-not $healthy) { throw "MongoDB não ficou healthy. Consulte: docker compose logs mongodb" }

docker compose up -d --build core-service audit-worker
if ($LASTEXITCODE -ne 0) { throw "Falha ao reconstruir API e worker." }

Write-Host ""
Write-Host "Recuperação concluída. Confira com: docker compose ps"
