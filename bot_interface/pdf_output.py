# Standard Library
from typing import Sequence

# Third Party Stuff
import pypandoc


def make_pdf_report(
    title: str,
    headers: Sequence,
    data: Sequence,
    footers: Sequence,
    output_file: str,
):
    table = array_to_md_table(
        array=data,
        headers=headers,
        footers=footers,
    )
    report = f"# {title}\n{table}"
    print(report)
    make_pdf_from_markdown(report, output_file)


def make_pdf_from_markdown(markdown: str, output_file: str):
    """
    Args:
        markdown: The markdown string to convert to pdf.
        output_file: The path to the output file.
    """
    header = """---
header-includes:
  - \\setmainfont{DejaVuSansMono}
---\n"""
    print(header + markdown)
    pypandoc.convert_text(
        source=header + markdown,
        to="pdf",
        format="md",
        outputfile=output_file,
        extra_args=[
            "--pdf-engine=xelatex",
        ],
    )


def array_to_md_table(array: Sequence, headers: Sequence, footers: Sequence) -> str:
    """
    Args:
        array: The array to convert to a markdown table.
        align: The alignment of the table.
    Returns:
        The markdown table.
    """
    table = "\n"
    for i, cell in enumerate(headers):
        if i == 0:
            table += f"{cell} "
        else:
            table += f"| {cell} "
    table += "\n"
    for i, cell in enumerate(headers):
        if i == 0:
            table += (len(str(cell)) + 1) * "-"
        else:
            table += "|"
            table += (len(str(cell)) + 2) * "-"
    table += "\n"

    for i, row in enumerate(array):
        for i, cell in enumerate(row):
            if i == 0:
                table += f"{cell} "
            else:
                table += f"| {cell} "
        table += "\n"
    for i, cell in enumerate(headers):
        if i == 0:
            table += (len(str(cell)) + 1) * "="
        else:
            table += "|"
            table += (len(str(cell)) + 2) * "="
    table += "\n"
    for i, cell in enumerate(footers):
        if i == 0:
            table += f"{cell} "
        else:
            table += f"| {cell} "
    return table


if __name__ == "__main__":
    headers = ["Name", "Age", "City"]
    array = [
        ["Alice in the wonderland", "24", "New York"],
        ["Лена", "19", "Paris"],
        ["Charlie", "32", "Madrid"],
    ]
    footers = ["Total", "75", "Paris"]

    make_pdf_report(
        title="Отчет по городам",
        headers=headers,
        data=array,
        footers=footers,
        output_file="temp/test_2.pdf",
    )
