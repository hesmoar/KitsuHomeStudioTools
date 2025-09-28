import subprocess


def convert_image_sequence_to_video(input, output, frames):
    command = f"ffmpeg -framerate {frames} -i {input} -c:v libx264 -crf 18 -pix_fmt yuv420p {output}"

    subprocess.run(command, shell=True, check=True)