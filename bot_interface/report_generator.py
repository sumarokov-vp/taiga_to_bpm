# Standard Library
import os
from decimal import Decimal
from enum import Enum

# Third Party Stuff
import validators
from prettytable import PrettyTable
from telebot.types import Message  # type: ignore[import-untyped]

# My Stuff
from bot_interface.bot_instance import (
    bot,
    replace_reserved_characters,
)
from bot_interface.pdf_output import make_pdf_report
from core.models import User
from db.db_worker import (
    get_all,
    get_one,
    query_columns,
)


class ReportEngine(Enum):
    """
    Report engines.
    Used for determining report output format (pdf, md, or raw telegram text)
    Stored in database bot_reports.report_engine column as string ReportEngine.value
    """

    PDF = "pdf"
    MD = "md"
    RAW = "raw"


def generate_report(user: User) -> Message:
    """
    Generate and send report to user telegram chat
    returns telegram message
    """
    chat_id = user.chat_id
    if not user.bot_state_value:
        return bot.send_message(
            chat_id=chat_id,
            text="Error: no report selected",
        )
    report_id = user.bot_state_value

    """
    Get report (query, name, engine, slug)
    slug is used for filename creation
    report_engine is used for determining report output format (pdf, md)
    report name is used for report title
    """
    query = """
    SELECT report_query, "name", report_engine, slug
    FROM bot_reports
    WHERE id = %(report_id)s
    """
    args = {"report_id": report_id}
    report_query_row = get_one(query, args)
    if not report_query_row:
        return bot.send_message(
            chat_id=chat_id,
            text="Error: report not found in database",
        )
    report_query: str = str(report_query_row[0])
    report_name: str = report_query_row[1]
    report_engine: str = report_query_row[2]
    slug: str = report_query_row[3]

    columns = query_columns(report_query)

    report_result_rows = get_all(report_query)
    if not report_result_rows:
        return bot.send_message(chat_id, "No data")

    # convert Tuples collection to list
    # result_list = [list(row) for row in report_result_rows]

    # convert cells to strings and result to list of lists
    result_list: list[list[str]] = []
    for row_tuple in report_result_rows:
        list_row = list(row_tuple)
        for i, cell in enumerate(list_row):
            if cell:
                list_row[i] = str(cell)
        result_list.append(list_row)

    # Calculate total
    # if last column is numeric sum it
    # if not just add empty string
    total = Decimal("0.0")
    total_footer: list[str] = []
    for row in result_list:
        try:
            total += Decimal(row[-1])
        except Exception:
            pass
    for cell in columns:
        total_footer.append("-")
    total_footer[-1] = str(total)
    total_footer[0] = "Total"

    # Replace reserved characters for markdown
    for row in result_list:
        for i, cell in enumerate(row):
            if cell:
                if not validators.url(cell):
                    row[i] = replace_reserved_characters(cell)

    # Make url links clickable for markdown -> pdf
    for row in result_list:
        for i, cell in enumerate(row):
            if validators.url(cell):
                row[i] = f"[link]({cell})"

    # Generate report based on engine
    match report_engine:
        case ReportEngine.PDF.value:
            # make file name
            file_name = slug + ".pdf"
            full_path = os.path.join(os.getcwd(), file_name)

            # Generate report file
            make_pdf_report(
                footers=total_footer,
                title=report_name,
                headers=columns,
                data=result_list,
                output_file=full_path,
            )

            # Send file
            return bot.send_document(chat_id, open(full_path, "rb"))

        case ReportEngine.MD.value:
            result_list.append(total_footer)

            table = PrettyTable()
            table.title = report_name
            all_columns = []
            for column in columns:
                all_columns.append(column[0])
            table.field_names = all_columns
            for i, row in enumerate(result_list):
                if i == len(result_list) - 2:
                    table.add_row(row, divider=True)
                else:
                    table.add_row(row)
            response = "```\n{}```".format(table.get_string())
            return bot.send_message(chat_id, response, parse_mode="MarkdownV2")

        case ReportEngine.RAW.value:
            text = ""
            for row in result_list:
                for cell in row:
                    text += f"{cell}\t"
                text += "\n"
            return bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="MarkdownV2",
            )

    return bot.send_message(chat_id, "Unknown report engine")
