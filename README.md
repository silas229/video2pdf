# video2pdf

Generate pdfs from videos

This programm generates a PDF file from a video (e.g. an online lecture).

## Setup

```shell
python -m venv .venv
./.venv/bin/activate
pip install -r ./requirements.txt
```

## Usage

Simply run `python app.py <name_of_the_video>.mp4`. The pdf will be saved as <name_of_the_video>.pdf.

## How it works

The program creates a frame every 10 seconds (ajustable) from the video, crops it and compares it with the previous one. If it differs enough it will be OCR'ed and appended as a new page to the pdf.

Note: Change the crop in line 26 from [90:-90, 280:-280] to [90:-90, 160:-160] for 16:9 videos
