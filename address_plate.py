from argparse import ArgumentParser
import io
import pickle
import re
from reportlab.pdfgen import canvas
from reportlab.lib.colors import PCMYKColor
import sys
import textwrap


def pt(mm: float) -> float:
    """ mm to pt
    """
    return mm*2.834645669  # 72/25.4


def _load_path():
    with open('paths' + '.pkl', 'rb') as f:
        return pickle.load(f)


THIN = 'thin'
WIDE = 'wide'

COLOR_WHITE = PCMYKColor(0, 0, 0, 0)
COLOR_DARK_BLUE = PCMYKColor(75, 65, 0, 75)
# пока будет так, если цвета не подойдут поменяю

HOUSE_NUMBER_RE_TUPLE = (
    re.compile(r'^(?P<lvl1>[1-9]\d*(-[1-9]\d*)?)$'),
    re.compile(r'^(?P<lvl1>[1-9]\d*(-[1-9]\d*)?)(?P<lvl2c>[А-Я]+)$'),
    re.compile(r'^(?P<lvl1>[1-9]\d*(-[1-9]\d*)?)(?P<lvl2_slash>/)(?P<lvl2s>[1-9]\d*)(?P<lvl3>[А-Я]*)$'),
    re.compile(r'^(?P<lvl1>[1-9]\d*(-[1-9]\d*)?)(?P<lvl2c> к[1-9]\d*)$'),
)

HOUSE_NUMBER_ARROW_RE_TUPLE = (
    re.compile(r'(?P<lvl_a1>^[1-9]\d*(-[1-9]\d*)?)(?P<lvl_a2c>[А-Я]+)?$'),
)

LVL1 = 'lvl1'  # (основной)
SLASH = 'lvl2_slash'
LVL2C = 'lvl2c'  # (литера)
LVL2S = 'lvl2s'  # (номер после дроби)
LVL3 = 'lvl3'  # (Літера номеру після дробу)
LVL_A1 = 'lvl_a1'
LVL_A2C = 'lvl_a2c'

SIZES_PT = {

    'thin_round_radius': pt(15.0),
    'wide_round_radius': pt(22.5),

    'thin_margin': pt(40),
    'thin_height': pt(215),

    'wide_margin': pt(60),
    'wide_height': pt(320),

    'thin_street_type_font': {'face': 'regular', 'size': 90.0},
    'thin_street_type_bl': pt(215-173),
    'thin_street_name_font': {'face': 'semi-bold', 'size': 220.0},
    'thin_street_name_bl': pt(215-94),
    'thin_street_line_width': 4.0,
    'thin_street_line_bl': pt(215-62),
    'thin_street_translit_font': {'face': 'regular', 'size': 90.0},
    'thin_street_translit_bl': pt(215-24),

    'wide_street_type_font': {'face': 'regular', 'size': 135.0},
    'wide_street_type_bl': pt(320-260),
    'wide_street_name_font': {'face': 'semi-bold', 'size': 330.0},
    'wide_street_name_bl': pt(320-140),
    'wide_street_line_width': 6.0,
    'wide_street_line_bl': pt(320-92),
    'wide_street_translit_font': {'face': 'regular', 'size': 135.0},
    'wide_street_translit_bl': pt(320-36),

    'thin_house_number_width': (pt(215), pt(280), pt(380), pt(440), pt(520)),
    'thin_house_number_bl': pt(215-50),
    'thin_house_number_font_lvl1': {'face': 'semi-bold', 'size': 480.0},
    'thin_house_number_font_lvl2c': {'face': 'bold', 'size': 300.0},
    'thin_house_number_font_lvl2s': {'face': 'semi-bold', 'size': 300.0},
    'thin_house_number_font_lvl3': {'face': 'semi-bold', 'size': 220.0},
    'thin_house_number_slash_size': {'face': 'slash', 'size': 80},
    # 'thin_house_number_slash_size': (pt(12), 75, pt(80), pt(6)),

    'wide_house_number_width': (pt(320), pt(420), pt(565), pt(640), pt(720)),
    'wide_house_number_bl': pt(320-75),
    'wide_house_number_font_lvl1': {'face': 'semi-bold', 'size': 720.0},
    'wide_house_number_font_lvl2c': {'face': 'bold', 'size': 450.0},
    'wide_house_number_font_lvl2s': {'face': 'bold', 'size': 450.0},
    'wide_house_number_font_lvl3': {'face': 'bold', 'size': 330.0},
    'wide_house_number_slash_size': {'face': 'slash', 'size': 125},
    # 'wide_house_number_slash_size': (pt(20), 75, pt(125), pt(9)),

    'thin_house_number_arrow_width': (pt(215), pt(215), pt(280), pt(340), pt(440)),
    'thin_house_number_arrow_bl': pt(215 - 90),
    'thin_house_number_arrow_font_lvl1': {'face': 'semi-bold', 'size': 380.0},
    'thin_house_number_arrow_font_lvl2c': {'face': 'bold', 'size': 240.0},
    'thin_house_number_arrow_font_lvl2s': {'face': 'bold', 'size': 240.0},
    'thin_house_number_arrow_font_lvl3': {'face': 'semi-bold', 'size': 140.0},
    'thin_house_number_arrow_slash_size': {'face': 'slash', 'size': 65},
    # 'thin_house_number_arrow_slash_size': (pt(10), 75, pt(65), pt(5)),
    'thin_house_number_arrow_arrow_bl': pt(215-62),
    'thin_house_number_arrow_arrow_size': {'line_width': 4, 'length': pt(9.8),
                                           'half_height': pt(8.5/2), 'half_space': pt(15/2)},
    'thin_house_number_arrow_number_bl': pt(215-24),
    'thin_house_number_arrow_number_font_lvl_a1': {'face': 'regular', 'size': 90.0},
    'thin_house_number_arrow_number_font_lvl_a2c': {'face': 'semi-bold', 'size': 50.0},

    'wide_house_number_arrow_width': (pt(320), pt(320), pt(420), pt(510), pt(660)),
    'wide_house_number_arrow_bl': pt(320 - 135),
    'wide_house_number_arrow_font_lvl1': {'face': 'semi-bold', 'size': 570.0},
    'wide_house_number_arrow_font_lvl2c': {'face': 'bold', 'size': 330.0},
    'wide_house_number_arrow_font_lvl2s': {'face': 'bold', 'size': 330.0},
    'wide_house_number_arrow_font_lvl3': {'face': 'bold', 'size': 210.0},
    'wide_house_number_arrow_slash_size': {'face': 'slash', 'size': 98},
    # 'wide_house_number_arrow_slash_size': (pt(12), 75, pt(98), pt(7.5)),
    'wide_house_number_arrow_arrow_bl': pt(320-94),
    'wide_house_number_arrow_arrow_size': {'line_width': 6, 'length': pt(18.8),
                                           'half_height': pt(14.8/2), 'half_space': pt(22.5/2)},
    'wide_house_number_arrow_number_bl': pt(320-37),
    'wide_house_number_arrow_number_font_lvl_a1': {'face': 'regular', 'size': 135.0},
    'wide_house_number_arrow_number_font_lvl_a2c': {'face': 'semi-bold', 'size': 75.0},

    'thin_vertical_width': pt(360),
    'thin_vertical_height': pt(480),
    'thin_vertical_margin': pt(36),
    'thin_vertical_street_type_font': {'face': 'regular', 'size': 65.0},
    'thin_vertical_street_type_bl': pt(36.0) + 32.625,
    'thin_vertical_street_name_font': {'face': 'semi-bold', 'size': 110.0, 'leading': 120.0},
    'thin_vertical_street_name_translate': pt(18) + 77.984375,
    'thin_vertical_street_line_width': pt(2.0),
    'thin_vertical_street_line_translate': pt(24.0),
    'thin_vertical_street_name_max_char': 15,
    'thin_vertical_street_translit_font': {'face': 'regular', 'size': 65.0, 'leading': 78.0},
    'thin_vertical_street_translit_translate': pt(24) + 32.625,
    'thin_vertical_street_translit_max_char': 30,
    'thin_vertical_house_number_bl': pt(480 - 48),
    'thin_vertical_house_number_font_lvl1': {'face': 'semi-bold', 'size': 540.0},
    'thin_vertical_house_number_font_lvl2c': {'face': 'bold', 'size': 312.0},
    'thin_vertical_house_number_font_lvl2s': {'face': 'bold', 'size': 312.0},
    'thin_vertical_house_number_font_lvl3': {'face': 'bold', 'size': 220.0},
    'thin_vertical_house_number_slash_size': {'face': 'slash', 'size': 80},
    # 'thin_vertical_house_number_slash_size': (pt(12), 75, pt(80), pt(6)),

    'wide_vertical_width': pt(540),
    'wide_vertical_height': pt(720),
    'wide_vertical_margin': pt(54),
    'wide_vertical_street_type_font': {'face': 'regular', 'size': 100.0},
    'wide_vertical_street_type_bl': pt(54.0) + 50.203125,
    'wide_vertical_street_name_font': {'face': 'semi-bold', 'size': 165.0, 'leading': 180.0},
    'wide_vertical_street_name_translate': pt(18) + 116.984375,
    'wide_vertical_street_name_max_char': 15,
    'wide_vertical_street_line_width': pt(3.0),
    'wide_vertical_street_line_translate': pt(36.0),
    'wide_vertical_street_translit_font': {'face': 'regular', 'size': 100.0, 'leading': 120.0},
    'wide_vertical_street_translit_translate': pt(57.0),
    'wide_vertical_street_translit_max_char': 30,
    'wide_vertical_house_number_bl': pt(720 - 72),
    'wide_vertical_house_number_font_lvl1': {'face': 'semi-bold', 'size': 810.0},
    'wide_vertical_house_number_font_lvl2c': {'face': 'bold', 'size': 470.0},
    'wide_vertical_house_number_font_lvl2s': {'face': 'bold', 'size': 470.0},
    'wide_vertical_house_number_font_lvl3': {'face': 'bold', 'size': 330.0},
    'wide_vertical_house_number_slash_size': {'face': 'slash', 'size': 80},
    # 'wide_vertical_house_number_slash_size': (pt(12), 75, pt(80), pt(6)),

}


def main():
    parser = ArgumentParser()

    parser.add_argument('--wide', help='Wide street', action='store_true')

    sub_parser = parser.add_subparsers(title='Address plate', description='Address plate description')

    street_name_parser = sub_parser.add_parser('name', help='Street name')
    street_name_parser.add_argument('--street_type', help='Street type', type=str, required=True)
    street_name_parser.add_argument('--street_name', help='Street name', type=str, required=True)
    street_name_parser.add_argument('--street_translit', help='Street translit', type=str, required=True)
    street_name_parser.set_defaults(func=StreetName)

    street_number_parser = sub_parser.add_parser('number', help='House number')
    street_number_parser.add_argument('--house_num', help='House number', type=str, required=True)
    street_number_parser.add_argument('--left_num', help='Left arrow', type=str)
    street_number_parser.add_argument('--right_num', help='Right arrow', type=str)
    street_number_parser.set_defaults(func=StreetNumber)

    vertical_parser = sub_parser.add_parser('vertical', help='Vertical')
    vertical_parser.add_argument('--street_type', help='Street type', type=str, required=True)
    vertical_parser.add_argument('--street_name', help='Street name', type=str, required=True)
    vertical_parser.add_argument('--street_translit', help='Street translit', type=str, required=True)
    vertical_parser.add_argument('--house_num', help='House number', type=str, required=True)
    vertical_parser.set_defaults(func=Vertical)

    args = parser.parse_args()
    func_args = dict(vars(args))
    func_args['wide'] = WIDE if args.wide else THIN
    del func_args['func']

    plate = args.func(**func_args)
    pdf = plate.pdf()

    if True:
        sys.stdout = sys.stdout.detach()
        sys.stdout.write(pdf.read())
    else:
        with open('test.pdf', 'wb') as out:
            out.write(pdf.read())


class BasePlate:

    def __init__(self):
        self.margin = self.width = self.height = self.radius = 0
        self.canvas = None
        self._init_margin()
        self._init_width()
        self._init_height()
        self._init_radius()
        self.width_without_margin = self.width - self.margin * 2

    def _init_margin(self):
        """ must be override in children class
        """
        pass

    def _init_width(self):
        """ must be override in children class
        """
        pass

    def _init_height(self):
        """ must be override in children class
        """
        pass

    def _init_radius(self):
        """ must be override in children class
        """
        pass

    def _draw_face(self):
        """ must be override in children class
        """
        pass

    def _draw_background(self):
        self.canvas.roundRect(0, 0, self.width, self.height, self.radius, stroke=0, fill=1)

    @staticmethod
    def parse_house_number(house_num_str, regex_tuple):

        for r in regex_tuple:
            match_res = r.match(house_num_str)
            if match_res:
                return match_res.groupdict()
        return None

    def pdf(self):
        pdf = io.BytesIO()
        self.canvas = canvas.Canvas(pdf, (self.width, self.height), bottomup=0)

        self.canvas.setFillColor(COLOR_DARK_BLUE)
        self._draw_background()

        self.canvas.setFillColor(COLOR_WHITE)
        self.canvas.setStrokeColor(COLOR_WHITE)
        self.canvas.translate(self.margin, 0)

        self._draw_face()

        self.canvas.showPage()
        self.canvas.save()
        self.canvas = None
        pdf.seek(0)
        return pdf


class StreetName(BasePlate):

    def __init__(self, street_type: str, street_name: str, street_translit: str, wide: str = THIN):
        self.street_type_text_path = TextPaths(text=street_type, font=SIZES_PT[f'{wide}_street_type_font'])
        self.street_name_text_path = TextPaths(text=street_name, font=SIZES_PT[f'{wide}_street_name_font'])
        self.street_translit_text_path = TextPaths(text=street_translit, font=SIZES_PT[f'{wide}_street_translit_font'])
        self.wide = wide
        super().__init__()

    def _init_margin(self):
        self.margin = SIZES_PT[f'{self.wide}_margin']

    def _init_width(self):
        self.width = ((max([text_path.get_path_extents()[2] for text_path in [
            self.street_translit_text_path, self.street_name_text_path, self.street_translit_text_path
        ]])+self.margin*0.7)//self.margin+2)*self.margin

    def _init_height(self):
        self.height = SIZES_PT[f'{self.wide}_height']

    def _init_radius(self):
        self.radius = SIZES_PT[f'{self.wide}_round_radius']

    def _draw_face(self):
        self._draw_street_type()
        self._draw_street_name()
        self._draw_line()
        self._draw_street_translit()

    def _draw_line(self):
        self.canvas.saveState()
        self.canvas.setLineWidth(SIZES_PT[f'{self.wide}_street_line_width'])
        self.canvas.line(0, SIZES_PT[f'{self.wide}_street_line_bl'],
                         self.width - SIZES_PT[f'{self.wide}_margin'] * 2, SIZES_PT[f'{self.wide}_street_line_bl'])
        self.canvas.restoreState()

    def _draw_street_type(self):
        self.canvas.saveState()
        self.canvas.translate(0, SIZES_PT[f'{self.wide}_street_type_bl'])
        self.street_type_text_path.draw(self.canvas)
        self.canvas.restoreState()

    def _draw_street_name(self):
        self.canvas.saveState()
        self.canvas.translate(0, SIZES_PT[f'{self.wide}_street_name_bl'])
        self.street_name_text_path.draw(self.canvas)
        self.canvas.restoreState()

    def _draw_street_translit(self):
        self.canvas.saveState()
        self.canvas.translate(0, SIZES_PT[f'{self.wide}_street_translit_bl'])
        self.street_translit_text_path.draw(self.canvas)
        self.canvas.restoreState()


class StreetNumber(BasePlate):

    def __init__(self, house_num: str, left_num: str = None, right_num: str = None, wide: str = THIN):
        self.house_num = house_num
        self.left_num = left_num
        self.right_num = right_num
        self.wide = wide
        self.arrow = '_arrow' if self.left_num or self.right_num else ''
        super().__init__()

    def _init_margin(self):
        self.margin = SIZES_PT[f'{self.wide}_margin']

    def _init_width(self):
        self.width = SIZES_PT[f'{self.wide}_house_number{self.arrow}_width'][min(len(self.house_num) - 1, 4)]

    def _init_height(self):
        self.height = SIZES_PT[f'{self.wide}_height']

    def _init_radius(self):
        self.radius = SIZES_PT[f'{self.wide}_round_radius']

    def _draw_face(self):
        self._draw_number()
        if self.left_num or self.right_num:
            self._draw_arrows()
        if self.left_num:
            self._draw_left_num()
        if self.right_num:
            self._draw_right_num()

    def _draw_number(self):

        house_number_dict = self.parse_house_number(self.house_num, HOUSE_NUMBER_RE_TUPLE)
        text_paths = {}
        house_number_width = 0
        
        for key in sorted(house_number_dict.keys()):
            font = SIZES_PT[f'{self.wide}_house_number{self.arrow}_font_{key}'] if key != SLASH else \
                SIZES_PT[f'{self.wide}_house_number_slash_size']
            text_paths[key] = TextPaths(house_number_dict[key], font)
            house_number_width += text_paths[key].get_current_point()[0]

        width = self.width_without_margin
        translate_x = (width - house_number_width)/2

        self.canvas.saveState()
        self.canvas.translate(0, SIZES_PT[f'{self.wide}_house_number{self.arrow}_bl'])

        if translate_x >= 0:
            self.canvas.translate(translate_x, 0)
        else:
            scale = width/house_number_width
        #         work_canvas.translate(SIZES_PT[f'{wide}_margin']*(1-scale), 0)
            self.canvas.scale(scale, scale)

        after_slash = False
        for key in text_paths.keys():
            if after_slash:
                self.canvas.translate(-text_paths[key].get_path_extents()[0], 0)
                after_slash = False
            text_paths[key].draw(self.canvas)
            self.canvas.translate(text_paths[key].get_current_point()[0], 0)
            if key == SLASH:
                after_slash = True

        self.canvas.restoreState()

    def _draw_arrow(self, x: float, y: float, k: int, length: float, half_height: float):
        """ k= -1 or 1
        """
        p = self.canvas.beginPath()
        p.moveTo(x, y)
        p.lineTo(x + k * length, y + half_height)
        p.lineTo(x + k * length, y - half_height)
        p.close()
        self.canvas.drawPath(p, fill=1, stroke=0)

    def _draw_arrows(self):
        arrow_size = SIZES_PT[f'{self.wide}_house_number_arrow_arrow_size']
        base_line = SIZES_PT[f'{self.wide}_house_number_arrow_arrow_bl']
        width = self.width_without_margin

        self.canvas.saveState()
        self.canvas.setLineWidth(arrow_size['line_width'])

        if self.left_num:
            self._draw_arrow(0, base_line, 1, arrow_size['length'], arrow_size['half_height'])
            self.canvas.line(arrow_size['length'], base_line, width/2-arrow_size['half_space'], base_line)
        else:
            self.canvas.line(0, base_line, width/2+arrow_size['half_space'], base_line)

        if self.right_num:
            self._draw_arrow(width, base_line, -1, arrow_size['length'], arrow_size['half_height'])
            self.canvas.line(width/2 + arrow_size['half_space'], base_line, width - arrow_size['length'], base_line)
        else:
            self.canvas.line(width/2 - arrow_size['half_space'], base_line, width, base_line)

        self.canvas.restoreState()

    def _draw_left_num(self):
        left_num_dict = self.parse_house_number(self.left_num, HOUSE_NUMBER_ARROW_RE_TUPLE)

        self.canvas.saveState()
        self.canvas.translate(0, SIZES_PT[f'{self.wide}_house_number_arrow_number_bl'])

        lvl_a1_path = TextPaths(left_num_dict[LVL_A1], SIZES_PT[f'{self.wide}_house_number_arrow_number_font_{LVL_A1}'])
        lvl_a1_path.draw(self.canvas)

        if left_num_dict[LVL_A2C]:
            lvl_a2c_path = TextPaths(left_num_dict[LVL_A2C],
                                     SIZES_PT[f'{self.wide}_house_number_arrow_number_font_{LVL_A2C}'])
            self.canvas.translate(lvl_a1_path.get_current_point()[0], 0)
            lvl_a2c_path.draw(self.canvas)

        self.canvas.restoreState()

    def _draw_right_num(self):

        right_num_dict = self.parse_house_number(self.right_num, HOUSE_NUMBER_ARROW_RE_TUPLE)

        self.canvas.saveState()
        self.canvas.translate(self.width_without_margin, SIZES_PT[f'{self.wide}_house_number_arrow_number_bl'])

        if right_num_dict[LVL_A2C]:
            lvl_a2c_path = TextPaths(right_num_dict[LVL_A2C],
                                     SIZES_PT[f'{self.wide}_house_number_arrow_number_font_{LVL_A2C}'])
            self.canvas.translate(-lvl_a2c_path.get_current_point()[0], 0)
            lvl_a2c_path.draw(self.canvas)

        lvl_a1_path = TextPaths(right_num_dict[LVL_A1],
                                SIZES_PT[f'{self.wide}_house_number_arrow_number_font_{LVL_A1}'])
        self.canvas.translate(-lvl_a1_path.get_current_point()[0], 0)
        lvl_a1_path.draw(self.canvas)
        self.canvas.restoreState()


class Vertical(BasePlate):
    def __init__(self, street_type: str, street_name: str, street_translit: str, house_num: str, wide: str = THIN):
        self.street_type = street_type
        self.street_name = street_name
        self.street_translit = street_translit
        self.house_num = house_num
        self.wide = wide
        super().__init__()


    def _init_margin(self):
        self.margin = SIZES_PT[f'{self.wide}_vertical_margin']

    def _init_width(self):
        self.width = SIZES_PT[f'{self.wide}_vertical_width']

    def _init_height(self):
        self.height = SIZES_PT[f'{self.wide}_vertical_height']

    def _init_radius(self):
        self.radius = SIZES_PT[f'{self.wide}_round_radius']

    def _draw_face(self):
        self._draw_street_type()
        self._draw_street_name()
        self._draw_line()
        self._draw_translit()
        self._draw_number()

    def _draw_street_type(self):
        self.canvas.saveState()
        self.canvas.translate(0, SIZES_PT[f'{self.wide}_vertical_street_type_bl'])

        street_type_text_path = TextPaths(text=self.street_type,
                                          font=SIZES_PT[f'{self.wide}_vertical_street_type_font'])
        street_type_text_path.draw(self.canvas)

    def _draw_street_name(self):
        street_name_text_path = TextPaths(text=self.street_name,
                                          font=SIZES_PT[f'{self.wide}_vertical_street_name_font'])
        self.canvas.translate(0, SIZES_PT[f'{self.wide}_vertical_street_name_translate'])
        if street_name_text_path.get_path_extents()[2] < self.width_without_margin:
            street_name_text_path.draw(self.canvas)
        else:
            str_list = textwrap.wrap(self.street_name, width=SIZES_PT[f'{self.wide}_vertical_street_name_max_char'],
                                     break_long_words=False)

            str_path_list = [TextPaths(text=s,
                                       font=SIZES_PT[f'{self.wide}_vertical_street_name_font']) for s in str_list]
            scale = min(1, self.width_without_margin / max([path.get_path_extents()[2] for path in str_path_list]))

            self.canvas.scale(scale, scale)
            for path in str_path_list:
                path.draw(self.canvas)
                if path != str_path_list[-1]:
                    self.canvas.translate(0, SIZES_PT[f'{self.wide}_vertical_street_name_font']['leading'])
            self.canvas.scale(1, 1)

    def _draw_line(self):
        self.canvas.translate(0, SIZES_PT[f'{self.wide}_vertical_street_line_translate'])
        self.canvas.setLineWidth(SIZES_PT[f'{self.wide}_vertical_street_line_width'])
        self.canvas.line(0, 0, self.width_without_margin, 0)

    def _draw_translit(self):
        street_translit_text_path = TextPaths(text=self.street_translit,
                                              font=SIZES_PT[f'{self.wide}_vertical_street_translit_font'])
        self.canvas.translate(0, SIZES_PT[f'{self.wide}_vertical_street_translit_translate'])
        if street_translit_text_path.get_path_extents()[2] < self.width_without_margin:
            street_translit_text_path.draw(self.canvas)
        else:
            str_list = textwrap.wrap(self.street_translit,
                                     width=SIZES_PT[f'{self.wide}_vertical_street_translit_max_char'],
                                     break_long_words=False)

            str_path_list = [TextPaths(text=s,
                                       font=SIZES_PT[f'{self.wide}_vertical_street_translit_font']) for s in str_list]
            scale = min(1, self.width_without_margin / max([path.get_path_extents()[2] for path in str_path_list]))
            self.canvas.scale(scale, scale)
            for path in str_path_list:
                path.draw(self.canvas)
                if path != str_path_list[-1]:
                    self.canvas.translate(0, SIZES_PT[f'{self.wide}_vertical_street_translit_font']['leading'])
            self.canvas.scale(1, 1)

        self.canvas.restoreState()

    def _draw_number(self):
        house_number_dict = self.parse_house_number(self.house_num, HOUSE_NUMBER_RE_TUPLE)
        text_paths = {}
        house_number_width = 0

        for key in sorted(house_number_dict.keys()):
            font = SIZES_PT[f'{self.wide}_vertical_house_number_font_{key}'] if key != SLASH else \
                SIZES_PT[f'{self.wide}_vertical_house_number_slash_size']
            text_paths[key] = TextPaths(house_number_dict[key], font)
            house_number_width += text_paths[key].get_current_point()[0]

        self.canvas.saveState()

        self.canvas.translate(0, SIZES_PT[f'{self.wide}_vertical_house_number_bl'])
        if house_number_width > self.width_without_margin:
            scale = self.width_without_margin / house_number_width
            self.canvas.scale(scale, scale)

        after_slash = False
        for key in sorted(house_number_dict.keys()):
            if after_slash:
                self.canvas.translate(-text_paths[key].get_path_extents()[0], 0)
                after_slash = False
            text_paths[key].draw(self.canvas)
            self.canvas.translate(text_paths[key].get_current_point()[0], 0)
            if key == SLASH:
                after_slash = True

        self.canvas.restoreState()


class TextPaths:
    """
    {
        'face_size_char': ([(operation_type, (points))], (current_point), (path_extents))
        'slash_size_/': ([(operation_type, (points))], (current_point), (path_extents))
    }
    """

    path_dict = _load_path()

    def __init__(self, text: str, font: dict):
        self.text = text
        self.face = font['face']
        self.size = font['size']
        self.operations = []
        self.current_point = (0, 0)
        self.path_extents = (0, 0, 0, 0)
        self._init_path()

    def _init_path(self):
        for char in self.text:
            self._append_char(char)

    def _append_char(self, char: str):
        char_operations, char_current_point, char_path_extends = self.path_dict[f"{self.face}_{self.size}_{char}"]
        self._appends_operations(char_operations)
        self._calc_path_extends(char_path_extends)
        self._calc_current_point(char_current_point)

    def _appends_operations(self, char_operations):
        for type_op, points in char_operations:
            self.operations.append((type_op, self._sum_points(self.current_point, points)))

    def _calc_current_point(self, char_current_point):
        self.current_point = self._sum_points(self.current_point, char_current_point)

    def _calc_path_extends(self, char_path_extends):
        path_extends = self._sum_points(self.current_point, char_path_extends)
        # may be change min-max ?
        self.path_extents = (
            min(self.path_extents[0], path_extends[0]),
            min(self.path_extents[1], path_extends[1]),
            max(self.path_extents[2], path_extends[2]),
            max(self.path_extents[3], path_extends[3]),
        )

    @staticmethod
    def _sum_points(point: tuple, points: tuple) -> tuple:
        """
        point (x, y)
        points (x1, y1, ..., xn, yn)
        """
        return tuple(x + y for x, y in zip(point*(len(points)//2), points))

    def draw(self, work_canvas: canvas.Canvas):
        p = work_canvas.beginPath()
        for type_op, points in self.operations:
            if type_op == 'moveTo':
                p.moveTo(*points)
            elif type_op == 'lineTo':
                p.lineTo(*points)
            elif type_op == 'curveTo':
                p.curveTo(*points)
            elif type_op == 'close':
                p.close()
        work_canvas.drawPath(p, fill=1, stroke=0)

    def get_path_extents(self):
        """
        x1: left of the resulting extents
        y1: top of the resulting extents
        x2: right of the resulting extents
        y2: bottom of the resulting extents

        :return: (x1, y1, x2, y2), all float
        """
        return self.path_extents

    def get_current_point(self):
        """

        :return: (x, y), both float
        """
        return self.current_point


if __name__ == '__main__':
    main()

