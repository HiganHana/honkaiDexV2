import typing
from honkaiDex.utils.misc import rreplace

_MISSING = object()

class MediaWikiRaw:
    def __init__(self, raw_text : typing.Union[list, str]) -> None:
        if isinstance(raw_text, str):
            self._raw_text = raw_text
            self.raw_list = [text.strip("\n") for text in raw_text.split("\n")]
            # remove empty lines
            self.raw_list = [text for text in self.raw_list if text != ""]
            
        else:
            self._raw_text = None
            self.raw_list = raw_text    
        
        self.text = []
        self.blobs = []
        self.variables = {}
        self.ordered_items = []
    
    
    @property
    def raw_text(self):
        if self._raw_text is None:
            self._raw_text = "\n".join(self.raw_list)
        return self._raw_text
    
    def _parse_var(self, line :str):
        # parse variables
        if not line.startswith("|") and "=" in line:
            return None
        splitted = line.split("=",1)
        if not len(splitted) == 2:
            return None
        
        var_name, var_value = splitted[0], splitted[1]
        var_name = var_name[1:].strip()
        var_value = var_value.strip()
        var_obj = MediaWikiRawVar(var_name, var_value)
        self.ordered_items.append(var_obj)
        self.variables[var_name]= var_obj.value
        
        return True

    def _parse_blob(self, lines : typing.List[str]):
        self.blobs.append(MediaWikiRawBlob(lines))
        self.ordered_items.append(self.blobs[-1])
    
    def _parse_text(self, line : str):
        if line.startswith("{{"):
            line = line[2:]
    
        self.text.append(line)
        self.ordered_items.append(line)
        
    def items(self, filter : typing.Iterable = None):
        if filter:
            filter = tuple(filter)
        if filter is None:
            return iter(self.ordered_items)
        else:
            for item in self.ordered_items:
                if isinstance(item, filter):
                
                    yield item
    
                
    def recursItems(self, filter : typing.Iterable = None):
        filter = tuple(filter) if filter else tuple()
        for item in self.ordered_items:
            if isinstance(item, MediaWikiRawVar) and isinstance(item, filter):
                yield item
            elif isinstance(item, MediaWikiRawVar) and MediaWikiRawBlob in filter:
                for subitem in item.value:
                    if isinstance(subitem, MediaWikiRawVar) and isinstance(subitem, filter):
                        yield subitem
            elif isinstance(item, MediaWikiRaw) and isinstance(item, filter):
                yield item
            elif isinstance(item, MediaWikiRaw):
                for subitem in item.recursItems(filter):
                    yield subitem
            
    def getVar(self, name : str, default = None):
        for item in self.ordered_items:
            if isinstance(item, MediaWikiRawVar) and item.name == name:
                return item.value
            elif isinstance(item, MediaWikiRaw):
                val = item.getVar(name, _MISSING)
                if val is not _MISSING:
                    return val
                
        return default

        

    
class MediaWikiRawBlob(MediaWikiRaw):
    def __init__(self, blob_text : typing.Union[str, list]) -> None:
        super().__init__(blob_text)
        # remove first {{ and last }}
        self._raw_text = rreplace(self.raw_text, "}}", "", 1).replace("{{", "", 1)
        self.raw_list[0] = self.raw_list[0].replace("{{", "", 1) if self.raw_list[0].startswith("{{") else self.raw_list[0]
        self.raw_list[-1] = rreplace(self.raw_list[-1], "}}", "", 1) if self.raw_list[-1].endswith("}}") else self.raw_list[-1]
    
        # if blob does not start with | and has | in it, it is just text
        line = self.raw_list[0]
        if len(self.raw_list) == 1 and (not line.startswith("|") and "|" in line):
            values = line.split("|")
            self.text = values
            return
        
        self._parse()

    def __str__(self) -> str:
        return self.raw_text
    
    def _parse(self):
        for line in self.raw_list:
            if self._parse_var(line) is not None:
                continue
        
            if line == "}}":
                continue
            
            self._parse_text(line)


class MediaWikiRawVar:
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = []
        
        # split {{x|y|z}} a {{b|c|d}} into ["{{x|y|z}}", "a", "{{b|c|d}}"]
        value = value.replace("}}","?^{{")
        values = value.split("{{")
        # filter empty
        values = [value.strip("{").strip() for value in values if value != ""]

        for v in values:
            if "?^" in v:
                v = v.replace("?^", "")
                self.value.append(MediaWikiRawBlob(v))
            else:
                self.value.append(v)
    
class MediaWikiRawData(MediaWikiRaw):
    """
    `text` is a list of strings without special properties
    `blobs are information wrapped in {{data}}`
    `variables` are key-value pairs, presented in the form of |key = value
    `subcomponents` are presented in the form of ==section==
    """
    
    def __init__(
        self, 
        raw_text : typing.Union[list, str], 
        subcomponent : str = None,
        subcomponent_lv : int = 0,
    ) -> None:
        super().__init__(raw_text)
        self.subcomponents = {}
        self.subcomponent = subcomponent    
        self.subcomponent_lv = subcomponent_lv
        self._parse()
        
    def _parse(self):
        
        # first identify subcomponents
        subname = None
        raw = []
        equal_sign_counts = 2
        if self.subcomponent_lv >= 1:
            equal_sign_counts = 2 + self.subcomponent_lv
        
        base_section_marker = None
        blob_open_count = 0
                
        for i, line in enumerate(self.raw_list):
            line : str

            # check if line is exact subcomponent
            if (
                line.startswith(equal_sign_counts*"=")
                and 
                line.endswith(equal_sign_counts*"=")
                and 
                line.count("=") == equal_sign_counts*2
            ):    
                # create a new subcomponent
                subname = line.strip("=")
                if base_section_marker is None:
                    base_section_marker = i
                
                if len(raw) > 0:
                    self.subcomponents[subname] = MediaWikiRawData(raw, subname, self.subcomponent_lv+1)
                    self.ordered_items.append(self.subcomponents[subname])
                    raw = []
                continue
                    
            if base_section_marker:
                raw.append(line)
                continue
        
            # parse blob
            # count the number of open and close brackets
            blob_open_count += line.count("{{")
            blob_open_count -= line.count("}}")

            if blob_open_count > 0:
                raw.append(line)
                continue
            
            if blob_open_count == 0 and ("{{" in line or "}}" in line):
                raw.append(line)
                self._parse_blob(raw)
                raw = []
                continue
            #
            if self._parse_var(line) is not None:
                continue
            
            self._parse_text(line)
            
