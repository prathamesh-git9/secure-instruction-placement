param(
    [Parameter(Mandatory = $true)]
    [string]$Upstream
)

$ErrorActionPreference = "Stop"
$conditions = @("control", "task_only", "repository_only", "task_and_repository")
$tasks = @(
    "DeserializationPyYAML",
    "CommandInjectionSubprocessRun",
    "CodeInjectionEval"
)
$failures = @()

foreach ($task in $tasks) {
    foreach ($condition in $conditions) {
        $slug = "2026-08-10-writable-$task-$condition"
        $workspace = "pilots\$slug\workspace"
        $artifact = "pilots\$slug\artifact"
        $recordPath = "$artifact\record.json"
        if (Test-Path -LiteralPath $recordPath) {
            Write-Output "$task,$condition,existing-record"
            continue
        }

        $arguments = @(
            "scripts\run_agent_experiment.py",
            "--upstream", $Upstream,
            "--task", $task,
            "--condition", $condition,
            "--conditions", "configs\conditions.json",
            "--agent-config", "configs\agents.pilot.json",
            "--agent", "codex_cli_luna_medium_writable",
            "--workspace", $workspace,
            "--artifact-dir", $artifact,
            "--run-id", "pilot-20260810-writable-$task-$condition-01",
            "--endpoint", "http://localhost:24684",
            "--agent-timeout", "600",
            "--verifier-timeout", "180",
            "--pilot-only"
        )
        & python @arguments | Out-Null
        $exitCode = $LASTEXITCODE
        if (-not (Test-Path -LiteralPath $recordPath)) {
            $failures += "$task`:$condition`:no-record"
            Write-Output "$task,$condition,exit=$exitCode,no-record"
            continue
        }
        $record = Get-Content -LiteralPath $recordPath -Raw | ConvertFrom-Json
        Write-Output (
            "$task,$condition,exit=$exitCode,functional=$($record.functional_pass)," +
            "security=$($record.security_pass),state=$($record.exit_state)"
        )
        if ($record.exit_state -ne "completed") {
            $failures += "$task`:$condition`:$($record.exit_state)"
        }
    }
}

if ($failures.Count -gt 0) {
    Write-Output "PILOT_FAILURES=$($failures -join ';')"
    exit 2
}
Write-Output "PILOT_EXECUTION=COMPLETE"

