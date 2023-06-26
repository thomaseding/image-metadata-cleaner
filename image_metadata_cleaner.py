from PIL import Image, PngImagePlugin

import os
import sys


UNICODE_TO_ASCII_MAP = {
    "’": "'",
    "φ": "phi",
}

def clean_metadata(input_path, output_path, debug):
    img = Image.open(input_path)
    if debug:
        print(img.info)

    metadata = PngImagePlugin.PngInfo()

    if 'parameters' in img.info:
        data = img.info['parameters']

        cleaned_data = []
        for char in data:
            if char in UNICODE_TO_ASCII_MAP:
                cleaned_data.append(UNICODE_TO_ASCII_MAP[char])
            elif ord(char) < 128:
                cleaned_data.append(char)
            else:
                # cleaned_data.append("<?>")
                cleaned_data.append(char)
        metadata.add_text('parameters', "".join(cleaned_data))

    if debug:
        print("")
        print(metadata)

    img.save(output_path, pnginfo=metadata)


def main_single(input_path, output_path, debug):
    clean_metadata(input_path, output_path, debug)


def main_batch(input_dir, output_dir, debug):
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

    for filename in os.listdir(input_dir):
        if filename.endswith(".png"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            clean_metadata(input_path, output_path, debug)


def main():
    args = sys.argv[1:]
    debug = False
    batch = False
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
            sys.exit(0)
        else:
            print(f"Error: Unexpected argument {args[i]}")
            sys.exit(1)

    if input_path is None or output_path is None:
        print("Error: --input and --output are required")
        sys.exit(1)

    if batch:
        main_batch(input_path, output_path, debug)
    else:
        main_single(input_path, output_path, debug)


if __name__ == "__main__":
    main()