from datetime import datetime
from typing import Optional
from flask import Flask, request, render_template, send_from_directory, send_file, redirect, url_for
import os
import argparse
import imghdr
import png
import pytz
from image_repository import ImageRepository, Image
import pathlib
from tzlocal import get_localzone


from automatic1111 import Automatic1111, is_automatic1111_path

app = Flask(__name__)
image_repository : Optional[ImageRepository] = None
automatic1111 : Optional[Automatic1111] = None

@app.route('/')
@app.route('/index')
def index():
    return redirect(url_for('library'))

@app.route('/models')
def models():
    if automatic1111 is None:
        return render_template("not_automatic1111.html")
    models = automatic1111.get_models()
    return render_template("models.html", models=models)

def convert_unix_to_local(unix_timestamp):
    # convert the unix timestamp to datetime
    utc_time = datetime.utcfromtimestamp(unix_timestamp)
    
    # set the timezone to UTC
    utc_time = pytz.utc.localize(utc_time)

    # get the local timezone
    local_tz = get_localzone()

    # convert the UTC datetime to local timezone
    local_time = utc_time.astimezone(local_tz)

    return local_time

@app.route('/library')
def library():
    selected_image_relpath = request.args.get('image')
    selected_category = request.args.get('category', 'images')  # Added: selected category is taken from query param
    images = image_repository.list(category=selected_category)  # Updated: only images from the selected category are displayed
    
    selected_image_index = None
    selected_image = None
    next_image_relpath = prev_image_relpath = None
    image_relpaths = [image.relpath for image in images]
    if selected_image_relpath:
        if selected_image_relpath in image_relpaths:
            selected_image_index = image_relpaths.index(selected_image_relpath)
            selected_image = images[selected_image_index]
            if selected_image_index < len(images) - 1:
                next_image_relpath = images[selected_image_index + 1].relpath
            if selected_image_index > 0:
                prev_image_relpath = images[selected_image_index - 1].relpath
        else:
            print('Selected image not found.')


    image_metadata = None
    png_chunks = None
    if selected_image:
        stats = os.stat(selected_image.abspath)
        image_metadata = {
            'created': convert_unix_to_local(stats.st_ctime),
            'modified': convert_unix_to_local(stats.st_mtime),
            'size': stats.st_size
        }

        if imghdr.what(selected_image.abspath) == 'png':
            png_chunks = {}
            reader = png.Reader(filename=selected_image.abspath)
            for chunk in reader.chunks():
                if chunk[0] == b'tEXt':
                    key, value = chunk[1].split(b'\x00')
                    png_chunks[key.decode()] = value.decode()

    return render_template(
        "library.html",
        images=images,
        selected_image=selected_image,
        image_metadata=image_metadata,
        next_image_relpath=next_image_relpath,
        prev_image_relpath=prev_image_relpath,
        png_chunks=png_chunks,
        categories=image_repository.categories(),  # Updated: pass all categories to the template
        selected_category=selected_category,  # Updated: pass selected category to the template
    )

@app.route('/image')
def serve_image():
    image_path = request.args.get('image')
    full_path = pathlib.Path(os.path.join(app.config['image_dir'], image_path))
    if not full_path.is_file():
        return "File not found", 404
    filename = full_path.name
    directory = full_path.parent
    return send_from_directory(directory, filename)

@app.route('/download')
def download_image():
    image_path = request.args.get('image')
    file_path = os.path.join(app.config['image_dir'], image_path)
    return send_file(file_path, as_attachment=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', default=os.getcwd(), help='The directory containing the sdwebui repo.')
    parser.add_argument('--port', default=7861, type=int, help='The port to run the server on.')
    args = parser.parse_args()

    if is_automatic1111_path(args.dir):
        automatic1111 = Automatic1111(args.dir)
        app.config['image_dir'] = os.path.abspath(automatic1111.image_output_path)
    else:
        app.config['image_dir'] = os.path.abspath(args.dir)
    image_repository = ImageRepository(app.config['image_dir'])
    app.run(debug=True, port=args.port)
