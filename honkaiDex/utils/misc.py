def rreplace(s : str, old :str, new : str, occurrence : int):
    """
    Replace the last occurrence of a string in a string.
    """
    
    li = s.rsplit(old, occurrence)
    return new.join(li)