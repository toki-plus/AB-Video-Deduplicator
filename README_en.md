# AB Video Deduplicator: Unique High-Frame-Rate Blending for Deduplication

[简体中文](./README.md) | [English](./README_en.md)

[![GitHub stars](https://img.shields.io/github/stars/toki-plus/AB-Video-Deduplicator?style=social)](https://github.com/toki-plus/AB-Video-Deduplicator/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/toki-plus/AB-Video-Deduplicator?style=social)](https://github.com/toki-plus/AB-Video-Deduplicator/network/members)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/toki-plus/AB-Video-Deduplicator/pulls)

> ### ⚠️ Important Disclaimer
> This open-source version is an early release intended for technical research and educational purposes only. Do not use it for any illegal activities. Due to platform algorithm updates, its deduplication effectiveness may not meet current standards.

**AB Video Deduplicator is an open-source desktop application for video creators, designed to fundamentally alter a video's data fingerprint using an innovative "high-frame-rate frame sampling and blending" technique. It aims to bypass originality checks and deduplication mechanisms on major short-video platforms like TikTok.**

<p align="center">
  <a href="https://www.bilibili.com/video/BV1HwgrzbEow" target="_blank">
    <img src="./assets/cover_demo.png" alt="Click to watch the demo video on Bilibili" width="800"/>
  </a>
  <br>
  <em>(Click the cover to watch the HD demo video on Bilibili)</em>
</p>

---

## 💡 How It Works

Traditional deduplication methods (filters, scaling, mirroring) are becoming less effective. This tool employs a more fundamental "frame blending" strategy:

1.  **Input Two Videos**:
    *   **Video A (Content Video)**: The main video you want to publish.
    *   **Video B (Material Video)**: An original, unrelated video.

2.  **Generate High-Frame-Rate Stream**: The tool creates a high-frame-rate (e.g., 60/120/240 fps) video stream.

3.  **Intelligent Frame Insertion**: Using a specific algorithm, frames from **Video A** are inserted into key positions of the new stream, while frames from **Video B** are used to fill the gaps between them.

4.  **Final Result**: Due to platform compression, viewers on mobile devices still see a smooth playback of **Video A**. However, at the data level, the newly generated video contains a substantial number of frames from **Video B**, making its MD5 hash and data fingerprint completely different from the original, thus achieving deep deduplication.

| Deduplication Level | Target FPS | Approx. A:B Frame Ratio |
| :--- | :---: | :---: |
| **50%** | 60 | 1 : 1 |
| **75%** | 120 | 1 : 3 |
| **87.5%**| 240 | 1 : 7 |

## ✨ Core Features

-   **Intuitive GUI**: Built with PyQt5 for simple, command-line-free operation.
-   **Three Deduplication Levels**: Offers 50% (60fps), 75% (120fps), and 87.5% (240fps) modes.
-   **🚀 NVIDIA GPU Acceleration**: Supports NVENC hardware encoding for significantly faster processing.
-   **Auto Resolution Matching**: Automatically resizes Video B to match Video A's resolution.
-   **Audio Preservation**: The original audio track from Video A is fully retained.
-   **Real-time Progress & Logging**: Clearly displays processing progress and detailed logs.
-   **Cross-Platform**: Runs on Windows, macOS, and Linux (with correct dependencies installed).

## 📸 Screenshots

<p align="center">
  <img src="./assets/cover_software.png" alt="Main UI" width="800"/>
  <br>
  <em>The clean and intuitive user interface.</em>
</p>

## 🚀 Quick Start

### System Requirements

1.  **Python**: Version 3.8 or newer.
2.  **FFmpeg**: **Must** be installed and its executable path added to the system's PATH environment variable.
    -   Windows: Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
    -   macOS: `brew install ffmpeg`
    -   Linux: `sudo apt update && sudo apt install ffmpeg`

### Installation & Launch

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/toki-plus/AB-Video-Deduplicator.git
    cd AB-Video-Deduplicator
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Generate Qt Resource File:**
    The application's icon resources need to be compiled manually. Run the following command:
    ```bash
    pyrcc5 src/resources.qrc -o src/resources.py
    ```
5.  **Run the application:**
    ```bash
    python src/main.py
    ```

## 📖 Usage Guide

1.  Click "Select Video A" to choose your **content video**.
2.  Click "Select Video B" to choose your **material video**.
3.  Select a mode from the "Deduplication Level" dropdown (start with 60fps for testing).
4.  Check "Enable GPU Acceleration" if you have a supported NVIDIA GPU.
5.  Click "Start Processing" and wait for the progress bar to complete.
6.  The processed video will be saved in the `output` folder.

---

<p align="center">
  <strong>For technical inquiries, please connect via:</strong>
</p>
<table align="center">
  <tr>
    <td align="center">
      <img src="./assets/wechat.png" alt="WeChat QR Code" width="200"/>
      <br />
      <sub><b>WeChat</b></sub>
      <br />
      <sub>ID: toki-plus (Note: "GitHub Customization")</sub>
    </td>
    <td align="center">
      <img src="./assets/gzh.png" alt="Public Account QR Code" width="200"/>
      <br />
      <sub><b>Public Account</b></sub>
      <br />
      <sub>Scan for tech articles & project updates</sub>
    </td>
  </tr>
</table>

## 📂 My Other Open-Source Projects

-   **[AI Video Workflow](https://github.com/toki-plus/ai-video-workflow)**: A fully automated AI-native video generation pipeline, integrating Text-to-Image, Image-to-Video, and Text-to-Music models to create AIGC short videos with one click.
-   **[AI Highlight Clip](https://github.com/toki-plus/ai-highlight-clip)**: An AI-driven tool that automatically discovers, analyzes, and clips "highlight moments" from long-form videos, complete with auto-generated viral titles.
-   **[AI TTV Workflow](https://github.com/toki-plus/ai-ttv-workflow)**: An AI-driven text-to-video tool that automatically converts any script into a short video with voiceover, subtitles, and a cover. Supports AI script extraction, rewriting, and translation.
-   **[Video Mover](https://github.com/toki-plus/video-mover)**: A powerful, fully automated pipeline that monitors creators, downloads their new videos, performs deep deduplication, generates AI-powered titles, and auto-publishes to different platforms.

## 🤝 Contributing

Contributions of any kind are welcome! If you have ideas for new features, have found a bug, or have suggestions for improvements, please:
-   Open an [Issue](https://github.com/toki-plus/AB-Video-Deduplicator/issues) to start a discussion.
-   Fork the repository and submit a [Pull Request](https://github.com/toki-plus/AB-Video-Deduplicator/pulls).

If you find this project helpful, please consider giving it a ⭐!

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
