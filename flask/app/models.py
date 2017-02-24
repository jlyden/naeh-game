from app import db

Base = declarative_base()


class Game(Base):
    __tablename__ = 'game'

    id = db.Column(db.Integer, primary_key=True)
    round_count = db.Column(db.Integer, default=0)
    round_over = db.Column(db.Boolean, default=True)
    diversion = db.Column(db.Boolean, default=False)

    available = db.relationship("Available", uselist=False,
                                back_populates="game")


class Available(Base):
    __tablename__ = 'available'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    game = db.relationship("Game", back_populates="available")



class Available(Base):
    __tablename__ = 'available'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    game = db.relationship("Game", back_populates="available")
    beads = db.Column(db.)

