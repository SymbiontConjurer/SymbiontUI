from flask import Flask, request, render_template, send_from_directory, send_file
import os
import argparse
import imghdr
import png

class ImageRepository:
    def __init__(self, directory):
        self.directory = directory

    def list(self):
        files_and_dirs = os.listdir(self.directory)
        images = sorted(
            [f for f in files_and_dirs if os.path.isfile(os.path.join(self.directory, f)) and imghdr.what(os.path.join(self.directory, f))],
            key=lambda x: os.stat(os.path.join(self.directory, x)).st_ctime,
            reverse=True  # Descending order
        )
        return images

app = Flask(__name__)

@app.route('/')
def index():
    selected_image = request.args.get('image')
    current_dir = request.args.get('dir', app.config['image_dir'])
    current_dir = os.path.abspath(current_dir)  # Ensure directory path is absolute
    if not os.path.commonpath([app.config['image_dir'], current_dir]).startswith(app.config['image_dir']):
        # Prevent directory traversal attacks
        current_dir = app.config['image_dir']

    image_repository = ImageRepository(current_dir)
    images = image_repository.list()
    files_and_dirs = os.listdir(current_dir)
    directories = sorted(
        [f for f in files_and_dirs if os.path.isdir(os.path.join(current_dir, f))],
    )

    next_image = prev_image = None
    if selected_image and selected_image in images:
        curr_index = images.index(selected_image)
        if curr_index < len(images) - 1:
            next_image = images[curr_index + 1]
        if curr_index > 0:
            prev_image = images[curr_index - 1]

    image_metadata = None
    png_chunks = None
    if selected_image:
        image_path = os.path.join(current_dir, selected_image)
        image_metadata = os.stat(image_path)

        if imghdr.what(image_path) == 'png':
            png_chunks = {}
            reader = png.Reader(filename=image_path)
            for chunk in reader.chunks():
                if chunk[0] == b'tEXt':
                    key, value = chunk[1].split(b'\x00')
                    png_chunks[key.decode()] = value.decode()

    return render_template(
        "index.html",
        directories=directories,
        images=images,
        selected_image=selected_image,
        image_metadata=image_metadata,
        current_dir=current_dir,
        next_image=next_image,
        prev_image=prev_image,
        png_chunks=png_chunks,
        image_dir=app.config['image_dir'],
    )
@app.route('/image')
def serve_image():
    image_path = request.args.get('image')
    dir_path = request.args.get('dir', app.config['image_dir'])
    return send_from_directory(dir_path, image_path)

@app.route('/download')
def download_image():
    image_path = request.args.get('image')
    dir_path = request.args.get('dir', app.config['image_dir'])
    file_path = os.path.join(dir_path, image_path)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', default=os.getcwd(), help='The directory containing images.')
    parser.add_argument('--port', default=7861, type=int, help='The port to run the server on.')
    args = parser.parse_args()

    image_dir = args.dir
    if not os.path.isdir(image_dir):
        print(f'Invalid directory: {image_dir}')
        exit(1)

    app.config['image_dir'] = os.path.abspath(image_dir)
    app.run(debug=True, port=args.port)
