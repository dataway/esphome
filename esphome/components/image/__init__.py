import logging

from esphome import core
import esphome.codegen as cg
from esphome.components import display, font
import esphome.config_validation as cv
from esphome.const import CONF_FILE, CONF_ID, CONF_RESIZE, CONF_TYPE
from esphome.core import CORE, HexInt

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['display']
MULTI_CONF = True

ImageType = {'binary': 0, 'grayscale': 1, 'rgb': 2}

Image_ = display.display_ns.class_('Image')

CONF_RAW_DATA_ID = 'raw_data_id'

IMAGE_SCHEMA = cv.Schema({
    cv.Required(CONF_ID): cv.declare_id(Image_),
    cv.Required(CONF_FILE): cv.file_,
    cv.Optional(CONF_RESIZE): cv.dimensions,
    cv.Optional(CONF_TYPE): cv.string,
    cv.GenerateID(CONF_RAW_DATA_ID): cv.declare_id(cg.uint8),
})

CONFIG_SCHEMA = cv.All(font.validate_pillow_installed, IMAGE_SCHEMA)


def to_code(config):
    from PIL import Image

    path = CORE.relative_config_path(config[CONF_FILE])
    try:
        image = Image.open(path)
    except Exception as e:
        raise core.EsphomeError(f"Could not load image file {path}: {e}")

    if CONF_RESIZE in config:
        image.thumbnail(config[CONF_RESIZE])

    if CONF_TYPE in config:
        if config[CONF_TYPE].startswith('GRAYSCALE'):
            width, height = image.size
            image = image.convert('L', dither=Image.NONE)
            pixels = list(image.getdata())
            data = [0 for _ in range(height * width)]
            pos = 0
            for pix in pixels:
                data[pos] = pix
                pos += 1
            rhs = [HexInt(x) for x in data]
            prog_arr = cg.progmem_array(config[CONF_RAW_DATA_ID], rhs)
            cg.new_Pvariable(config[CONF_ID], prog_arr, width, height, ImageType['grayscale'])
        elif config[CONF_TYPE].startswith('RGB'):
            width, height = image.size
            image = image.convert('RGB')
            pixels = list(image.getdata())
            data = [0 for _ in range(height * width * 3)]
            pos = 0
            for pix in pixels:
                data[pos] = pix[0]
                pos += 1
                data[pos] = pix[1]
                pos += 1
                data[pos] = pix[2]
                pos += 1
            rhs = [HexInt(x) for x in data]
            prog_arr = cg.progmem_array(config[CONF_RAW_DATA_ID], rhs)
            cg.new_Pvariable(config[CONF_ID], prog_arr, width, height, ImageType['rgb'])
    else:
        image = image.convert('1', dither=Image.NONE)
        width, height = image.size
        if width > 500 or height > 500:
            _LOGGER.warning("The image you requested is very big. Please consider using"
                            " the resize parameter.")
        width8 = ((width + 7) // 8) * 8
        data = [0 for _ in range(height * width8 // 8)]
        for y in range(height):
            for x in range(width):
                if image.getpixel((x, y)):
                    continue
                pos = x + y * width8
                data[pos // 8] |= 0x80 >> (pos % 8)

        rhs = [HexInt(x) for x in data]
        prog_arr = cg.progmem_array(config[CONF_RAW_DATA_ID], rhs)
        cg.new_Pvariable(config[CONF_ID], prog_arr, width, height)
