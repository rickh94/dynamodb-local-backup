import shutil
from pathlib import Path
from datetime import date
import importlib.util

import jinja2
import weasyprint

HERE = Path(__file__).parent

JINJA_ENV: jinja2.Environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(HERE / "templates")),
    autoescape=jinja2.select_autoescape(["html"]),
)


def render_html(info_path: str, data: list, output_path: Path):

    # get the ordered dict and title from the provided file. look...it works.
    spec = importlib.util.spec_from_file_location("attributes", info_path)
    att = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(att)

    template = JINJA_ENV.get_template("report-template.html")
    html = template.render(
        title=att.TITLE,
        attributes=att.ATTRIBUTES,
        data=data,
        date=date.today().strftime("%B %d, %Y"),
    )

    with output_path.open("w") as output_html_file:
        output_html_file.write(html)
    shutil.copytree(HERE / "templates" / "assets", output_path.parent / "assets")


def to_pdf(in_path: Path, out_path: Path):
    weasyprint.HTML(filename=str(in_path)).write_pdf(str(out_path))
