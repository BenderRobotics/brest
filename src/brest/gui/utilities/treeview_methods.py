def dict_to_treeview(dict_to_add, treeview, node_id=""):
    """
    Method takes a dictionary which appends a dictionary to
    the given treeview. If node_id is also given, dict will be
    appender under the node.

    :param dict: Dictionary for converting
    :type  dict: dict
    :param treeview: Treeview object or its child
                     to where the dict should be appended
    :type  treeview: :class:`~tkinter.ttk.Treeview`
    :param node_id: Append the dict under given Treeview's node
    :type  node_id: str
    """

    for key, value in dict_to_add.items():
        __add_child(key, value, treeview, node_id)


def __add_child(key, value, treeview, node_id=""):
    if not key or not value or not treeview:
        return

    node_id = node_id if node_id else ""

    if isinstance(value, dict):
        node_ = treeview.insert(node_id, "end", text=key)
        for key_, value_ in value[key].items():
            __add_child(key_, value_, node_)
    else:
        treeview.insert(node_id, "end", text=(key), values=[value])
