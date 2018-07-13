import hashdb.raw_reader

TEST_FILE = b"""\
0000000000000000000000000000000000000000:0
1111111111111111111111111111111111111111:1
2222222222222222222222222222222222222222:2
"""

TEST_FILE_2 = b"""\
1111111111111111111111111111111111111111:1
2222222222222222222222222222222222222222:2
3333333333333333333333333333333333333333:3
"""

def test_read_at():
    reader = hashdb.raw_reader.RawReader(TEST_FILE)
    assert reader.read_at(0) == (b'0000000000000000000000000000000000000000', b'0')
    assert reader.read_at(43) == (b'1111111111111111111111111111111111111111', b'1')
    assert reader.read_at(2*43) == (b'2222222222222222222222222222222222222222', b'2')

    reader = hashdb.raw_reader.RawReader(TEST_FILE.replace(b"\n", b"\r\n"))
    assert reader.read_at(0) == (b'0000000000000000000000000000000000000000', b'0')
    assert reader.read_at(44) == (b'1111111111111111111111111111111111111111', b'1')
    assert reader.read_at(2*44) == (b'2222222222222222222222222222222222222222', b'2')

def test_binsearch():
    for index in [False, True]:
        reader = hashdb.raw_reader.RawReader(TEST_FILE)
        if index:
            reader.build_index()
        assert reader.binsearch(b'0000000000000000000000000000000000000000') == 0
        assert reader.binsearch(b'0000000000000000000000000000000000000001') == 43
        assert reader.binsearch(b'1111111111111111111111111111111111111111') == 43
        assert reader.binsearch(b'1111111111111111111111111111111111111110') == 43
        assert reader.binsearch(b'2222222222222222222222222222222222222222') == 2*43
        assert reader.binsearch(b'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF') == 3*43

        reader = hashdb.raw_reader.RawReader(TEST_FILE_2)
        if index:
            reader.build_index()
        assert reader.binsearch(b'0000000000000000000000000000000000000000') == 0

def test_query():
    for index in [True, False]:
        reader = hashdb.raw_reader.RawReader(TEST_FILE)
        if index:
            reader.build_index()
        assert reader.query(b'0000000000000000000000000000000000000000') == b'0'
        assert reader.query(b'1111111111111111111111111111111111111111') == b'1'
        assert reader.query(b'2222222222222222222222222222222222222222') == b'2'
        assert reader.query(b'2222222222222222222222222222222222222223') == None

        reader = hashdb.raw_reader.RawReader(TEST_FILE_2)
        if index:
            reader.build_index()
        assert reader.query(b'0000000000000000000000000000000000000000') == None
