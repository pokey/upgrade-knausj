import typer

app = typer.Typer()


@app.command()
def main():
    """
    Upgrade knausj
    """
    typer.echo("FIXME: do upgrade")
