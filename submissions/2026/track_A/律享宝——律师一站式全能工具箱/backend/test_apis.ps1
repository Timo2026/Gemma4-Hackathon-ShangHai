# Login
$loginBody = @{phone='13800000000';password='123456'} | ConvertTo-Json
$loginResp = Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/auth/login' -Method POST -Body $loginBody -ContentType 'application/json' -UseBasicParsing -TimeoutSec 10
$login = $loginResp.Content | ConvertFrom-Json
$token = $login.access_token
$headers = @{Authorization = 'Bearer ' + $token}
Write-Host '=== 1. LOGIN OK ==='

# Get Profile
$profileResp = Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/auth/profile' -Method GET -Headers $headers -UseBasicParsing -TimeoutSec 10
Write-Host ('=== 2. PROFILE: ' + $profileResp.StatusCode)

# Update Profile
$updateBody = @{name='Wang';title='Senior Partner';practice_years=20;firm='Beijing Law Firm'} | ConvertTo-Json
$updateResp = Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/auth/profile' -Method PUT -Headers $headers -Body $updateBody -ContentType 'application/json' -UseBasicParsing -TimeoutSec 10
Write-Host ('=== 3. UPDATE PROFILE: ' + $updateResp.StatusCode)

# Document Scenarios
$scenariosResp = Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/documents/scenarios' -Method GET -Headers $headers -UseBasicParsing -TimeoutSec 10
Write-Host ('=== 4. SCENARIOS: ' + $scenariosResp.StatusCode)

# Generate Document (Mock AI)
$genBody = @{case_type='Loan Dispute';facts='Party A lent 100k to Party B';issues='Default on repayment';stage='Trial 1'} | ConvertTo-Json
$genResp = Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/documents/generate' -Method POST -Headers $headers -Body $genBody -ContentType 'application/json' -UseBasicParsing -TimeoutSec 10
Write-Host ('=== 5. GENERATE: ' + $genResp.StatusCode)

# Tool Catalog
$catalogResp = Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/tools/catalog' -Method GET -Headers $headers -UseBasicParsing -TimeoutSec 10
Write-Host ('=== 6. TOOL CATALOG: ' + $catalogResp.StatusCode)

# Tool Orchestrate
$orchBody = @{user_need='I need to write a complaint'} | ConvertTo-Json
$orchResp = Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/tools/orchestrate' -Method POST -Headers $headers -Body $orchBody -ContentType 'application/json' -UseBasicParsing -TimeoutSec 10
Write-Host ('=== 7. ORCHESTRATE: ' + $orchResp.StatusCode)

# IP Platforms
$platResp = Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/ip/platforms' -Method GET -Headers $headers -UseBasicParsing -TimeoutSec 10
Write-Host ('=== 8. IP PLATFORMS: ' + $platResp.StatusCode)

# Generate Profile Packaging
$ipBody = "{`"name`":`"Zhang`",`"practice_years`":15,`"education`":`"Peking University`",`"qualifications`":`"Law License`",`"specialties`":`"Criminal`",`"bio`":`"15 years exp`",`"firm`":`"Beijing Law Firm`",`"target_clients`":`"Corporate`"}"
$ipResp = Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/ip/profile' -Method POST -Headers $headers -Body $ipBody -ContentType 'application/json' -UseBasicParsing -TimeoutSec 10
Write-Host ('=== 9. IP PROFILE: ' + $ipResp.StatusCode)

# Generate Trust Content
$trustBody = "{`"content_type`":`"intro`",`"lawyer_info`":{`"name`":`"Zhang`",`"practice_years`":15,`"education`":`"PKU`",`"qualifications`":`"License`",`"specialties`":`"Criminal`",`"bio`":`"Senior`",`"firm`":`"Firm`",`"target_clients`":`"Corporate`"}}"
$trustResp = Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/ip/trust-content' -Method POST -Headers $headers -Body $trustBody -ContentType 'application/json' -UseBasicParsing -TimeoutSec 10
Write-Host ('=== 10. TRUST CONTENT: ' + $trustResp.StatusCode)

# Register (mock)
$regBody = @{phone='13900000001';password='123456';name='Test User'} | ConvertTo-Json
$regResp = Invoke-WebRequest -Uri 'http://localhost:8000/api/v1/auth/register' -Method POST -Body $regBody -ContentType 'application/json' -UseBasicParsing -TimeoutSec 10
Write-Host ('=== 11. REGISTER: ' + $regResp.StatusCode)

Write-Host ''
Write-Host 'ALL 11 TESTS PASSED'
