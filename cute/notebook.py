# -*- encoding: utf-8 -*-
import sys, string, os
import wx
import treelist
import  wx.html as  html

def treelist_add(parent):
    cols = [u'邮件状态', u'附件', u'分类',u'发件人',u'邮件主题',u'日期',u'邮件大小']          
    
    trees = []    
    tree = treelist.VirtualTreeListCtrl(parent, column=cols, style = wx.SIMPLE_BORDER)
    trees.append(tree)
    
    return trees

class ListBook(wx.Notebook):
    def __init__(self, *args, **kwargs):        
        #treemodel = kwargs.pop('treemodel')
        #log = kwargs.pop('log')
        cols = [u'邮件状态',u'分类',u'发件人',u'邮件主题',u'日期',u'邮件大小']
        kwargs['style'] = wx.SIMPLE_BORDER        
        super(ListBook, self).__init__(*args, **kwargs)
        self.trees = []
        for class_, title in [(treelist.VirtualTreeListCtrl, u'时间排序'),
                              (treelist.VirtualTreeListCtrl, u'线索排序')]:
            tree = class_(self, column=cols)
            self.trees.append(tree)
            self.AddPage(tree, title)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        
    def OnPageChanged(self, event):
        oldTree = self.GetPage(event.OldSelection)
        newTree = self.GetPage(event.Selection)
        #newTree.RefreshItems()
        #newTree.SetExpansionState(oldTree.GetExpansionState())
        event.Skip()

    def GetIndicesOfSelectedItems(self):
        tree = self.trees[self.GetSelection()]
        if tree.GetSelections():
            return [tree.GetIndexOfItem(item) for item in tree.GetSelections()]
        else:
            return [()]

    def RefreshItems(self):
        tree = self.trees[self.GetSelection()]
        tree.RefreshItems()
        tree.UnselectAll()

class ViewBook(wx.Panel):
    def __init__(self, parent):        
        wx.Panel.__init__(self, parent, -1, size=(300,300))        
        #sub = wx.StaticText(self, -1, "主题: ", style=wx.ALIGN_LEFT )
        #sizer = wx.BoxSizer(wx.VERTICAL)
        htmlcnt = html.HtmlWindow(parent, -1, style=wx.NO_FULL_REPAINT_ON_RESIZE)
        htmlcnt.Hide()
        #sizer.Add(sub, 0, wx.LEFT | wx.TOP, 2)
        #sizer.Add(htmlcnt, 0, wx.LEFT | wx.TOP, 2)
        #self.SetSizer(sizer)
        


        
