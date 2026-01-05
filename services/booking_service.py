from models.models import Booking
from typing import Dict
from utils.logger import logger


class BookingService:
    def __init__(self, db):
        self.db = db

    def booking_service(self, user_id: str, planning_response: Dict[str, any]):
        booking = Booking(user_id=user_id, planning_response=planning_response)
        self.db.add(booking)
        self.db.commit()
        logger.info(f"Booking created: {booking}")
        return booking
