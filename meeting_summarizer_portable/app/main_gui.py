import sys
import threading
from pathlib import Path

from PyQt5 import QtWidgets

from .pipeline import process_one


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Meeting Summarizer")
        self.resize(900, 600)

        self.base_dir = str(Path(__file__).resolve().parents[1])

        self.inputList = QtWidgets.QListWidget()
        self.btnAdd = QtWidgets.QPushButton("MP4 추가")
        self.btnClear = QtWidgets.QPushButton("목록 비우기")

        self.configPath = QtWidgets.QLineEdit(str(Path(self.base_dir) / "config.ini"))
        self.btnConfig = QtWidgets.QPushButton("config 선택")

        self.outDir = QtWidgets.QLineEdit(str(Path(self.base_dir) / "out"))
        self.btnOut = QtWidgets.QPushButton("출력 폴더 선택")

        self.btnRun = QtWidgets.QPushButton("실행")
        self.btnRun.setStyleSheet("font-weight:bold; padding:10px")
        self.progress = QtWidgets.QProgressBar()
        self.progress.setValue(0)

        self.logBox = QtWidgets.QPlainTextEdit()
        self.logBox.setReadOnly(True)

        topRow = QtWidgets.QHBoxLayout()
        topRow.addWidget(self.btnAdd)
        topRow.addWidget(self.btnClear)

        cfgRow = QtWidgets.QHBoxLayout()
        cfgRow.addWidget(QtWidgets.QLabel("config.ini"))
        cfgRow.addWidget(self.configPath)
        cfgRow.addWidget(self.btnConfig)

        outRow = QtWidgets.QHBoxLayout()
        outRow.addWidget(QtWidgets.QLabel("out"))
        outRow.addWidget(self.outDir)
        outRow.addWidget(self.btnOut)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(topRow)
        layout.addWidget(self.inputList)
        layout.addLayout(cfgRow)
        layout.addLayout(outRow)
        layout.addWidget(self.btnRun)
        layout.addWidget(self.progress)
        layout.addWidget(self.logBox)
        self.setLayout(layout)

        self.btnAdd.clicked.connect(self.add_files)
        self.btnClear.clicked.connect(self.inputList.clear)
        self.btnConfig.clicked.connect(self.pick_config)
        self.btnOut.clicked.connect(self.pick_outdir)
        self.btnRun.clicked.connect(self.run)

    def log(self, s: str):
        self.logBox.appendPlainText(s)
        self.logBox.verticalScrollBar().setValue(self.logBox.verticalScrollBar().maximum())

    def add_files(self):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "MP4 선택", "", "MP4 Files (*.mp4)")
        for f in files:
            self.inputList.addItem(f)

    def pick_config(self):
        f, _ = QtWidgets.QFileDialog.getOpenFileName(self, "config.ini 선택", "", "INI (*.ini);;All (*.*)")
        if f:
            self.configPath.setText(f)

    def pick_outdir(self):
        d = QtWidgets.QFileDialog.getExistingDirectory(self, "출력 폴더 선택")
        if d:
            self.outDir.setText(d)

    def run(self):
        items = [self.inputList.item(i).text() for i in range(self.inputList.count())]
        if not items:
            QtWidgets.QMessageBox.warning(self, "오류", "MP4 파일을 추가하세요")
            return

        cfg = self.configPath.text().strip()
        out = self.outDir.text().strip()
        if not cfg:
            QtWidgets.QMessageBox.warning(self, "오류", "config.ini 경로가 비었습니다")
            return

        self.btnRun.setEnabled(False)
        self.progress.setValue(0)

        def worker():
            try:
                total = len(items)
                for idx, f in enumerate(items):
                    self._thread_log(f"=== ({idx+1}/{total}) {Path(f).name} ===")
                    process_one(
                        f,
                        base_dir=self.base_dir,
                        out_root=out,
                        cfg_path=cfg,
                        log=self._thread_log,
                    )
                    self._thread_progress(int(((idx+1)/total)*100))
                self._thread_log("ALL DONE")
            except Exception as e:
                self._thread_log(f"ERROR: {e}")
            finally:
                self._thread_done()

        threading.Thread(target=worker, daemon=True).start()

    def _thread_log(self, s: str):
        QtWidgets.QApplication.instance().postEvent(
            self,
            _LogEvent(s),
        )

    def _thread_progress(self, v: int):
        QtWidgets.QApplication.instance().postEvent(self, _ProgressEvent(v))

    def _thread_done(self):
        QtWidgets.QApplication.instance().postEvent(self, _DoneEvent())

    def customEvent(self, event):
        if isinstance(event, _LogEvent):
            self.log(event.text)
        elif isinstance(event, _ProgressEvent):
            self.progress.setValue(event.value)
        elif isinstance(event, _DoneEvent):
            self.btnRun.setEnabled(True)


class _LogEvent(QtWidgets.QEvent):
    TYPE = QtWidgets.QEvent.Type(QtWidgets.QEvent.registerEventType())
    def __init__(self, text: str):
        super().__init__(self.TYPE)
        self.text = text


class _ProgressEvent(QtWidgets.QEvent):
    TYPE = QtWidgets.QEvent.Type(QtWidgets.QEvent.registerEventType())
    def __init__(self, value: int):
        super().__init__(self.TYPE)
        self.value = value


class _DoneEvent(QtWidgets.QEvent):
    TYPE = QtWidgets.QEvent.Type(QtWidgets.QEvent.registerEventType())
    def __init__(self):
        super().__init__(self.TYPE)


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
