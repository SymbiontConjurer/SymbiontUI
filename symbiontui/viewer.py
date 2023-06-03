from typing import Optional
from flask import Flask, request, render_template, send_from_directory, send_file, redirect, url_for
import os
import argparse
import imghdr
import png
from image_repository import ImageRepository, Image

app = Flask(__name__)
image_repository : Optional[ImageRepository] = None

@app.route('/')
def index():
    selected_image_relpath = request.args.get('image')
    selected_category = request.args.get('category', 'images')  # Added: selected category is taken from query param
    images = image_repository.list(category=selected_category)  # Updated: only images from the selected category are displayed
    
    selected_image_index = None
    selected_image = None
    next_image_relpath = prev_image_relpath = None
    image_relpaths = [image.relpath for image in images]
    print(image_relpaths)
    if selected_image_relpath:
        if selected_image_relpath not in image_relpaths:
            print("Redirecting to index page")
            return redirect(url_for('index'))  # redirect to index page without selected image
        else:
            selected_image_index = image_relpaths.index(selected_image_relpath)
            selected_image = images[selected_image_index]
            if selected_image_index < len(images) - 1:
                next_image_relpath = images[selected_image_index + 1].relpath
            if selected_image_index > 0:
                prev_image_relpath = images[selected_image_index - 1].relpath

    image_metadata = None
    png_chunks = None
    if selected_image:
        image_metadata = os.stat(selected_image.abspath)

        if imghdr.what(selected_image.abspath) == 'png':
            png_chunks = {}
            reader = png.Reader(filename=selected_image.abspath)
            for chunk in reader.chunks():
                if chunk[0] == b'tEXt':
                    key, value = chunk[1].split(b'\x00')
                    png_chunks[key.decode()] = value.decode()

    return render_template(
        "index.html",
        images=images,
        selected_image=selected_image,
        image_metadata=image_metadata,
        next_image=next_image_relpath,
        prev_image=prev_image_relpath,
        png_chunks=png_chunks,
        categories=image_repository.categories(),  # Updated: pass all categories to the template
        selected_category=selected_category,  # Updated: pass selected category to the template
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
    image_repository = ImageRepository(app.config['image_dir'])
    app.run(debug=True, port=args.port)
