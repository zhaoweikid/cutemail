# coding: utf-8
import os, sys

menu = [u'文件', [
                [wx.NewId(), "ID_FILE_OPEN", u'打开', 'open.png', 'On', None],
                [wx.NewId(), "ID_FILE_SAVE_AS", u'另存为', 'saveas.png', 'On', None],
                0,
                [wx.NewId(), "ID_FILE_GET_MAIL", u'收取邮件', 'mail_get.png', 'On', None],
                [wx.NewId(), "ID_FILE_SEND_MAIL", u'发送邮件', 'mail_send.png', 'On', None],
                [wx.NewId(), "ID_FILE_GET_ALL_MAIL", u'收取所有账户邮件', 'mail_get.png', 'On', None],
                [wx.NewId(), "ID_FILE_SEND_ALL_MAIL", u'发送所有账户邮件', 'mail_send.png', 'On'None],
                0,
                [wx.NewId(), "ID_FILE_IMPORT", u'导入邮件', 'down.png', 'On'],
                [wx.NewId(), "ID_FILE_EXPORT", u'导出邮件', 'up.png', 'On'],
                0,
                [wx.NewId(), "ID_FILE_EXIT", u'退出', 'exit.png', 'On'],
                ],
        u'查看', [
                [wx.NewId(), 'ID_VIEW_MAIL', u'邮件内容窗口', 'contents.png', 'On', None],
                [wx.NewId(), 'ID_VIEW_ATTACH', u'附件内容窗口', 'attach.png', 'On', None],
                [wx.NewId(), 'ID_VIEW_CONTACT', u'联系人窗口', 'contact.png', 'On', None],
                [wx.NewId(), 'ID_VIEW_SOURCE', u'信件原文', 'note.png', 'On', None],
                [wx.NewId(), 'ID_VIEW_TEMPLATE', u'模板管理', 'template.png', 'On', None],
                0,
                [wx.NewId(), 'ID_VIEW_ENCODE', u'编码', '', 'On', [
                    [wx.NewId(), 'ID_ENCODING_AUTO', u'自动选择', '', 'On', None],
                    [wx.NewId(), 'ID_ENCODING_GBK', u'简体中文(gbk)', '', 'On', None],
                    [wx.NewId(), 'ID_ENCODING_GB18030', u'简体中文(gb18030)', '', 'On', None],
                    [wx.NewId(), 'ID_ENCODING_BIG5', u'繁体中文(big5)', '', 'On', None],
                    [wx.NewId(), 'ID_ENCODING_UTF8', u'UTF-8', '', 'On', None],
                ]],
                ],
        u'邮件', [
                [wx.NewId(), 'ID_MAIL_WRITE', u'写新邮件', 'mail_new.png', 'On', None],
                [wx.NewId(), 'ID_MAIL_REPLY', u'回复邮件', 'mail_reply.png', 'On', None],
                [wx.NewId(), 'ID_MAIL_REPLY_ALL', u'回复全部', 'mail_replyall.png', 'On', None],
                [wx.NewId(), 'ID_MAIL_FORWARD', u'转发邮件', 'mail_send.png', 'On', None],
                [wx.NewId(), 'ID_MAIL_SEND_SEC', u'再次发送', 'mail_send.png', 'On', None],
                [wx.NewId(), 'ID_MAIL_ATTACH', u'作为附件发送', 'mail_send.png', 'On', None],
                [wx.NewId(), 'ID_MAIL_FLAG', u'标记为', 'flag.png', 'On', None],
                [wx.NewId(), 'ID_MAIL_SEARCH', u'查找', 'mail_find.png', 'On', None],
                ],
        u'邮箱', [[]],
        u'帮助']

toolbar = [[]]

