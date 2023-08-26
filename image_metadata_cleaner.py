import contextlib
import os
import sys

from PIL import Image, PngImagePlugin

UNICODE_TO_ASCII_MAP = {
    # (187)
    "»": ",",
    # (263)
    "ć": "c",
    # (269)
    "č": "c",
    # (281)
    "ę": "e",
    # (283)
    "ě": "e",
    # (285)
    "ĝ": "g",
    # (287)
    "ğ": "g",
    # (322)
    "ł": "l",
    # (324)
    "ń": "n",
    # (339)
    "œ": "ae",
    # (345)
    "ř": "r",
    # (347)
    "ś": "s",
    # (353)
    "š": "s",
    # (357)
    "ţ": "t",
    # (363)
    "ű": "u",
    # (382)
    "ž": "z",
    # (966)
    "φ": "phi",
    # (8208)
    "‐": "-",
    # (8211)
    "–": "-",
    # (8220)
    "“": '"',
    # (8221)
    "”": '"',
    # (8216)
    "‘": "'",
    # (8217)
    "’": "'",
    # (9792)
    "♀": "female",
    # (10023)
    "✧": "star",
    # (10024)
    "✨": "star",
    # (12539)
    "・": " ",
    # (20161)
    "仁": "?",
    # (20799)
    "儿": "?",
    # (61443)
    "": " ",
    # (61458)
    "": ",",
    # (65292)
    "，": ",",
}


@contextlib.contextmanager
def with_image(path):
    img = Image.open(path)
    try:
        yield img
    finally:
        img.close()


def clean_metadata(input_path, output_path, debug, log_file):
    with with_image(input_path) as img:
        if debug:
            print(img.info)

        metadata = PngImagePlugin.PngInfo()

        if "parameters" in img.info:
            data = img.info["parameters"]

            cleaned_data = []
            for char in data:
                if char in UNICODE_TO_ASCII_MAP:
                    cleaned_data.append(UNICODE_TO_ASCII_MAP[char])
                elif ord(char) < 255:
                    cleaned_data.append(char)
                else:
                    msg = (
                        f"Found unicode character {char} ({ord(char)}) in {input_path}"
                    )
                    if log_file is not None:
                        log_file.write(msg)
                        log_file.flush()
                    else:
                        print(msg)
                    cleaned_data.append(f"U{ord(char):04x}")
            metadata.add_text("parameters", "".join(cleaned_data))

        if debug:
            print("")
            print(metadata)

        img.save(output_path, pnginfo=metadata)


def main_single(input_path, output_path, debug, log_file):
    clean_metadata(input_path, output_path, debug, log_file)


def main_batch(input_dir, output_dir, debug, log_file):
    if not os.path.exists(input_dir):
        print(f"Error: {input_dir} does not exist")
        sys.exit(1)
    if not os.path.isdir(input_dir):
        print(f"Error: {input_dir} is not a directory")
        sys.exit(1)
    if os.path.exists(output_dir) and not os.path.isdir(output_dir):
        print(f"Error: {output_dir} is not a directory")
        sys.exit(1)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    index = 0
    for filename in os.listdir(input_dir):
        if filename.endswith(".png"):
            index += 1
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            clean_metadata(input_path, output_path, debug, log_file)
            if index % 100 == 0:
                print(f"Processed {index} images")


# List of absolute file paths to override batch mode. Nice for hacking.
batch_override = []


def main():
    args = sys.argv[1:]
    debug = False
    batch = False
    log_path = None
    input_path = None
    output_path = None

    i = 0
    while i < len(args):
        if args[i] == "--input":
            input_path = args[i + 1]
            i += 2
        elif args[i] == "--output":
            output_path = args[i + 1]
            i += 2
        elif args[i] == "--debug":
            debug = True
            i += 1
        elif args[i] == "--batch":
            batch = True
            i += 1
        elif args[i] == "--help":
            print("Usage:")
            print("  python image_metadata_cleaner.py <args>")
            print("")
            print("Args:")
            print("  --help           Print this help message")
            print("  --input <path>   Path to the input image/directory")
            print("  --output <path>  Path to the output image/directory")
            print("  --debug          Print debug info")
            print("  --batch          Use batch mode to process directory of images")
            print("  --log <path>     Path to the log file")
            sys.exit(0)
        else:
            print(f"Error: Unexpected argument {args[i]}")
            sys.exit(1)

    if input_path is None or output_path is None:
        print("Error: --input and --output are required")
        sys.exit(1)

    def go_log(log_file):
        if batch:
            if batch_override:
                for path in batch_override:
                    main_single(path, path, debug, log_file)
            else:
                main_batch(input_path, output_path, debug, log_file)
        else:
            main_single(input_path, output_path, debug, log_file)

    if log_path is None:
        go_log(None)
    else:
        with open(log_path, "w") as log_file:
            go_log(log_file)


if __name__ == "__main__":
    main()
