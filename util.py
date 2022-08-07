from click import echo, style


def echo_error(message):
    echo(f"[{style('error', fg='red')}] {message}", err=True)


def quote_string(string):
    return '"' + string + '"'


def unquote_string(quoted_string):
    return quoted_string[1:-1]
