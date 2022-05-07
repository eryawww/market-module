import typer

app = typer.Typer()

@app.command()
def update(symbol: str):
    """
        Update the symbol
    """
    print(f"Updating {symbol}")
    download_data(symbol)

if __name__ == "__main__":
    app()

def download_data(symbol: str):
    """
        Download the data for the symbol
    """
    print(f"Downloading {symbol}")