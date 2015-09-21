from xml.etree import ElementTree

from werobot.messages import MESSAGE_TYPES, UnknownMessage
from werobot.utils import to_text


def parse_user_msg(xml):
    """
    Parse xml from wechat server and return an Message
    :param xml: raw xml from wechat server.
    :return: an Message object
    """
    if not xml:
        return

    root = ElementTree.fromstring(xml)
    wechat_message = dict((child.tag, to_text(child.text))
                          for child in root)
    locationinfo = root.find('SendLocationInfo')
    if locationinfo:
        wechat_message.pop("SendLocationInfo")
        wechat_message.update(dict((child.tag, to_text(child.text))
                          for child in locationinfo))
    wechat_message["raw"] = xml
    wechat_message["type"] = wechat_message.pop("MsgType")

    message_type = MESSAGE_TYPES.get(wechat_message["type"], UnknownMessage)
    return message_type(wechat_message)
