from pathlib import Path

import bibtexparser
import dataset
import typer
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

app = typer.Typer()


@app.command()
def convert(
    bibtex_file: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, resolve_path=True),
    sqlite_file: Path = typer.Argument(..., exists=False, file_okay=True, dir_okay=False, resolve_path=True),
):
    """Convert a bibtex file to sqlite"""
    typer.echo(f"Opening {bibtex_file} ...")
    with bibtex_file.open() as f:
        typer.echo(f"Parsing bibtex ...")
        parser = BibTexParser()
        parser.customization = convert_to_unicode
        bibtex_db = bibtexparser.load(f, parser=parser)

    for entry in bibtex_db.entries:
        entry["citekey"] = entry.pop("ID", None)
        entry["mendeleytags"] = entry.pop("mendeley-tags", None)

    typer.echo(f"Creating {sqlite_file}")
    with dataset.connect(f"sqlite:///{sqlite_file}") as tx:
        typer.echo(f"Writing {len(bibtex_db.entries)} records ...")
        bibliography = tx.create_table("bibliography", primary_id="sqliteID")
        bibliography.insert_many(bibtex_db.entries)
    typer.echo(f"Done.")


if __name__ == "__main__":
    typer.run(convert)
