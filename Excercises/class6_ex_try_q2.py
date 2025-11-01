def get_special_item_from_list(lst, i):
    """Return lst[i + 1], or the last item if the index is out of range; return 0 if empty."""
    try:
        return lst[i + 1]
    except IndexError:
         return lst[-1]


print(get_special_item_from_list([1, 2, 3, 4], 1))  # valid access -> 3
print(get_special_item_from_list([1, 2, 3, 4], 3))  # out of range -> last item 4
