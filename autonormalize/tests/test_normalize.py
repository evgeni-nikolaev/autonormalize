import pandas as pd
from pandas.util.testing import assert_frame_equal

from autonormalize import classes, normalize

# from classes import Dependencies

# from normalize import normalize, find_most_comm, split_on_dep


def test_normalize():

    # how to test that relations remain the same???

    # check that there are no new relations?
    # there can be less however?
    dep_dic = {
        'A': [], 'B': [], 'C': [], 'D': [['F']],
        'E': [['A', 'B', 'C', 'D']], 'F': [['A', 'B']]}
    dep = classes.Dependencies(dep_dic)
    new = normalize.normalize(dep)
    dep_dic = dep.serialize()
    for x in new:
        assert x.find_trans_deps() == []
        assert x.find_partial_deps() == []
        dic = x.serialize()
        for rhs in dic:
            for lhs in dic[rhs]:
                assert lhs in dep_dic[rhs]


def test_find_most_comm():
    rels = [(set(['a']), 'b'), (set(['b']), 'c'), (set(['b']), 'a'),
            (set(['d']), 'a')]
    assert normalize.find_most_comm(rels) == set(['b'])
    rels = [(set(['a', 'c']), 'b'), (set(['b']), 'c'), (set(['b']), 'a'),
            (set(['d']), 'a'), (set(['a', 'c']), 'b')]
    assert normalize.find_most_comm(rels) == set(['b'])


def test_split_on_dep():
    dep_dic = {'A': [], 'B': [], 'C': [['A'], ['B']], 'D': [['B']]}
    new = normalize.split_on_dep(['B'], classes.Dependencies(dep_dic))
    assert new[0].serialize() == {'A': [], 'B': []}
    assert new[1].serialize() == {'B': [], 'C': [['B']], 'D': [['B']]}


def test_drop_primary_dups():
    df_dic = {"city": ['honolulu', 'boston', 'honolulu', 'dallas', 'seattle', 'honolulu', 'boston', 'honolulu', 'seattle', 'boston'],
              "state": ['HI', 'MA', 'HI', 'TX', 'WA', 'AL', 'MA', 'HI', 'WA', 'NA'],
              "is_liberal": [True, True, True, False, True, True, True, True, True, False]}
    df = pd.DataFrame(df_dic)
    dep_dic = {"city": [], "state": [["city"]], "is_liberal": [["city"]]}
    deps = classes.Dependencies(dep_dic)

    new_df = normalize.drop_primary_dups(df, deps)

    df_new_dic = {"city": ["boston", "dallas", "honolulu", "seattle"],
                  "state": ["MA", "TX", "HI", "WA"],
                  "is_liberal": [True, False, True, True]}
    assert_frame_equal(pd.DataFrame(df_new_dic), new_df)

    dep_dic = {"requires_light": [], "is_dark": [], "light_on": [["requires_light", "is_dark"]]}
    deps = classes.Dependencies(dep_dic)
    df = pd.DataFrame([[True, True, True], [True, True, True], [False, True, False],
                       [True, False, False], [True, False, False], [False, True, False], [True, False, True]],
                      columns=["requires_light", "is_dark", "light_on"])

    new_df = normalize.drop_primary_dups(df, deps)
    compare_df = pd.DataFrame([[True, False, False], [False, True, False], [True, True, True]],
                              columns=["requires_light", "is_dark", "light_on"])
    print(new_df)
    print(compare_df)
    assert_frame_equal(compare_df, new_df)