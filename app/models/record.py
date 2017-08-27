from app import db


class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    round_count = db.Column(db.Integer, nullable=False)
    from_board_num = db.Column(db.Integer, nullable=False)
    to_board_num = db.Column(db.Integer, nullable=False)
    beads_moved = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "<Record: Game %r, Round %r, From  %r, To %r, \
                 Beads %r >" % (self.game_id,
                                self.round_count,
                                self.from_board_num,
                                self.to_board_num,
                                self.beads_moved)


class Count(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    round_count = db.Column(db.Integer, nullable=False)
    board_num = db.Column(db.Integer, nullable=False)
    beads = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "<End Count: Game %r, Round %r, Board %r, \
                 Beads %r >" % (self.game_id,
                                self.round_count,
                                self.board,
                                self.beads)


class Decision(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    round_count = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(500))

    def __repr__(self):
        return "<Decision: Game %r, Round %r - %r >" % (self.game_id,
                                                        self.round_count,
                                                        self.note)
