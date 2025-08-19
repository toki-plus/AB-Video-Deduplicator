import os
import sys
import cv2
import time
import ffmpeg
import itertools
import subprocess
import numpy as np
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog, QLabel,
                             QRadioButton, QVBoxLayout, QWidget, QProgressBar, QHBoxLayout,
                             QTextEdit, QFrame, QButtonGroup, QCheckBox)
try:
    import resources
except ImportError:
    print("警告: 资源文件 'resources.py' 未找到。图标可能无法显示。")
    print("请使用 'pyrcc5 resources.qrc -o resources.py' 生成它。")

qss = """
QWidget {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e1e2f, stop:1 #141422);
    color: #e0e0e0;
}
QFrame {
    background: rgba(40, 40, 60, 0.9);
    border: none;
    border-radius: 10px;
    padding: 15px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}
QLabel#section_title {
    font-size: 14px;
    font-weight: 600;
    color: #ffffff;
}
QLabel#path_label {
    background: rgba(60, 60, 80, 0.8);
    border: 1px solid #555;
    border-radius: 5px;
    padding: 8px;
    font-size: 14px;
    color: #e0e0e0;
}
QPushButton#select_button {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4a90e2, stop:1 #357abd);
    color: white;
    border: none;
    padding: 8px 15px;
    font-size: 14px;
    border-radius: 5px;
    transition: all 0.3s;
}
QPushButton#select_button:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5aa1f2, stop:1 #4688d1);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}
QRadioButton, QCheckBox {
    font-size: 14px;
    color: #e0e0e0;
}
QRadioButton::indicator, QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border-radius: 5px;
    border: 2px solid #ffd700;
    background: #2a2a3a;
}
QRadioButton::indicator {
    border-radius: 10px;
}
QRadioButton::indicator:checked, QCheckBox::indicator:checked {
    background: #ffd700;
    border: 2px solid #ffd700;
}
QRadioButton::indicator:hover, QCheckBox::indicator:hover {
    border: 2px solid #ffea00;
}
QPushButton#run_button {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff7e5f, stop:1 #feb47b);
    color: white;
    border: none;
    padding: 12px 25px;
    font-size: 16px;
    font-weight: bold;
    border-radius: 8px;
    transition: all 0.3s;
}
QPushButton#run_button:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff926f, stop:1 #ffc48b);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}
QPushButton#run_button:disabled {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #999, stop:1 #777);
    color: #ccc;
}
QProgressBar {
    background: rgba(40, 40, 60, 0.8);
    border-radius: 5px;
    text-align: center;
    font-size: 14px;
    color: #ffffff;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4a90e2, stop:1 #357abd);
    border-radius: 5px;
}
QTextEdit {
    background: rgba(30, 30, 50, 0.9);
    border: 1px solid #555;
    border-radius: 5px;
    font-size: 12px;
    color: #d0d0d0;
}
QTextEdit::verticalScrollBar {
    background: #2a2a3a;
    width: 10px;
    margin: 0px;
}
QTextEdit::verticalScrollBar::handle {
    background: #4a90e2;
    border-radius: 5px;
}
QTextEdit::verticalScrollBar::add-line, QTextEdit::verticalScrollBar::sub-line {
    background: none;
}
QLabel {
    background: transparent;
}
"""

def get_video_info(video_path):
    try:
        probe = ffmpeg.probe(video_path, cmd='ffprobe')
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        if not video_stream:
            raise ValueError("未找到视频流")
        width = int(video_stream['width'])
        height = int(video_stream['height'])
        r_frame_rate = video_stream.get('r_frame_rate', '0/1')
        if '/' in r_frame_rate:
            num, den = map(int, r_frame_rate.split('/'))
            fps = num / den if den > 0 else 0
        else:
            fps = float(r_frame_rate)
        duration_str = video_stream.get('duration')
        if duration_str:
            duration = float(duration_str)
        else:
            duration = float(probe.get('format', {}).get('duration', 0))
        total_frames_str = video_stream.get('nb_frames', '0')
        if total_frames_str != '0' and total_frames_str.isdigit():
             total_frames = int(total_frames_str)
        else:
            if duration > 0 and fps > 0:
                total_frames = int(duration * fps)
            else:
                cap = cv2.VideoCapture(video_path)
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                cap.release()
        if fps == 0 or total_frames == 0 or duration == 0:
            raise ValueError("视频元数据不完整或无效 (fps/duration/frames is zero)")
        return width, height, fps, duration, total_frames
    except Exception as e:
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"无法打开视频文件: {video_path}")
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            cap.release()
            if fps == 0 or total_frames == 0:
                raise ValueError("OpenCV无法获取有效的视频信息")
            return width, height, fps, duration, total_frames
        except Exception as cv_e:
            raise RuntimeError(f"无法获取视频信息 {video_path}: FFmpeg错误: {e}, OpenCV回退错误: {cv_e}")

def resize_video(input_path, output_path, width, height, use_gpu=False):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入视频文件 {input_path} 不存在！")
    encoder = 'h264_nvenc' if use_gpu else 'libx264'
    quality_param = '-preset p6' if use_gpu else '-crf 23'
    cmd_list = [
        'ffmpeg', '-y', '-i', input_path,
        '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2',
        '-c:v', encoder,
    ]
    cmd_list.extend(quality_param.split())
    cmd_list.extend(['-c:a', 'aac', '-b:a', '128k', output_path])
    try:
        creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        result = subprocess.run(
            cmd_list,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            creationflags=creation_flags
        )
        if not os.path.exists(output_path):
            raise RuntimeError(f"FFmpeg未能创建输出文件 {output_path}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg处理失败：\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}")

def frame_reader(video_path, width, height):
    command = [
        'ffmpeg', '-i', video_path,
        '-f', 'image2pipe', '-pix_fmt', 'bgr24', '-vcodec', 'rawvideo', '-'
    ]
    creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
    pipe = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        bufsize=width*height*3*10,
        creationflags=creation_flags
    )
    frame_size = width * height * 3
    try:
        while True:
            raw_frame = pipe.stdout.read(frame_size)
            if not raw_frame or len(raw_frame) != frame_size:
                break
            frame = np.frombuffer(raw_frame, dtype='uint8').reshape((height, width, 3))
            yield frame
    finally:
        pipe.kill()
        pipe.wait()

def get_a_positions(fps, N_a):
    if fps == 60:
        return {m if m <= 2 else 2 + 2 * (m - 2) for m in range(N_a)}
    elif fps == 120:
        return {m if m <= 1 else 1 + 4 * (m - 1) for m in range(N_a)}
    elif fps == 240:
        if N_a == 0: return set()
        if N_a <= 2: return set(range(N_a))
        positions = {0, 1}
        next_pos = 1
        intervals = [8, 9, 7]
        for i in range(2, N_a):
            next_pos += intervals[(i - 2) % 3]
            positions.add(next_pos)
        return positions
    else:
        raise ValueError("不支持的帧率！")

class VideoProcessor(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, video_a_path, video_b_path, output_path, fps, temp_dir, use_gpu=False):
        super().__init__()
        self.video_a_path = video_a_path
        self.video_b_path = video_b_path
        self.output_path = output_path
        self.fps = fps
        self.temp_dir = temp_dir
        self.use_gpu = use_gpu

    def run(self):
        start_time = time.time()
        writer_process = None
        temp_b_path = os.path.join(self.temp_dir, "resized_b.mp4")
        temp_output_path = os.path.join(self.temp_dir, "temp_output.mp4")
        path_b_to_process = self.video_b_path
        temp_files_to_clean = [temp_output_path]
        reader_a_gen = None
        reader_b_gen = None
        try:
            if not os.path.exists(self.temp_dir):
                os.makedirs(self.temp_dir)
            self.status.emit(f"开始处理，检查视频信息... (t={time.time() - start_time:.2f}s)")
            self.progress.emit(5)
            width_a, height_a, fps_a, duration_a, total_frames_a = get_video_info(self.video_a_path)
            self.status.emit(f"视频A信息: {width_a}x{height_a}, {fps_a:.2f}fps, {duration_a:.2f}s, {total_frames_a}帧")
            width_b, height_b, _, _, _ = get_video_info(self.video_b_path)
            self.status.emit(f"视频B信息: {width_b}x{height_b}")
            if not duration_a or duration_a <= 0:
                raise ValueError("无法获取视频A的有效时长，处理中止。")
            if (width_a, height_a) != (width_b, height_b):
                self.status.emit(f"分辨率不一致，将视频B ({width_b}x{height_b}) 调整为视频A的尺寸 ({width_a}x{height_a})... (t={time.time() - start_time:.2f}s)")
                resize_video(self.video_b_path, temp_b_path, width_a, height_a, self.use_gpu)
                path_b_to_process = temp_b_path
                temp_files_to_clean.append(temp_b_path)
            else:
                self.status.emit("分辨率一致，跳过尺寸调整。")
            self.progress.emit(10)
            total_frames_c = int(duration_a * self.fps)
            self.status.emit(f"目标视频C: {self.fps}fps, 时长与A一致({duration_a:.2f}s), 总帧数: {total_frames_c}")
            self.status.emit(f"准备帧序列混合... (t={time.time() - start_time:.2f}s)")
            positions_a = get_a_positions(self.fps, total_frames_a)
            encoder = 'h264_nvenc' if self.use_gpu else 'libx264'
            quality_param = '-preset p6' if self.use_gpu else '-crf 23'
            writer_cmd = [
                'ffmpeg', '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo',
                '-pix_fmt', 'bgr24', '-s', f'{width_a}x{height_a}', '-r', str(self.fps),
                '-i', '-', '-c:v', encoder
            ]
            writer_cmd.extend(quality_param.split())
            writer_cmd.extend(['-pix_fmt', 'yuv420p', temp_output_path])
            creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            writer_process = subprocess.Popen(
                writer_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                creationflags=creation_flags
            )
            self.status.emit(f"开始混合帧... (t={time.time() - start_time:.2f}s)")
            self.progress.emit(20)
            try:
                reader_a_gen = frame_reader(self.video_a_path, width_a, height_a)
                reader_b_gen = frame_reader(path_b_to_process, width_a, height_a)
                reader_b_cycled = itertools.cycle(reader_b_gen)
                a_frame_counter = 0
                for i in range(total_frames_c):
                    frame_to_write = None
                    try:
                        if i in positions_a and a_frame_counter < total_frames_a:
                            frame_to_write = next(reader_a_gen)
                            a_frame_counter += 1
                        else:
                            frame_to_write = next(reader_b_cycled)
                        writer_process.stdin.write(frame_to_write.tobytes())
                        if (i + 1) % 50 == 0 or (i + 1) == total_frames_c:
                            progress = 20 + int(70 * (i + 1) / total_frames_c)
                            self.progress.emit(min(progress, 89))
                            self.status.emit(f"处理帧: {i + 1} / {total_frames_c} (t={time.time() - start_time:.2f}s)")
                    except StopIteration:
                        self.status.emit(f"警告: 视频流在第 {i} 帧提前结束。")
                        break
            finally:
                if reader_a_gen:
                    reader_a_gen.close()
                if reader_b_gen:
                    reader_b_gen.close()
            self.status.emit(f"混合完成，正在生成最终视频文件... (t={time.time() - start_time:.2f}s)")
            writer_process.stdin.close()
            _, stderr_output = writer_process.communicate()
            if writer_process.returncode != 0:
                raise RuntimeError(f"FFmpeg写入视频失败: {stderr_output.decode('utf-8', errors='ignore')}")
            self.progress.emit(90)
            self.status.emit(f"合并音频... (t={time.time() - start_time:.2f}s)")
            final_cmd = [
                'ffmpeg', '-y', '-i', temp_output_path, '-i', self.video_a_path,
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k', '-shortest', self.output_path
            ]
            subprocess.run(
                final_cmd,
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                creationflags=creation_flags
            )
            self.progress.emit(100)
            self.status.emit(f"视频处理完成! (总耗时: {time.time() - start_time:.2f}s)")
            self.finished.emit()
        except Exception as e:
            import traceback
            self.error.emit(f"错误：{str(e)}\n{traceback.format_exc()}")
        finally:
            if writer_process and writer_process.poll() is None:
                writer_process.kill()
                writer_process.wait()
            for f in temp_files_to_clean:
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except OSError as e:
                        self.status.emit(f"无法删除临时文件 {f}: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AB视频去重工具")
        try:
            self.setWindowIcon(QIcon(":/logo.png"))
        except:
            print("图标资源 :logo.png 未找到，请检查resources.qrc和resources.py文件。")
        self.setGeometry(100, 100, 600, 850)
        self.init_ui()
        sys.excepthook = self.except_hook

    def init_ui(self):
        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        video_a_frame = QFrame()
        video_a_layout = QHBoxLayout()
        video_a_layout.setSpacing(10)
        video_a_title = QLabel("视频A路径（搬运）")
        video_a_title.setObjectName("section_title")
        self.label_a = QLabel("未选择")
        self.label_a.setObjectName("path_label")
        self.label_a.setWordWrap(True)
        self.btn_a = QPushButton("选择")
        self.btn_a.setObjectName("select_button")
        self.btn_a.clicked.connect(self.select_video_a)
        video_a_layout.addWidget(video_a_title)
        video_a_layout.addWidget(self.label_a, 1)
        video_a_layout.addWidget(self.btn_a)
        video_a_frame.setLayout(video_a_layout)
        main_layout.addWidget(video_a_frame)
        video_b_frame = QFrame()
        video_b_layout = QHBoxLayout()
        video_b_layout.setSpacing(10)
        video_b_title = QLabel("视频B路径（原创）")
        video_b_title.setObjectName("section_title")
        self.label_b = QLabel("未选择")
        self.label_b.setObjectName("path_label")
        self.label_b.setWordWrap(True)
        self.btn_b = QPushButton("选择")
        self.btn_b.setObjectName("select_button")
        self.btn_b.clicked.connect(self.select_video_b)
        video_b_layout.addWidget(video_b_title)
        video_b_layout.addWidget(self.label_b, 1)
        video_b_layout.addWidget(self.btn_b)
        video_b_frame.setLayout(video_b_layout)
        main_layout.addWidget(video_b_frame)
        output_frame = QFrame()
        output_layout = QHBoxLayout()
        output_layout.setSpacing(10)
        output_title = QLabel("输出路径")
        output_title.setObjectName("section_title")
        self.label_output = QLabel("未选择")
        self.label_output.setObjectName("path_label")
        self.label_output.setWordWrap(True)
        self.btn_output = QPushButton("选择")
        self.btn_output.setObjectName("select_button")
        self.btn_output.clicked.connect(self.select_output_path)
        output_layout.addWidget(output_title)
        output_layout.addWidget(self.label_output, 1)
        output_layout.addWidget(self.btn_output)
        output_frame.setLayout(output_layout)
        main_layout.addWidget(output_frame)
        options_frame = QFrame()
        options_layout = QVBoxLayout()
        options_layout.setSpacing(15)
        fps_title = QLabel("去重强度")
        fps_title.setObjectName("section_title")
        options_layout.addWidget(fps_title)
        self.radio_60 = QRadioButton("去重率50%（DY+TK）")
        self.radio_120 = QRadioButton("去重率75%（仅TK）")
        self.radio_240 = QRadioButton("去重率87.5%（仅TK）")
        self.radio_60.setChecked(True)
        fps_button_group = QButtonGroup(self)
        fps_button_group.addButton(self.radio_60)
        fps_button_group.addButton(self.radio_120)
        fps_button_group.addButton(self.radio_240)
        fps_options_layout = QHBoxLayout()
        fps_options_layout.addWidget(self.radio_60)
        fps_options_layout.addWidget(self.radio_120)
        fps_options_layout.addWidget(self.radio_240)
        fps_options_layout.addStretch()
        options_layout.addLayout(fps_options_layout)
        gpu_title = QLabel("性能选项")
        gpu_title.setObjectName("section_title")
        options_layout.addWidget(gpu_title)
        self.gpu_checkbox = QCheckBox("启用GPU加速（需要NVIDIA显卡和驱动）")
        self.gpu_checkbox.setChecked(False)
        options_layout.addWidget(self.gpu_checkbox)
        options_frame.setLayout(options_layout)
        main_layout.addWidget(options_frame)
        self.btn_run = QPushButton("运行")
        self.btn_run.setObjectName("run_button")
        self.btn_run.setMinimumWidth(200)
        self.btn_run.clicked.connect(self.run_processing)
        self.btn_run.setEnabled(False)
        main_layout.addWidget(self.btn_run, alignment=Qt.AlignCenter)
        progress_log_frame = QFrame()
        progress_log_layout = QVBoxLayout()
        progress_log_layout.setSpacing(10)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_log_layout.addWidget(self.progress_bar)
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        progress_log_layout.addWidget(self.text_output)
        progress_log_frame.setLayout(progress_log_layout)
        main_layout.addWidget(progress_log_frame)
        container.setLayout(main_layout)
        self.video_a_path = ""
        self.video_b_path = ""
        self.output_path = ""
        self.temp_dir = os.path.join(os.path.expanduser("~"), ".video_temp_optimized")
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def select_video_a(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择视频A", "", "视频文件 (*.mp4 *.avi *.mov)")
        if path:
            self.video_a_path = path
            self.label_a.setText(path)
            self.check_run_enable()

    def select_video_b(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择视频B", "", "视频文件 (*.mp4 *.avi *.mov)")
        if path:
            self.video_b_path = path
            self.label_b.setText(path)
            self.check_run_enable()

    def select_output_path(self):
        path, _ = QFileDialog.getSaveFileName(self, "选择输出路径", "C.mp4", "视频文件 (*.mp4)")
        if path:
            self.output_path = path
            self.label_output.setText(path)
            self.check_run_enable()

    def check_run_enable(self):
        if self.video_a_path and self.video_b_path and self.output_path:
            self.btn_run.setEnabled(True)
        else:
            self.btn_run.setEnabled(False)

    def run_processing(self):
        if self.radio_60.isChecked():
            fps = 60
        elif self.radio_120.isChecked():
            fps = 120
        else:
            fps = 240
        use_gpu = self.gpu_checkbox.isChecked()
        self.set_controls_enabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("")
        self.text_output.clear()
        if use_gpu:
            self.append_text("已启用GPU加速模式。")
        else:
            self.append_text("使用CPU模式处理。")
        self.processor = VideoProcessor(self.video_a_path, self.video_b_path, self.output_path, fps, self.temp_dir, use_gpu)
        self.processor.progress.connect(self.update_progress)
        self.processor.status.connect(self.append_text)
        self.processor.finished.connect(self.processing_finished)
        self.processor.error.connect(self.show_error)
        self.processor.start()

    def set_controls_enabled(self, enabled):
        self.btn_a.setEnabled(enabled)
        self.btn_b.setEnabled(enabled)
        self.btn_output.setEnabled(enabled)
        is_ready = bool(enabled and self.video_a_path and self.video_b_path and self.output_path)
        self.btn_run.setEnabled(is_ready)
        self.radio_60.setEnabled(enabled)
        self.radio_120.setEnabled(enabled)
        self.radio_240.setEnabled(enabled)
        self.gpu_checkbox.setEnabled(enabled)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def append_text(self, text):
        self.text_output.append(f"• {text}")
        self.text_output.verticalScrollBar().setValue(self.text_output.verticalScrollBar().maximum())

    def processing_finished(self):
        self.set_controls_enabled(True)
        self.append_text("处理完成！")

    def show_error(self, message):
        self.set_controls_enabled(True)
        self.text_output.append(f"❌ {message}")
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e74c3c, stop:1 #c0392b); border-radius: 5px; }")

    def closeEvent(self, event):
        import shutil
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            except Exception as e:
                print(f"退出时清理临时文件失败: {e}")
        super().closeEvent(event)

    def except_hook(self, exc_type, exc_value, exc_traceback):
        import traceback
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        if hasattr(self, 'text_output'):
            self.show_error(f"发生未捕获的异常：\n{error_msg}")
            self.setWindowTitle("AB视频去重工具 - 发生严重错误")
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

if __name__ == "__main__":
    if sys.platform.startswith('win'):
        from multiprocessing import freeze_support
        freeze_support()
    app = QApplication(sys.argv)
    app.setStyleSheet(qss)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
