import os
import hashlib
from flask import Flask, request, send_from_directory, jsonify, render_template
from models import db, FileInfo, FileName

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///files.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = 'uploads'

db.init_app(app)
with app.app_context():
    db.create_all()

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    if file:
        # 创建临时文件以计算MD5
        temp_file_path = os.path.join(UPLOAD_FOLDER, 'temp_' + file.filename)
        file.save(temp_file_path)
        md5 = calculate_md5(temp_file_path)
        os.remove(temp_file_path)
        
        # 创建以MD5命名的文件夹
        md5_folder = os.path.join(UPLOAD_FOLDER, md5)
        if not os.path.exists(md5_folder):
            os.makedirs(md5_folder)
        
        # 保存文件到MD5文件夹中
        file_path = os.path.join(md5_folder, file.filename)
        file.seek(0)
        file.save(file_path)
        
        file_record = FileInfo.query.filter_by(md5=md5).first()
        if file_record:
            file_record.version += 1
            file_record.file_path = file_path
            file_record.del_flag = False
            # 检查文件名是否已存在
            filename_record = FileName.query.filter_by(md5=md5, filename=file.filename).first()
            if not filename_record:
                filename_record = FileName(md5=md5, filename=file.filename)
                db.session.add(filename_record)
        else:
            file_record = FileInfo(md5=md5, file_path=file_path)
            db.session.add(file_record)
            # 添加第一个文件名
            filename_record = FileName(md5=md5, filename=file.filename)
            db.session.add(filename_record)
        db.session.commit()
        return jsonify({
            'message': 'File uploaded successfully',
            'md5': md5,
            'version': file_record.version
        }), 200


@app.route('/download/<md5>/<filename>', methods=['GET'])
def download_file(md5, filename):
    # 检查文件记录是否存在
    file_record = FileInfo.query.filter_by(md5=md5, del_flag=False).first()
    if not file_record:
        return jsonify({'message': '文件记录不存在'}), 404
    
    # 检查文件名是否存在
    filename_record = FileName.query.filter_by(md5=md5, filename=filename).first()
    if not filename_record:
        return jsonify({'message': '文件名不存在'}), 404
    
    try:
        md5_folder = os.path.join(UPLOAD_FOLDER, md5)
        file_path = os.path.join(md5_folder, filename)
        
        # 检查文件是否实际存在
        if not os.path.exists(file_path):
            return jsonify({'message': '文件不存在'}), 404
            
        return send_from_directory(md5_folder, filename, as_attachment=True)
    except Exception as e:
        return jsonify({'message': f'下载失败：{str(e)}'}), 500


@app.route('/query/<md5>', methods=['GET'])
def query_file(md5):
    file_record = FileInfo.query.filter_by(md5=md5, del_flag=False).first()
    if file_record:
        return jsonify(file_record.to_dict()), 200
    else:
        return jsonify({'message': 'File not found with this MD5'}), 404


@app.route('/query_by_file', methods=['POST'])
def query_by_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    temp_file_path = os.path.join(UPLOAD_FOLDER, 'temp_' + file.filename)
    file.save(temp_file_path)
    md5 = calculate_md5(temp_file_path)
    os.remove(temp_file_path)
    file_record = FileInfo.query.filter_by(md5=md5, del_flag=False).first()
    if file_record:
        return jsonify(file_record.to_dict()), 200
    else:
        return jsonify({'message': 'File not found with this MD5'}), 404


@app.route('/delete/<md5>', methods=['DELETE'])
def delete_file(md5):
    file_record = FileInfo.query.filter_by(md5=md5, del_flag=False).first()
    if file_record:
        file_record.del_flag = True
        db.session.commit()
        return jsonify({'message': '文件删除成功'}), 200
    else:
        return jsonify({'message': '未找到该文件，无法删除'}), 404


@app.route('/list', methods=['GET'])
def list_files():
    files = FileInfo.query.filter_by(del_flag=False).all()
    return jsonify([file.to_dict() for file in files])


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    