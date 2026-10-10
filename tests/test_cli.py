from click.testing import CliRunner
from tasklite.cli import cli

def test_cli_enqueue():
    runner = CliRunner()
    result = runner.invoke(cli, ['enqueue', '--handler', 'mock_email', '--payload', '{"to": "user@example.invalid"}'])
    assert result.exit_code == 0
    assert "Enqueued job" in result.output

def test_cli_list_and_status():
    runner = CliRunner()
    enq_res = runner.invoke(cli, ['enqueue', '--handler', 'mock_email'])
    assert enq_res.exit_code == 0
    job_id = enq_res.output.strip().split()[-1]
    
    status_res = runner.invoke(cli, ['status', job_id])
    assert status_res.exit_code == 0
    assert '"status": "queued"' in status_res.output
    
    list_res = runner.invoke(cli, ['list'])
    assert list_res.exit_code == 0
    assert job_id in list_res.output

def test_cli_cancel():
    runner = CliRunner()
    enq_res = runner.invoke(cli, ['enqueue', '--handler', 'mock_email'])
    job_id = enq_res.output.strip().split()[-1]
    
    cancel_res = runner.invoke(cli, ['cancel', job_id])
    assert cancel_res.exit_code == 0
    assert f"Cancelled job {job_id}" in cancel_res.output

def test_cli_worker_burst():
    runner = CliRunner()
    runner.invoke(cli, ['enqueue', '--handler', 'mock_email'])
    worker_res = runner.invoke(cli, ['worker', '--burst'])
    assert worker_res.exit_code == 0

def test_cli_stats():
    runner = CliRunner()
    runner.invoke(cli, ['enqueue', '--handler', 'mock_email'])
    res = runner.invoke(cli, ['stats'])
    assert res.exit_code == 0
    assert '"total"' in res.output
    assert '"queued"' in res.output
