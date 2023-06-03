from flask import Flask, request, render_template, send_from_directory, send_file, redirect, url_for
import os
import argparse
import imghdr
import png
from image_repository import ImageRepository

app = Flask(__name__)

@app.route('/')
def index():
    selected_image = request.args.get('image')

    image_repository = ImageRepository(app.config['image_dir'])
    images = image_repository.list()

    if selected_image and selected_image not in images:
        return redirect(url_for('index'))  # redirect to index page without selected image

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
        image_path = os.path.join(app.config['image_dir'], selected_image)
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
        images=images,
        selected_image=selected_image,
        image_metadata=image_metadata,
        next_image=next_image,
        prev_image=prev_image,
        png_chunks=png_chunks,
    )

@app.route('/image')
def serve_image():
    image_path = request.args.get('image')
    return send_from_directory(app.config['image_dir'], image_path)

@app.route('/download')
def download_image():
    image_path = request.args.get('image')
    file_path = os.path.join(app.config['image_dir'], image_path)
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
