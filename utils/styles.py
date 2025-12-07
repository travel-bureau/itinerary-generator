from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont

def register_styles():
    pdfmetrics.registerFont(TTFont("Symbola", "fonts/Symbola.ttf"))
    pdfmetrics.registerFont(TTFont("Montserrat", "fonts/Montserrat-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("Merienda", "fonts/Merienda-SemiBold.ttf"))
    pdfmetrics.registerFont(TTFont("Poppins", "fonts/Poppins-SemiBold.ttf"))
    pdfmetrics.registerFont(TTFont("Paprika", "fonts/Paprika-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("FacultyGlyphic", "fonts/FacultyGlyphic-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("Sansation", "fonts/Sansation-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("FiraSans", "fonts/FiraSans-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("FiraSans-Bold", "fonts/FiraSans-SemiBold.ttf"))
    pdfmetrics.registerFont(TTFont("FiraSans-Italic", "fonts/FiraSans-Italic.ttf"))

    registerFontFamily("FiraSans", normal="FiraSans", bold="FiraSans-Bold")

    THEME_COLOR = colors.HexColor("#7E952E")
    EMOJI_COLOR = colors.HexColor("#423904")

    emoji_style = ParagraphStyle(
        name="EmojiText",
        fontName="Symbola",
        fontSize=12,
        leading=14,
        spaceAfter=6,
        alignment=TA_LEFT,
        textColor=EMOJI_COLOR
    )

    link_style = ParagraphStyle(
        name="LinkText",
        fontName="Symbola",
        fontSize=12,
        leading=14,
        spaceAfter=6,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#002759")
    )

    heading_style = ParagraphStyle(
        name="CenterHeading",
        alignment=TA_CENTER,
        fontName="Merienda",
        fontSize=18,
        spaceAfter=14,
        leading=22,
        textColor=THEME_COLOR
    )

    sub_heading_style = ParagraphStyle(
        name="SubHeading",
        alignment=TA_CENTER,
        fontName="Sansation",
        fontSize=16,
        spaceAfter=14,
        leading=22,
        textColor=THEME_COLOR
    )

    day_style = ParagraphStyle(
        name="DayHeading",
        alignment=TA_LEFT,
        fontName="Paprika",
        fontSize=14,
        spaceAfter=8,
        leading=18,
        textColor=THEME_COLOR
    )

    normal_style = ParagraphStyle(
        name="NormalText",
        alignment=TA_LEFT,
        fontName="FiraSans",
        fontSize=12,
        spaceAfter=6,
        leading=16
    )

    small_style = ParagraphStyle(
        name="SmallText",
        alignment=TA_LEFT,
        fontName="FiraSans",
        fontSize=10,
        spaceAfter=4,
        leading=14,
        textColor=colors.HexColor("#555555")
    )

    return emoji_style, link_style, heading_style, sub_heading_style, day_style, normal_style, small_style, THEME_COLOR, EMOJI_COLOR