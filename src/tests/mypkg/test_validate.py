from mypkg.validate import is_name_rate_valid

def is_name_rate_valid_returns_good_output():
    assert is_name_rate_valid(backendName='CMSACO2020PREV7',rate='Default') == True
    assert is_name_rate_valid(backendName='CMSACO2020PEV7',rate='Default') == False
    assert is_name_rate_valid(backendName='CMSACO2020PEV7',rate='Defaultr') == False
    assert is_name_rate_valid(backendName='CMSACO2020PREV7',rate='Defaultr') == False