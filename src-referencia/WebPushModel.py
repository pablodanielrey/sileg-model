"""
https://github.com/web-push-libs/vapid/tree/master/python
https://mushfiq.me/2017/09/25/web-push-notification-using-python/
https://code.luasoftware.com/tutorials/pwa/develop-web-push-notification-server-with-python/
https://mushfiq.me/2017/09/25/web-push-notification-using-python/
"""


import logging
import os
import json
import uuid
import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Subscriber(Base):
    __tablename__ = 'subscriber'

    id = Column(String(), primary_key=True, default=None)
    created = Column(DateTime())
    modified = Column(DateTime())
    subscription_info = Column(Text())
    is_active = Column(Boolean(), default=True)

    @property
    def subscription_info_json(self):
        return json.loads(self.subscription_info)

    @subscription_info_json.setter
    def subscription_info_json(self, value):
        self.subscription_info = json.dumps(value)


from pywebpush import webpush, WebPushException
WEBPUSH_VAPID_PRIVATE_KEY = os.environ['WEBPUSH_VAPID_PRIVATE_KEY']
WEBPUSH_VAPID_PUBLIC_KEY = os.environ['WEBPUSH_VAPID_PUBLIC_KEY']
WEBPUSH_VAPID_EMAIL = os.environ['WEBPUSH_VAPID_EMAIL']

class WebPushModel:

    @classmethod
    def public_key(cls):
        return WEBPUSH_VAPID_PUBLIC_KEY

    @classmethod
    def broadcast(cls, session, message):
        count = 0
        items = session.query(Subscriber).filter(Subscriber.is_active == True).all()
        for _item in items:
            try:
                webpush(
                    subscription_info=_item.subscription_info_json,
                    data=message,
                    vapid_private_key=WEBPUSH_VAPID_PRIVATE_KEY,
                    vapid_claims={
                        "sub": "mailto:webpush@mydomain.com"
                    }
                )
                count += 1
            except WebPushException as ex:
                logging.exception(ex)
        return count            

    @classmethod
    def subscribe(cls, session, subscription_info, is_active):
        item = session.query(Subscriber).filter(Subscriber.subscription_info == subscription_info).first()
        if not item:
            item = Subscriber()
            item.id = str(uuid.uuid4())
            item.created = datetime.datetime.utcnow()
            item.subscription_info = subscription_info

        item.is_active = is_active
        item.modified = datetime.datetime.utcnow()
        session.add(item)
        return item.id