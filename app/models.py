from app import db

class Folders(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	folder = db.Column(db.String(), index=True, unique=True)
	# folioid = db.Column(db.Integer, index=True)
	keywords = db.Column(db.String(), index=True)

	def __repr__(self):
		return '<Folder: {} | Keywords: {}>'.format(self.folder, self.keywords)