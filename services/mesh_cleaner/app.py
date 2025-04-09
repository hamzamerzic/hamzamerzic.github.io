import os
import uuid
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from clean_mesh import clean_mesh

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "/tmp/uploads"
RESULT_FOLDER = "/tmp/results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


@app.route("/upload", methods=["POST"])
def upload():
    f = request.files["file"]
    mass = float(request.form.get("mass", 1.0))
    save_normals = request.form.get("save_normals", "false").lower() == "true"
    use_convex_hull = request.form.get("use_convex_hull", "false").lower() == "true"

    filename = str(uuid.uuid4()) + "_" + f.filename
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    f.save(input_path)

    try:
        output_text, cleaned_path = clean_mesh(
            input_path, mass, output_dir=RESULT_FOLDER, save_normals=save_normals, use_convex_hull=use_convex_hull
        )
        return jsonify(
            {
                "metrics": output_text,
                "download_url": f"/download/{os.path.basename(cleaned_path)}",
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download/<filename>")
def download(filename):
    return send_file(os.path.join(RESULT_FOLDER, filename), as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
