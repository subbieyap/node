from plumber import (
    extend,
    default,
    Part,
)
from zope.interface import implements
from zope.interface.common.mapping import IReadMapping
from node.interfaces import (
    INode,
    IReference,
)

class Order(Part):

    @extend
    def insertbefore(self, newnode, refnode):
        self._validateinsertion(newnode, refnode)
        nodekey = newnode.__name__
        refkey = refnode.__name__
        index = self._nodeindex(refnode)
        prevnode = None
        prevkey = None
        if index > 0:
            prevkey = self.keys()[index - 1]
            prevnode = self._dict_impl().__getitem__(self, prevkey)
        if prevnode is not None:
            self._dict_impl().__getitem__(self, prevkey)[2] = nodekey
            newnode = [prevkey, newnode, refkey]
        else:
            self._dict_impl().lh = nodekey
            newnode = [_nil, newnode, refkey]
        self._dict_impl().__getitem__(self, refkey)[0] = nodekey
        self._dict_impl().__setitem__(self, nodekey, newnode)
        self[nodekey] = newnode[1]

    @extend
    def insertafter(self, newnode, refnode):
        self._validateinsertion(newnode, refnode)
        nodekey = newnode.__name__
        refkey = refnode.__name__
        index = self._nodeindex(refnode)
        nextnode = None
        nextkey = None
        keys = self.keys()
        if index < len(keys) - 1:
            nextkey = self.keys()[index + 1]
            nextnode = self._dict_impl().__getitem__(self, nextkey)
        if nextnode is not None:
            self._dict_impl().__getitem__(self, nextkey)[0] = nodekey
            newnode = [refkey, newnode, nextkey]
        else:
            self._dict_impl().lt = nodekey
            newnode = [refkey, newnode, _nil]
        self._dict_impl().__getitem__(self, refkey)[2] = nodekey
        self._dict_impl().__setitem__(self, nodekey, newnode)
        self[nodekey] = newnode[1]
    
    @extend
    def detach(self, key):
        node = self[key]
        del self[key]
        if hasattr(self, '_index') and self._index is not None:
            node._index = { int(node.uuid): node }
            node._index_nodes()
        return node
    
    @default
    def _validateinsertion(self, newnode, refnode):
        nodekey = newnode.__name__
        if nodekey is None:
            raise ValueError, u"Given node has no __name__ set."
        if self.node(newnode.uuid) is not None:
            raise KeyError, u"Given node already contained in tree."
        index = self._nodeindex(refnode)
        if index is None:
            raise ValueError, u"Given reference node not child of self."

    @default
    def _nodeindex(self, node):
        index = 0
        for key in self.keys():
            if key == node.__name__:
                return index
            index += 1
        return None

    # orderable related
    @default
    def _index_nodes(self):
        for node in self.values():
            try:
                uuid = int(node.uuid)
            except AttributeError:
                # non-Node values are a dead end, no magic for them
                continue
            self._index[uuid] = node
            node._index = self._index
            node._index_nodes()
