from __future__ import annotations

from typing import Any, Sequence

from ..lowlevel import IRaster, IWgsMapset3Reader
from .protocols import IWgsMapset3Selector
from .types import (
    Color,
    MapEdgeRenderOptions,
    MapFillRenderOptions,
    MapImageRenderOptions,
)


class PilMapFillRenderer:
    @property
    def defaultOptions(self) -> MapFillRenderOptions:
        return MapFillRenderOptions()

    def render(
        self,
        reader: IWgsMapset3Reader,
        selector: IWgsMapset3Selector,
        options: MapFillRenderOptions | None = None,
    ) -> Any:
        return self.renderRaster(
            selector.readRaster(reader),
            self.defaultOptions if options is None else options,
        )

    def renderRaster(
        self,
        raster: IRaster,
        options: MapFillRenderOptions,
    ) -> Any:
        return _renderFillToRgba(raster, options)


class PilMapEdgeRenderer:
    @property
    def defaultOptions(self) -> MapEdgeRenderOptions:
        return MapEdgeRenderOptions()

    def render(
        self,
        reader: IWgsMapset3Reader,
        selector: IWgsMapset3Selector,
        options: MapEdgeRenderOptions | None = None,
    ) -> Any:
        return self.renderRaster(
            selector.readRaster(reader),
            self.defaultOptions if options is None else options,
        )

    def renderRaster(
        self,
        raster: IRaster,
        options: MapEdgeRenderOptions,
    ) -> Any:
        return _renderEdgeToRgba(raster, options)


class PilMapImageRenderer:
    def __init__(
        self,
        fillRenderer: PilMapFillRenderer | None = None,
        edgeRenderer: PilMapEdgeRenderer | None = None,
    ):
        self._useFastPath = fillRenderer is None and edgeRenderer is None
        self._fillRenderer = fillRenderer or PilMapFillRenderer()
        self._edgeRenderer = edgeRenderer or PilMapEdgeRenderer()

    @property
    def defaultOptions(self) -> MapImageRenderOptions:
        return MapImageRenderOptions()

    def render(
        self,
        reader: IWgsMapset3Reader,
        selector: IWgsMapset3Selector,
        options: MapImageRenderOptions | None = None,
    ) -> Any:
        effective_options = self.defaultOptions if options is None else options
        raster = selector.readRaster(reader)
        return self.renderRaster(raster, effective_options)

    def renderRaster(
        self,
        raster: IRaster,
        options: MapImageRenderOptions,
    ) -> Any:
        if self._useFastPath:
            fast_image = _renderImageToRgba(raster, options)
            if fast_image is not None:
                return fast_image
        image_module = _load_image_module()
        fill = self._fillRenderer.renderRaster(raster, options.fillOptions)
        if options.edgeOptions is None:
            return fill
        edge = self._edgeRenderer.renderRaster(raster, options.edgeOptions)
        return image_module.alpha_composite(
            fill.convert("RGBA"),
            edge.convert("RGBA"),
        )


def _load_image_module() -> Any:
    try:
        from PIL import Image
    except ImportError as exception:
        raise ImportError("Pillow is required to use PIL map renderers") from exception
    return Image


def _renderFillToRgba(raster: IRaster, options: MapFillRenderOptions) -> Any:
    palette_image = _renderFillWithPalette(raster, options)
    if palette_image is not None:
        return palette_image
    image_module = _load_image_module()
    width = raster.width
    height = raster.height
    data = _rasterData(raster)
    default_color = _colorToBytes(options.defaultColor)
    colors = {
        value: _colorToBytes(color)
        for value, color in options.colors.items()
    }
    color_resolver = options.colorResolver
    pixels = bytearray(width * height * 4)
    offset = 0
    if color_resolver is None:
        for image_y in range(height):
            row_offset = (height - image_y - 1) * width
            for raster_x in range(width):
                pixels[offset : offset + 4] = colors.get(
                    data[row_offset + raster_x],
                    default_color,
                )
                offset += 4
    else:
        for image_y in range(height):
            raster_y = height - image_y - 1
            row_offset = raster_y * width
            for raster_x in range(width):
                value = data[row_offset + raster_x]
                color = colors.get(value)
                if color is None:
                    resolved = color_resolver(value, raster_x, raster_y)
                    color = default_color if resolved is None else _colorToBytes(resolved)
                pixels[offset : offset + 4] = color
                offset += 4
    return image_module.frombytes("RGBA", (width, height), bytes(pixels))


def _renderEdgeToRgba(raster: IRaster, options: MapEdgeRenderOptions) -> Any:
    edge_width = _validateEdgeWidth(options.edgeWidth)
    image_module = _load_image_module()
    image = image_module.new(
        "RGBA",
        (raster.width, raster.height),
        _colorToTuple(options.backgroundColor),
    )
    image.paste(
        image_module.new("RGBA", image.size, _colorToTuple(options.edgeColor)),
        mask=_boundaryMaskFromRaster(raster, options.includeZero, edge_width),
    )
    return image


def _renderImageToRgba(raster: IRaster, options: MapImageRenderOptions) -> Any | None:
    if options.edgeOptions is None:
        return _renderFillToRgba(raster, options.fillOptions)
    pillow_image = _renderImageWithPillow(raster, options)
    if pillow_image is not None:
        return pillow_image
    edge_options = options.edgeOptions
    edge_width = _validateEdgeWidth(edge_options.edgeWidth)
    if edge_width != 1:
        return None
    if edge_options.edgeColor.a != 255 or edge_options.backgroundColor.a != 0:
        return None

    image_module = _load_image_module()
    width = raster.width
    height = raster.height
    data = _rasterData(raster)
    fill_options = options.fillOptions
    default_color = _colorToBytes(fill_options.defaultColor)
    colors = {
        value: _colorToBytes(color)
        for value, color in fill_options.colors.items()
    }
    color_resolver = fill_options.colorResolver
    edge_color = _colorToBytes(edge_options.edgeColor)
    include_zero = edge_options.includeZero
    pixels = bytearray(width * height * 4)
    offset = 0
    if color_resolver is None:
        for image_y in range(height):
            raster_y = height - image_y - 1
            row_offset = raster_y * width
            for raster_x in range(width):
                value = data[row_offset + raster_x]
                pixels[offset : offset + 4] = (
                    edge_color
                    if _isBoundaryDataPixel(data, width, height, raster_x, raster_y, row_offset, include_zero)
                    else colors.get(value, default_color)
                )
                offset += 4
    else:
        for image_y in range(height):
            raster_y = height - image_y - 1
            row_offset = raster_y * width
            for raster_x in range(width):
                value = data[row_offset + raster_x]
                if _isBoundaryDataPixel(data, width, height, raster_x, raster_y, row_offset, include_zero):
                    color = edge_color
                else:
                    color = colors.get(value)
                    if color is None:
                        resolved = color_resolver(value, raster_x, raster_y)
                        color = default_color if resolved is None else _colorToBytes(resolved)
                pixels[offset : offset + 4] = color
                offset += 4
    return image_module.frombytes("RGBA", (width, height), bytes(pixels))


def _renderFillWithPalette(raster: IRaster, options: MapFillRenderOptions) -> Any | None:
    if options.colorResolver is not None:
        return None
    label_result = _createLabelImage(raster)
    if label_result is None:
        return None
    label_image, value_to_label = label_result
    colors = {
        value: _colorToTuple(color)
        for value, color in options.colors.items()
    }
    default_color = _colorToTuple(options.defaultColor)
    return _labelImageToRgba(label_image, value_to_label, colors, default_color)


def _renderImageWithPillow(raster: IRaster, options: MapImageRenderOptions) -> Any | None:
    edge_options = options.edgeOptions
    if edge_options is None:
        return _renderFillWithPalette(raster, options.fillOptions)
    edge_width = _validateEdgeWidth(edge_options.edgeWidth)
    if edge_options.backgroundColor.a != 0:
        return None
    fill_options = options.fillOptions
    if fill_options.colorResolver is not None:
        return None
    label_result = _createLabelImage(raster)
    if label_result is None:
        return None

    image_module = _load_image_module()
    label_image, value_to_label = label_result
    fill_colors = {
        value: _colorToTuple(color)
        for value, color in fill_options.colors.items()
    }
    fill = _labelImageToRgba(
        label_image,
        value_to_label,
        fill_colors,
        _colorToTuple(fill_options.defaultColor),
    )
    zero_label = value_to_label.get(0)
    mask = _boundaryMaskFromLabelImage(
        label_image,
        zero_label,
        edge_options.includeZero,
        edge_width,
    )
    edge_layer = image_module.new("RGBA", label_image.size, (0, 0, 0, 0))
    edge_layer.paste(
        image_module.new("RGBA", label_image.size, _colorToTuple(edge_options.edgeColor)),
        mask=mask,
    )
    return image_module.alpha_composite(fill, edge_layer)


def _createLabelImage(raster: IRaster) -> tuple[Any, dict[int, int]] | None:
    values = sorted(raster.valueSet())
    if len(values) > 256:
        return None
    image_module = _load_image_module()
    width = raster.width
    height = raster.height
    data = _rasterData(raster)
    value_to_label = {value: index for index, value in enumerate(values)}
    pixels = bytearray(width * height)
    offset = 0
    for image_y in range(height):
        row_offset = (height - image_y - 1) * width
        for raster_x in range(width):
            pixels[offset] = value_to_label[data[row_offset + raster_x]]
            offset += 1
    return image_module.frombytes("L", (width, height), bytes(pixels)), value_to_label


def _boundaryMaskFromRaster(
    raster: IRaster,
    include_zero: bool,
    edge_width: int,
) -> Any:
    label_result = _createLabelImage(raster)
    if label_result is not None:
        label_image, value_to_label = label_result
        return _boundaryMaskFromLabelImage(
            label_image,
            value_to_label.get(0),
            include_zero,
            edge_width,
        )
    return _expandMask(_boundaryMaskFromData(raster, include_zero), edge_width)


def _boundaryMaskFromData(raster: IRaster, include_zero: bool) -> Any:
    image_module = _load_image_module()
    width = raster.width
    height = raster.height
    data = _rasterData(raster)
    pixels = bytearray(width * height)
    offset = 0
    for image_y in range(height):
        raster_y = height - image_y - 1
        row_offset = raster_y * width
        for raster_x in range(width):
            pixels[offset] = (
                255
                if _isBoundaryDataPixel(data, width, height, raster_x, raster_y, row_offset, include_zero)
                else 0
            )
            offset += 1
    return image_module.frombytes("L", (width, height), bytes(pixels))


def _labelImageToRgba(
    label_image: Any,
    value_to_label: dict[int, int],
    colors: dict[int, tuple[int, int, int, int]],
    default_color: tuple[int, int, int, int],
) -> Any:
    image = label_image.convert("P")
    palette = [0] * (256 * 3)
    alpha = [255] * 256
    for value, label in value_to_label.items():
        color = colors.get(value, default_color)
        palette[label * 3 : label * 3 + 3] = color[:3]
        alpha[label] = color[3]
    image.putpalette(palette)
    if any(component != 255 for component in alpha):
        image.info["transparency"] = bytes(alpha)
    return image.convert("RGBA")


def _boundaryMaskFromLabelImage(
    label_image: Any,
    zero_label: int | None,
    include_zero: bool,
    edge_width: int,
) -> Any:
    from PIL import ImageChops

    width, height = label_image.size
    right = label_image.copy()
    if width > 1:
        right.paste(label_image.crop((1, 0, width, height)), (0, 0))
    up = label_image.copy()
    if height > 1:
        up.paste(label_image.crop((0, 0, width, height - 1)), (0, 1))

    right_mask = ImageChops.difference(label_image, right).point(
        lambda value: 255 if value > 0 else 0,
        mode="L",
    )
    up_mask = ImageChops.difference(label_image, up).point(
        lambda value: 255 if value > 0 else 0,
        mode="L",
    )

    if not include_zero and zero_label is not None:
        current_nonzero = label_image.point(
            lambda value: 0 if value == zero_label else 255,
            mode="L",
        )
        right_nonzero = right.point(
            lambda value: 0 if value == zero_label else 255,
            mode="L",
        )
        up_nonzero = up.point(
            lambda value: 0 if value == zero_label else 255,
            mode="L",
        )
        right_mask = ImageChops.multiply(
            ImageChops.multiply(right_mask, current_nonzero),
            right_nonzero,
        )
        up_mask = ImageChops.multiply(
            ImageChops.multiply(up_mask, current_nonzero),
            up_nonzero,
        )
    return _expandMask(ImageChops.lighter(right_mask, up_mask), edge_width)


def _expandMask(mask: Any, edge_width: int) -> Any:
    if edge_width == 1:
        return mask
    image_module = _load_image_module()
    from PIL import ImageChops

    width, height = mask.size
    left = (edge_width - 1) // 2
    right = edge_width // 2
    result = image_module.new("L", mask.size, 0)
    for dy in range(-left, right + 1):
        for dx in range(-left, right + 1):
            src_left = max(0, -dx)
            src_top = max(0, -dy)
            src_right = min(width, width - dx)
            src_bottom = min(height, height - dy)
            if src_left >= src_right or src_top >= src_bottom:
                continue
            shifted = image_module.new("L", mask.size, 0)
            shifted.paste(
                mask.crop((src_left, src_top, src_right, src_bottom)),
                (max(0, dx), max(0, dy)),
            )
            result = ImageChops.lighter(result, shifted)
    return result


def _rasterData(raster: IRaster) -> Sequence[int]:
    data = raster.toArray()
    expected_size = raster.width * raster.height
    if len(data) != expected_size:
        raise ValueError("raster array size does not match raster dimensions")
    return data


def _isBoundaryDataPixel(
    data: Sequence[int],
    width: int,
    height: int,
    x: int,
    y: int,
    row_offset: int,
    include_zero: bool,
) -> bool:
    value = data[row_offset + x]
    if x + 1 < width:
        neighbor_value = data[row_offset + x + 1]
        if neighbor_value != value and (include_zero or (value != 0 and neighbor_value != 0)):
            return True
    if y + 1 < height:
        neighbor_value = data[row_offset + width + x]
        if neighbor_value != value and (include_zero or (value != 0 and neighbor_value != 0)):
            return True
    return False


def _colorToBytes(color: Color) -> bytes:
    return bytes(_colorToTuple(color))


def _colorToTuple(color: Color) -> tuple[int, int, int, int]:
    values = (color.r, color.g, color.b, color.a)
    for component in values:
        if component < 0 or component > 255:
            raise ValueError("color components must be in range 0..255")
    return values


def _validateEdgeWidth(edge_width: int) -> int:
    if edge_width < 1:
        raise ValueError("edgeWidth must be greater than or equal to 1")
    return edge_width
