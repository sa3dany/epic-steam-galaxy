# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------
from click import echo, style


# ----------------------------------------------------------------------
# Utility functions
# ----------------------------------------------------------------------
def echo_error(message):
    echo(f"[{style('error', fg='red')}] {message}", err=True)


def echo_info(message):
    echo(f"[{style('info', fg='blue')}] {message}")


def quote_string(string):
    return '"' + string + '"'


def unquote_string(quoted_string):
    return quoted_string[1:-1]
