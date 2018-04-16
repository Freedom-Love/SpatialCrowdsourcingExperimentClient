from models import *


class DBUtil:
    def __init__(self):
        pass

    @classmethod
    def set_worker_attributes(cls, uid, longitude, latitude, capacity=None, reliability=None, min_lon=None,
                              min_lat=None, max_lon=None, max_lat=None, is_online=None, commit=True):
        user_detail = session.query(WorkerDetail).filter_by(id=uid, is_online=is_online).first()
        if user_detail is None:
            user_detail = WorkerDetail()
            user_detail.id = uid
            user_detail.is_online = is_online
        user_detail.longitude = longitude
        user_detail.latitude = latitude
        user_detail.capacity = capacity
        user_detail.reliability = reliability
        user_detail.region_min_lon = min_lon
        user_detail.region_min_lat = min_lat
        user_detail.region_max_lon = max_lon
        user_detail.region_max_lat = max_lat
        session.add(user_detail)

        if commit:
            session.commit()

    @classmethod
    def create_hit(cls, longitude, latitude, arrival_time, expire_time, require_answer_count, entropy, confidence,
                   is_valid=None, commit=True):
        hit_detail = HitDetail()
        hit_detail.is_valid = is_valid
        session.add(hit_detail)
        if entropy is not None:
            hit_detail.entropy = entropy
        if confidence is not None:
            hit_detail.confidence = confidence
        hit_detail.longitude = longitude
        hit_detail.latitude = latitude
        hit_detail.begin_time = arrival_time
        hit_detail.end_time = expire_time
        hit_detail.required_answer_count = require_answer_count
        session.flush()
        session.refresh(hit_detail)
        if commit:
            session.commit()
        return hit_detail.id

    @classmethod
    def clear(cls):
        session.query(HitDetail).delete()
        session.query(WorkerDetail).delete()
        session.commit()

    @classmethod
    def initialize_db(cls):
        DBUtil.clear()
