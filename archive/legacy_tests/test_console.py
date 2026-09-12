from lcars.service.console import LCARSConsole


def test_console_help_and_status_execute_without_signal_errors():
    console = LCARSConsole()

    output = []
    console.Execute("help", output.append)
    assert output, "help command should produce output"
    assert any("LCARS CONSOLE" in line for line in output)

    status = []
    console.Execute("status", status.append)
    assert status, "status command should produce output"
    assert any("[OK]" in line or "[ERROR]" in line for line in status)
