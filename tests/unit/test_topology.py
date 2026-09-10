import pytest
from string_sm_sat.geometry.cicy import benchmark,CICY
from string_sm_sat.geometry.chern import euler_number,tangent_chern
@pytest.mark.parametrize('name,c2,euler',[('quintic',(50,),-200),('bicubic',(36,36),-162),('7862',(24,)*4,-128),('7447',(24,)*5,-80)])
def test_topology(name,c2,euler):
    g=benchmark(name)
    assert g.c2==c2
    assert euler_number(g.ambient,g.configuration)==euler==2*(g.h11-g.h21)
    assert not any(sum(k)==1 for k in tangent_chern(g.ambient,g.configuration))
    if name in ('7862','7447'):
        for i in range(g.h11):
            for j in range(g.h11):
                for k in range(g.h11): assert g.d[i][j][k]==(2 if len({i,j,k})==3 else 0)
    if name=='quintic': assert g.d==(((5,),),)
    if name=='bicubic': assert g.d==(((0,3),(3,3)),((3,3),(3,0)))

def test_reject_non_cy():
    with pytest.raises(ValueError): CICY('bad',(4,),((4,),),1,0)
