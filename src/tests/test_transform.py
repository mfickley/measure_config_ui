from mypkg.transform import assigned_measure_dict

def test_assigned_measure_dict():
    assert assigned_measure_dict(initiative = 'MSSP-TEST',backendName='CMSACO2020CARE2',rate='Default') == False