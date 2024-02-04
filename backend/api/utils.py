from decimal import Decimal
import io
from pathlib import Path
import re

from borb import pdf
from borb.io.write.any_object_transformer import AnyObjectTransformer
from borb.io.write.transformer import WriteTransformerState
from borb.pdf import Alignment
from borb.pdf.canvas.font.simple_font.true_type_font import TrueTypeFont
from django.contrib.staticfiles import finders

FORMAT_STRING = '{name} ({measurement_unit}) - {amount}'
SPLIT_REGEX = re.compile('(?<=.)(?=[A-Z])')
FONT_FILE = 'fonts/arialnova_light.ttf'


def save_pdf(file, document):
    """Save document object to given file."""
    AnyObjectTransformer().transform(
        object_to_transform=document,
        context=WriteTransformerState(
            root_object=document,
            destination=file,
        ),
        destination=file,
    )


def get_pdf(ingredients, format_string=None, font_path=None):
    """
    Construct PDF file with ingredients list.

    Parameters
    ----------
    ingredients : dict
        Dictionary with ingredients ids.
        Dictionary items must have the same parameters as `format_string`.
    format_string : str
        Format string to represent ingredients as text list items.
        By default '{name} ({measurement_unit}) - {amount}'.
    font_path : Path
        Path to ttf file. By default uses arialnova_light font from app
        static/fonts. Standart PDF fonts can't display cirilyc latters.

    Returns
    -------
    BytesIO
        Buffer with PDF file.
    """
    if format_string is None:
        format_string = FORMAT_STRING
    if font_path is None:
        font_path = Path(finders.find(FONT_FILE))
    document = pdf.Document()
    page = pdf.Page()
    document.add_page(page)
    layout = pdf.SingleColumnLayout(page)
    custom_font = TrueTypeFont.true_type_font_from_file(font_path)
    layout.add(pdf.Paragraph(
        'Список покупок',
        font_size=Decimal(20),
        font=custom_font,
        horizontal_alignment=Alignment.CENTERED
    ))
    pdf_list = pdf.UnorderedList()
    for ingredient in ingredients.values():
        pdf_list.add(pdf.Paragraph(
            format_string.format(**ingredient),
            font=custom_font
        ))
    layout.add(pdf_list)
    buffer = io.BytesIO()
    save_pdf(buffer, document)
    buffer.seek(0)
    return buffer


def class_name(name):
    """Split class name by capital latters."""
    return ' '.join(re.split(SPLIT_REGEX, name))
