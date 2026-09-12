
import sys
from argparse import ArgumentParser
from typing import List

from lcars.engineering.generators.component_factory import LcarsComponentFactory

# Парсинг аргументів командного рядка
def parse_args(args: List[str] = None):
    parser = ArgumentParser(description="LCARS QML component generator CLI")
    parser.add_argument(
        "component",
        nargs="?",
        help="type of component (button, panel, klingon_button, etc)" ,
    )
    parser.add_argument("name", nargs="?", help="name for the generated file")
    parser.add_argument(
        "image",
        nargs="?",
        help="path to SVG/PNG used by the component (not used for klingon_button)",
    )

    parser.add_argument(
        "--color",
        "-c",
        default="#40E0D0",
        help="base color for the component",
    )
    parser.add_argument("--text", "-t", default="SYSTEM", help="label text")
    parser.add_argument("--width", type=int, default=250)
    parser.add_argument("--height", type=int, default=80)
    parser.add_argument("--font-size", type=int, default=14)
    parser.add_argument("--output", "-o", default="lcars/qml/generated")

    # palette mode
    parser.add_argument(
        "--palette",
        nargs=2,
        metavar=("FACTION", "ERA"),
        help="generate a small set using the faction palette",
    )
    return parser.parse_args(args)

# Головна функція
# Використовується для генерації компонентів
def main():
    opts = parse_args()
    factory = LcarsComponentFactory(output_dir=opts.output)

    if opts.palette:
        faction, era = opts.palette
        files = factory.generate_from_palette(faction, era)
        print("generated", files)
        return 0

    if not opts.component or not opts.name or not opts.image:
        print("error: component, name and image are required unless --palette is used", file=sys.stderr)
        return 1

    try:
        path = factory.generate_component(
            component_type=opts.component,
            name=opts.name,
            image_path=opts.image,
            color=opts.color,
            text=opts.text,
            width=opts.width,
            height=opts.height,
            font_size=opts.font_size,
        )
        print("created", path)
        return 0
    except Exception as exc:
        print(f"generation failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
