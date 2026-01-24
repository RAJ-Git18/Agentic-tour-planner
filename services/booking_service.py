from models.models import Booking
from typing import Dict
from utils.logger import logger


class BookingService:
    def __init__(self, db):
        self.db = db

    def booking_service(self, user_id: str, title:str):
        booking = Booking(user_id=user_id, title=title)
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        logger.info(f"Booking created: {booking.id}")
        return {
            "status": "success",
            "booking_id": booking.id,
            "message": "Booking confirmed successfully.",
        }
