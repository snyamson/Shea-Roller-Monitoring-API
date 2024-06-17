from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

# Create a base class for declarative class definitions
Base = declarative_base()

class Hub(Base):
    __tablename__ = 'hubs'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    # Relationship Link
    submissions = relationship('Submission', back_populates='hub')

    def __repr__(self):
        attrs = ", ".join(f"{attr}={getattr(self, attr)!r}" for attr in self.__dict__)
        return f"<Hub({attrs})>"

class Submission(Base):
    __tablename__ = 'submissions'
    id = Column(Integer, primary_key=True)
    hub_id = Column(Integer, ForeignKey('hubs.id'), nullable=False)
    submission_id = Column(Integer, nullable=False)
    today = Column(DateTime, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    age = Column(String)
    age_range = Column(String)
    gender = Column(String)
    contact = Column(String)
    date_of_rental = Column(Date)
    did_roller_help = Column(String)
    bowls_usually_picked = Column(Integer)
    bowls_picked_with_roller = Column(Integer)
    additional_shea_collected_due_to_roller = Column(Integer)
    less_difficulty_using_roller = Column(String)
    time_saved = Column(String)
    time_saved_used_for = Column(String)
    time_saved_used_for_other = Column(String)
    hours_taken_to_use = Column(String)
    why_long_hours_of_use = Column(String)
    uuid = Column(String)
    status = Column(String)
    submission_time = Column(DateTime)
    
    # Relationship Link
    hub = relationship('Hub', back_populates='submissions')

    def __repr__(self):
        attrs = ", ".join(f"{attr}={getattr(self, attr)!r}" for attr in self.__dict__)
        return f"<Submission({attrs})>"
