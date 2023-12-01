from openpyxl.styles import Alignment, Border, Side, PatternFill, NamedStyle
from openpyxl.styles.colors import Color

color_fills={
        "grey": PatternFill(patternType='solid', fgColor=Color('D9D9D9')),
        "findings_identified": PatternFill(patternType='solid', fgColor=Color('C5D9F1')),
        "apricot": PatternFill(patternType='solid', fgColor=Color('FCD5B4')),
        "user_notes": PatternFill(patternType='solid', fgColor=Color('DAEEF3')),
        "light_grey_band": PatternFill(patternType='solid', fgColor=Color('E9E9E9')),
    }

border = Border(left=Side(style='thin'), 
        right=Side(style='thin'), 
        top=Side(style='thin'), 
        bottom=Side(style='thin'))

vsmt_style_wrap_top=NamedStyle(name="vsmt_style_wrap_top")
vsmt_style_wrap_top.alignment=Alignment(wrap_text=True, vertical='top')

vsmt_style_grey_row=NamedStyle(name="vsmt_style_grey_row")
vsmt_style_grey_row.fill=color_fills["grey"]
vsmt_style_grey_row.border=border