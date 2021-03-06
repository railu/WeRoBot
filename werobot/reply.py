# -*- coding: utf-8 -*-
import time

from werobot.messages import WeChatMessage
from werobot.utils import is_string, to_text


class Article(object):
    def __init__(self, title, description, img, url):
        self.title = title
        self.description = description
        self.img = img
        self.url = url

class mpArticle(object):
    def __init__(self, title="a", content="a", description="", author="", url="http://www.shwlzy.com/", thumb_media_id=u'2iIgl91zWlbZuQx0guQeH65bT2ZYs7-6mrQXsHHqTCrR9RI4V-yywMvwpoF4RzApijbXBLKO9Sy_be83J9wintg', show_cover_pic="0"):
        self.title = title
        self.id = thumb_media_id
        self.author = author
        self.url = url
        self.content = content
        self.description = description
        self.show_cover_pic = show_cover_pic

class WeChatReply(object):
    def __init__(self, message=None, **kwargs):
        if "source" not in kwargs and isinstance(message, WeChatMessage):
            kwargs["source"] = message.target

        if "target" not in kwargs and isinstance(message, WeChatMessage):
            kwargs["target"] = message.source

        if 'time' not in kwargs:
            kwargs["time"] = int(time.time())

        args = dict()
        for k, v in kwargs.items():
            if is_string(v):
                v = to_text(v)
            args[k] = v

        self._args = args

    def render(self):
        raise NotImplementedError()

class TextReply(WeChatReply):
    TEMPLATE = to_text("""
    <xml>
    <ToUserName><![CDATA[{target}]]></ToUserName>
    <FromUserName><![CDATA[{source}]]></FromUserName>
    <CreateTime>{time}</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[{content}]]></Content>
    </xml>
    """)

    def render(self):
        return TextReply.TEMPLATE.format(**self._args)

class ImageReply(WeChatReply):
    TEMPLATE = to_text("""
    <xml>
    <ToUserName><![CDATA[{target}]]></ToUserName>
    <FromUserName><![CDATA[{source}]]></FromUserName>
    <CreateTime>{time}</CreateTime>
    <MsgType><![CDATA[image]]></MsgType>
    <Image>
        <MediaId><![CDATA[{media_id}]]></MediaId>
    </Image>
    </xml>
    """)

    def render(self):
        return ImageReply.TEMPLATE.format(**self._args)

class VoiceReply(WeChatReply):
    TEMPLATE = to_text("""
    <xml>
    <ToUserName><![CDATA[{target}]]></ToUserName>
    <FromUserName><![CDATA[{source}]]></FromUserName>
    <CreateTime>{time}</CreateTime>
    <MsgType><![CDATA[voice]]></MsgType>
    <Voice>
        <MediaId><![CDATA[{media_id}]]></MediaId>
    </Voice>
    </xml>
    """)

    def render(self):
        return VoiceReply.TEMPLATE.format(**self._args)

class VideoReply(WeChatReply):
    TEMPLATE = to_text("""
    <xml>
    <ToUserName><![CDATA[{target}]]></ToUserName>
    <FromUserName><![CDATA[{source}]]></FromUserName>
    <CreateTime>{time}</CreateTime>
    <MsgType><![CDATA[video]]></MsgType>
    <Video>
        <MediaId><![CDATA[{media_id}]]></MediaId>
        <Title><![CDATA[{title}]]></Title>
        <Description><![CDATA[{description}]]></Description>
    </Video>
    </xml>
    """)

    def render(self):
        return VideoReply.TEMPLATE.format(**self._args)

class NewsReply(WeChatReply):
    TEMPLATE = to_text("""
    <xml>
    <ToUserName><![CDATA[{target}]]></ToUserName>
    <FromUserName><![CDATA[{source}]]></FromUserName>
    <CreateTime>{time}</CreateTime>
    <MsgType><![CDATA[news]]></MsgType>
    <Content><![CDATA[{content}]]></Content>
    <ArticleCount>{count}</ArticleCount>
    <Articles>{items}</Articles>
    </xml>
    """)

    ITEM_TEMPLATE = to_text("""
    <item>
    <Title><![CDATA[{title}]]></Title>
    <Description><![CDATA[{description}]]></Description>
    <PicUrl><![CDATA[{img}]]></PicUrl>
    <Url><![CDATA[{url}]]></Url>
    </item>
    """)

    def __init__(self, message=None, **kwargs):
        super(NewsReply, self).__init__(message, **kwargs)
        self._articles = []

    def add_article(self, article):
         if len(self._articles) >= 10:
             raise AttributeError("Can't add more than 10 articles"
                                 " in an ArticlesReply")
         else:
             self._articles.append(article)

    def render(self):
        items = []
        for article in self._articles:
            items.append(NewsReply.ITEM_TEMPLATE.format(
                title=to_text(article.title),
                description=to_text(article.description),
                img=to_text(article.img),
                url=to_text(article.url)
            ))
        self._args["items"] = ''.join(items)
        self._args["count"] = len(items)
        if "content" not in self._args:
            self._args["content"] = ''
        return NewsReply.TEMPLATE.format(**self._args)

def create_reply(reply, message=None):
    if isinstance(reply, WeChatReply):
        return reply.render()
    elif is_string(reply):
        reply = TextReply(message=message, content=reply)
        return reply.render()
    elif isinstance(reply, list) and all([len(x) == 4 for x in reply]):
        if len(reply) > 10:
            raise AttributeError("Can't add more than 10 articles"
                                 " in an ArticlesReply")
        r = NewsReply(message=message)
        for article in reply:
            article = Article(*article)
            r.add_article(article)
        return r.render()
