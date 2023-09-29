from community import db, login_manager
from datetime import datetime
from flask_login import UserMixin

# Isso serve para dizermos ao login_manager que a função abaixo é a que retorna o ID do Usuário
@login_manager.user_loader
def load_user(id_user):
    usuario = Usuario.query.get(int(id_user))
    return usuario

# Banco de dados dos Usuários
class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)
    sobrenome = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    senha = db.Column(db.String, nullable=False)
    foto_perfil = db.Column(db.String, default='default.jpg')
    posts = db.relationship('Post', backref='autor', lazy=True)
    tech_principal = db.Column(db.String, nullable=False, default='Não Informado')

    def count_posts(self):
        return len(self.posts)
    
    
    
# Banco de Dados dos posts dos usuários
class Post(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String, nullable=False)
    corpo = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)