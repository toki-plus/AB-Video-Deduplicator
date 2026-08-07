# AB Video Processor

A desktop tool for frame-mixing, transcoding, and visual-feature experiments.

The project samples, mixes, and re-encodes frames from two videos to evaluate how frame rate, encoding settings, and GPU acceleration affect the visual and data characteristics of the output.

> Process only media that you are authorized to use. This project is not intended to bypass platform review, copyright detection, or other security controls.

## Context

Video production workflows often need repeatable experiments across frame rates, resolutions, mixing strategies, and encoding parameters. Running individual FFmpeg commands makes iteration difficult for non-technical users.

This project packages the workflow in a desktop interface with reusable settings and progress reporting.

## Capabilities

- Inspect source media metadata
- Sample and mix frames from two videos
- Align resolution, frame rate, and encoding parameters
- Provide multiple processing profiles
- Use NVIDIA GPU acceleration when supported
- Report task status and progress through a PyQt5 interface

## Processing Flow

```text
Video A + Video B
    -> Media inspection
    -> Resolution alignment
    -> Frame sampling and mixing
    -> FFmpeg encoding
    -> Output validation
```

Core technologies: Python, PyQt5, NumPy, OpenCV, and FFmpeg.

## Quick Start

### Requirements

- Python 3.8+
- FFmpeg available on `PATH`

```bash
git clone https://github.com/toki-plus/AB-Video-Deduplicator.git
cd AB-Video-Deduplicator
python -m venv venv
```

After activating the virtual environment:

```bash
pip install -r requirements.txt
pyrcc5 src/resources.qrc -o src/resources.py
python src/main.py
```

## Usage

1. Select two video sources that you are authorized to process.
2. Choose processing parameters and an output directory.
3. Enable GPU acceleration when a compatible NVIDIA and FFmpeg environment is available.
4. Run the job and validate the output video, audio, and duration.

## Current Limitations

- Results depend on source resolution, frame rate, and encoding format.
- GPU acceleration depends on the local FFmpeg build and driver environment.
- The repository includes basic test utilities but not a full automated regression suite.

## License

See [LICENSE](./LICENSE).
