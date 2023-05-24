import io
import os
import subprocess
import tempfile
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, Form, UploadFile 
from fastapi.middleware.cors import CORSMiddleware
from utils import getDetailedLog

app = FastAPI()

async def compress_video(video, filename: str, ext: str):
    # Read the video file from the FileStorage object
    # Write the video bytes to a temporary file
    input_path = output_path = ''
    
    try: 
        video_bytes = await video.read()
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(video_bytes)
            input_path = f.name

        # Compress the video using ffmpeg
        output_path = f'compressed_video.{ext}'
        command = ['ffmpeg',
                '-i', input_path,
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                '-crf', '35',
                '-vf', 'scale=360:-1',
                output_path]
        subprocess.run(command, check=True)

        # Read the compressed video data from the output file
        with open(output_path, 'rb') as f:
            compressed_video = f.read()

        # Remove the temporary files
        os.remove(input_path)
        os.remove(output_path)
        
        return compressed_video
    except Exception as e:
        # getDetailedLog(e) <- used in development
        raise Exception(e)
    
    finally: 
        if(os.path.exists(input_path)):
           os.remove(input_path)
        if(os.path.exists(output_path)):
           os.remove(output_path)
       
@app.post('/compress_form_data_video/')
async def compress_video_route(file: UploadFile, filename: str = Form(None), ext: str = Form(None)):  
    try: 
        video_bytes = await compress_video(file, 
                                        filename or file.filename,
                                        ext or file.filename.split('.')[-1].lower())

        # Return a response with the video bytes
        return StreamingResponse(io.BytesIO(video_bytes), media_type='application/octet-stream')
    
    except Exception as e: 
        # getDetailedLog(e) <- used in development
        return {'error': str(e)}

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
)

if __name__ == '__main__':
    import uvicorn 
    uvicorn.run('main:app', host='0.0.0.0', port=8000, log_level='info', reload=True)