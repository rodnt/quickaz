import typer

def color_good(text: str):

    message_start = ""

    if text:
        ending = typer.style(text, fg=typer.colors.GREEN, bold=True)
    
    message = message_start + ending
    return message

def color_bad(text: str):
    message_start = ""

    if text:
        ending = typer.style(text, fg=typer.colors.WHITE, bg=typer.colors.RED)
    
    message = message_start + ending
    return message

def color_found(text: str):

    message_start = ""

    if text:
        ending = typer.style(text, fg=typer.colors.MAGENTA, bold=True)
    
    message = message_start + ending
    return message

def color_info(text: str):

    message_start = ""

    if text:
        ending = typer.style(text, fg=typer.colors.WHITE, bold=True)
    
    message = message_start + ending
    return message

def color_collect(text: str):

    message_start = ""

    if text:
        ending = typer.style(text, fg=typer.colors.YELLOW, bold=True)
    
    message = message_start + ending
    return message