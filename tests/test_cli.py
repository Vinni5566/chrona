from typer.testing import CliRunner
from chrona.cli.commands import app

runner = CliRunner()

def test_scan_cli():
    result = runner.invoke(app, ["scan", "."])
    assert result.exit_code == 0
    assert "Scanning repository at" in result.stdout
