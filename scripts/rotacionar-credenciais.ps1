$ErrorActionPreference = "Stop"

function Invoke-Docker {
    param([string[]]$Arguments, [string]$Failure)
    & docker @Arguments
    if ($LASTEXITCODE -ne 0) { throw $Failure }
}

function Set-EnvValue {
    param([string]$Name, [string]$Value)
    $script:lines = @($script:lines | Where-Object { $_ -notmatch "^\s*$([regex]::Escape($Name))\s*=" })
    $script:lines += "$Name=$Value"
    [System.IO.File]::WriteAllLines($script:envFile, $script:lines, [System.Text.UTF8Encoding]::new($false))
}

function New-Secret {
    param([int]$Bytes = 32)
    $buffer = New-Object byte[] $Bytes
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($buffer) } finally { $rng.Dispose() }
    return ([BitConverter]::ToString($buffer) -replace '-', '').ToLowerInvariant()
}

$root = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $root ".env"
if (-not (Test-Path $envFile)) { throw ".env não encontrado na raiz." }

$branch = (& git -C $root branch --show-current).Trim()
if ($branch -ne "feat/reservas-avaliacoes-contas") {
    throw "Branch incorreta: $branch. Mude para feat/reservas-avaliacoes-contas antes de continuar."
}

$lines = @(Get-Content $envFile)
$values = @{}
foreach ($line in $lines) {
    if ($line -match '^\s*([^#=]+)=(.*)$') {
        $values[$matches[1].Trim()] = $matches[2].Trim().Trim('"').Trim("'")
    }
}
foreach ($required in @("POSTGRES_USER","POSTGRES_DB","MONGO_ADMIN_PASSWORD","RABBITMQ_USER","RABBITMQ_PASSWORD")) {
    if ([string]::IsNullOrWhiteSpace($values[$required])) { throw "Variável obrigatória ausente ou vazia: $required" }
}
if ($values["POSTGRES_USER"] -ne "postgres") {
    throw "Este script foi preparado para o usuário PostgreSQL postgres; encontrado outro usuário."
}
if ($values["RABBITMQ_USER"] -ne "hotel_app") {
    throw "Este script foi preparado para o usuário RabbitMQ hotel_app; encontrado outro usuário."
}

$backup = "$envFile.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
Copy-Item $envFile $backup
Write-Host "Backup criado: $backup"

# Confirma os serviços necessários antes de alterar qualquer credencial.
foreach ($container in @("hotel-postgres","hotel-rabbitmq","hotel-mongo")) {
    $status = (& docker inspect --format '{{.State.Health.Status}}' $container 2>$null).Trim()
    if ($LASTEXITCODE -ne 0 -or $status -ne "healthy") {
        throw "O container $container não está healthy. Nenhuma credencial foi alterada."
    }
}

$newMongo = New-Secret
$newPostgres = New-Secret
$newRabbit = New-Secret
$newSecretKey = New-Secret

Write-Host "Parando API e worker para evitar conexões durante a rotação..."
Invoke-Docker -Arguments @("compose","stop","core-service","audit-worker") -Failure "Falha ao parar API/worker."

$tempContainer = $null
try {
    Write-Host "Trocando credencial do MongoDB sem remover o volume..."
    Invoke-Docker -Arguments @("compose","stop","mongodb") -Failure "Falha ao parar MongoDB."
    $tempContainer = (& docker compose run -d --no-deps --entrypoint mongod mongodb --dbpath /data/db --bind_ip_all --noauth).Trim()
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($tempContainer)) {
        throw "Não foi possível iniciar MongoDB temporário."
    }
    Start-Sleep -Seconds 6
    $mongoJs = @"
const adminDb = db.getSiblingDB("admin");
if (adminDb.getUser("admin")) {
  adminDb.updateUser("admin", { pwd: "$newMongo" });
} else {
  adminDb.createUser({ user: "admin", pwd: "$newMongo", roles: [{ role: "root", db: "admin" }] });
}
"@
    $mongoJs | & docker exec -i $tempContainer mongosh --quiet
    if ($LASTEXITCODE -ne 0) { throw "Falha ao atualizar usuário admin do MongoDB." }

    & docker stop $tempContainer | Out-Null
    & docker rm $tempContainer | Out-Null
    $tempContainer = $null

    Set-EnvValue -Name "MONGO_ADMIN_PASSWORD" -Value $newMongo
    Set-EnvValue -Name "MONGODB_URL" -Value "mongodb://admin:$newMongo@mongodb:27017/?authSource=admin"

    Invoke-Docker -Arguments @("compose","up","-d","mongodb") -Failure "Falha ao iniciar MongoDB com a nova credencial."
    $mongoHealthy = $false
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Seconds 2
        $health = (& docker inspect --format '{{.State.Health.Status}}' hotel-mongo 2>$null).Trim()
        if ($health -eq "healthy") { $mongoHealthy = $true; break }
    }
    if (-not $mongoHealthy) { throw "MongoDB não ficou healthy após a troca." }

    Write-Host "Trocando senha do PostgreSQL..."
    Invoke-Docker -Arguments @("exec","-u","postgres","hotel-postgres","psql","-U","postgres","-d",$values["POSTGRES_DB"],"-v","ON_ERROR_STOP=1","-c","ALTER USER postgres WITH PASSWORD '$newPostgres';") -Failure "Falha ao trocar senha PostgreSQL."
    Set-EnvValue -Name "POSTGRES_PASSWORD" -Value $newPostgres

    Write-Host "Trocando senha do RabbitMQ..."
    Invoke-Docker -Arguments @("exec","hotel-rabbitmq","rabbitmqctl","change_password","hotel_app",$newRabbit) -Failure "Falha ao trocar senha RabbitMQ."
    Set-EnvValue -Name "RABBITMQ_PASSWORD" -Value $newRabbit

    Set-EnvValue -Name "SECRET_KEY" -Value $newSecretKey

    Write-Host "Reconstruindo e iniciando os serviços..."
    Invoke-Docker -Arguments @("compose","up","-d","--build") -Failure "Falha ao reconstruir/iniciar os serviços."

    Write-Host ""
    Write-Host "Rotação concluída. Nenhum volume foi removido."
    Write-Host "As credenciais não foram exibidas. Backup local: $backup"
    Write-Host "Verifique com: docker compose ps"
}
finally {
    if ($tempContainer) {
        & docker stop $tempContainer 2>$null | Out-Null
        & docker rm $tempContainer 2>$null | Out-Null
    }
}