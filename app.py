from io import BytesIO
import cv2
import PyPDF2
import pytesseract
from PIL import Image
import os
from skimage.metrics import structural_similarity
import typer
from rich.progress import Progress, TextColumn, SpinnerColumn, BarColumn, TimeElapsedColumn


def main(file: str):
    video_capture = cv2.VideoCapture(file)
    merger = PyPDF2.PdfMerger()
    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        SpinnerColumn(),
        BarColumn(),
        TimeElapsedColumn(),
    )

    threshold = 0.95
    frame_interval = 10  # seconds
    ret, previous_frame = video_capture.read()
    # Crop image if needed; xCrop 160 for 16:9, 280 for 4:3
    previous_frame = previous_frame[90:-90, 160:-160]

    fps = int(video_capture.get(cv2.CAP_PROP_FPS))
    totalFrames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_multiplier = (frame_interval * fps)
    steps = int(totalFrames / frame_multiplier)

    with progress:
        cropTask = progress.add_task("Crop image…", total=steps)
        compareTask = progress.add_task("Compare image…", total=steps)
        ocrTask = progress.add_task("Run text recognition…", total=steps)

        for i in progress.track(range(steps), description="Processing frames…"):
            video_capture.set(cv2.CAP_PROP_POS_FRAMES, i*frame_multiplier)
            ret, frame = video_capture.read()
            if not ret:
                break

            frame = frame[90:-90, 160:-160]
            progress.update(cropTask, advance=1)

            # Convert images to grayscale
            before_gray = cv2.cvtColor(
                previous_frame, cv2.COLOR_BGR2GRAY)
            after_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Compute SSIM between the two images
            (score, diff) = structural_similarity(
                before_gray, after_gray, full=True)
            # print("Image Similarity: {:.4f}%".format(score * 100))
            progress.update(compareTask, advance=1)

            if score < threshold:
                image = Image.fromarray(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                # image.save('out.pdf', optimize=True, append=True)
                pdf = pytesseract.image_to_pdf_or_hocr(
                    image, 'eng', extension='pdf')

                merger.append(BytesIO(pdf))
            progress.update(ocrTask, advance=1)
            previous_frame = frame

    video_capture.release()
    cv2.destroyAllWindows()

    file_without_extension = os.path.splitext(file)[0]
    merger.write(file_without_extension + ".pdf")
    print(f"PDF saved as {file_without_extension}.pdf")


if __name__ == "__main__":
    typer.run(main)
