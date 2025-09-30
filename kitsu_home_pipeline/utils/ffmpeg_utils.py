import subprocess


def convert_image_sequence_to_video(input, output, frames):
    command = f"ffmpeg -framerate {frames} -i {input} -c:v libx264 -crf 18 -pix_fmt yuv420p {output}"

    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Video created successfully: {output}")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
    except FileNotFoundError:
        print("FFmpeg executable not found. Ensure it's installed and in your PATH.")