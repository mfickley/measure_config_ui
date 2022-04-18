from mypkg.validate import is_name_rate_valid

def test_validNameValidRate():
    assert is_name_rate_valid(backendName='CMSACO2020PREV7',rate='Default') == True

def test_invalidNameValidRate():
    assert is_name_rate_valid(backendName='CMSACO2020PEV7',rate='Default') == False

def test_validNameInvalidRate():
    assert is_name_rate_valid(backendName='CMSACO2020PREV7',rate='Defaultr') == False

def test_invalidNameInvalidRate():
    assert is_name_rate_valid(backendName='CMSACO2020PEV7',rate='Defaultr') == False