"""Minimal XLSX writer using inline strings and standard-library OOXML."""
from __future__ import annotations
from datetime import date, datetime
from numbers import Number
from pathlib import Path
from xml.sax.saxutils import escape
import math
import zipfile

MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_DOC = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL_PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
CONTENT = "http://schemas.openxmlformats.org/package/2006/content-types"


def _column_name(index: int) -> str:
    result = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def _cell(ref, value):
    if value is None:
        return ""
    try:
        if value != value:  # NaN
            return ""
    except Exception:
        pass
    if isinstance(value, bool):
        return f'<c r="{ref}" t="b"><v>{int(value)}</v></c>'
    if isinstance(value, Number):
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            return ""
        return f'<c r="{ref}"><v>{value}</v></c>'
    if isinstance(value, (datetime, date)):
        value = value.isoformat()
    text = str(value)
    # XML 1.0 does not allow most ASCII control characters.
    text = "".join(ch for ch in text if ch in "\t\n\r" or ord(ch) >= 32)
    preserve = ' xml:space="preserve"' if text[:1].isspace() or text[-1:].isspace() else ""
    return f'<c r="{ref}" t="inlineStr"><is><t{preserve}>{escape(text)}</t></is></c>'


def write_xlsx(tables, destination):
    destination = Path(destination)
    count = len(tables)
    if not count:
        raise ValueError("At least one worksheet is required")
    sheet_names = [f"table_{i}"[:31] for i in range(count)]
    content_overrides = [
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
    ]
    workbook_sheets = []
    workbook_rels = []
    for i, name in enumerate(sheet_names, start=1):
        content_overrides.append(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
        workbook_sheets.append(f'<sheet name="{escape(name)}" sheetId="{i}" r:id="rId{i}"/>')
        workbook_rels.append(f'<Relationship Id="rId{i}" Type="{REL_DOC}/worksheet" Target="worksheets/sheet{i}.xml"/>')
    workbook_rels.append(f'<Relationship Id="rId{count+1}" Type="{REL_DOC}/styles" Target="styles.xml"/>')
    content_overrides.append('<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>')
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="{CONTENT}"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>{"".join(content_overrides)}</Types>')
        archive.writestr("_rels/.rels", f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{REL_PKG}"><Relationship Id="rId1" Type="{REL_DOC}/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        archive.writestr("xl/workbook.xml", f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="{MAIN}" xmlns:r="{REL_DOC}"><sheets>{"".join(workbook_sheets)}</sheets></workbook>')
        archive.writestr("xl/_rels/workbook.xml.rels", f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{REL_PKG}">{"".join(workbook_rels)}</Relationships>')
        archive.writestr("xl/styles.xml", f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="{MAIN}"><fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts><fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills><borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>')
        for sheet_no, table in enumerate(tables, start=1):
            columns = list(table.columns)
            xml_rows = []
            header_cells = "".join(_cell(f"{_column_name(j)}1", label) for j, label in enumerate(columns, 1))
            xml_rows.append(f'<row r="1">{header_cells}</row>')
            for row_no, values in enumerate(table.itertuples(index=False, name=None), start=2):
                cells = "".join(_cell(f"{_column_name(j)}{row_no}", value) for j, value in enumerate(values, 1))
                xml_rows.append(f'<row r="{row_no}">{cells}</row>')
            last_col = _column_name(max(1, len(columns)))
            xml = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="{MAIN}"><dimension ref="A1:{last_col}{len(table)+1}"/><sheetViews><sheetView workbookViewId="0"/></sheetViews><sheetFormatPr defaultRowHeight="15"/><sheetData>{"".join(xml_rows)}</sheetData><pageMargins left="0.7" right="0.7" top="0.75" bottom="0.75" header="0.3" footer="0.3"/></worksheet>'
            archive.writestr(f"xl/worksheets/sheet{sheet_no}.xml", xml)
    return destination
