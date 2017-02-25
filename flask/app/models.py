from app import db

Base = db.declarative_base()


class Game(Base):
    __tablename__ = 'game'

    id = db.Column(db.Integer, primary_key=True)
    round_count = db.Column(db.Integer, default=0)
    round_over = db.Column(db.Boolean, default=True)
    diversion = db.Column(db.Boolean, default=False)

    available = db.relationship("available", uselist=False,
                                back_populates="game")
    market = db.relationship("market", uselist=False,
                             back_populates="game")
    unsheltered = db.relationship("unsheltered", uselist=False,
                                  back_populates="game")
    intake = db.relationship("intake", uselist=False,
                             back_populates="game")
    emergency = db.relationship("emergency", uselist=False,
                                back_populates="game")
    rapid = db.relationship("rapid", uselist=False,
                            back_populates="game")
    outreach = db.relationship("outreach", uselist=False,
                               back_populates="game")
    transitional = db.relationship("transitional",
                                   uselist=False,
                                   back_populates="game")
    permanent = db.relationship("permanent", uselist=False,
                                back_populates="game")


class Available(Base):
    __tablename__ = 'available'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    game = db.relationship("Game", back_populates="available")
    beads = db.Column(db.Array(db.Integer))


class Market(Base):
    __tablename__ = 'market'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    game = db.relationship("Game", back_populates="market")
    beads = db.Column(db.Array(db.Integer))


class Unsheltered(Base):
    __tablename__ = 'unsheltered'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    game = db.relationship("Game", back_populates="unsheltered")
    beads = db.Column(db.Array(db.Integer))


class Intake(Base):
    __tablename__ = 'intake'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    game = db.relationship("Game", back_populates="intake")
    beads = db.Column(db.Array(db.Integer))


class Emergency(Base):
    __tablename__ = 'emergency'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    game = db.relationship("Game", back_populates="emergency")
    beads = db.Column(db.Array(db.Integer))


class Rapid(Base):
    __tablename__ = 'rapid'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    game = db.relationship("Game", back_populates="rapid")
    beads = db.Column(db.Array(db.Integer))


class Outreach(Base):
    __tablename__ = 'outreach'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    game = db.relationship("Game", back_populates="outreach")
    beads = db.Column(db.Array(db.Integer))


class Transitional(Base):
    __tablename__ = 'transitional'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    game = db.relationship("Game", back_populates="transitional")
    beads = db.Column(db.Array(db.Integer))


class Permanent(Base):
    __tablename__ = 'permanent'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    game = db.relationship("Game", back_populates="permanent")
    beads = db.Column(db.Array(db.Integer))
