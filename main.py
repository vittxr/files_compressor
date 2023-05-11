import os
import subprocess
import tempfile
from fastapi import Depends, FastAPI, Request, UploadFile 
from pydantic import BaseModel

app = FastAPI()

def compress_video(video_bytes, ext: str = 'mp4'):
    # Read the video file from the FileStorage object
    # Write the video bytes to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(video_bytes)
        input_path = f.name

    # Compress the video using ffmpeg
    output_path = f'compressed_video.{ext}'
    command = ['ffmpeg',
               '-threads', '3',
               '-i', input_path,
               '-c:v', 'libx264',
               '-preset', 'medium',
               '-crf', '28',
               '-f', 'mp4', 
               output_path]
    subprocess.run(command, check=True)

    # Read the compressed video data from the output file
    with open(output_path, 'rb') as f:
        compressed_video = f.read()

    # Remove the temporary files
    os.remove(input_path)
    os.remove(output_path)

    # Return the compressed video as a bytes object
    return compressed_video 

@app.post('/compress_form_data_video/')
async def compress_form_data_video_route(file: UploadFile):
    video_bytes = await file.read()
    video_bytes = compress_video(video_bytes, file.filename.split('.')[-1].lower)
    return video_bytes

if __name__ == '__main__':
    # uvicorn.run(app, host='127.0.0.1', port=8000, reload=True)
    import uvicorn 
    uvicorn.run('main:app', host='0.0.0.0', port=8000, log_level='info', reload=True)