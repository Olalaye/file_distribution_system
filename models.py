from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class FileInfo(db.Model):
    __tablename__ = 'files'
    
    md5 = db.Column(db.String(32), primary_key=True)
    file_path = db.Column(db.String(255), nullable=False)
    version = db.Column(db.Integer, default=1)
    del_flag = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    filenames = db.relationship('FileName', backref='file_info', lazy=True)
    
    def to_dict(self):
        return {
            'md5': self.md5,
            'filenames': [fn.filename for fn in self.filenames],
            'file_path': self.file_path,
            'version': self.version,
            'del_flag': self.del_flag
        }

class FileName(db.Model):
    __tablename__ = 'filenames'
    __table_args__ = (db.UniqueConstraint('md5', 'filename', name='uix_md5_filename'),)
    
    id = db.Column(db.Integer, primary_key=True)
    md5 = db.Column(db.String(32), db.ForeignKey('files.md5'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    
    def to_dict(self):
        return {
            'filename': self.filename
        }