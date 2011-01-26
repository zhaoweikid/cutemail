# coding: utf-8
import os, sys
import wx

menu = [u'文件', [
                [wx.NewId(), "ID_FILE_OPEN", u'打开', 'open.png', 'OnFileOpen', None],
                [wx.NewId(), "ID_FILE_SAVE_AS", u'另存为', 'saveas.png', 'OnFileSaveAs', None],
                0,
                [wx.NewId(), "ID_FILE_GET_MAIL", u'收取邮件', 'mail_get.png', 'OnFileGetMail', None],
                [wx.NewId(), "ID_FILE_SEND_MAIL", u'发送邮件', 'mail_send.png', 'OnFileSendMail', None],
                [wx.NewId(), "ID_FILE_GET_ALL_MAIL", u'收取所有账户邮件', 'mail_get.png', 'OnFileGetAllMail', None],
                [wx.NewId(), "ID_FILE_SEND_ALL_MAIL", u'发送所有账户邮件', 'mail_send.png', 'OnFileSendAllMail', None],
                0,
                [wx.NewId(), "ID_FILE_IMPORT", u'导入邮件', 'down.png', 'OnFileImport', None],
                [wx.NewId(), "ID_FILE_EXPORT", u'导出邮件', 'up.png', 'OnFileExport', None],
                0,
                [wx.NewId(), "ID_FILE_EXIT", u'退出', 'exit.png', 'OnCloseWindow', None],
                ],
        u'查看', [
                [wx.NewId(), 'ID_VIEW_MAIL', u'邮件内容窗口', 'contents.png', 'OnViewMail', None],
                [wx.NewId(), 'ID_VIEW_ATTACH', u'附件内容窗口', 'attach.png', 'OnViewAttach', None],
                [wx.NewId(), 'ID_VIEW_CONTACT', u'联系人窗口', 'contact.png', 'OnViewContact', None],
                0,
                [wx.NewId(), 'ID_VIEW_SOURCE', u'信件原文', 'note.png', 'OnViewSource', None],
                [wx.NewId(), 'ID_VIEW_TEMPLATE', u'模板管理', 'template.png', 'OnViewTemplate', None],
                0,
                [wx.NewId(), 'ID_VIEW_ENCODE', u'编码', '', '', [
                    [wx.NewId(), 'ID_ENCODING_AUTO', u'自动选择', '', 'OnEncodeAuto', None],
                    [wx.NewId(), 'ID_ENCODING_GBK', u'简体中文(gbk)', '', 'OnEncodeGBK', None],
                    [wx.NewId(), 'ID_ENCODING_GB18030', u'简体中文(gb18030)', '', 'OnEncodeGB18030', None],
                    [wx.NewId(), 'ID_ENCODING_BIG5', u'繁体中文(big5)', '', 'OnEncodeBIG5', None],
                    [wx.NewId(), 'ID_ENCODING_UTF8', u'UTF-8', '', 'OnEncodeUTF8', None],
                ]],
                ],
        u'邮件', [
                [wx.NewId(), 'ID_MAIL_WRITE', u'写新邮件', 'mail_new.png', 'OnMailWrite', None],
                [wx.NewId(), 'ID_MAIL_REPLY', u'回复邮件', 'mail_reply.png', 'OnMailReply', None],
                [wx.NewId(), 'ID_MAIL_REPLY_ALL', u'回复全部', 'mail_replyall.png', 'OnMailReplyAll', None],
                [wx.NewId(), 'ID_MAIL_FORWARD', u'转发邮件', 'mail_send.png', 'OnMailForward', None],
                [wx.NewId(), 'ID_MAIL_SEND_SEC', u'再次发送', 'mail_send.png', 'OnMailSendSec', None],
                [wx.NewId(), 'ID_MAIL_ATTACH', u'作为附件发送', 'mail_send.png', 'OnMailAttach', None],
                0,
                [wx.NewId(), 'ID_MAIL_FLAG', u'标记为', 'flag.png', 'OnMailFlag', None],
                [wx.NewId(), 'ID_MAIL_SEARCH', u'查找', 'mail_find.png', 'OnMailSearch', None],
                ],
        u'邮箱', [
                [wx.NewId(), 'ID_MAILBOX_USER_NEW', u'新建邮箱账户', 'user.png', 'OnMailboxUserNew', None],
                [wx.NewId(), 'ID_MAILBOX_USER_RENAME', u'重命名邮箱账户', 'user.png', 'OnMailboxUserRename', None],
                [wx.NewId(), 'ID_MAILBOX_USER_DEL', u'删除邮箱账户', 'user.png', 'OnMailboxUserDel', None],
                0,
                [wx.NewId(), 'ID_MAILBOX_NEW', u'新建邮件夹', 'folder_open.png', 'OnMailboxNew', None],
                [wx.NewId(), 'ID_MAILBOX_RENAME', u'重命名邮件夹', 'folder_red.png', 'OnMailboxRename', None],
                [wx.NewId(), 'ID_MAILBOX_DEL', u'删除邮件夹', 'folder_grey.png', 'OnMailboxDel', None],
                0,
                [wx.NewId(), 'ID_MAILBOX_CLEAR_TRASH', u'清空删除邮件', '', 'OnMailboxClearTrash', None],
                [wx.NewId(), 'ID_MAILBOX_CLEAR_SPAM', u'清空垃圾邮件', '', 'OnMailboxClearSpam', None],
                0,
                [wx.NewId(), 'ID_MAILBOX_USER_OPTIONS', u'属性', 'preferences.png', 'OnMailboxUserOptions', None],
               ],
        u'导入导出',[
                [wx.NewId(), 'ID_MAILBOX_IMPORT', u'导入账户/联系人', '', '', [
                    [wx.NewId(), 'ID_IMPORT_CUTE_ACCOUT', u'导入cutemail账户', '', 'OnImportCuteUser', None],
                    [wx.NewId(), 'ID_IMPORT_CUTE_CONTACT', u'导入cutemail联系人', '', 'OnImportCuteContact', None],
                    [wx.NewId(), 'ID_IMPORT_OUTLOOK_ACCOUT', u'导入outlook账户', '', 'OnImportOutlookUser', None],
                    [wx.NewId(), 'ID_IMPORT_OUTLOOK_CONTACT', u'导入outlook联系人', '', 'OnImportOutlookContact', None],
                    [wx.NewId(), 'ID_IMPORT_FOXMAIL_ACCOUT', u'导入foxmail账户', '', 'OnImportFoxmailUser', None],
                    [wx.NewId(), 'ID_IMPORT_FOXMAIL_CONTACT', u'导入foxmail联系人', '', 'OnImportFoxmailContact', None],
                    ]],
                [wx.NewId(), 'ID_MAILBOX_EXPORT', u'导出账户/联系人', '', '', [
                    [wx.NewId(), 'ID_EXPORT_CUTE_ACCOUT', u'导出cutemail账户', '', 'OnExportCuteUser', None],
                    [wx.NewId(), 'ID_EXPORT_CUTE_CONTACT', u'导出cutemail联系人', '', 'OnExportCuteContact', None],
                    ]],
                ],
        u'帮助', [
                [wx.NewId(), 'ID_HELP', u'帮助主题', 'help.png', 'OnHelp', None],
                [wx.NewId(), 'ID_HELP_UPDATE', u'检查更新', 'help.png', 'OnHelpUpdate', None],
                [wx.NewId(), 'ID_HELP_ABOUT', u'关于', 'help.png', 'OnHelpAbout', None],
                ],
        ]

toolbar = [
        [wx.NewId(), 'ID_TOOLBAR_MAIL_GET', u'收取邮件', 'bitmaps/32/mail_get.png', u'收取邮件', 'OnFileGetMail'],
        [wx.NewId(), 'ID_TOOLBAR_MAIL_SEND', u'发送邮件', 'bitmaps/32/mail_send.png', u'发送发件箱中的邮件', 'OnFileSendMail'],
        0,
        [wx.NewId(), 'ID_TOOLBAR_MAIL_NEW', u'新邮件', 'bitmaps/32/mail_new.png', u'写新邮件', 'OnMailWrite'],
        [wx.NewId(), 'ID_TOOLBAR_MAIL_REPLY', u'回复', 'bitmaps/32/mail_reply.png', u'回复邮件', 'OnMailReply'],
        [wx.NewId(), 'ID_TOOLBAR_MAIL_FORWARD', u'转发', 'bitmaps/32/mail_forward.png', u'转发邮件', 'OnMailForward'],
        [wx.NewId(), 'ID_TOOLBAR_MAIL_DELETE', u'删除', 'bitmaps/32/mail_delete.png', u'删除邮件', 'OnMailDel'],
        0,
        [wx.NewId(), 'ID_TOOLBAR_ADDR', u'联系人', 'bitmaps/32/toggle_log.png', u'联系人', 'OnViewContact'],
        [wx.NewId(), 'ID_TOOLBAR_WWW', u'主页', 'bitmaps/32/home.png', u'主页', 'OnWebsite'],
        ]

