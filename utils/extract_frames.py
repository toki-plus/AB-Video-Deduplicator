import os
import cv2
import argparse

def extract_frames(video_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"错误：无法打开视频文件 {video_path}")
        return
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_filename = os.path.join(output_dir, f"frame_{frame_count:04d}.jpg")
        cv2.imwrite(frame_filename, frame)
        frame_count += 1
    cap.release()
    print(f"成功从视频中提取 {frame_count} 帧")
    print(f"帧已保存到目录: {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="将视频拆分为单独的帧")
    parser.add_argument("-i", "--input", default="a.mp4", help="输入视频文件路径 (默认: a.mp4)")
    parser.add_argument("-o", "--output", default="output", help="输出目录 (默认: output)")
    args = parser.parse_args()
    extract_frames(args.input, args.output)
