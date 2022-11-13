import unittest
from honkaiDex.scrapper.scrap import wiki_instance, api_url
import requests
from honkaiDex.models.mediawikiRaw import MediaWikiRawData, MediaWikiRawVar, MediaWikiRawBlob
import cProfile

class t_mediawiki(unittest.TestCase):
    def test_1(self):
        x = wiki_instance.categorytree("Battlesuits", depth=1)
        pass
    
    def test_2(self):
        page = wiki_instance.page("Crimson Impulse")
        raw_text = page.wikitext
        
        # profiler
        profiler = cProfile.Profile()
        profiler.enable()
        
        data = MediaWikiRawData(raw_text)
        
        profiler.disable()
        # export 
        profiler.dump_stats("test_2.prof")
        
        for item in data.recursItems([MediaWikiRawVar]):
            item : MediaWikiRawVar
            print_values = item.value
            if any(isinstance(item, MediaWikiRawBlob) for item in item.value):
                print_values = [str(item) for item in item.value]
            
            print(item.name, print_values)
        
        
        print(data.getVar("core_strengths"))
        print(data.getVar("version"))
        print(data.getVar("rank"))
        print(data.getVar("type"))
        print(data.getVar("leader"))
        print(data.getVar("leaderEffect"))
        print(data.getVar("special"))
        print(data.getVar("specialEffect"))
        print(data.getVar("passive"))
        print(data.getVar("passiveEffect"))
        print(data.getVar("ultimate"))
        print(data.getVar("ultimateEffect"))
        print(data.getVar("evasion"))
        print(data.getVar("evasionEffect"))
        print(data.getVar("basic"))
        print(data.getVar("basicEffect"))
        print(data.getVar("shared"))
        print(data.getVar("profile"))
